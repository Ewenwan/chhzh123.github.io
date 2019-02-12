---
layout: post
title: 高级编程语言vs硬件描述语言
tag: pl
---

很多老师都将硬件描述语言当成一门编程语言来教，我本人也一直认为硬件描述语言与传统的编程语言类似，只不过添加了时序特征。
但其实这都是非常不正确的，硬件描述语言并不同于传统的编程语言，它更多是所见即所得--用于**描述**硬件功能，而不是告知程序如何运行...

<!--more-->

## 对比
* 高级**编程**语言(High-Level Programming Language, HLL)大家都比较熟悉，如C/C++/Java/Python等等都属于这个范畴，它告诉计算机程序的执行过程，即**怎么做(how)**
* 硬件**描述**语言(Hardware Description Language, HDL)重点则在于**描述**，目前主流的有Verilog和VHDL，它告诉计算机电路图的模样/电路图是怎么连的（输入输出端口、连接方式等），即**是什么(what)**

虽然Verilog语法与C类似（就像很多伪代码也会用类C的语法，会用`//`作为注释符等等），但它们本质上是完全不同的，也就是前面所说的要区分**编程**与**描述**两者之间的差异。

* HDL与HLL最大的区别在于HDL显性包含了**时间**的语义，但HLL是没有的，这也是HLS关键要处理的一个问题。
* HLL是过程性的(procedural)，更HDL更多包含了并行(concurrency)的元素
* HLL编译后将产生一条条指令，而HDL编译后则直接变成一个个门

三种硬件描述语言的形式
1. 结构化模型(structural modeling)：照着**原理图**(schematic)给出元件名，是什么，输入输出是什么
	- 例化 `and U1 (c,a,b)`
2. 数据流模型(dataflow modeling)：直接给出输入与输出的**逻辑表达式**
	- 连续赋值 `assign y=(a&b)|(~c)`
3. 行为模型(behavior modeling)：
	- 真值表 `case`

## 历史
* 1971，引入RTL及第一门有影响力的HDL(Golden Bell)
* 1985，第一门现代的HDL Verilog诞生(Gateway Design Automation)
* 1987，VHDL(US Department of Defense)

## 现状
由前面的历史可以知道Verilog最开始是被设计为一门模拟(simulation)的语言，用于debug因而赋予了更多功能，但这些testbench是不会放入板上的；
而不是用于综合(synthesis)，即它是一个可综合语义的超集(superset of synthesizable syntax)。

因而这样的语言在编写过程中会出现很多问题，后面才会出现更多新的语言。
下面主要提及两个，一个是UCB设计的[Chisel](https://chisel.eecs.berkeley.edu/)，另一个是Stanford设计的[Spatial](https://spatial-lang.org/)。

### Chisel
Chisel (Constructing Hardware In a Scala Embedded Language)

传统HDL的缺点：
* 可综合部分必须从语言当中推断
* 缺少现代语言的抽象设施
* 需要大量进行设计空间探索(design space exploration, DSE)，但难以参数化

解决方法有：
* 采用宏(macro)语言（如Perl, Python），自动生成大量重复的模块；但这实际上只是简单的替代，且需要大量人工编写优化的替代文本，根本没有考虑到硬件的类型及语义
* 领域专用语言，但不通用

因而采用嵌入宿主语言的方案。

### Spatial
Spatial (Specify Parameterized Accelerators Through Inordinately Abstract Language)

#### 简介
* C/C++并不适合用作硬件综合语言，因无法显式控制内存、无法并行（不加并行库）
* Chisel寄于Scala做了抽象，具有强大的元编程能力，但依然是在有时序的电路层进行电路设计

HDL
* 性能(performance)高：能够生成任意RTL结构
* 生产力(productivity)低：没有高层抽象
* 可移植性(portability)低：大量针对目标硬件的(target-specific)程序

HLS (C+Pragmas)
* 性能低：无法处理内存层级结构，不能处理任意流水
* 生产力一般：可以处理嵌套循环，但混杂着软件和硬件的特性(ac-hoc mix of sw/hw)，且难优化
* 可移植性：针对单一生产商

> Rethink outside of the C box for HLS

一门好的高层硬件语言应该可以
* 依赖分支、嵌套循环
* 存储层次结构
    - 片外(DRAM)
    - 片上(BRAM)
    - 寄存器
* 异构主机接口(host interfaces)
* 设计空间探索

#### 语法
![Experimental results]({{"/assets/images/TVM/Spatial-syntax.PNG"|absolute_url}})

#### 编译器
Scala写的编译器，编译到Chisel
![Spatial passes]({{"/assets/images/TVM/Spatial-passes.PNG"|absolute_url}})
HyperMapper调参

## 参考资料
1. 硬件描述语言的可综合性是什么？如何保证它的实现？ - 林名的回答 - 知乎 <https://www.zhihu.com/question/263578952/answer/295405073>
2. Hardware Description Language, <https://en.wikipedia.org/wiki/Hardware_description_language>
3. Register-Transfer Level, <https://en.wikipedia.org/wiki/Register-transfer_level>
4. <https://www.design-reuse.com/articles/7330/fpga-programming-step-by-step.html>
5. 串讲数字电路与系统设计之一：三种硬件描述语言的形式 - 其实我是老莫的文章 - 知乎 <https://zhuanlan.zhihu.com/p/51477553>
6. Jonathan Bachrach, et al., Chisel: Constructing Hardware in a Scala Embedded Language, DAC, 2012
7. David Koeplinger, et al., Spatial: A Language and Compiler for Application Accelerators, PLDI, 2018