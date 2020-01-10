---
layout: post
title: 分布式系统（11） - 补充内容
date: 2020-01-10
tag: [summary]
---

## 大数据
MapReduce的相关内容见[并行编程-MapReduce]({{site.url}}/summary/parallel-computing/mapreduce/)

## 分布式机器学习
详情见李沐的论文

Mu Li, David G. Andersen, Jun Woo Park, Alexander J. Smola, Amr Ahmed, Vanja Josifovski, James Long, Eugene J. Shekita, Bor-Yiing Su, *[Scaling Distributed Machine Learning with the Parameter Server](https://www.cs.cmu.edu/~muli/file/parameter_server_osdi14.pdf)*, OSDI, 2014

将集群中的结点分为**计算结点**和**参数服务结点**，后者通过分布式存储，各自存储全局参数一部分，并作为服务方接受计算结点参数查询和更新请求。

* server节点的主要功能是保存模型参数、接受worker节点计算出的局部梯度、汇总计算全局梯度，并更新模型参数
* worker节点的主要功能是各保存部分训练数据，从server节点拉取最新的模型参数，根据训练数据计算局部梯度，上传给server节点

![Param Server](https://d3i71xaburhd42.cloudfront.net/0de0c3240bda7972bd0a3c8369ebc4b4f2e4f9c2/7-Figure4-1.png)
![update process](https://www.researchgate.net/publication/319970697/figure/download/fig1/AS:541320822833153@1506072349338/The-second-generation-parameter-server-system.png)

## 分布式深度学习
见[分布式深度学习]({{site.url}}/blogs/2019-05-11-dl-parallel/)

## Kubernetes (K8s)
详情可见
* [Kubernetes: Container Orchestration and Micro-Services](https://courses.cs.washington.edu/courses/cse550/16au/notes/kubernetes.pdf)
* [The illustrated Children's Guide to Kubernetes](https://azure.microsoft.com/en-gb/resources/videos/the-illustrated-children-s-guide-to-kubernetes/)或[PDF版](https://www.cncf.io/wp-content/uploads/2019/07/The-Illustrated-Childrens-Guide-to-Kubernetes.pdf)

可以理解成是一种云OS了，**统一管理服务器集群上成千上万的Docker容器**，基本的功能都有
* Scheduling: Decide where my containers should run
* Lifecycle and health: Keep my containers running despite failures
* Scaling: Make sets of containers bigger or smaller
* Naming and discovery: Find where my containers are now
* Load balancing: Distribute traffic across a set of containers
* Storage volumes: Provide data to containers
* Logging and monitoring: Track what's happening with my containers
* Debugging and introspection: Enter or attach to containers
* Identity and authorization: Control who can do things to my containers

{% include image.html fig="DistributedSystems/Kubernetes.png" width="70" %}

基本组成：
* Container：里面包裹应用及其依赖环境
* Pod：一个可运行工作单元，里面可放一个或多个容器（如果容器紧耦合），带有label
* ReplicaSets：包含一个Pod模板，可以被多次复制
* Services：永久化存储，提供IP地址（注意K8s中IP都被映射到集群内部，即不通过NAT的形式），通过label selector找到pod
* Volumes：Pod可以直接mount一个文件系统
* Namespaces：则是将上述内容全部包裹在一起