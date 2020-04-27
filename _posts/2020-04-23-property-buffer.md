---
layout: post
title: Property buffers for concurrent graph jobs
tag: [graph,pl]
---

刚好投完[SC](https://sc20.supercomputing.org/)，还是记录下这次想法的由来，也算是占坑了。简而言之，我们设计了一个并发图系统[Krill](https://github.com/chhzh123/Krill)，以支持在同一shared graph上面跑多个图算法/任务(job)。一开始只做了kernel fusion的runtime，而这一次则进一步从compiler层面实现了property fusion，从而最大程度提升访存局部性，大幅提升了并发图处理的性能。

<!--more-->

通过kernel fusion改变遍历顺序后一个很严峻的问题即在最内层循环需要不断访问不同任务的property data，而这些property data都封装在各自job的class中，意味着没有办法全部提取出来做布局优化，以提升访问局部性。核心问题在于job与job之间是**天然有隔阂**的，你没有办法很好地将这些property组织在一起。如果强行组织，那相当于硬编码，是毫无灵活性可言的。对于异步时间提交的任务，那就更加没有办法hard-code了。

那么我们要做的第一步就是要**打破这层隔阂**：将各个job的property全部拎出来，而不再是在job class内部声明。此为**decouple**，也是最基础的奠基工作。

有了奠基，那么具体怎么实现呢？想想如果对于每个job set都要用户自己重新写property data的组织，那这样解耦带来的麻烦事也太多了。既然用户没有办法亲自完成，那我们就可以尝试交由计算机来做——让计算机自己写property data的组织。此即rewriter，更通用的说法即compiler。毕竟编译器本来就是元编程的思想——**造一个能够帮自己写程序的程序**。这样的话，用户只要简单地描述他们的property组织方式，我们的compiler就可以将其编译为头文件，在原来的算法程序中直接通过调用API就可以访问数据，进而<u>原本算法不用改变，系统层面又可以对这些property进行重新组织</u>。

为了快速实现原型，我先用C++写了个想要生成的代码样例，然后在Python里对照着写codegen。至于前端语言则是我们提出的property buffer description，用类似C/C++的语法声明就可以了。像下面就是一个BFS的property data的声明方式。
```csharp
property BFS {
    int Parent;
}
```

期望生成下面的头文件组织。
```cpp
// BFS.pb.h
namespace BFS_Prop {
class Parent {
public:
    Parent(size_t n); // # of vertices
    ~Parent();
    int get(int i);
    void set(int i, int val);
private:
    int* data;
};
}
```

通过简单的尝试发现这样子可行，源程序基本不用改动，只是将访问数据的部分转换成`get`和`set`语法。

当然为了支持不同property data的**统一管理**，我们还需要生成一个`PropertyManager`的类，里面有对应的构造析构函数。而且这也相当自然地，支持runtime的动态内存分配，只要用户调用`add_Parent`语句，在`PropertyManager`中就会自行计数，当所有任务声明完成后调用`initialize`方法，即可实现统一初始化。

按照这个逻辑写好前端parser和后端codegen的架构后，就可以自由探索不同的**数据布局**了，比如统一`malloc`、property fusion等等。

另外一方面，你会发现这种decouple的方式实在太好用了，几乎所有的图系统都可以采用这种方法并入我的property buffer中，毕竟只要加一个头文件，然后对相应的数据访问API进行修改。所以它也能无缝衔接入**分布式系统**，并且打包property data的方式也方便数据传输，可以有效减少通信代价。

最终做出来的效果确实也如预期，大大减少了我的工作量，同时也对原本的runtime性能做了进一步的提升。

--------------------------

这次提出property buffer的经历有点Eureka moment的感觉，但更多还是水到渠成。Eureka的点在于发现自己走在一条正确的路子上，似乎能踩上前人的脚印。大概也就能理解之前system会议上很多看似平淡无奇的想法其实都不是拍脑袋想出来的，而是实际问题导向的。就像decouple，并不是所有应用都可以做这样的decouple，也不是别人做decouple你要去做；而是正好写到那里感觉麻烦，思索了一下发现decouple出来才是最优解，然后才去做decouple。所以如果没有自己亲身大量实践写过类似的代码，是不会明白为什么现在很多DSL都推崇decouple出各个组分的。

当然这次的想法得益于最近一段时间一直在看编译、编程语言相关的工作，包括[TVM]({% post_url 2020-03-26-tvm-overview %})、[DSL]({% post_url 2020-03-19-dsl-revisit %})、[静态程序分析]({% post_url 2020-03-24-spa-nju %})等。像Halide[^1]和TVM[^2]提供了最初的schedule和algorithm decouple的方式，而GraphIt[^4]将其拓展到图计算领域；Taichi[^5]和HeteroCL[^3]则针对data structure和algorithm进行decouple，这些都是非常棒的工作。

另一方面也得益于上个学期各种大杂烩的课程，虽然这种一个学期十几门硬课的填鸭式教学模式让我们学得生不如死，但是不得不说，这种不同领域思想的交互还是给了我很大启发。特别是上学期分布式系统和计算机图形学的课程，使很多看上去不相干的东西都交织在一起了。

分布式系统的课程其中有个作业是远程过程调用[gRPC](https://github.com/chhzh123/Assignments/blob/master/DistributedSystems/HW3/main.pdf)，需要采用[Protocol Buffer](https://developers.google.com/protocol-buffers/docs/cpptutorial)进行数据传输。虽然是一个很简单的作业，但是当时就觉得这个机制真的神奇，居然是生成头文件（Python则是库文件）和对应的类让你去链接编译（有点reflection的概念在），运行时PB就会自动帮你将数据进行编码/序列化打包。同时支持client-server通信，以同样的方式编码解码进而不用像写[套接字](https://github.com/chhzh123/Assignments/blob/master/ComputerNetworking/Lab3-Socket_Programming-II/client.c)一样自己算所需的buffer大小。这种方式可以最大程度减少用户对源代码的修改，又支持运行时的数据优化，同时还支持异步数据传输，可谓是系统设计的典范，因而这也就促使我们提出property buffer compiler，以对property data实现类似的功能。（顺带一提，在翻PB的源码时发现第一版的代码居然有Jeff Dean的名字，真的强。）

还有则是想起上学期被计算机图形学支配的恐惧。一个简单的OpenGL shader调了一个多星期终于调通，虽然图形学理论没多大长进，但是对OpenGL的编译原理倒是看了不少。印象最深的就是直接在C程序中写一段shader代码，然后在程序**内部**调用shader编译器来对其进行编译链接，参见[shader.c](https://github.com/chhzh123/Assignments/blob/master/ComputerGraphics/Homework3/shader.c)。这其实有点像现在TVM的机制了，只不过TVM封装得更加漂亮，用户几乎没有感知，毕竟就是在Python里调用`build`一下就完了。那我们现在提出的property buffer也类似于这种机制，需要经过两层编译，但实际buffer的生成却是在runtime完成的。

最后一点体会则是一定要自己**亲自去尝试**一下，而不要只是空想。我一开始也挺纠结到底要不要做这样的一个compiler，毕竟还是有一定工程量的，如果做出来反倒负优化了性能，那岂不是得不偿失。不过最后有点破釜沉舟的心态了，想着就去试试吧，不成对原本的论文也没有多大影响。所以一开始也没有提前跟导师说想法，而是先自己实施了。结果花一天时间写出来之后还真的成了，至少性能跟原来相比没有下降，再接着添加其他优化，就会发现欸这种思路居然顺带着还带来其他大量的好处。

去年提出kernel fusion的时候只是因为自己对compiler没有多少了解，所以直接在框架runtime层面进行了实施。事实上kernel fusion（事实上和loop fusion差不多）就应该在compiler里面实现。然后会发现自己写language和compiler其实比直接用C++的metaprogramming爽多了，后者水太深且没有办法做特定优化，而自己造轮子基本上是想干什么就干什么，完全是开启了新世界。

既然有了简易的property buffer，那之后的研究方向其实就有很多了，比如：
* 类似于Taichi的平展数据结构，以支持更复杂的层次化结构图应用。
* 完整的language for graph processing，包括compute和property declaration两个部分。当然需要与GraphIt做一个区分，比如对类似database的query的支持。
* 更优的数据访问模式，SIMD。
* 自动调优数据结构，auto-tuning的思路。
* ...

不管论文结果怎样，这次的project算是一次完整的工程实践了，既熟悉了各种自动化编译工具的使用，又让我更加深入了解C++/Python的一些语法实现；加上实验的Makefile代码，这个project也破万行代码了。使用各种语言打码创造自己想创造的东西的过程让我深刻体会到**全栈式优化**的乐趣，这也是我对system optimization如此痴迷的原因吧:)

## Reference
[^1]: Jonathan Ragan-Kelley (MIT), Connelly Barnes, Andrew Adams, Sylvain Paris, Frédo Durand, and Saman Amarasinghe, *Halide: A Language and Compiler for Optimizing Parallelism, Locality, and Recomputation in Image Processing Pipelines*, PLDI, 2013
[^2]: Tianqi Chen (UW), Thierry Moreau, Ziheng Jiang, Lianmin Zheng, Eddie Yan, Arvind Krishnamurthy, et al., *TVM: An Automated End-to-End Optimizing Compiler for Deep Learning*, OSDI, 2018
[^3]: Yi-Hsiang Lai (Cornell), Yuze Chi, Yuwei Hu, Jie Wang, Cody Hao Yu, Yuan Zhou, Jason Cong, Zhiru Zhang, *HeteroCL: A Multi-Paradigm Programming Infrastructure for Software-Defined Reconfigurable Computing*, FPGA, 2019
[^4]: Yunming Zhang (MIT), Mengjiao Yang, Riyadh Baghdadi, Shoaib Kamil, Julian Shun, Saman Amarasinghe, *GraphIt: A High-Performance Graph DSL*, OOPSLA, 2018
[^5]: Yuanming Hu (MIT), Tzu-Mao Li, Luke Anderson, Jonathan Ragan-Kelley, Frédo Durand, *Taichi: A Language for High-Performance Computation on Spatially Sparse Data Structures*, SIGGRAPH Asia, 2019