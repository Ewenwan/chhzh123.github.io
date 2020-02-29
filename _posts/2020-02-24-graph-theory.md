---
layout: post
title: 图表示学习(0) - 图的基本理论
tags: [dl,graph]
---

这是**图表示学习(representation learning)的基础部分**，主要介绍图(graph)/网络(network)的基本定义与理论。

<!--more-->

本文主要参考Oxford的课程讲义[^1]。

# 基本结构性质
## 定义
图定义成结点(vertex)和边(edge)的集合$\mathcal{G}=(\mathcal{V},\mathcal{E})$，邻接矩阵$A$为结点的连边关系，满足

$$A_{ij}=\begin{cases}1 & (v_i,v_j)\in E\\ 0 & \text{otherwise}\end{cases}$$

如果是有权图，邻接矩阵的值也可以代表边权。

## 度分布
对于无向图，结点的度(degree)为连边数目，即

$$k_i=\sum_{j=1}^nA_{ij}\left(=\sum_{j=1}^nA_{ji}\right)$$

如果所有顶点的度都相同，则称为**正则图**(regular)。

由握手定理有

$$\sum_{i=1}^n k_i=\sum_{i=1}^n\sum_{j=1}^nA_{ij}=2m$$

现实世界中的大多数图都满足长尾分布/幂律分布(long-tailed/power-law)，即度分布（度为$k$的频率）

$$p(k)\propto k^{-\gamma}$$

## 路径
结点$v_i$到$v_j$的距离定义为$d(v_i,v_j)$。
图的直径定义为$D=\max_{u,v\in V}d(u,v)$。

如果两个结点间存在一条路径，则称它们是相连的(connected)。
如果某个集合内的结点都互相连通，则该结点集合构成一个连通分量(connected components, CC)。

## 中心性
中心性(centrality)衡量了结点在网络中的重要程度。
1. 邻近中心性(closeness)：从结点$v_i$到其他结点的距离平均的逆
$$\text{clossness}_i=\frac{N-1}{\sum_{j=1;j\ne i}^n d(v_i,v_j)}$$
2. 中间中心性(betweenness)：途径结点$v_i$的所有**最短**路径所占比例，其中$\sigma_{jl}$是连接$v_j$和$v_l$的最短路径数目，$\sigma_{jl}^i$是这些路径中途径$v_i$路径的数目
$$\text{betweenness}_i=1/\binom{n-1}{2}\sum_{j=1;j\ne i}^{n}\sum_{l=1;l\ne i}^{j-1}\frac{\sigma_{jl}^i}{\sigma_{jl}}$$
3. Katz中心性：$v_i$到$v_j$不同距离的路径数目之和
$$\text{Katz}_i=\sum_{j=1}^n(I+\alpha A+\alpha^2 A^2+\cdots)=\sum_{j=1}^n[(I-\alpha A)^{-1}]_{ij}$$

## 谱性质
定义度矩阵为$D$，对角矩阵，其中$D_{ii}=k_i$。
拉普拉斯(Laplace)阵为$L=D-A$（梯度的散度），也为对称阵。归一化拉普拉斯为

$$\tilde{L}=D^{-1/2}LD^{-1/2}=I-D^{-1/2}AD^{-1/2}$$



## References
[^1]: R. Lambiotte, Oxford Math C5.4: Networks, <https://courses.maths.ox.ac.uk/node/42624>