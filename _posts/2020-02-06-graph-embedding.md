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

## Graph Embedding
放到图(graph)上来说也是类似的，考虑图中的边表相似关系，<u>如果两个结点之间的路径越短，则意味着这两个结点之间的相似度越高</u>。如果仅仅用邻接矩阵表示图的相邻关系的话，是很难看出结点之间的相似关系的（至多看到一度关系）。

考虑图$G(V,E)$，在其基础上添加顶点的类别，则形成标注图(labeled graph)$G_L=(V,E,X_E,Y)$，其中$X_E\in\mathbb{r}^{|V|\times d}$为顶点嵌入，$Y\in\mathbb{r}^{|V|\times |Y|}$，$d$为一个小的隐含维数，$Y$为标签集。
注意这种写法指$X$和$Y$均为**矩阵**，$X$一共有$|V|$行，每行对应一个顶点的特征向量，有$S$维；并且每个结点可能属于**多个类别**（指multi-label classification，而不是multi-class每个样本只归属一类别）。
目标则是学习得到嵌入表示$X_E$，或者说映射$\Phi:E\mapsto X_E$，使得在低维的嵌入空间中，图结点有很好的**分布式连续表达**，能够很好保持图的邻接结构，即<u>结点向量间的距离能够衡量原图中的邻接关系强弱</u>。

下图展现了一个2维图嵌入表示，可以看到如果图嵌入做得好，是能够很好保持原图结构的（该网络来源于著名的空手道俱乐部网络Karate network[^4]，并用力导向方法进行呈现，结点颜色则是依据modularity进行的社群检测）。
![karate](https://1.bp.blogspot.com/-hx5DlfIn7xk/XRJlD47Mv6I/AAAAAAAAEO4/o9ztIaCTz7Ie2eVEczhyGuciQPxV7JKFACLcBGAs/s640/Screenshot%2B2019-06-25%2Bat%2B11.11.05%2BAM.png)

既然也是做嵌入，那能否将既有NLP中成熟的词嵌入方法移植过来呢？于是就有了DeepWalk[^3]。

## DeepWalk
很简单的类比，就是将<font color="blue">图上的结点</font>当成是<font color="red">词语</font>，而几个结点构成的连续<font color="blue">路径</font>则当成<font color="red">句子</font>。
那么问题就变成<u>怎么找到这些合适的路径</u>。

### Random walk
最早一批发表的图表示学习文章DeepWalk[^3]就采用了**随机游走**(random walk)的方式，来生成这些路径，实际上就是从一个结点出发走$L$步到达另一个结点的路径。
形式化定义则令出发结点为$v_i$，随机游走是一个随机过程

$$\mathcal{W}_{v_i}:\mathcal{W}_{v_i}^1,\mathcal{W}_{v_i}^2,\ldots,\mathcal{W}_{v_i}^k$$

使得$\mathcal{W}_{v_i}^{k+1}$是从$v_k$的邻居中随机挑选出的结点。

随机游走的好处是明显的：
* 并行性：显然可以同时开多个walker从不同结点出发进行游走
* 适应性：可以轻松应对动态网络，一旦有网络结构更新，只要有足够多的walker进行重新采样，就可以对其嵌入表示进行更新

而通过随机游走，我们也可以发现图和文本的相似之处——它们都符合幂律/长尾分布(power law)，或者说是scale free的。
![power law](https://sutheeblog.files.wordpress.com/2017/10/powerlaws.png?w=452&h=287)

### Skip-gram
因此可以尝试套用NLP中的语言模型(Language Model, LM)来做结点嵌入。

LM的目标是<u>估计特定序列/句子在语料中的出现概率</u>，比如给定一个句子$W_1^n=(w_0,w_1,\ldots,w_n)$，那么最大化

$$\mathrm{Pr}(w_n\mid w_0,w_1,\ldots,w_{n-1})$$

在所有训练语料中的概率。

放在图中则变为给定随机游走的前$i-1$个结点，最大化$\mathrm{Pr}(v_i\mid (v_1,v_2,\ldots,v_{i-1}))$。

目标是<u>学习结点的嵌入表示</u>，而不仅仅是结点的共现(co-occurance)情况。引入映射函数$\Phi:v\in V\mapsto\mathbb{R}^{|V|\times d}=X_E$，估计下式

$$\mathrm{Pr}\left(v_i\mid (\Phi(v_1),\Phi(v_2),\ldots,\Phi(v_{i-1}))\right)$$

但由于计算量太大，因此我们还是看看NLP中是怎么做的。
在word2vec[^1]中提到了两种LM，一种CBOW，输入为前后$w$个词，输出为中间词；而另外一种是skip-gram，输入中间词，输出前后$w$，这可以大大减轻计算量，也是我们着重关注的。

如下图展现了窗口大小为2的情况，skip-gram可以用于生成词语之间的共现(cooccurance)情况。
![skip-gram](http://mccormickml.com/assets/word2vec/training_data.png)

假设映射为$\Phi$，则优化问题为

$$\min_{\Phi}\;-\log\mathrm{Pr}(\{v_{i-w},\ldots,v_{i-1},v_{i+1},\ldots,v_{i+w}\}\mid\Phi(v_i))$$

注意这里符号的意思是在$[i-w,i+w]$区间上任取**一个**。


<!-- 这里使用的是**无监督方法**[^3] -->

## Reference
[^1]: Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg Corrado, Jeffrey Dean (Google), *Efficient Estimation of Word Representations in Vector Space*, arXiv:1301.3781v3
[^2]: Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg Corrado, Jeffrey Dean (Google), *Distributed Representations of Words and Phrases and their Compositionality*, NeurIPS, 2013
[^3]: Bryan Perozzi, Rami Al-Rfou, Steven Skiena (Stony Brook), *DeepWalk: Online Learning of Social Representations*, KDD, 2014
[^4]: Wayne W. Zachary, *An Information Flow Model for Conflict and Fission in Small Groups*, Journal of Anthropological Research, 1977