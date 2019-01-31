---
layout: post
title: 深度学习框架与图分析框架的异同
---

### 什么是框架(Framework)？
* 对某个**特定领域**的**各种**算法进行**抽象**
* 抽取其中**大量重复**利用的单元成为**算子**
* 在**现有**编程语言（Python/C++）基础上提供**API接口**
* 注意尚未达到编程语言的级别，如果连语法语义也一并规定，那就变成领域特定语言(Domain Specific Language, DSL)

| | 深度学习框架 | 图框架 |
| :---: | :---: | :---: |
| 算子 | 卷积conv<br/>池化pooling<br/>激活relu | 收集gather<br/>应用apply<br/>分发scatter |
| 自定义函数 | `forward` | `process_message` |
| 现有框架 | [Pregel (Google)](https://kowshik.github.io/JPregel/)<br/> [Giraph (Facebook)](http://giraph.apache.org/)<br/> [Spark (Apache)](https://spark.apache.org/graphx/) | [Tensorflow (Google)](https://www.tensorflow.org/)<br/> [Pytorch (Facebook)](https://pytorch.org/)<br/> [MXNet (Amazon)](https://mxnet.apache.org/) |

注意上表中的内容只是举例，还有很多算子、函数和框架并未列出

### 框架的好处
* 统一算子并提供API，在这些算子的基础上搭建上层建筑就好（有点C++标准库的感觉）
* 一定程度上规定了用户的行为，优化变得简单，只需对算子进行优化即可
* 可以利用自己熟悉的语言进行操作，无需学习新的语法语义；所谓调包实际上也是这个道理，因为只用查API就可以快速实现算法

### 抽象的抽象！
框架是对所有领域特定算法的抽象，那对各种框架再做一层抽象会变成什么...

<center><b><p style="font-size:120%">全栈编译器(compiler stack)！</p></b></center>


* 深度学习框架大一统的编译器：[TVM (Tensor Virtual Machine)](https://tvm.ai/)

作用是将**不同深度学习框架**上写的模型，映射到**不同的硬件**上（下图来自陈天奇在TVM Conference上的[演讲](https://sampl.cs.washington.edu/tvmconf/slides/Tianqi-Chen-TVM-Stack-Overview.pdf)
![TVM Overview]({{"/assets/images/TVM/TVM-Compiler-Stack.PNG"|absolute_url}})

<!-- 训练好的模型(model)，需要具体实施到硬件上跑推断(inference)，那么怎么实现这些操作就显得十分关键 -->
<!-- 图层面（粗粒度）的优化和算子（细粒度）的优化 -->

	> TODO TVM挖坑之后填((( 顺带要解释啥是虚拟机，llvm为啥也是虚拟机

* 图框架大一统的编译器：？？？

这是一个无人涉足的领域...

相对于深度学习应用，图应用的不规则程度高，导致算子的抽取更加困难。
其实现在的图框架做的抽象都不那么好，虽说图计算的存算比高，但算子粒度还是太大了，导致比较难做优化。

### 说到编程语言...
很诡异的是机器学习界居然没有人想要造一门新的DSL，猜想可能的原因：
* Python大法好！
* 写Tensorflow几乎就在写一门新的语言...

而图分析这边，CSAIL在2018年发了OOPSLA，正式提出[GraphIt](http://graphit-lang.org/)（写文章的时候查了一下[Github](https://github.com/GraphIt-DSL/graphit)上的热度，似乎有点火...）

	> TODO GraphIt是个啥，居然比原有state-of-the-art的框架性能高出一个数量级？？？

<!-- 新的编程语言/IR的好处
* 规范用户行为
* 更好进行编译优化 -->