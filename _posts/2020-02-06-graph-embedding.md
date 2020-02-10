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

使得$\mathcal{W}_{v_i}^{k+1}$是从$v_k$的**邻居中随机**挑选出的结点。

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

目标是<u>学习结点的嵌入表示</u>，而不仅仅是结点的共现(co-occurance)情况。引入映射函数$\Phi:v\in V\mapsto\mathbb{R}^{\vert V\vert \times d}=X_E$，估计下式

$$\mathrm{Pr}\left(v_i\mid (\Phi(v_1),\Phi(v_2),\ldots,\Phi(v_{i-1}))\right)$$

但由于计算量太大，所以需要采用其他方法。而该优化形式在NLP中已经被研究得很多，因此尝试采用NLP的方法来解决。
在word2vec[^1]中提到了两种LM，一种CBOW，输入为前后$w$个词，输出为中间词；而另外一种是skip-gram，输入中间词，输出前后$w$，这可以大大减轻计算量，也是我们着重关注的。

如下图展现了窗口大小为2的情况，skip-gram可以用于生成词语之间的共现(cooccurance)情况。
![skip-gram](http://mccormickml.com/assets/word2vec/training_data.png)

最终得到**优化问题**为

$$\min_{\Phi}\;-\log\mathrm{Pr}(\{v_{i-w},\ldots,v_{i-1},v_{i+1},\ldots,v_{i+w}\}\mid\Phi(v_i))$$

注意这里符号的意思是在$[i-w,i+w]$区间上任取**一个**，即其将随机游走中的序给消除了。

其实到这里，整体的算法流程就很清晰了：
1. 每次随机选择一个起始点$v_i$
2. 从$v_i$开始，做长为$\vert\mathcal{W}_{v_i}\vert=t$的随机游走
3. 依据得到的$\mathcal{W}\_{v_i}$，做skip-gram。即对每一$v_j\in\mathcal{W}\_{v_i}$，每一$u_k\in\mathcal{W}\_{v_i}[j-w:j+w]$，做梯度下降更新参数

$$
\begin{aligned}
J(\Phi)&=-\log\mathrm{Pr}(u_k\mid\Phi(v_j))\\
\Phi&=\Phi-\alpha\frac{\partial J}{\partial\Phi}
\end{aligned}
$$

这里还有一些优化的地方：
* 为了让SGD更快收敛，一般是将所有的顶点打乱后，再进行顺序遍历（如果完全随机，很难做到每个点都能被采样到）
* 利用层次Softmax[^2]来加快计算，即$\mathrm{Pr}(u_k\mid\Phi(v_j))=\prod_{l=1}^{\lceil\log\vert V\vert\rceil}\mathrm{Pr}(b_l\mid\Phi(v_j))$，其中$b_i$是二叉树的结点，$b_0$是根
* 进一步可以利用Haffman编码来加快二叉树的访问
* 由于顶点十分稀疏，更新也是稀疏的，故可以直接上异步SGD，甚至不用加锁

注意DeepWalk很强的一点在于它使用的是**无监督方法**，即只需知道图结构，就可以学出对应的隐含表示。

### Experiments
DeepWalk分别在BlogCatalog、Flicker和YouTube三个数据集上做多标签分类，下面给出这三个数据集的基本数据，以便有一个直观感受。

| Name | BlogCatalog | Flickr | YouTube |
| :--: | :---------: | :----: | :-----: |
| $\vert V\vert$ | 10,312      | 80,513 | 1,138,499 |
| $\vert E\vert$ | 333,983    | 5,899,882 | 2,990,443 |
| $\vert Y\vert$ | 39         | 195       | 47 |
| Labels | Interests | Groups    | Groups |

可以看到这些数据集相比起Graph500的规模是非常小的。

各超参数的值也附在这里，作为参考。
| $\gamma$ | $w$ | $d$ |
| :--: | :--: | :--: |
| 80 | 10 | 128 |

至于多标签分类，可见下图，即给出比如10%的标记结点作为训练集，剩下的90%则作为测试集。

![Relational Learning via Latent Social Dimensions (SocDim)](https://image1.slideserve.com/2010663/sociodim-framework-l.jpg)

得到隐含表示后，聚类则变得很简单，DeepWalk是采用了one-vs-rest的logistic回归来分类。最终的实验结果是非常好的，只用1%的训练数据，宏F1和微F1指标都远超之前的方法。


## node2vec[^5]
目标和DeepWalk一样，也是<u>自动地学习结点特征，生成隐含表示(latent representation)</u>。

传统的方法常常是有监督的，需要人工进行特征工程，会加入大量前提假设；或者直接采用PCA等方法对图的邻接/Laplace矩阵进行变换，但是矩阵分解工程量很大，可扩展性极低。

而DeepWalk一个很明显的缺点就是它**均匀**地对每个结点的邻居进行采样，这样会造成其无法很好控制其访问的邻居，因此node2vec的最大改进之处就是**将采样方式给参数化了**。

形式化地来说，对于每一源结点$u\in V$，定义其由采样策略$S$得到的邻居为$N_S(u)\subset V$（<font color="red">这里一定要注意，采样策略得到的邻居并不一定是直接邻居，后面会再阐述</font>），希望在给定嵌入表示的前提下，最大化该邻居出现的概率，即

$$\max_\Phi\sum_{u\in V}\log\mathrm{Pr}(N_S(u)\mid \Phi(u))$$

为了解决上述优化问题，又有以下假设：
* 条件独立性：即邻居之间都相互独立
$$\mathrm{Pr}(N_S(u)\mid\Phi(u))=\prod_{n_i\in N_S(u)}\mathrm{Pr}(n_i\mid\Phi(u))$$
* 特征空间对称性：源结点和其邻居在彼此的特征空间中应该有对称的影响，因此用点积进行模拟（$a\cdot b=b\cdot a$），有softmax函数
$$\mathrm{Pr}(n_i\mid f(u))=\frac{\exp(\Phi(n_i)^T \Phi(u))}{\sum_{v\in V}\exp(\Phi(v)^T \Phi(u))}$$

结合上述假设，优化问题变为

$$\max_\Phi\sum_{u\in V}\left[-\log Z_u+\sum_{n_i\in N_S(u)}\Phi(n_i)^T \Phi(u)\right]$$

其中$Z_u=\sum_{v\in V}\exp(\Phi(v)^T \Phi(u))$计算量非常大，采用负采样(negative sampling)[^2]的方法进行优化。

### Equivalance
在预测任务中其实主要关注两种相似性:
* 同质性(homophily equiv)：相互连结或同属一个社群的结点，其嵌入应比较靠近，如下图的$s_1$和$u$
* 结构性(structural equiv)：在社群中扮演同样的角色的结点，其嵌入应比较靠近，如下图的$u$和$s_6$都是各自社群的中心结点

![bfs dfs](https://d3i71xaburhd42.cloudfront.net/36ee2c8bd605afd48035d15fdc6b8c8842363376/2-Figure1-1.png)

而用BFS和DFS就可以分别生成对应的相似性，这里直观理解可能容易理解反，因此参考知乎的[评论](https://zhuanlan.zhihu.com/p/64200072)
> BFS（微观特性）：对于两个结构性比较类似的结点，BFS构建两个节点在类似位置的context序列的概率更高，因此可以更好的学习到结构性；进一步假设，如果两个点有大量相同的邻居节点，那么node2vec训练时，具有相同context的概率更高，embedding向量应该更接近<br/>DFS（宏观特性）：对于两个距离比较近的节点，出现在相同sequence context的几率比较高，因此近距离的节点容易学习出相似的embedding向量

### 2nd-Order Random Walk
下图则是node2vec的精髓，其定义了一个带$p$和$q$两参数的二阶随机游走，在每个结点处访问不同邻居的概率是不同的。
![search bias](https://miro.medium.com/max/987/1*44_Ys2JeD8B0NVdbJ4TQlg.png)

其考虑的是**二阶邻居**的关系$t\to v\to x$，$t$到$x$的最短距离$d_{tx}$只能是$\{0,1,2\}$三个值。
那么可定义搜索偏差(search bias)

$$
\alpha_{pq}(t,x)=
\begin{cases}
\frac{1}{p} & ,d_{tx}=0\\
1 & ,d_{tx}=1\\
\frac{1}{q} & ,d_{tx}=2
\end{cases}
$$

其中，
* $p$为return参数，控制在随机游走中立即返回上一结点的概率，如果设得很大（$>\max(q,1)$），则意味着更大机率往外走，且避免2-hop内的重复采样
* $q$为in-out参数，控制在随机游走中往外/内走的概率，如果设得很大（$>1$），则更倾向于往里走(BFS)；否则，则倾向于往外走(DFS)

最后进行归一化，可得到随机游走的转移概率

$$
\mathrm{Pr}=(c_i=x\mid c_{i-1}=v)=
\begin{cases}
\frac{\alpha_{pq}(t,x)\cdot w_{vx}}{Z} & (v,x)\in E\\
0 & \mathrm{otherwise}
\end{cases}
$$

其中$w_{vx}$为边权。

随机游走比传统的BFS和DFS具有空间和时间复杂性的好处（依照原文），但这里存疑，暂缓不表。

综上就有了node2vec的算法，相比起DeepWalk，它将三个阶段彻底分离，更加方便每个阶段的并行。
1. 预处理计算转移概率
2. 生成大量随机游走
3. 利用这些游走进行SGD

### Link Prediction
node2vec还有一个创新之处在于，其将无监督嵌入表示方法拓展到了连边预测上。

其实有了结点的嵌入表示$\Phi(u)$和$\Phi(v)$后，构造边的嵌入也比较简单，即将这两者做一个二元操作

$$g(u,v)=\Phi(u)\circ\Phi(v): V\times V\mapsto\mathbb{R}^{d'}$$

### Experiments
最后的实验也做得很详实，果然数据挖掘顶会的平均水准还是远高于AI顶会的（10页双栏，与系统会议类似）。

实验主要包括以下几个部分
1. 在Les Misérables网络上对BFS/DFS随机游走的可视化（用k-means聚类），上图展现同质性，下图展现结构性
![vis](https://pic2.zhimg.com/v2-94f4c7dfb29fc922d992c408f2448e8d_1200x500.jpg)
2. 实验设置（Spectral clustering, DeepWalk, LINE），C/C++/Python实现， <http://snap.stanford.edu/node2vec>
3. 多标签分类
4. 敏感性分析
5. 扰动(perturbation)分析（缺信息情况下的表现）
6. 可扩展性（采样占据了绝大多数时间，优化的时间其实比较小，这才有了后面KnightKing的工作）
7. 连边预测

最终实验结果也是吊打前者，故在此不再赘述。

## Reference
[^1]: Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg Corrado, Jeffrey Dean (Google), *Efficient Estimation of Word Representations in Vector Space*, arXiv:1301.3781v3
[^2]: Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg Corrado, Jeffrey Dean (Google), *Distributed Representations of Words and Phrases and their Compositionality*, NeurIPS, 2013
[^3]: Bryan Perozzi, Rami Al-Rfou, Steven Skiena (Stony Brook), *DeepWalk: Online Learning of Social Representations*, KDD, 2014
[^4]: Wayne W. Zachary, *An Information Flow Model for Conflict and Fission in Small Groups*, Journal of Anthropological Research, 1977
[^5]: Aditya Grover, Jure Leskovec (Stanford), *node2vec: Scalable Feature Learning for Networks*, KDD, 2016