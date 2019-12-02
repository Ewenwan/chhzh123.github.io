---
layout: post
title: 并行编程-MapReduce
tag: [summary, parallel]
---

动机：数据量越来越大，希望有更好更易用的编程框架，能够同时并行上百个CPU

MapReduce能够自动并行化大规模计算，是一种并行编程模型和具体的实现。

## 基本概念与简介
* job：mapper和reducer在数据集上执行的全程序
* task：一个mapper或reducer在数据**片段**(slice)上的执行，即task in progress(TIP)
* task attempt：在机器上执行task的特殊实例尝试

如20个文件的单词计数是一个job，而20个map是task
* 一个特定的task会被执行至少一次，如果在执行过程中崩溃的话
* 一个task的多次尝试会被并行执行，预测执行会被开启

两个基本操作
* `map (in_key, in_value) -> (out_key, intermediate_value) list`
* `reduce (out_key, intermediate_value list) -> out_value list`

一些特性
* map和reduce都能被并行执行，瓶颈在于**reduce不能在map完成前启动**（一个慢的disk controller就能使整个进程变慢）
	- master冗余地执行slow-moving map任务，用第一个完成的拷贝结果
	- combiner函数能够在同台机器上作为mapper运行
	- 在真正地reduce阶段开始之前形成一个mini-reduce阶段，减少带宽浪费
* map会尽可能将task安排在同个机器或rack上，以physical file data的形式
* map的task会将输入划分为64MB的block

## 运行时系统
* 将输入数据分割(partition)
* 调度：Yarn(resource manager)、FIFO
* 处理机器失败
* 管理进程间通信

## 错误容忍(fault tolerance)
* master检测到worker失败
	- 重执行**已经完成**和**过程中**的map task
	- 重执行过程中的reduce task
* master检测到特别的键值会导致map崩溃，就会在重执行时跳过
	- 即使第三方库有bug也能work
* master周期性ping worker
	- map错误：重执行，所有输出都会被局部存储
	- reduce错误：只会重执行部分已经完成的task，输出到全局文件系统

## 问题执行流程
1. 读入大量数据：一个作为master，其他是worker
2. map：提取需要的record（从shard中读取，输出中间键值对-buffered in RAM），存入disk，告知master
3. 重排序(shuffle & sort)：master告知disk location给reduce worker，让其从远端存储中读取中间数据，并重排
4. reduce：aggregate, summarize, filter, transform；worker将unique/associated键值传递进reduce，reduce输出并添加到partition output file
5. 写结果：master在所有task执行完后唤醒用户进程

## 优势
最大化减少并行编程的复杂性
* 减少同步开销
* 自动划分数据
* 提供透明失败(failure transparency)
* 处理负载均衡

## Hadoop
开源的MapReduce实施。
Hadoop主要就是由HDFS和MapReduce组成。
Hadoop的框架最核心的设计就是：HDFS和MapReduce。HDFS为海量的数据提供了存储，而MapReduce则为海量的数据提供了计算。