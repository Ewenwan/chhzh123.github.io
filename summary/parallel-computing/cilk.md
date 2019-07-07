---
layout: summary
title: 并行编程-Cilk
---

Cilk是一个非常轻量的并行编程框架，仅仅添加了三个[关键词](https://www.cilkplus.org/tutorial-cilk-plus-keywords)

## 基本知识
* `#include <cilk/cilk.h>`
* `cilk_spawn`：等价于`fork`，生成一个子任务，不阻塞，与原/主线程并行执行，主线程后面的部分称之为continuation（子任务只是放在当前线程的工作队列中，它并不指定如何/怎么执行这些生成的任务）
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

假设只是pthread的元编程，开销会非常大
* 一个spawn产生一个线程，产生/切换上下文开销都太大
* 线程数多于核数
* 更大的working set，更低的cache局部性

因此Cilk Plus有自己的运行时系统，维护了一个线程池
* lazy产生线程，只有遇到第一个`cilk_spawn`才产生
* 将continuation放在工作队列中，如果有线程空闲就可以偷（双向链表，从上面偷，减少冲突）
    - 先执行continuation：child可以被偷
    - 先执行child：continuation可以被偷
    - steal都从调用树的开始偷，这是更大的任务片段，之后的计算能够被继续分摊
* fast clone近似于函数调用，slow clone则是完整的fork/join

```cpp
for (int i = 0; i < N; ++i)
    cilk_spawn foo(i);
cilk_sync;
```

调度策略：
* 先continuation：caller会在执行前将所有子任务都生成；若没有偷的话，执行顺序会与原来有很大区别，相当于在call graph上做BFS
* 先child（**实际实施方案**）：caller只创建了一个**continuation**可以被偷(`cont:i=0`)；若没有偷的话，连续量会不断从工作队列中弹出，并插入新的连续量，执行顺序与原来相同，相当于做DFS
* sync
    - 在没有偷的情况下，sync就是无操作
    - Stalling join策略
        - 创建标识符(descriptor)，包括block ID、生成子任务的数目、完成子任务的数目
        - 只有生成=完成时，在主线程上continuation才会继续执行，子线程需要发消息告知
    - greedy join策略（Cilk**实际实施的方案**，局部性感知调度器）
        - 不管是否是主线程，只要空闲，都可以从其他线程队列中偷任务；因此不会在join等待，会直接向其他线程索要任务
        - 同样有标识符，会在最后一个执行完的线程继续执行continuation（通过标识符告知）
        - 只有在stealing发生时才会创建标识符

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