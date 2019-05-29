---
layout: summary
title: 并行计算
date: 2019-05-20
---

这里简要介绍并行编程的一些基本概念，以及几种用于并行编程的工具/框架。

<!--more-->

## 并行程序基础
并行计算中最重要的即为Amdahl's law

$$\text{Speedup}=\frac{1}{(1-p)+p/n}$$

它给出了并行程序的加速比，其中$$p$$是可并行占用的时间比例，$$1-p$$为串行占用的时间比例，$$n$$为线程的数目。但太过乐观估计，没有考虑并行的开销，如创建线程等。

并发和并行的概念区分
* 并发(concurrency)：并没有明确的时间先后，可以同时执行（执行时段可重叠），如单核的多任务
* 并行(parallelism)：就是**同时**执行，如多核多线程

### SIMD
Single Instruction Multiple Data ([SIMD](https://www.codingame.com/playgrounds/283/sse-avx-vectorization/what-is-sse-and-avx))是提升CPU性能一个很重要的技术，即数据并行---在CPU内部添加向量寄存器
* Multi Media Extensions ([MMX](https://en.wikipedia.org/wiki/MMX_(instruction_set)))：Intel最早的SIMD尝试(1997)，于Pentium系列CPU
* Streaming SIMD Extensions ([SSE](https://en.wikipedia.org/wiki/Streaming_SIMD_Extensions))：最早在Pentium III引入，由SSE1到SSE4.2，均为128位寄存器
* Advanced Vector Extensions ([AVX](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions))：Intel Sandy bridge架构引入256位向量寄存器(2008)，后来又引入512位向量寄存器(2016)
    - `#include <immintrin.h>`
    - 详情见[AVX指令集]({% post_url 2019-03-03-AVX %})
    - AVX2: Haswell, 2011
![AVX-256](https://www.codingame.com/servlet/fileservlet?id=16426525647340)

## 并行编程模型
### 共享内存模型
* 任务之间共享一块通用的内存地址空间，无需显式进行通信
* 难以控制数据访问的局部性
* 有UMA(uniform memory access)和NUMA架构

并行程序可能出现的问题
* 线程创建开销
* 数据划分粒度
* 负载均衡
* 竞态(race condition, RC)问题处理

### 消息传递/分布式内存模型
* 每个任务有自己的私有地址空间
* 交流通过显式的消息传递

### 数据并行模型
* 结构化的计算
* 同样共享地址空间

### [Fork-join](https://en.wikipedia.org/wiki/Fork%E2%80%93join_model)
![fork-join](https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Fork_join.svg/400px-Fork_join.svg.png)
注意这里fork的东西是任务(task)或纤程(fiber/lightweight thread)，而不是线程

## 并行方法论
### 增量并行化
* 每次找最耗时的串行程序部分，将其改为并行

### Culler的设计方法
* 分解(decomposition)：将原问题分解为多个能被并行的子问题
    - 核心：确定依赖关系
* 指派(assignment)：将线程/工人分配到每一个子问题上
    - 负载均衡(load-balanced)
    - 减少通信开销
    - 可静态或动态，即调度
* 协调(orchestration)：不同线程间的交流
    - 减少通信/同步开销
    - 保留数据间的局部性
* 映射(mapping)：将并行执行逻辑对应到硬件资源上

### Foster的设计方法
* 划分(partition)
    - 按域/数据划分
    - 按功能/任务划分
* 通信(communication)
* 归并(agglomeration)
    - 将小人物合并为大任务，提升性能，减少编程工作量
* 映射(mapping)

## Tools
### [Pthreads](https://en.wikipedia.org/wiki/POSIX_Threads)
在POSIX(Portable Opearing System Interface for Unix)中，pthreads是关于线程的界面。
关于C/C++下pthreads的使用，可见[C/C++多线程]({% post_url 2019-03-14-cpp-multithreading %})。

注意：创建线程的开销依然很大，需要10k个量级的时钟周期，因此尽可能少创建线程，最好线程数等于核数。

### OpenMP
见[并行计算-OpenMP]({{ site.baseurl }}/summary/parallel-computing/openmp)

### Clik-Plus
见[并行计算-Clik]({{ site.baseurl }}/summary/parallel-computing/cilk)

### MPI
见[并行计算-MPI]({{ site.baseurl }}/summary/parallel-computing/mpi)

### [Intel TBB](https://software.intel.com/en-us/articles/migrate-your-application-to-use-openmp-or-intelr-tbb-instead-of-intelr-cilktm-plus?_ga=2.174275746.1279103381.1550824040-508775473.1544510410)
从Intel C++ Compiler 18.0开始Cilk Plus就被废除了，而交由MIT自己维护。
转而取代的是Intel Threading Building Blocks (TBB)
* `task_group t; t.run([](){ })`
* `t.wait()`
* `tbb::parallel_for()`