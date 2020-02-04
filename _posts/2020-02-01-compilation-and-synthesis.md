---
layout: post
title: 程序综合与编译
tags: [compiler]
---

程序综合(synthesis)和程序编译(compilation)常常会被混淆。我们大多数人熟知的是**编译**，比如<u>将C++代码编译为x86汇编</u>；而在FPGA中我们更多会采用**综合**一词，比如<u>高层次综合、逻辑综合、物理综合</u>等等。两者工作似乎都是将一种语言翻译为另一种语言，但事实上仔细分析一下还是有很多区别。

<!--more-->

粗略地来讲，编译器仅仅做了一个翻译的功能，即高级语言只是描述了要做什么(**what**)任务（传统的C/C++/Java等编程语言大多是命令式编程）；而综合器做的事情则更多，它还需要去探索怎么(**how**)去执行这个任务。

区别两者一个很重要的特征在于有无搜索(search)的过程。编译器通常是将一个预定义的调度(schedule)进行转换，而综合器则是根据程序的描述找到一个最优的调度来满足需求。不过事实上，很多现代的编译器都已经具备有自动优化(autotuning)的功能，比如[TVM]({% post_url 2019-02-08-TVM %})，因此编译与综合的界限其实在逐渐模糊。

另外，程序综合也很像机器学习。仔细思考一下现在的机器学习，其实也是一个程序到程序的映射，或者说我们一开始写的就是元程序(metaprogram)。大多机器学习算法都包括训练(training)和推断(inference)两个过程，训练实际上就是读入源程序然后进行优化/综合的过程，把其中未确定的参数给确定下来，进而得到最终的程序/模型；而推断则是利用训练好的**确定的程序**运行得到结果。

那么到底什么是程序综合？

> Program Synthes is correspond to a class of techniques that are able to generate a program from a collection of artifacts that establish semantic and syntactic requirements for the generated code.

现在的程序综合研究主要关注以下几个方面：
* 从高层描述中自动生成算法
* 将综合技术应用在广泛的问题上面，比如Excel的自动填充[FlashFill]、代码自动打分等
* 逆向工程，低层实现转为高层等价表示，如将Java转为SQL

而高层次综合(HLS)同样是给出是什么(what)，然后综合器告知应该怎么做。HLS和传统编译的区别可见[该文]({% post_url 2019-02-12-hls %})。

## 参考资料
1. [Armando Solar-Lezama](http://people.csail.mit.edu/asolar/) (MIT), *Introduction to Program Synthesis* - [Lecture 1](http://people.csail.mit.edu/asolar/SynthesisCourse/Lecture1.htm), 2018