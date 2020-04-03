---
layout: post
title: TVM Overview
tags: [dl, tvm]
---

时隔一年再回来看TVM，诸多感受。

<!--more-->

在这一年我做其他方面工作的时间里，某种意义上已经错失了做深度学习编译器的良机。TVM的坑早早挖出来，第一批研究的学者已经在自动调度[FlexTensor ASPLOS'20]、CPU推断[NeoCPU ATC'19]、异构计算平台[HeteroCL FPGA'19]等方面做出了一定的成果，所以现在入坑似乎已经有点晚了。但看看TVM这一年的飞速发展，现在v0.7版本将要发布，Relay IR的提出、VTA编译的更多支持、异构图划分，各大[厂商](https://tvm.apache.org/community)（亚马逊、阿里巴巴、华为、Intel等）及高校（UW、Cornell、UCB、UCLA等）的支持，Apache基金会的加持，[Github项目](https://github.com/apache/incubator-tvm/)的持续更新，开源社区的不断壮大，两次[TVM Conference](https://tvmconf.org/)的举办，都意味着TVM这个平台的愈发成熟，而不是一个demo project轻易就会消亡。因此，从这个角度上来说，在项目发展中期入坑依然可以探索出很多工作，而且文档逐步完善也避免了走大量弯路。未来TVM很有可能成为深度学习时代一个不可获取的工具，不管是将其作为一个工具使用，或是将其作为研究对象都是不错的选择。

第一代的TVM以NNVM作为前端编译器，将不同框架编写的模型以统一的格式映射到NNVM的计算图上，然后再对计算图进行优化进入到TVM，最后经由TVM输出后端代码，整体流程如下图所示。
![NNVM](https://tvm.apache.org/images/nnvm/nnvm_compiler_stack.png)

而第二代的NNVM则是将Relay IR作为前端，提供了更为<u>简洁的文本形式</u>，<u>强类型系统</u>，增添了对<u>控制流的支持</u>，同时支持<u>自动微分</u>(automatic differentiation, AD)及<u>异构编译</u>（需要手动划分）。

{% include image.html fig="TVM/tvm-overview.jpg" width="80" %}

总体编译流程可见[TVM-代码生成流程]({% post_url 2020-03-26-tvm-flow %})。简而言之分为以下几个步骤：
1. Relay将不同框架读入的模型转换为Relay IR
2. **计算图层面**(graph-level)的优化（比如整个神经网络）
3. 生成优化后的计算图送入TVM
4. **算子层面**(operator-level)的优化（比如一个卷积算子）
5. 对每一算子lower，生成后端代码

传统的深度学习框架如PyTorch和TensorFlow往往只在计算图层面进行优化，很难做到适配不同硬件的优化（计算图结点并没有告知该算子如何实施）。而TVM则是更深入到算子层面，因此优化粒度更细，可以针对不同硬件特性来做优化（比如说在CPU上用AVX做并行），这也是TVM这种深度学习**编译器**能够胜过之前深度学习**框架**的原因。

另一方面，在算子层面TVM还引入了AutoTVM进行自动调参，虽然还没达到AutoSchedule的级别，但是已经能够很好地针对不同硬件进行schedule的**参数**调整了。这也相当于TVM将ML和system双向打通，既是system for ML，也用到了ML for system来做优化，两者相辅相成，最终才能达到这么好的效果。

再看一下天奇在第二届TVM Conf的报告[*TVM: Where are we going*](https://tvmconf.org/slides/2019/tvmconf-keynote-dec19.pdf)，就会发现TVM的全栈真的不是开玩笑的，应该整个UW CS系都投入其中了，现在他们着手在以下几个点：
* Relay虚拟机：用来处理动态计算图（如有递归和循环的图结构）
* $\mu$TVM：在边缘端无需OS的运行时系统，自动与AutoTVM进行交互
    {% include image.html fig="TVM/mu-tvm.jpg" width="100" %}
* VTA：第二代已经用Chisel进行实现
    {% include image.html fig="TVM/vta-stack.jpg" width="100" %}
* TSIM：自研硬件模拟器
    {% include image.html fig="TVM/tsim.jpg" width="100" %}
* 大一统运行时：不同设备的runtime都可以用Python直接call，所以所有工作都可以在直接TVM内完成（似乎现在已经实现了大半）
* 大一统的IR：类似谷歌[MLIR](https://mlir.llvm.org/)的工作，弥合高层和低层的IR表示，也即现在的Relay IR和底层TVM用的Tensor Expression
* 全栈自动化：现在AutoTVM只是在TVM算子的实现部分对schedule的参数进行搜索，希望做到对IR本身或者Schedule本身也进行自动化搜索
* 其他：量化、低精度、训练支持、自动微分等

所以事实上TVM给了很多科研人员大量的研究空间，为深度学习系统架构的研究铺平了道路。最关键是它的所有代码都是开源的，因此从源代码入手也可以着手很多底层的工作。