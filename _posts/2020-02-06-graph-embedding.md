---
layout: post
title: 图表示学习（1）- 图嵌入
tags: [dl,graph]
---

由于今年要着手一些图结合AI的工作，因此在此对一些经典文献做一些总结。

这是**图表示学习(representation learning)的第一部分——图嵌入(graph embedding)**，主要涉及DeepWalk [KDD'14]、node2vec [KDD'16]、KnightKing [SOSP'19]、GraphZoom [ICLR'20]四篇论文。

<!--more-->

关于图数据挖掘/表示学习的内容强烈建议去看Stanford [Jure Leskovec](https://cs.stanford.edu/people/jure/)的[Tutorial - Representation Learning on Networks (WWW'18)](http://snap.stanford.edu/proj/embeddings-www/)。

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

考虑图$G(V,E)$，在其基础上添加顶点的类别，则形成标注图(labeled graph)$G_L=(V,E,X_{em},Y)$，其中$X_{em}\in\mathbb{R}^{|V|\times d}$为顶点嵌入，$Y\in\mathbb{R}^{|V|\times |\mathcal{C}|}$，$d$为特征维数，$Y$为标签集。
注意这种写法指$X$和$Y$均为**矩阵**，$X$一共有$|V|$行，每行对应一个顶点的特征向量，有$d$维；并且每个结点可能属于**多个类别**$\subset \mathcal{C}$。（指multi-label classification，而不是multi-class每个样本只归属一类别）。
目标则是学习得到嵌入表示$X_{em}$，或者说映射$\Phi:V\mapsto X_{em}$，使得在低维的嵌入空间中，图结点有很好的**分布式连续表达**，能够很好保持图的邻接结构，即<u>结点向量间的距离能够衡量原图中的邻接关系强弱</u>。

下图展现了一个2维图嵌入表示，可以看到如果图嵌入做得好，是能够很好保持原图结构的（该网络来源于著名的空手道俱乐部网络Karate network[^4]，并用力导向方法进行呈现，结点颜色则是依据modularity进行的社群检测）。
![karate](https://1.bp.blogspot.com/-hx5DlfIn7xk/XRJlD47Mv6I/AAAAAAAAEO4/o9ztIaCTz7Ie2eVEczhyGuciQPxV7JKFACLcBGAs/s640/Screenshot%2B2019-06-25%2Bat%2B11.11.05%2BAM.png)

既然也是做嵌入，那能否将既有NLP中成熟的词嵌入方法移植过来呢？于是就有了DeepWalk[^3]。

## DeepWalk[^3]
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

其考虑的是**二阶邻居**的关系$t\to v\to x$，$t$到$x$的最短距离$d_{tx}$只能是$\{0,1,2\}$三个值（比原来更近、和原来一样、比原来更远）。
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


## KnightKing[^6]
从前面的叙述可以看出，虽然随机游走取得了很好的效果，但是其**采样**的部分占据了绝大多数训练时间，因此如何对随机游走的采样进行加速就变成了一个重要的问题。

而随机游走实际上是一个图计算的问题，因此可以用图计算系统来解决，包括单机的[Ligra](https://github.com/jshun/ligra)、分布式的[Gemini](https://github.com/thu-pacman/GeminiGraph)等，但是这些图系统基本是以顶点为中心(vertex-centric)的，没有办法很好地解决随机游走的问题（主要原因是难以记录整条路径），故有了KnightKing这一以游走者为中心(walker-centric)的图计算引擎。

### Random Walk Taxonomy
要建起一个针对随机游走都通用的系统，最关键一步就是找这些算法的**共通之处**，然后进行**抽象**，得到**统一表达**。

首先进行算法的分类，从转移概率来说，随机游走可分为
* 无偏(unbiased)：均匀分布
* 有偏(biased)：转移概率依赖边权
* 静态：转移概率在游走过程中不会改变（无状态stateless）
* 动态：转移概率会因游走过来时的路径而改变（有状态）
    * 进而可分阶次(order)，一阶只关乎当前节点，为静态；二阶关心过来的邻居，为动态；高阶以此类推

然后可用统一的转移概率公式来表达（注意这里并**未做归一化**）

$$P(e)=P_s(e)\cdot P_d(e,v,w)\cdot P_e(v,w)$$

这是十分直接的公式化，即某一条出边$e$的转移概率，等于静态成分、动态成分、扩展成分三者相乘。
详细地说，游走者$w$当前处于结点$v$，
* 静态成分$P_s$只关乎当前的边$e$
* 动态成分$P_d$关乎这条边以及游走者过来的路径/状态（$w$含有$v$**之前**所有的状态）
* 扩展成分$P_e$则不与出边相关（这里可能是为了解决其他一些未考虑到的情况，这一项的形式化方法存疑）

那么一些随机游走的算法就可以通过这三项轻松表达，其中$P_e(v,w)$被设置成到达最大长度（$\vert w+v\vert =L$）则返回0，其余两项的取值如下表所示（$w_e$指边$e$的边权）

|          | $P_s(e)$ | $P_d(e,v,w)$ |
| :--:     | :--:     | :--:         |
| DeepWalk  | $1$ or $kw_e$  | $1$            |
| Meta-path | $kw_e$  | $\begin{cases}1 & \text{if }type(e)=S_{k\mod\vert S\vert} \\\\ 0 & \text{otherwise}\end{cases}$ |
| node2vec  | $kw_e$  | $\begin{cases}\frac{1}{p} & ,d_{tx}=0 \\\\ 1 & ,d_{tx}=1 \\\\ \frac{1}{q} & ,d_{tx}=2\end{cases}$ |

### Existing Optimization
对于静态的随机游走，常见的采样方法有以下两种
{% include image.html fig="Graph/knightking-its_alias.png" width="70" %}

* ITS：计算边转移概率的累积概率分布，然后抽随机数，二分查找看落在哪个区间（假设$n$条出边，则$O(n)$时间空间建立查找表，$O(\log n)$时间查找）
* Alias：将每条边分成多份，放入不同的桶中，确保每个桶至多两条边且总和相同。采样时随机采样一个桶，然后随机采样两条边中的一条即可（同样$O(n)$预处理时间，但只需$O(1)$时间查找）

但这个时空开销对于动态游走来说都是不合适的，因此传统的深度学习系统(Tensorflow)也不能很好处理，可扩展性极低。进而现在更多关于随机游走的优化是从算法层面实现的，通过近似采样，实现复杂度的降低。

### Sampling
抽象只是解决了编程一致性的问题，但怎么算得快依然是没有解决的，而下面的部分才是本论文最高能的地方。
论文作者翻出了一篇几十年前的文章，专门讲**从任意的概率分布中采样的方法**，然后他们成功地将该论文的方法用到随机游走采样上并获得了奇效。这种采样方法称之为Rejection Sampling，参见下图。

{% include image.html fig="Graph/knightking-rejection_sampling.png" width="70" %}

核心思想是**将1维的概率采样，转化为2维的采样**（想想前面的两种优化方法，ITS算是1D的，Alias算半个2D，因为确实要采样两次，但是却把查找的时间复杂度降了下来）。
1. 建立概率分布，间隔为1，高度即为每条边的转移概率（未归一化）
2. 选取一个最大的信封(envelop)，可以框住所有的概率分布
3. 在2D空间随机撒点，落在概率分布内接受采样，否则拒绝
4. 拒绝则继续重复3，直至采样成功

正确性保证在下面书中有
> David JC MacKay and David JC Mac Kay. 2003. Information theory, inference and learning algorithms. Cambridge university press.

看上去好像跟原来的1D采样也没什么不同，但是细想一下，就会发现rejection sampling很牛逼。
因为原来你都是需要将所有转移概率算出来，然后才采样，看落在哪个区间；但现在是先采样，然后再判定是否符合要求。前者需要检查**所有出边**，而后者只需检查**一条边**，时间复杂度瞬间降下来了。（而且注意这种方法是**精确**采样而不是取近似哦）

上面图中的例子只是无偏的，如果考虑有偏，那只需更改每个小矩形的宽即可。而前面的抽象正好也给了这种对应机会，即小矩形的宽是$P_s$，而小矩形的高是$P_d$，由于信封高度$Q(v)$为$P_d$的最大值，而这些在随机游走算法中是确定的（比如node2vec就是$1/p$、$1/q$和$1$三者的最大值），因此采样只需先判x落在哪个$P_s$区间中（这里用1D的采样方法即可解决），然后直接采$y$，判断$y$是否小于$P_d$，即可判接受还是拒绝。显而易见，这种方法对于动态随机游走是没有多余的预处理时间的（如累加），只需一开始将$P_s$处理好即可（存在一个数组中）。

这种方法的核心问题/开销在于如何快速地采样到有效区域，因此后面的优化也是trivial的。

{% include image.html fig="Graph/knightking-optimization.png" width="70" %}

* 将过高矩形(outlier)进行裁剪补到后面以降低$Q(v)$，如上图所示。但是这种方法有很严重的问题是不知道到底要裁剪多少，因为你现在只采样了一个矩形，frankly来说你是不知道其他矩形的情况的（文中脚注作者说是设一个threshold，当成超参数让用户自己调。这种方法看上去就是根据node2vec这种特殊情况进行适配的，因为只有三个概率取值，因此可以很好估计最大值多少，去除最大值之后应该怎么剪）；另一方面，一次裁剪就足够了吗，如果一次裁剪依然是非常高的矩形那又应该怎么办呢，本文似乎回避了这个问题，或者说认为这种情况发生概率非常小。
* 另外一个优化则是针对低矩形的，如果采样比所有矩阵都低，那当然就可以直接确认了，谓之为pre-acceptance（但似乎这一个优化只是减少了一个比较操作吧...）

编程模型的API就不说了，毕竟就是那几个参数怎么设的问题。

### Experiments
不比前面那些算法论文只跑小图，KnightGraph跑了真实的大规模图，最大的是UK-Union，有134M个顶点，5.51B条边，估计在几十G的大小。

实验没有测端到端，只是测了**路径采样**的部分；并且没有跟深度学习框架(Tensorflow)等比，只跟Gemini比了，在动态采样上达到了惊人的4个阶的加速比提升，当然这也是可预见的（其实这完全归功于算法）。

### Summary
本文诠释了一个好的idea就能出一篇paper，其余的工作其实都是工程实现。总结来说就三个贡献点：

<center><b>一个简单通用的抽象（系统层面）+好的采样方法（算法层面）+实验</b></center>

同时也可以看出，算法提升带来的收益远大于系统层面优化带来的收益，“系统设计是重要的，但算法设计同样也很重要”。

<!-- 系统设计固然重要，但也不要忽视了算法设计的重要性 -->

## GraphZoom[^7]


## Reference
[^1]: Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg Corrado, Jeffrey Dean (Google), *Efficient Estimation of Word Representations in Vector Space*, arXiv:1301.3781v3
[^2]: Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg Corrado, Jeffrey Dean (Google), *Distributed Representations of Words and Phrases and their Compositionality*, NeurIPS, 2013
[^3]: Bryan Perozzi, Rami Al-Rfou, Steven Skiena (Stony Brook), *DeepWalk: Online Learning of Social Representations*, KDD, 2014
[^4]: Wayne W. Zachary, *An Information Flow Model for Conflict and Fission in Small Groups*, Journal of Anthropological Research, 1977
[^5]: Aditya Grover, Jure Leskovec (Stanford), *node2vec: Scalable Feature Learning for Networks*, KDD, 2016
[^6]: Ke Yang, MingXing Zhang, Kang Chen, Xiaosong Ma, Yang Bai, Yong Jiang (Tsinghua), *KnightKing: A Fast Distributed Graph Random Walk Engine*, SOSP, 2019
[^7]: Chenhui Deng, Zhiqiang Zhao, Yongyu Wang, Zhiru Zhang (Cornell), Zhuo Feng, *GraphZoom: A Multi-Level Spectral Approach for Accurate and Scalable Graph Embedding*, ICLR (Oral), 2020