---
layout: post
title: 软件2.0时代与TVM
tags: [dl,system]
---

最近重读了一些文章，感觉对深度学习又有了一些更加深层次的理解。

<!--more-->

在过去，我们在ACM/OI比赛或者程设/算法课上写的大多数程序都是**确定性的**，我们用这些程序写算法，然后通过编译器把<font color="red">算法</font>编译成<font color="red">机器指令</font>在硬件上执行。

而现在，深度学习的出现改变了这种范式，看上去我们依然还是在写程序，程序还是在机器上跑。但是仔细想想，不是这样的，事实上我们已经高了一层。我们现在做的已经算某种意义上的元编程(metaprogramming)了，我们在写深度学习模型时，实际上编写了一个**能够自己写程序的程序**。

为什么这样说？因为现在我们真正做的，是写一个带参数的模型[源程序]，然后把它优化[编译]，得到一个新的带参数的模型[目标程序]，而我们输入的是<font color="red">训练数据</font>，输出的是<font color="red">学习的参数</font>。事实上我们在训练(training)的过程中做的就是将一个**不确定的**程序编译成另一个程序，而推断(inference)才是传统意义上确定性的程序。其实这里用**阶数(order)**可能更加合适，传统我们写的是一阶程序$P_0$，直接喂输入数据出结果；而深度学习写的是**高阶程序**，是一个程序不断更新迭代发生变化的过程

$$P_0\to P_1\to\cdots\to P_n$$

我们每一轮迭代得到的都是一个新的程序（因为程序/模型参数不同），直到最后优化过程收敛，我们才得到最终的程序$P_n$，至此才进入到喂输入得输出（推理）的过程。这就是现在所谓的可微编程(differential programming)，要确保程序中的每一个算子/primative都是可微的，这样的迭代过程才有办法进行下去。

因此，从编程语言的角度看，事实上我们的**编程范式**已经发生改变，我们已经从软件1.0时代进化到**软件2.0时代**，只是很多人仍没有这种察觉。

