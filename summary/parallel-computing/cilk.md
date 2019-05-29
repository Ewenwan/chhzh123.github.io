---
layout: summary
title: 并行编程-Cilk
---

Cilk是一个非常轻量的并行编程框架，仅仅添加了三个[关键词](https://www.cilkplus.org/tutorial-cilk-plus-keywords)

## 基本知识
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
    - Intel的编译器icpc在具体实施时采用了[work-stealing](https://en.wikipedia.org/wiki/Work_stealing)的调度方法，动态地对任务进行分配
* gcc
    - `g++ -O3 -fcilkplus -lcilkrts <source>`
    - 从5.0版本以后才内置
* [Tapir/LLVM](http://cilk.mit.edu/)
    - MIT CSAIL的又一神作，PPoPP'17的Best paper，在LLVM IR中添加并行设施
    > Tao B. Schardl, William S. Moses, Charles E. Leiserson, *Tapir: Embedding Fork-Join Parallelism into LLVM's Intermediate Representation*, PPoPP, 2017

## 参考资料
* 官网，<https://www.cilkplus.org/>