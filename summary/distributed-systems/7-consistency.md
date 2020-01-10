---
layout: post
title: 分布式系统（7） - 一致性和复制
date: 2020-01-09
tag: [summary]
---

为保证复制的一致性，通常需保证所有冲突操作无论在任何地方都以相同顺序执行。

存在两种操作冲突：
* 读写冲突
* 写写冲突

## 以数据为中心的一致性模型
**一致性模型**实质上是进程与数据存储之间的一个约定，如果进程统一遵守某些规则，则数据存储将正常运行。

持续一致性/连续一致性/一致性程度
* 绝对/相对**数值**偏差：股票市场价格记录的复制、Web缓存
* 新旧偏差：天气预报滞后几个小时被更新（无论数值相差多少都是可以接受的）
* 顺序(ordering)偏差：不同副本更新操作**顺序和数量**可能不同

一致性单元(Consistency Unit, Conit)：参照下面这篇论文

Haifeng Yu, Amin Vahdat, [*Design and evaluation of a conit-based continuous consistency model for replicated services*](https://www.comp.nus.edu.sg/~yuhf/tocs02.pdf), TOCS, 2002

![conit](https://d3i71xaburhd42.cloudfront.net/8a0aeb2b07851e7c9466162bb6787f6c683cca87/5-Figure2-1.png)

### 顺序一致性 (Sequential Consistency)
> The result of any execution is the same as if the (read and write) operations by all processes on the data store were executed in some sequential order and the operations of-each individual process appear in this sequence in the order specified by its program. -- Lamport, 1979

SC：所有读写操作按程序顺序执行，所有进程都只能看到**单一**操作执行顺序

| :--- | :---    | :---      | :---     | :---    | :---   |
| P1:| W(x)a |
| P2:|       |  W(x)b  |
| P3:|       |         | R(x)b  | R(x)a |
| P4:|       |         |        | R(x)b | R(x)a |

如上图，W(x)a代表对数据项x写a，R(x)b代表从数据项x中读出b，其他同理。
对于P3和P4来说，他们看到的操作都是一致的，即P2写b，然后P1写a。

但如果换成下图，则不满足顺序一致性，因为P3和P4观察到的P1和P2操作顺序不同。

| :--- | :---    | :---      | :---     | :---    | :---   |
| P1:| W(x)a |
| P2:|       |  W(x)b  |
| P3:|       |         | R(x)b  | R(x)a |
| P4:|       |         |        | R(x)a | R(x)b |

### 因果一致性 (Causal Consistency)
CC：所有进程都以相同的顺序看到具有**潜在因果关系**的**写**操作

通常是对于同一数据项，P1写，P2读后写，可参见[微信朋友圈因果一致性例子][wechat]。
如下图，P1和P2对a,b的读写有因果关系，因此P3和P4读出a,b的顺序应该相同，但a,c由于没有因果关系，故可以并发读取（即顺序不定，不满足顺序一致性）。

| :--- | :---    | :---      | :---     | :---    | :---   |
| P1:| W(x)a |         |        | W(x)c |
| P2:|       |  R(x)a  | W(x)b  |
| P3:|       |  R(x)a  |        | R(x)c | R(x)b |
| P4:|       |  R(x)a  |        | R(x)b | R(x)c |

## 以客户为中心的一致性模型

{% include image.html fig="DistributedSystems/mobile_user.png" width="70" %}

### 最终一致性(Eventual Consistency)
如果很长一段时间没有更新操作，则所有副本都逐渐成为一致的（e.g. WWW）
* 优点：避免写写操作冲突
* 缺点：达到一致所需时间长

### 单调读
如果一个进程读x得到a，那么该进程对x执行的任何后续操作都**不会得到比a更老的值**。

如下图，WS(x)代表写操作集合，x后的标识代表时间戳，WS(x1;x2)代表W(x1)是W(x2)的一部分，即W(x2)看到x1的值后才会执行。

| :--- | :--- | :--- | :--- | :--- |
| L1 | WS(x1) |  | R(x1) |
| L2 | | WS(x1;x2) |     | R(x2) |

下面则是一个不符合单调读的例子，其并没有保证x1的操作被传递到x2

| :--- | :--- | :--- | :--- | :--- |
| L1 | WS(x1) |  | R(x1) |
| L2 |  | WS(x2) |     | R(x2) |

### 单调写
一个进程对数据项x的写操作必须在该进程对x执行任何后续写操作之前完成

| :--- | :--- | :--- | :--- | :--- |
| L1 | W(x1) |  |  |
| L2 | | WS(x1;x2) |     | W(x2) |

即其他进程的写操作应传播到当前进程后才能进行后续操作。

| :--- | :--- | :--- | :--- | :--- |
| L1 | W(x1) |  |  |
| L2 | |  |     | W(x2) |

### 读写一致性 (Read-Your-Writes)
E.g. 更新Web页面，使其能够展示最新版本数据，而不是缓存内容；或者用户看完文章后才可以评论。

同一个进程对数据项x执行的读操作之后的写操作，保证发生在与x读取值相同或比之更新的值上

| :--- | :--- | :--- | :--- | :--- |
| L1 | W1(x1) |  |  |
| L2 | | W2(x1;x2) |     | R1(x2) |

而下面的例子则不满足读写一致性，因为x1可能还未传播过来

| :--- | :--- | :--- | :--- | :--- |
| L1 | W1(x1) |  |  |
| L2 | | W2(x1\|x2) |     | R1(x2) |

### 写读一致性 (Writes-Follow-Reads)
E.g. 网络新闻组用户只有在看到原文章后才能写新的回应文章

同个进程对x执行的读操作之后的写操作，保证发生在与x读取值相同或比之更新的值上

| :--- | :--- | :--- | :--- | :--- |
| L1 | WS(x1) |  | R(x1) |
| L2 | | WS(x1,x2) |     | W(x2) |

## 复制协议
### 基于主备份协议的复制协议
#### 远程写协议
在数据项x上做写操作，
1. 将操作转给x主服务器
2. 主服务器本地副本更新
3. 更新转发给备份服务器
4. 备份服务器更新副本
5. 备份->主备份返回确认
6. 主备份->初始进程

也即客户->主备份->其他备份->主备份->客户
 
#### 本地写协议
定位x主副本，移到自己位置，在本地做写操作，主备份更新完成，再将更新传播给其他副本（即离线操作）

### 基于团体的复制写协议
$$N$$个副本服务器，得到$$NR$$个读团体成员同意，$$NW$$个写团体成员同意，满足

$$\begin{aligned}
NR&+NW>N\\
NW&>N/2
\end{aligned}$$


## 一致性模型总结
* 以数据为中心的一致性模型：读写并重（计算密集型任务）
* 以客户为中心的一致性模型：读多写少（内容分发、手机应用）

各种模型的比较见[Consistency Models](http://jepsen.io/consistency)一文。

[wechat]: https://www.cnblogs.com/hzmark/p/consistency_model.html