![software 2.0](https://github.com/chhzh123/ToolsSeminar-CS/raw/master/Week07-MachineLearning/fig/ml_today.png)

而从上面的叙述中，我们也会发现，在软件2.0时代，<u>深度学习模型</u>和<u>程序</u>并无二义，**深度学习模型就等同于程序**，我们要优化程序性能，实际上就是在优化模型；以前我们设计更好的算法/程序，现在我们设计更好的模型。（当然这里某种程度上混淆了深度学习与机器学习，只是现在深度学习已经占据了机器学习的半壁江山，所以才特别以深度学习作为例子方便叙述。）

那么进一步地，程序需要编译才能运行，深度学习模型同样需要编译。优化相当于**横向编译**，由源程序$P_0$迭代到目标程序$P_n$，而得到的这个目标程序，也要编译才能在现实的机器上跑起来，我们可以称之为**纵向编译**。注意到程序形式已经发生了根本性的变化，我们现在的程序已经变成了深度学习模型，是一个**特定领域的程序**，因此对于这一特定领域的程序，其实我们是可以做更多特定的优化的，这也是为什么我们有了TensorFlow和PyTorch等一众深度学习框架后，这两年深度学习编译器又带起了浪潮。

这样看来TVM真的是一个相当有前瞻性的项目，它早早就提出了深度学习编译器。跟传统编译流程做一个对照就可以得到下表，某种程度上现在的深度学习框架就是领域特定编程语言 (DSL)，因为他只提供了规范 (specification)，而不提供具体的算法/模型实施。

| 抽象Spec | 编程语言 (C/C++/...) | DL框架 (TF/PyTorch/...) |
| :--: | :--: | :--: |
| 实体 | 算法程序 | DL模型 |
| 中间表示 | LLVM IR | Relay |
| 编译优化 | LLVM | TVM |
| 后端硬件 | CPU/GPU/FPGA | CPU/GPU/FPGA/TPU |

有了编程语言才会有编译器，深度学习领域也是如此。而各种编程语言又种类繁多，后端硬件也不断涌现，不同的指令集架构都可以算是一种CPU，这给不同语言的编译器、算法设计师都带来很大的负担，因此21世纪初编译器领域最大的成就就是提出了LLVM (Low-Level Virtual Machine)，使得各种语言只要接入LLVM，进行类似的优化Pass，然后就可以输出到不同后端硬件（后端硬件接入优化也是同理）。各种编程语言提出了几十年，人们才想到了这么绝妙的想法；而现在深度学习领域框架层的竞争基本大局已定，TVM此时入场正是一个好时候。

至于深度学习框架大多都采用计算图(computational graph)作为抽象（相当于传统编译领域里的数据流(dataflow)图），TensorFlow是静态图，表达力低下但优化效率高；而PyTorch是动态图，表达力高又优化效率低。因此是需要有一种新的抽象，能够灵活高效地表达各种深度学习算子，同时也便于优化。

第一版TVM用的是NVMM的中间表示，支持更细粒度的算子表达(operator-level)，而不是深度学习框架使用的图层面(graph-level)的算子，这也是借鉴了LLVM Low-level的思想，一个结点就代表一个作用在张量或者程序输入的算子，而边则是它们之间的数据依赖关系，进而可以做更加细粒度的编译优化，比如各种循环优化及算子融合。

这里的算子看上去没什么可优化的，但其实不是这样，深度学习中大量的算子其实都是复杂的规则循环，而这些用传统的Polyhedron也可以做大量的优化。比如说一个矩阵乘法简单的实现就相当于三重循环，但是循环体怎么排布，每一层循环多少格这些都是可以进行优化的。

```cpp
for (int i = 0; i < m; i++)
    for (int j = 0; j < n; j++)
        for (int k = 0; k < l; k++)
            c[i][k] += a[i][j] * b[j][k]
```

上面所说的涵盖了深度学习的大部分情况，但我们会发现这里遗漏了很关键的一点，即**对控制流的支持**。我们做编译或者综合的人就知道，无论是数据流还是控制流，对程序来说都是非常重要的组成部分。不支持控制语句的编程语言没有办法做到图灵完备，某种意义上也是瘸脚的。因此在TVM新一轮迭代中，他们提出了新的中间表示Relay，真正的low-level IR，真正去弥合表达力和效率，同时也像LLVM一样放出了自定义Pass方便程序员做优化工作。

尽管TVM现在还在开发中，但是它一定是大势所趋。它是软件2.0时代的编译器，结合了当今最前沿的编译技术（其实现在应该叫[编译综合]({% post_url 2020-02-01-compilation-and-synthesis %})了）。就像LLVM出现后，C/C++还有之后各种语言都会留前端给LLVM一样，现在各大厂也都给了TVM支持，[TVM Conf](https://sampl.cs.washington.edu/tvmconf/)也越做越大。LLVM是教科书的样例，现在做编译优化的无人不知LLVM，也是各种高级编译原理课程必学的工具之一；可以预见未来TVM也会奠定这样的格局。

## Related Problems
另外关于几个相关问题，这里放出我的理解。

* Q1：为什么目前TVM主要针对预训练模型，即针对推理部分进行编译优化？<br/>
A：训练多了dropout这些概率层，更使模型/程序难优化，很多原有的优化pass都用不了；但现在TVM也已经在着手训练方面的工作，估计在1.0版本正式发布之时TVM也可以优化训练模型了。

* Q2：预训练模型中的参数TVM是怎么处理的？<br/>
A：以PyTorch的模型为例，实际上它的参数都已经包含在`Model`类中了，因此估计TVM只需将其分离出来即可。

* Q2：TVM的输出中为什么还会包括新的参数？<br/>
A：TVM的优化Pass会根据不同后端硬件改变数据layout，但参数内容不会改变。这和传统编译是一样的，你至少要保证程序的正确性。

## References
* Kunle Olukutun, *Designing Computer Systems for Software 2.0*, ISCA'19 Keynote
* Tensor Virtual Machine (TVM), <https://tvm.ai/>
* Tianqi Chen, Thierry Moreau, Ziheng Jiang, Lianmin Zheng, Eddie Yan, Meghan Cowan, Haichen Shen, Leyuan Wang, Yuwei Hu, Luis Ceze, Carlos Guestrin, Arvind Krishnamurthy, *TVM: An Automated End-to-End Optimizing Compiler for Deep Learning*, OSDI, 2019
* <http://colah.github.io/posts/2015-09-NN-Types-FP/>