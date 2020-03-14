---
layout: post
title: 黄金时代！
tag: arch
---

本文内容节选自2017年图灵奖得主John Hennesy (Stanford)和David Patterson (UCB)在体系结构顶会ISCA'18的[lecture](https://www.youtube.com/watch?v=3LVeEjsn8Ts)

<center><b>
A New Golden Age for Computer Architecture:<br/>
Domain-Specific Hardware/Software Co-Design,<br/>
Enhanced Security, Open Instruction Sets, and Agile Chip Development<br/>
</b></center>

<!--more-->

## 历史
RISC vs CISC

这个放以后有时间再写。

## 现状
技术上的限制
* 登纳德缩放定律(Dennard scaling)的失效：能耗成为主要约束
* 摩尔定律(Moore's Law)日渐式微：晶体管数量提升减缓

结构上的限制
* 无法继续提升指令级并行，单机时代终结(2004)
* Amdahl定律以及它的推论终结简单的多核时代

## 未来
### 机会在哪？
* SW-centric
	- 现代的脚本语言都是被解释的、动态类型、重用性高
	- 便利于程序员但不利于执行
* HW-centric
	- 领域特定结构
	- 仅仅做了几项工作，但是效果非常好
* Combination!
	- 领域特定语言及结构

简单的Python乘法
* 用C写可提升47x
* 加并行循环366x
* 加内存优化6727x
* 加SIMD指令62806x

### 领域特定结构(DSA)
* 通过裁剪结构仅适合领域特征来提升性能
	- 并非一种应用，而是整个领域的应用
	- 需要更多领域特定知识
* 例子：
	- TPU、GPU、VR

为什么DSA能赢
* 更多高效并行
* 更好优化内存访问
* 消减不必要精度
* [领域特定编程语言]({% post_url 2019-02-12-dsl %})
	- OpenGL, Tensorflow, P4
	- 如果DSL维持无关结构特性，那么编译器设计将会很复杂，如Tensorflow的[XLA](https://developers.googleblog.com/2017/03/xla-tensorflow-compiled.html)

### 开放的指令集
RISC-V

### 安全
可验证的(verifiable)

### 敏捷开发(Agile HW)
* 云FPGA->所有人都能设计和定制化硬件：FireSim
* 敏捷硬件开发->所有人都可以支付得起制造小芯片：Chisel