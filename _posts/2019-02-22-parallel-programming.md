---
layout: post
title: 并行编程
tag: [tools, parallel]
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
    - Intel的编译器icpc在具体实施时采用了[work-stealing](https://en.wikipedia.org/wiki/Work_stealing)的调度方法，动态地对任务进行分配
* gcc
    - `g++ -O3 -fcilkplus -lcilkrts <source>`
    - 从5.0版本以后才内置
* [Tapir/LLVM](http://cilk.mit.edu/)
    - MIT CSAIL的又一神作，PPoPP'17的Best paper，在LLVM IR中添加并行设施
    > Tao B. Schardl, William S. Moses, Charles E. Leiserson, *Tapir: Embedding Fork-Join Parallelism into LLVM's Intermediate Representation*, PPoPP, 2017

### [OpenMP](https://www.openmp.org/)
开放多处理过程(Open Multi-Processing, OpenMP)显式地控制线程，属于共享内存模型
* `#include <omp.h>`
* `#pragma omp task`
* `#pragma omp taskwait`
* `#pragma omp parallel for`
`g++ -O3 -fopenmp <source>`

一般来讲，icpc的性能要比普通的OpenMP强不少

#### [Fork-join](https://en.wikipedia.org/wiki/Fork%E2%80%93join_model)
![fork-join](https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Fork_join.svg/400px-Fork_join.svg.png)
注意这里fork的东西是任务(task)或纤程(fiber/lightweight thread)，而不是线程

#### API
OpenMP提供了三种API
* 编译指示(directive)：`#pragma omp <directive-name> [clause,...]`
* 运行时库例程(routine)
* 环境变量

常用API
* `omp_get_thread_num()`：线程id
* `omp_get/set_num_threads()`：使用的线程数目
* `#pragma omp parallel for`：循环内不能含跳转、跳出指令，且循环次数应确定
    - 如果仅仅是`parallel`，则循环只是被简单拷贝，循环体执行多次
    - 如果是`parallel for`，则会触发调度器，内层循环不会被拷贝
* `private (<variable list>)`：将变量声明为私有变量
    - 不可使用先前定义的值
    - 私有变量在循环开始前未定义，可通过`firstprivate`继承之前定义的值，`lastprivate`返回最后的值至全局
    - 在循环内不再可以访问该全局变量
* `single`：单线程执行，如处理IO
* `master`：仅对主线程进行操作
* `sections`和`section`：`sections`作用域内所有的`section`都可以并行执行
* `reduction (op:list)`
    - 每一个list中变量依据op被创建且初始化
    - 所有的拷贝都被线程局部更新
    - 最后所有局部拷贝的值经过op操作归并为一个值

```cpp
// Example 1
int i, j, k;
float **a, **b;
// initialize b[][] as 1-hop distance matrix
for (k = 0; k < N; ++k)
    #pragma omp parallel for private(j)\
    num_threads(8)
    for (i = 0; i < N; ++i)
        for (j = 0; j < M; ++j)
            a[i][j] = min(a[i][j], b[i][k] + b[k][j]);
// copy a[][] to b[][]

// Example 2
#pragma omp parallel shared(a,b,c,d) private(i)
{
    #pragma omp sections
    {
        #pragma omp section
        {
            for (i = 0; i < N; ++i)
                c[i] = a[i] + b[i];
        }
        #pragma omp section
        {
            for (i = 0; i < N; ++i)
                d[i] = a[i] * b[i];
        }
    } /* end of sections */
}/* end of parallel section */
```

#### 竞态与同步
下面这种机制由于判断`flag`和`flag`置位是两个操作，故并不能保证互斥，需要有原子性的TS(test-and-set)操作

```cpp
// initialize flag = 0
while(flag != 0) /* wait */;
flag = 1;
```

* `barrier`：同步，类似于join
* `nowait`：告诉编译器没有必要加同步，如在循环执行中
* `critical`：临界区，保证互斥（只有一个线程可以进入），都会变成串行执行
* `atomic`：没有冲突的部分会被并行执行

#### 优化方法
* 调度：`schedule(dynamic[,chunk])`
* 循环变换：裂变(fission)、融合(fusion)、交换(exchange)

#### 优点和缺点
* 增量式并行，串行等价
* 对任务分解并不友好
* 编译器无法查死锁或RC问题，因是编译指令

### [Intel TBB](https://software.intel.com/en-us/articles/migrate-your-application-to-use-openmp-or-intelr-tbb-instead-of-intelr-cilktm-plus?_ga=2.174275746.1279103381.1550824040-508775473.1544510410)
从Intel C++ Compiler 18.0开始Cilk Plus就被废除了，而交由MIT自己维护。
转而取代的是Intel Threading Building Blocks (TBB)
* `task_group t; t.run([](){ })`
* `t.wait()`
* `tbb::parallel_for()`

### [MPI(Message Passing Interface)](http://www.mpich.org/)
消息传递型机制，大多采用SPMD(Single Program Multiple Data)模型

#### 基本操作
两个基本操作send和receive，有三种类型
* buffered blocking：拷贝到通信缓存后立即返回
* buffered non-blocking：初始化后DMA后就返回
* non-buffered blocing：收到receive操作后才返回

一个关键在于要**重叠通信和计算**
* `int MPI_Send(void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)`
* `int MPI_Recv(void *buf, int count, MPI_Datatype datatype, int source, int tag, MPI_Comm comm, MPI_Status *status)`
* `int MPI_Isend(void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm,
MPI_Request *request)`
* `int MPI_Irecv(void *buf, int count, MPI_Datatype datatype, int source, int tag, MPI_Comm comm, MPI_Request *request)`

MPI的发送模式
* `MPI_Send`/`MPI_Isend`：标准模式（阻塞/非阻塞），直到使用发送缓冲才返回
* `MPI_Bsend`/`MPI_Ibsend`：缓冲模式，立即返回，可以使用发送缓冲
    - 相关操作：`MPI_buffer_attach`、`MPI_buffer_detach`
* `MPI_Ssend`/`MPI_Issend`：同步模式，不会返回直到收到posted
* `MPI_Rsend`/`MPI_Irsend`：只有在matching receive已经就绪时才使用

```cpp
typedef struct MPI_Status {
    int MPI_SOURCE;
    int MPI_TAG;
    int MPI_ERROR;
};
```

解决死锁：
* 顺序调整：P0 send完receive，P1 receive完后send
* 在发送同时提供receive缓存：`sendrecv`
* 将自己的空间作为发送缓存：`Bsend`+`recv`
* 非阻塞操作：`lsend`+`lrecv`+`waitall`

常用API
* `MPI_Init`
* `MPI_Finalize`
* `MPI_Comm_size`：确定进程数目
* `MPI_Comm_rank`：确定调用进程的标号
* `int MPI_Test(MPI_Request *request, int *flag, MPI_Status *status)`：测试消息是否收到
* `int MPI_Wait(MPI_Request *request, MPI_Status *status)`

```cpp
#include <mpi.h>

int main(int argc, char* argv[])
{
    int npes, myrank;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &npes);
    MPI_Comm_rank(MPI_COMM_WORLD, &myrank);
    printf("From process %d out of %d, Hello World!\n", myrank, npes);
    MPI_Finalize();
}
```

编译指令
* `mpicc`、`mpic++`
* `mpirun -np 2 foo : -np 4 bar`
* `--hostfile`、`--host`：确定主机

#### 群组通信和计算
