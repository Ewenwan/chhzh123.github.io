---
layout: post
title: 并行编程
tag: [tools, parallel]
---

这里简要介绍并行编程的一些基本概念，以及几种用于并行编程的工具/框架。

<!--more-->

## [Fork-join](https://en.wikipedia.org/wiki/Fork%E2%80%93join_model)
![fork-join](https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Fork_join.svg/400px-Fork_join.svg.png)
注意这里fork的东西是任务(task)或纤程(fiber/lightweight thread)，而不是线程

## [Work-stealing](https://en.wikipedia.org/wiki/Work_stealing)
有一个调度器，动态处理任务分配

## SIMD
Single Instruction Multiple Data ([SIMD](https://www.codingame.com/playgrounds/283/sse-avx-vectorization/what-is-sse-and-avx))是提升CPU性能一个很重要的技术，即数据并行---在CPU内部添加向量寄存器
* [MMX](https://en.wikipedia.org/wiki/MMX_(instruction_set))：Intel最早的SIMD尝试(1997)，于Pentium系列CPU
* Streaming SIMD Extensions ([SSE](https://en.wikipedia.org/wiki/Streaming_SIMD_Extensions))：最早在Pentium III引入，由SSE1到SSE4.2，均为128位寄存器
* Advanced Vector Extensions ([AVX](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions))：Intel Sandy bridge架构引入256位向量寄存器(2011)，后来又引入512位向量寄存器(2016)
    - `#include <immintrin.h>`
    - 之后有空再开文讲
![AVX-256](https://www.codingame.com/servlet/fileservlet?id=16426525647340)

## Tools
### [Cilk Plus](https://www.cilkplus.org/)
一个非常轻量的并行编程框架，仅仅添加了三个[关键词](https://www.cilkplus.org/tutorial-cilk-plus-keywords)
* `#include <cilk/cilk.h>`
* `cilk_spawn`：等价于`fork`，并不是重新产生线程，而是说可以继续执行(continuation)
* `cilk_sync`：等价于`join`，同步设施
* `cilk_for`：更加好的运行时/调度系统

```cpp
int fib(int n)
{
    if (n < 2)
        return n;
    int x = fib(n-1);
    int y = fib(n-2);
    return x + y;
}

// parallelism
int fib(int n)
{
    if (n < 2)
        return n;
    int x = cilk_spawn fib(n-1);
    int y = fib(n-2);
    cilk_sync;
    return x + y;
}
```

采用spawn-sync的例子
![spawn-sync](https://www.cilkplus.org/sites/cilk/images/for_cilk_spawn_dag.png)

采用`cilk_for`
![cilk_for](https://www.cilkplus.org/sites/cilk/images/cilk_for_dag.png)

注意Cilk Plus是一种编程模型，有几种工具都支持
* [Intel Cilk Plus](https://www.cilkplus.org/)
    - `icpc -O3 <source>`
    - 但Intel从18.0版本的编译器开始就废除了Cilk，见下文详情
* gcc
    - `g++ -O3 -fcilkplus -lcilkrts <source>`
    - 从5.0版本以后才内置
* [Tapir/LLVM](http://cilk.mit.edu/)
    - MIT CSAIL的又一神作，PPoPP'17的Best paper，在LLVM IR中添加并行设施
    > Tao B. Schardl, William S. Moses, Charles E. Leiserson, *Tapir: Embedding Fork-Join Parallelism into LLVM's Intermediate Representation*, PPoPP, 2017

### [OpenMP](https://www.openmp.org/)
* `#include <omp.h>`
* `#pragma omp task`
* `#pragma omp taskwait`
* `#pragma omp parallel for`
`g++ -O3 -fopenmp <source>`

一般来讲，`icpc`的性能要比普通的`openmp`强不少

### [Intel TBB](https://software.intel.com/en-us/articles/migrate-your-application-to-use-openmp-or-intelr-tbb-instead-of-intelr-cilktm-plus?_ga=2.174275746.1279103381.1550824040-508775473.1544510410)
从Intel C++ Compiler 18.0开始Cilk Plus就被废除了，而交由MIT自己维护。
转而取代的是Intel Threading Building Blocks (TBB)
* `task_group t; t.run([](){ })`
* `t.wait()`
* `tbb::parallel_for()`