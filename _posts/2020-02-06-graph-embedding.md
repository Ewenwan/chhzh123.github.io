---
layout: post
title: 图嵌入(Graph Embedding)
tags: [dl,graph]
---

由于今年要着手一些图结合AI的工作，因此在此对一些经典文献做一些总结。

<!--more-->

## Word Embeddding

先从NLP说起，当代基于深度学习的NLP取得巨大突破很大的原因是将**离散低维的词语符号表示**，转化为**高维空间的连续分布式的语义表示**。

举个例子，
> 我 爱 苹果<br/>我 爱 雪梨

原来用数字索引或one-hot表示，一个词语就对应着一个数字（一维表示 $\mathbb{N}$），那么上面的4个词语就可以变成
* 我 0 [1,0,0,0]
* 爱 1 [0,1,0,0]
* 苹果 2 [0,0,1,0]
* 雪梨 3 [0,0,0,1]

但显然这种方法是无法表现出词语之间的**相似性关系**的，因此后来就有了更聪明的方法，考虑将这些词语用高维空间中的向量表示（$\mathbb{R}^n$），<u>如果两个词向量之间的距离近，那么它们对应的词就具有越高的<b>语义相似性</b></u>，这种思想即word2vec[^2]。

比如将上述四个词encode成以下几个3维向量
* 我 [1,1,1]
* 爱 [1,-1,1]
* 苹果 [-1,1,0.5]
* 雪梨 [-1,1,0.4]

那么可以直观地看出苹果和雪梨在语义上较为接近，因为都是水果。

在Pytorch的简单实现上，[`nn.Embedding`](https://pytorch.org/docs/stable/nn.html#embedding)实际上做的就是一个线性映射，其中的权重也是可以训练的。由于是one-hot输入，与矩阵相乘，因此作用相当于一个查找表(Look-Up Table)，如下所示。

![LUT](http://mccormickml.com/assets/word2vec/matrix_mult_w_one_hot.png)

### Skip-gram
而在生成语言模型(Language Model, LM)上又有两种方法[^1]，一种CBOW，输入为前后$w$个词，输出为中间词；而另外一种是skip-gram，输入中间词，输出前后$w$，这可以大大减轻计算量，也是我们着重关注的。

如下图展现了窗口大小为2的情况，skip-gram可以用于生成词语之间的共现(cooccurance)情况。
![skip-gram](http://mccormickml.com/assets/word2vec/training_data.png)

假设映射为$\Phi$，则优化问题为

$$\min_{\Phi}\;-\log\mathrm{Pr}(\{v_{i-w},\ldots,v_{i-1},v_{i+1},\ldots,v_{i+w}\}\mid\Phi(v_i))$$

注意这里符号的意思是在$[i-w,i+w]$区间上任取**一个**。

## Graph Embedding
放到图(graph)上来说也是类似的，考虑图中的边表相似关系，<u>如果两个结点之间的路径越短，则意味着这两个结点之间的相似度越高</u>。如果仅仅用邻接矩阵表示图的相邻关系的话，是很难看出结点之间的相似关系的（至多看到一度关系）。

考虑图$G(V,E)$，在其基础上添加顶点的特征(feature)表示以及顶点的类别，则形成标注图(labeled graph)$G_L=(V,E,X,Y)$，其中$X\in\mathbb{r}^{|V|\times S}$，$Y\in\mathbb{r}^{|V|\times |Y|}$，$S$为顶点特征维数，$Y$为标签集（即以one-hot形式标注）。
注意这种写法指$X$和$Y$均为矩阵，$X$一共有$|V|$行，每行对应一个顶点的特征向量，有$S$维。

[^3]

## Reference
[^1]: Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg Corrado, Jeffrey Dean (Google), *Efficient Estimation of Word Representations in Vector Space*, arXiv:1301.3781v3
[^2]: Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg Corrado, Jeffrey Dean (Google), *Distributed Representations of Words and Phrases and their Compositionality*, NeurIPS, 2013
[^3]: Bryan Perozzi, Rami Al-Rfou, Steven Skiena (Stony Brook), *DeepWalk: Online Learning of Social Representations*, KDD, 2014