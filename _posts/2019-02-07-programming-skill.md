---
layout: post
title: 何谓编程能力？
tag: [pl,arch,system,hidden]
---

因为现在开始做系统，所以对下面这篇文章深有感触，可装裱成文，每日一读！

> 本文转载自知乎[@圆角骑士魔理沙](https://www.zhihu.com/people/0251012c87c2d3f56ac34de7d71cdcbc) [什么才算是真正的编程能力？](https://www.zhihu.com/question/31034164/answer/553533545)

<!--more-->

0.**可以完全理解问题并给出代码**

往窄了点说，这就是acm在培养的东西。

并且这不能靠调api完全解决：有的时候，你的问题需要你把多个标准算法串一起。

比如说最近有个把STLC AST从implicit sharing变成explicit sharing的任务，这靠LCA+reverse topo dependency calculation（没这步LCA的时候scope跟着term一起被reorder了，根本做不出），最后接上metaocaml style letlist，搞定。

有的时候，根本没有任何API，需求是从一个算法改成另一个。比如说[D\*](https://link.zhihu.com/?target=https%3A//www.microsoft.com/en-us/research/wp-content/uploads/2016/02/main-65.pdf)算法复杂度是O(nv^3)的，很不好，我们想优化下，把复杂度往下降点，这一样没有任何包可以调。

往广了说，大一点的需求也能用这种能力。既然有‘[组合性](https://www.zhihu.com/question/34819931/answer/482024102)’这个概念，我们就能倒过来，给出一个大型问题，分解成多个子问题，各个被单独解决后再组合一起。

名书SICP里面就很推崇这种‘理解，分解，破解’的套路，而图灵奖得主Edward Dijkstra甚至更极端，认为这方法是唯一一种编程的方法。
无论这是不是唯一法，这能力都是很不可或缺的基本功。

当你掌握这方法以后，你会发现你做的很多是在脑袋中去推敲这问题的性质，试图分解这个问题，如果可以的话调用/组合已有API/算法。。
是不是很像数学？因为计算机程序在某种意义上就是Mathematical Object - Curry Howard Isomorphism/[Stepwise Refinement](https://zhuanlan.zhihu.com/p/20885133)/Program Calculation都是在说这个。
而当你把这套玩熟，如果你喜欢，甚至可以做到**正射必中**：对于给定问题，产生绝对正确的代码。
这不难理解嘛，毕竟都说了是数学对象了，证明一下就好了。

1.**能在0之上加上工程方法**

有时候这套方法不管用：比如说你跟其他人在已有code base上协作，比如说需求变更了，比如说你死活分解不出来，又比如说你根本不知道具体的需求，得慢慢探索。。
其实这问题本质是，软件实在太复杂了，一个数百万行代码的项目已经超越了人类物理意义上的理解极限 - 看都看不完。这也是为什么重头起编写一个系统很难：spec太复杂，各个组件的assumption太多，并且持续进化，不可能一口气搞定，就算给定各个预先写好的组件，也会因为assumption不match而难以组合在一起，只能通过不停的prototype，不停的重构，甚至不停的重写来加深对系统的理解。

在这之上，SICP的‘一次性理解法’已经失效，这时候就需要不精确，比起逻辑学更像生物学的技巧 - 软件工程了。

该怎么设计？

该怎么重构？

啥时候不重构而是顶着debt继续往前（不然会无限重构做不出东西来）？

该用啥技术？在各种tradeoff间如何选择？

再加上debugger/unit test/ci/git/integration test这些tool。。

这些（系统编程） [@h8liu](https://www.zhihu.com/question/31034164/answer/50423838) 说得很好了，就不多说了。

2.**对整个计算机stack有认识，把各种技能混着耍**

比如说，学过[计算机体系结构](https://www.zhihu.com/question/24975949/answer/370015097)，明白dennard scaling死掉后单线程已经上不去，GPU等massively parallel architecture是未来，然后给neural network迁移上GPU（deep learning）。

然后，会deep learning，发现这货给出的答案不一定是对的，但是可以当heuristic/hint，给传统方法加速（Alphago的MCTS（AI），Learn Indexed Structure中预测结果存在那（数据库），AutoTVM的快速评分（编译器），[DeepCoder](https://www.zhihu.com/question/56250357/answer/148934031)的降低搜索空间（Program Synthesis），Peloton的给数据库预测负载（数据库））

又或者，会FPGA，知道GPU之上还有很多优化空间，于是直接把整个matrix multiply fuse成电路（TPU），又或者会quantization，去研究怎么给quantized NN做ASIC（Bit Fusion）。

还有，会PL，发现Deep Learning的computation graph其实就是个first order PL，为了加入控制流（RNN/LSTM/TreeLSTM。。）以Lambda Cube为基础设计一个IR，再想办法在上面做反向传播，来做program optimization（TVM上的Relay）。

除了理解力到位，试图把未知的新工具用上已知领域，还有个更简单粗暴的用法：降低/消除低效接口带来的额外开销。

学了Memory Hierarchy以后，在用一个内存以前可以提前fetch，降低软件的memory access latency（prefetching）

如果有FPGA，可以把一部分任务schedule并offload上硬件，提高性能（Hardware/Software codesign）

有task要在docker里面跑？既然docker都有保护了，那还凭啥要跑一个有保护模式的OS，要多个address space并且不停在kernel/user上跑？Unikernel走起！

把这套玩到炉火纯青，还能像Midori这样，大手一挥，重新设计整个Software Stack，把里面的各种多余的抽象（protection类型系统给了，就不需要OS上搞）整合掉，爽不？

3.**对不理解的CS和数学知识能够在遇到的时候快速补起来**

计算机科学实在太广太深，学习中碰到不会的东西已经是很正常了，所以说能力中还有一部分是：在代码/paper中发现完全不会的定义，如何在最短时间内学习/跳过，并不影响后续理解/debug？

而这些概念不一定只有CS的，有时候还有数学，所以还要打好最低限度的数学基础，达到‘看到不认识的数学定义不会去手足失措而是能慢慢啃/推敲’。不过还好，用到的数学跟数学系的双比不深，挺喜欢的一篇paper，[Partially-Static Data as Free Extension of Algebras](https://link.zhihu.com/?target=https%3A//www.cl.cam.ac.uk/%7Ejdy22/papers/partially-static-data-as-free-extension-of-algebras.pdf) 也就用到了Free Algebra，属于很基础的抽象代数，并没深到那去，老板给我的paper，[Sampling Can Be Faster Than Optimization](https://link.zhihu.com/?target=https%3A//arxiv.org/abs/1811.08413v1) ，能抓出重点，搞懂Metropolis–Hastings跟MALA（Intro to Stats就会教了，很浅），然后明白主Theorem是啥，也就差不多了，毕竟CS水这么深，主次要分清，数学能抓多少就抓多少吧。。

**这些就是我所认为的不会随着时间而失效，也不能被体力劳动+调包取代的，真正的编程能力：**

* 不停扩充自己的toolbox，并对自己的tool或多或少有本质上的理解(Machine Learning/GPU Programming)
* 根据自己对这些工具的理解，想出新的组合法(Deep Learning)
* 把自己的idea构建成一个复杂，大而全的系统，而不仅仅是一个玩具(Pytorch)
* 落实到一个小功能的时候，能够通过算力，设计出一个好用的API，编写一个正确高效的实现(Reverse Mode Automatic Differentiation)

**如果要用一句话概况，我猜编程能力是“对不同复杂度的问题（领域级/系统级/问题级），采用相对应工具降低复杂度，最后击破”的能力吧。**