---
layout: post
title: Tools Setup!
---

**工具是重要的！**这点其实很多老师都不会讲述。
然而好用的用得顺手的工具可以使工作效率大大提升，不好用的工具虽然也可以用，但是会增加很多不必要的时间。

最简单的例子是很多非计院的同学学了一整个学期代码（C++/Java），都还在**非常古老的**IDE上写程序（我说的是Dev(((）。
这当然可以写，但是常言道“优秀的程序员都是不用IDE的！”
如果有更强大的工具可以让你事半功倍，何乐而不为呢？

这篇文章列举我目前所使用的一些工具作为参考，都是使用了很长时间，亲测比较好用。

### 电脑与服务器
* 手提电脑配置
	- Intel i7 CPU (8核）+ GTX 1050 + 8G内存 + 256G SSD + 1T移动硬盘
	- Windows 10 + Ubuntu 18.04 LTS (subsystem)
* 腾讯云服务器：自己租的用来搞事情
	- Intel Xeon CPU E5-26xx (单核) + 2G内存 + 50G云硬盘
	- CentOS 7.2
* 实验室服务器：
	- Intel Xeon CPU Gold 5118 (24核) + Titan V (2块) + 64G内存 + 11T硬盘
	- Ubuntu 18.04 LTS

### 文本编辑器
这一项放在第二点叙述可以说明其重要性
* [Sublime Text 3](http://www.sublimetext.com/)<br/>
Sublime的重度用户，每天跟它打交道的时间估计超过10个小时。
打代码、做笔记、记事情、写报告、写论文全部都用它。

优点：
* 添加LaTeX(TexLive)和C++(MinGW)编译支持，彻底跟IDE说再见<br/>
配置方法可见[这篇文章](https://www.cnblogs.com/fantacity/p/5100434.html)和[这篇文章](https://www.jianshu.com/p/86c0822cc89b)
* 多种语言的代码高亮，包括Verilog、MIPS等硬件类的小众语言都原生支持
* 多个光标多行编辑，这个是真的强，很少见有编辑器支持（个人成见）
* 自动补全，包括单词的和整段代码的补全，还有LaTeX的引用、参考文献等的搜索补全
* 替换功能强大，可以整词、大小写敏感、按段落，还支持正则表达式
* 可以安装各种package，进一步提升sublime的能力（比如做两个文本的区别高亮、字数统计等）
* 内置控制行，可以直接打Python代码

### 笔记
笔记怎么做也是我这一年多来摸索的东西，现在基本上用下面两个工具啦。
* LaTeX<br/>
极重度用户，已经到了写篇文科小报告都要拿LaTeX打的地步...
日常的话，[数学](https://github.com/chhzh123/Notes-of-Math)和[CS](https://github.com/chhzh123/CS-Notes)的笔记都会用LaTeX打，目前数学大致有一百多页的样子，CS也有几十页，算是给自己大学的学习留档吧。
因为使用太频繁，到年初才自己制作了份[模板](https://github.com/chhzh123/mylatextmpl)，又瞬间让自己生产力爆炸。

目前想到的一些不那么大众的点有
1. tikzcd画流程图很爽
2. biblatex要学会，生成参考文献神器
3. 表格可以不用自己打，Excel有宏可以支持

* [TiddlyWiki](https://tiddlywiki.com/)<br/>
这一个比较少人用，但是非常方便，也是满足了我写md、写LaTeX、贴代码的要求。
就是一个html页面，里面存自己的笔记，但是页面布局都已经帮你设置好了，直接可以写，还可以上传到服务器上让所有人都可以访问（但是几M大小基本加载不出来...）。
平时文科类的笔记会存在里面，还有部分有用的代码，其他的话...就当成网页收藏夹了...

### 文献管理
* [Zotero](https://www.zotero.org/)：学长推荐，必属精品(

优点：
* 分类归档论文，可以加Tag和Related
* 可以添加笔记
* 可以直接在网上下载pdf文件并解析文本生成条目
* 可以全仓库搜索文件
* 自动管理参考文献，且可以导出为BibLaTeX
* 支持不同格式的文件读入
* 好像还有云同步，但并没有用过

### 流程图/模型图绘制
写论文或者建模就知道画图的苦，以前一直都羡慕人家的文章中能够画出那么漂亮的图片，因为以往都只知道函数图怎么画，但不知道有什么比较好用的流程图工具
* [draw.io](https://draw.io)<br/>
在线画图，有网格，图形多，使用方便，画什么都容易，不足是对插图的处理不强，原生LaTeX在导出时常常出现问题
* [ipe](http://ipe.otfried.org/)<br/>
下载解压即用，有网格，但自动吸附格点，使用极其麻烦（要记一堆快捷键，有种CAD的感觉），但对LaTeX的支持非常好
* [tikzcd](http://ctan.math.washington.edu/tex-archive/graphics/pgf/contrib/tikz-cd/tikz-cd-doc.pdf)<br/>
刚才提到的LaTeX包，用`&`即可实现对齐，绘制简单的流程图非常方便

### 数据可视化
这个也是写论文必备
* [Matplotlib](https://matplotlib.org/)<br/>
Python包，功能强大，不过我主要用来画折线图、柱形图；语法还算简单，添加标签标注等等也不会太麻烦，标签可以直接输入LaTeX代码
* [Mathematica(MMA)](https://www.wolfram.com/mathematica/)<br/>
上大学之前就只知道MMA画函数/3D/等高线图，其实用matplotlib画2D函数图会简单很多；而直到这一次建模也才直到MMA这么强大，还可以直接制作有数值的地图，完全是开外挂...
	<!-- > TODO MMA 剑魔 -->
* [Plotly](https://plot.ly/)<br/>
在线网站，可以用Python调用API，功能很强大，但还未自己试过

### 服务器
可能很多人会问自己租服务器用来干嘛。
其实是可以干非常多事情的。
现在[腾讯云学生特价](https://cloud.tencent.com/act/campus?fromSource=gwzcw.594708.594708.594708)，一个月10元就有一台还不错的服务器（0.8折！），于是爽快入坑连续包了3年(((

下面是目前我用服务器干的一些事情：
* [jupyter notebook](https://jupyter.org/)<br/>
这个无论什么服务器平台都会装，因为实在太好用，内置命令行和python环境，非常方便
* ftp<br/>
偶尔与服务器传输大型文件，同时可以搭建班级内部的提交作业平台<br/>
本地用来与服务器建立ssh连接与传输文件可用[xmanager](https://www.netsarang.com/en/xmanager/)(xftp+xshell)
* [seafile](https://www.seafile.com/)<br/>
自建轻量级网盘，效果奇佳，从电脑往手机传数据再也不用数据线了！
* 国内科学上网<br/>
这个不言而喻
* git<br/>
代码版本管理，学校小组项目会用到

### 编程语言
对的，这里我把各种编程语言也当成工具看待，以后（有时间的话）应该会把这些语言都写一篇Blog的吧。

#### 正统语言
* C：学完计组再回看会发现很多底层的细节被忽略了
* C++：各种算法及框架最常用，高效易写
* Python：Python大法好！
	<!-- - pip, Anaconda, numpy, pandas -->
* Haskell：函数式赞歌！
* Wolfram：MMA的编程语言，算半个吧(
* Verilog：传统的硬件描述语言
* [Chisel](https://chisel.eecs.berkeley.edu/)（在学）：UCB造的硬件锤子！

#### 其他玩意儿
* Markdown<br/>
不用关心排版，层次化分明
* 正则表达式<br/>
其实掌握常用匹配指令就好了，一开始觉得很复杂，后来觉得也还好，人家还不是图灵完备的(

### 人工智能
我就偏不说Tensorflow(((
当时入深度学习坑时选择TF，折腾了很久连它语法都没搞清楚，对初学者非常不友善，于是就此放弃
* [Pytorch](https://pytorch.org/)<br/>
原生Python语法，动态图，部署网络非常方便
* [Visdom](https://github.com/facebookresearch/visdom)<br/>
Pytorch对应的可视化工具，界面还可以接受，但目前还不够完善
* [Sklearn](https://scikit-learn.org/)：机器学习
* [numpy](http://www.numpy.org/)+[pandas](https://pandas.pydata.org/)：数据挖掘

### 线性规划求解器
因为我目前研究的调度算法需要用整数线性规划(Integer Linear Programming, ILP)解出最优解，所以会用到一些求解器，如下所示。
* [IBM CPLEX](https://ibm.onthehub.com/WebStore/OfferingDetails.aspx?o=733c3d21-0ce1-e711-80fa-000d3af41938&pmv=00000000-0000-0000-0000-000000000000)：学生可以申请免费
* [CBC](https://projects.coin-or.org/Cbc)：免费，有Python支持
* [PuLP](https://pythonhosted.org/PuLP/)：Python包集成了几个求解器，CBC是其中之一