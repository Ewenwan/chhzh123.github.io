---
layout: post
title: 原子操作
tag: [parallel, memory]
---

并行编程中为避免线程之间的访问冲突，往往需要添加**锁**来进行同步。

<!--more-->

## 原子操作
而所谓的原子(atomic)操作就是不会被其他线程打断的操作。

> Any time two threads operate on a shared variable concurrently, and one of those operations performs a write, both threads must use atomic operations.

之所以会被打断，是由操作系统调度决定的。
很有可能读了数据计算时，原始数据已经被其他线程改变了。
为避免这种情况，就要声明是原子操作或加锁。
否则结果是不可预测的(undefined behaviour)。

## C++11
* 从C++11标准中添加了对原子操作的支持，`#include <atomic>`
* `atomic<T>`用于声明T类型的原子变量

基本原子操作如下

| :---: | :---: |
| `=x` | read the value of x |
| `x=` | write the value of x, and return it |
| `x.fetch_and_store(y)` | do x=y and return the old value of x |
| `x.fetch_and_add(y)` | do x+=y and return the old value of x |
| `x.compare_and_swap(y,z)` | if x equals z, then do x=y. In either case, return old value of x |

## 参考资料
1. What does “atomic” mean in programming? <https://stackoverflow.com/questions/15054086/what-does-atomic-mean-in-programming>
2. Atomic Operations, <https://www.threadingbuildingblocks.org/docs/help/tbb_userguide/Atomic_Operations.html>
3. 关于锁和同步（一）原子操作和非原子操作, <https://blog.csdn.net/zhangqhn/article/details/80876177>