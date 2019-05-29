---
layout: post
title: 分布式深度学习
tag: [dl]
---

因为经常会搞混一些基本的并行概念，所以特此记录一下。

<!--more-->

之所以要上分布式并行，是因为单机的计算力/资源不够。如果单机计算力已经足够强，那完全没有必要上分布式，毕竟还有通信开销。

对于深度学习来说，由于计算量太大，所以有时GPU单卡太慢，那就有必要上多卡。如果多卡不是共享内存，那就相当于分布式了。下面讲的两种模型并行方法则都是**分布式**并行，一定要与共享内存的区分开来。

注意分布式并行有足够强的数学理论基础（凸优化理论），保证了其正确性。

## 数据并行
![data parallel](https://pic1.zhimg.com/v2-47a5f6f4ac3bcd1c355d604367802231_b.jpg)

每个处理器/节点上存储一份模型，这里所有的模型都是同一个，属于重复存储。然后不同的节点取**不同的数据**，各自完成前向和后向的梯度计算，这是worker干的事情。然后每一个worker将各自算得的梯度送到参数服务器(parameter server)上，由参数服务器进行更新操作，再将更新后的模型传回各个节点。

## 模型并行
![model parallelism](https://pic4.zhimg.com/v2-528d241081fb4c35cde7c37c7bd51653_b.jpg)

如果神经网络非常大的话，就需要将其划分成多份，存储在不同的GPU上，实际上也相当于将矩阵进行分块。

而通过流水线的方法可以实现模型并行，即每一个GPU上放一层（或某几层），然后依次传播。第一个数据读入(t1)，由第一个GPU算第一层；第二个数据读入(t2)，第一个GPU算第二个数据的第一层，第二个GPU算第一个数据的第二层，以此类推。

![pipelining](https://pic2.zhimg.com/80/v2-dc91370dcd3e73f3014ea5d1d1ef7959_hd.jpg)

## 参考资料
* 分布式机器学习里的 数据并行 和 模型并行 各是什么意思？ - 李哲龙的回答 - 知乎 <https://www.zhihu.com/question/53851014/answer/158794752>
* 深度学习的模型并行是什么原理？ - winston.wen的回答 - 知乎 <https://www.zhihu.com/question/55480951/answer/540737527>