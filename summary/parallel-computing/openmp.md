---
layout: summary
title: 并行编程-OpenMP
---


开放多处理过程(Open Multi-Processing, OpenMP)显式地控制线程，属于共享内存模型。

## 编译指令
* `#include <omp.h>`
* `#pragma omp task`
* `#pragma omp taskwait`
* `#pragma omp parallel for`
`g++ -O3 -fopenmp <source>`

一般来讲，icpc的性能要比普通的OpenMP强不少

## API
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

## 竞态与同步
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

## 优化方法
* 调度：`schedule(dynamic[,chunk])`
* 循环变换：裂变(fission)、融合(fusion)、交换(exchange)

## 优点和缺点
* 增量式并行，串行等价
* 对任务分解并不友好
* 编译器无法查死锁或RC问题，因是编译指令

## 参考资料
* 官网，<https://www.openmp.org/>
* 嵌套并行原理，<https://docs.oracle.com/cd/E19205-01/819-5270/aewbc/index.html>