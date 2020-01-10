---
layout: post
title: 分布式系统（4）-通信
date: 2020-01-11
tag: [summary]
---

## 中间件
中间件层插在传输层和应用层之间，提供通用服务和协议，可用于支撑不同应用
* 包含丰富通信协议
* 压包、解包，系统集成
* 命名协议，允许资源共享
* 安全协议用于安全通信
* 扩展机制，复制和缓存

面向消息的中间件：目的在于进行高层次的持久化、异步通信
* 进程之间互相发送消息，这些消息会被排队
* 发送进程可以继续做其他事情，不需要等待及时回应
* 中间件提供容错机制

## 远程过程调用(RPC)
RPC：本地程序允许调用其他机器上的进程
客户端调用RPC后，实际调用的函数为

{% include image.html fig="DistributedSystems/RPC.png" width="70" %}

<center>客户端进程->stub压包->OS->远程OS->stub解包->本地调用进程->进程返回</center>

RPC的参数传递不仅仅是将参数封装在消息中
* 客户端和服务器可能有不同的数据表示->字节序列转换
* 应该得有相同的编码机制来表达复杂数据类型

RPC客户端-服务器绑定
* 定位服务器所在机器
* 定位该机器上相应的进程

远程过程调用缺点
* 服务器不一定运行
* 同步阻塞

## 面向消息的瞬时通信
Berkeley套接字(socket)

![socket](https://media.geeksforgeeks.org/wp-content/uploads/Socket_server.png)

套接字缺点
* 抽象层不对，只提供简单的send和receive操作
* 套接字使用通用协议栈TCP/IP进行通信，不适用于专用协议
* 灵活性差，提供功能简单

之后有了消息传递接口(MPI)

## 面向消息的持久通信
通过中间件(middleware)的队列支持实现异步持久的通信，队列相当于通信服务器缓冲区
* 队列管理器
* 消息路由
* 消息转换器

## 面向流的通信
* 数据流是数据单元的序列，可以应用于离散的媒体，也可应用于连续媒体
* 数据流传输模式
	- 异步传输
	- 同步传输
	- 等时传输

## 多播通信
### 基本概念比较
1. 点对点通信：分布式系统中两个特定实体之间的通信
2. 广播：一个特定实体将消息发送到系统中其他所有实体
3. 多播：一个特定实体将消息发送到一组特定实体中

## Chord结构中的应用层多播
![chord](https://sujithjay.com/public/DHT-Dynamo.png)

初始化一个多播标识符mid，在指纹表(finger table)中找到succ(mid)，令其为多播树根
* 当一个结点要加入多播树时
	- 执行Lookup(mid)，并发送join请求给根
	- 他成为一个树中的转发者(forwarder)
* 当join到达Q时
	- 如果Q未见过标记为mid的join请求，则它变为forwarder，P成为Q的孩子，Q会继续转发join请求给根
	- 如果Q已经是mid的一个forwarder，则P成为Q的孩子，且不再转发join请求
* 发送多播消息
	- 查询Lookup(mid)，通过根发送消息
	- 根将消息传播到整棵树

实际上是从Chord中构建多播树
![chord multicast](https://www.researchgate.net/profile/Nguyen_Hoaison/publication/254020375/figure/fig7/AS:668428058771461@1536377076268/An-example-of-Chord-based-multicast-method-In-this-example-Node-1-sends-messages-to-all.ppm)

## Gossip数据通信
依靠感染行为传播，即感染(epidemic)协议

### 反熵模型
结点P随机选取另一结点Q，与其交换更新信息
* Push：P发给Q
* Pull：Q发给P
* Push-Pull：双向

### 流言(rumor)/gossiping传播模型
结点P更新x，与任意结点Q通信，将消息发送给Q。若发现Q已被另一结点更新，则P有$$1/k$$概率不再传播。