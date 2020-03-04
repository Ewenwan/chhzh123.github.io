---
layout: post
title: 图表示学习（3）-图神经网络框架
tags: [dl,graph]
---

这是**图表示学习(representation learning)的第三部分——图神经网络框架**，主要涉及DGL [ICLR'19]、PyG [ICLR'19]、NeuGraph [ATC'19]和AliGraph [VLDB'19]四篇论文。

<!--more-->

## Deep Graph Library[^1]


## Pytorch Geometric[^2]


## NeuGraph[^3]
**深度学习系统最大问题在于没有办法高效表示图数据，而图系统最大的问题在于没法自动微分！**

现有用得最广泛的框架是[DGL (Deep Graph Library)](https://github.com/dmlc/dgl)，但DGL只是提供了一个编程框架（面向图的消息传递模型），并没有深度解决计算的问题（这很大程度也是GCN很难火起来的原因，因为无法做到很高的可扩展性）。在GCN的原作[实现](https://github.com/tkipf/gcn)和GraphSAGE的原作[实现](https://github.com/williamleif/GraphSAGE)中，都使用了TensorFlow进行编程，但是他们所采用的方法都是简单暴力的矩阵乘，这样其实很大程度忽略了图计算框架这些年取得的成果。因此NeuGraph的出现也正是为了弥合这两者，将图计算与深度学习有机地融合起来。（某种意义上，这也是matrix-based和matrix-free两种方法的对碰。）

（之前以为腾讯的[Plato](https://github.com/Tencent/plato)作为企业级图系统，应该可以支持GNN的计算，然而Plato只是将[Gemini](https://github.com/thu-pacman/GeminiGraph)和[KnightKing]({% post_url 2020-02-06-graph-embedding %})套了个壳，所以目前也只支持这两个框架所支持的算法，即传统的图算法以及随机游走。）

NeuGraph把常见的GNN分为三类：图卷积、图循环、图注意力网络。
进而提出了SAGA-NN (Scatter-ApplyEdge-Gather-ApplyVertex with Neural Networks)编程模型，其中<u>S</u>A<u>G</u>A部分属于图计算的消息传递，而两个A则是深度学习神经网络的应用。

![saga-nn](https://d3i71xaburhd42.cloudfront.net/7a47891bc52c93c48c4a9309f61d5b16a2c5459c/4-Figure2-1.png)

由于GCN相比起传统的图算法来说（在图计算层面上）要简单很多，就是对全图不断进行遍历，因此Scatter和Gather是确定的，而两个Apply阶段则是用户自定义的函数。（所以似乎NeuGraph没法实现GraphSAGE，因为GraphSAGE的邻居是由一定策略采样出来的，而不是取全部邻居）。

### GPU Execution
目前的深度学习框架都很难处理大图，因为GPU的内存无法存储这么大规模的图，因此NeuGraph在数据流抽象的基础上进行了图划分。

（关于计算硬件，这里是值得考虑的。GPU在稠密矩阵计算上具有先天优势，但如果换成稀疏阵优势是否还存在呢。图处理框架的发展证明了CPU集群有办法承担大规模的图计算任务，从这种角度来看的话是否CPU在GNN的处理上也更存在优势呢？或者更加激进地，利用FPGA实现这样既能高效遍历又能高效算矩阵的架构是否有办法呢？）

简而言之，按边划分为chunk（准确来说是把邻接阵按列划分），然后送到不同的GPU上进行计算，下面补充了几点文中提到的优化方法(streaming out of GPU core)：
* 使用selective scheduling，先用CPU筛一遍有用的边，再把这些边送去GPU算
* 为了确保足够的局部性，采用了Kernighan-Lin算法进行图划分（METIS包），确保同一个chunk中的大部分边都连向同一个节点
* 用pipeline scheduling最大程度重叠IO和计算时间

### Experiments
NeuGraph在TensorFlow上实现，包含5000行的C++代码和3000行的Python代码。实验服务器2*28核CPU+512G内存+8块NVIDIA Tesla P100 GPU。最大的数据集为Amazon，8.6M的顶点和231.6M的边，特征96，类别22。

比较对象包括TensorFlow、GraphSAGE、DGL，提速比在2.5倍到8.1倍之间（单GPU），但没有办法跟多GPU的Tensorflow比，因为直接爆内存了。而不加优化的多GPU版TF-SAGA大概比NerGraph慢2.4到4.9倍，这一部分才比较客观地表明提出的优化方法的高效性。


## AliGraph[^4]
AliGraph是Alibaba内部的图计算系统，已经是商用在淘宝各种预测任务上，并且取得了很好的效果。这篇文章则是从算法到底层系统逐一分析的集大成者。

它提出目前GNN面临着四个问题：**大规模、异构、属性、动态**图。

关于GNN的抽象，AliGraph就比NeuGraph要做得更好一些，因为他们考虑到了采样过程。

{% include image.html fig="Graph/aligraph-gnn.png" width="80" %}

而整体的系统架构从上到下包括应用层、算法层、算子层、采样层和存储层，如下图。

{% include image.html fig="Graph/aligraph-overview.png" width="80" %}

### Storage Level
* 图划分：采用了四种方法（METIS、顶点/边割、2D划分、流式划分），由用户自行选择
* 图属性存储：很棒，AliGraph考虑到了图结构(structure)和图属性(attribute)的存储方式（解耦了！），见下图，以索引方式并分开两个表存，这就很数据库了（确保第二范式）。也许会牺牲一定的计算时间，但是考虑到数据量过大，同时属性信息千奇百怪，因此这样存储可能是比较合适的。论文作者也考虑到访问时间的问题，因此加了两个cache在这，用LRU策略。

{% include image.html fig="Graph/aligraph-storage.png" width="80" %}

* 缓存邻居结点：通过计算一个指标来衡量（结点的$k$跳入度除以$k$跳出度），选指标最大的那些进行缓存

### Sampling Level
考虑三种采样方式：Traverse、Neighborhood、Negative，都是直接调用别人的库。

### Operator Level
包括Aggreate和Combine两种方式，对应的就是不同种类的GNN。

### Conclusions
这篇文章有种虎头蛇尾的感觉，实验部分连实验平台都没有提，也没有提AliGraph是怎么实现的（当时去参加CNCC'19印象中是他们直接在TensorFlow上搭建），更多是像在推销自家提出来的几种GNN有多强。说实话没有太多系统层面的优化，都是直接套用别人的东西，然后融合为几个层就结束了，更没有考虑层与层之间的交互。也许本文当成综述性的文章更为合适，不过它也确实提到了现在这些互联网大厂在关心什么问题，以及他们的解决思路。

## Reference
[^1]: Minjie Wang (NYU), Lingfan Yu, Da Zheng, Quan Gan, Yu Gai, Zihao Ye, Mufei Li, Jinjing Zhou, Qi Huang, Chao Ma, Ziyue Huang, Qipeng Guo, Hao Zhang, Haibin Lin, Junbo Zhao, Jinyang Li, Alexander Smola, Zheng Zhang, *Deep Graph Library: Towards Efficient and Scalable Deep Learning on Graphs*, ICLR, 2019
[^2]: Matthias Fey, Jan E. Lenssen (Dortmund), *Fast Graph Representation Learning with PyTorch Geometric*, ICLR workshop, 2019
[^3]: Lingxiao Ma, Zhi Yang, Youshan Miao, Jilong Xue, Ming Wu, Lidong Zhou (MSRA), Yafei Dai (PKU), *NeuGraph: Parallel Deep Neural Network Computation on Large Graphs*, ATC, 2019
[^4]: Rong Zhu, Kun Zhao, Hongxia Yang, Wei Lin, Chang Zhou, Baole Ai, Yong Li, Jingren Zhou (Alibaba), *AliGraph: A Comprehensive Graph Neural Network Platform*, VLDB, 2019