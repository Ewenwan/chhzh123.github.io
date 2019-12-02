---
layout: post
title: 并行编程-Spark
tag: [summary, parallel]
---

数据量远比处理的速度增长要快，只能在大规模集群上并行

## 面临的问题
传统网络编程：节点间的通信(MPI)，但难以扩展至大规模
* 如何分割问题：需要考虑网络、数据局部性
* 如何处理失败：大规模不可避免
* 更麻烦的是：straggler，节点不失败，但很慢
* 以太网慢
* 需要为每一台机器写程序，故很少用于数据中心

MapReduce的局限性
* 单趟计算很好，但多趟(multi-pass)不行
	- 算完一次写磁盘，重新读再进行第二轮迭代
* 没有有效的数据共享原语(primitive)
	- step之间的state会去向分布式文件系统
	- 复制、硬盘存储，因此很慢（90%时间在IO）

## 数据流模型
限制编程界面，将job当成高层算子的图
* 易于编程：高层函数，不用处理消息传递
* 广泛采用：比MPI更为常见，特别是near data
* 大规模集群可扩展性

## [Spark](spark.apache.org)
Spark是UC Berkeley AMP lab所开源的类Hadoop MapReduce的通用并行框架，不同的是Job中间输出结果可以保存在内存中，从而不再需要读写HDFS，因此Spark能更好地适用于数据挖掘与机器学习等需要迭代的MapReduce的算法（适应多趟应用）。

Spark采用了弹性分布式数据集(Resilient Distributed Datasets, RDD)进行数据存储。其提供了一种高度受限的共享内存模型，即RDD是只读的记录分区的集合，只能通过在其他RDD执行确定的转换操作（如map、join和group by）而创建，这些限制使得实现容错的开销很低。
对开发者而言，RDD可以看作是Spark的一个对象，它本身运行于内存中，如读文件是一个RDD，对文件计算是一个RDD，结果集也是一个RDD，不同的分片、数据之间的依赖、key-value类型的map数据都可以看做RDD。
* 不可变的对象集合，用户控制的划分与存储(memory, disk)，扩展(spread)至整个集群
* 静态类型`RDD[T]`
* 通过并行变换实现(map, filter)
* 实现在错误上自动重建

Spark在Apache上开源，有Scala、Java、Python、R等API。

Spark实现在**同一个引擎**上的数据提取，模型训练以及询问交互（针对同一个分布式文件系统DFS）。