---
layout: post
title: Tools Setup!
tag: [research, tools]
---

**工具是重要的！**这点其实很多老师都不会讲述。
然而好用的用得顺手的工具可以使工作效率大大提升，不好用的工具虽然也可以用，但是会增加很多不必要的时间。

最简单的例子是很多非计院的同学学了一整个学期代码（C++/Java），都还在**非常古老的**IDE上写程序（我说的是Dev(）。
这当然可以写，但是常言道“优秀的程序员都是不用IDE的！”
如果有更强大的工具可以让你事半功倍，何乐而不为呢？

这篇文章列举/总结我目前所使用的一些工具作为参考，都是使用了很长时间，亲测比较好用。

（基于这点motivation，所以我在2019-2020年度开了门ToolsSeminar的研讨会，详细内容可见[这里](/seminar)。）

<!--more-->

## 电脑与服务器
* 手提电脑配置
	- Intel i7 CPU (8核）+ GTX 1050 + 8G内存 + 256G SSD + 1T移动硬盘
	- Windows 10 + Ubuntu 18.04 LTS (subsystem)
* 腾讯云服务器：自己租的用来搞事情
	- Intel Xeon CPU E5-26xx (单核) + 2G内存 + 50G云硬盘
	- CentOS 7.2
* 实验室服务器：
	- Intel Xeon CPU Gold 5118 (24核) + Titan V (2块) + 64G内存 + 11T硬盘
	- Ubuntu 18.04 LTS

## 装机基础配置
之后考虑将这些东西打包成Docker上传上云，这样就不用每次换电脑都重新安装了。
* Microsoft Office（一般都会预装，新机要登陆激活）
* Google Chrome
* VS Code + Sublime Text
* Windows Subsystem for Linux (WSL)
* TeXLive 2020
	* 可直接在[清华镜像](https://link.zhihu.com/?target=https%3A//mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/Images/)下载
	* Windows安装双击`install-tl-windows.bat`文件，可能需要几个小时安装时间
* WeChat + Tim

## 日常工作
* [Microsoft To Do](https://todo.microsoft.com/tasks/)
	* 极其好用的代办事项工具
	* 可以分类创建列表
	* 支持加备注加提醒
	* 多终端多平台
* [Google Calendar](https://calendar.google.com/calendar/r)
	* 极其好用的日历工具，我所有课程表都创在上面了
	* 可定期（如每周一或重复几次）提醒，这点太重要了！
	* 多种颜色tag选择
	* 可加备注加提醒
	* 多终端多平台

## WSL配置
安装在Microsoft Store搜索Ubuntu即可，注意安装后打开前需要先在控制面板-程序和功能-启用或关闭Windows功能中将"适用于Linux的Windows子系统"打开并重启。详细安装教程可见Microsoft[官网](https://docs.microsoft.com/en-us/windows/wsl/install-win10)。其中也有说明如何升级至WSL2，需要先升级Windows版本至2004(Build 19041)，然后才有办法启用。WSL1和WSL2的比较见[此文](https://docs.microsoft.com/en-us/windows/wsl/compare-versions)。

```bash
# 参照清华镜像站换源
# https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak
sudo vim /etc/apt/sources.list

# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse

# 预发布软件源，不建议启用
# deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-proposed main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-proposed main restricted universe multiverse

sudo apt-get update
sudo apt-get upgrade

## install gcc compiler
sudo apt install build-essential
gcc --version

## install pip
sudo apt install python3-pip

## python virtualenv
which python3
sudo apt install python3-virtualenv
virtualenv -p /home/.../python3 pydev
source pydev/bin/activate
python -V
deactivate

# pip change source
# ~/.pip/pip.conf
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple

# graphics apps (open Xming in Windows first)
sudo apt-get install x11-apps
export DISPLAY=:0 # WSL1
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0 # WSL2, need to set `-ac` for X server
# https://github.com/microsoft/WSL/issues/4106
xeyes
# desktop
sudo apt-get install xfce4-terminal
sudo apt-get install xfce4
startxfce4

## accelerate git
sudo apt-get install proxychains
vim /etc/proxychains.conf
# change socks4 127.0.0.1 9095 to
socks5 127.0.0.1 1080

proxychains git clone ...

# mount external storage
sudo mount -t drvfs G: /mnt/g
sudo unmount /mnt/g
```

可能出现的问题
* `dpkg: error processing package libc6:amd64 (--configure)`，参见[此文](https://stackoverflow.com/questions/60944370/stuck-with-apt-fix-broken-install-libc6amd64-package-post-installation)
* `[WSL1] [glibc] sleep: cannot read realtime clock: Invalid argument`，这是WSL1的bug，需[重新编译sleep](https://github.com/microsoft/WSL/issues/4898)

## 文本编辑器
目前使用主要使用两个文本编辑器，Sublime Text用来做一些轻量级的工作（因为打开速度实在是快），VS Code用来做一些大一点的项目。

### [Sublime Text 3](http://www.sublimetext.com/)
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

### [VS Code](https://code.visualstudio.com/)
不得不说，经过大半年的发展，微软爸爸的文本编辑器已经相当成熟了。

优点：
* sublime有的基本都有
* Intellisense
* 大量插件支持
	* Python / Jupyter notebook原生支持
	* Markdown预览
	* LaTeX编译显示
* 自动跳转至定义位置（大项目必备）
* 跨文件/全局搜索
* SSH远端支持

## 笔记
笔记怎么做也是我这一年多来摸索的东西，现在基本上用下面两个工具啦。
* LaTeX<br/>
极重度用户，已经到了写篇文科小报告都要拿LaTeX打的地步...
日常的话，[数学](https://github.com/chhzh123/Notes-of-Math)和[CS](https://github.com/chhzh123/CS-Notes)的笔记都会用LaTeX打，目前数学大致有一百多页的样子，CS也有几十页，算是给自己大学的学习留档吧。
因为使用太频繁，到年初才自己制作了份[模板](https://github.com/chhzh123/mylatextmpl)，又瞬间让自己生产力爆炸。

目前想到的一些不那么大众的点有
1. TikZ-cd画流程图很爽
2. BibTeX要学会，生成参考文献神器
3. 表格可以不用自己打，Excel有宏可以支持

* [TiddlyWiki](https://tiddlywiki.com/)<br/>
这一个比较少人用，但是非常方便，也是满足了我写md、写LaTeX、贴代码的要求。
就是一个html页面，里面存自己的笔记，但是页面布局都已经帮你设置好了，直接可以写，还可以上传到服务器上让所有人都可以访问（但是几M大小基本加载不出来...）。
平时文科类的笔记会存在里面，还有部分有用的代码，其他的话...就当成网页收藏夹了...

## 文献管理
* [Zotero](https://www.zotero.org/)：学长推荐，必属精品(

优点：
* 分类归档论文，可以加Tag和Related
* 可以添加笔记
* 可以直接在网上下载pdf文件并解析文本生成条目
* 可以全仓库搜索文件
* 自动管理参考文献，且可以导出为BibLaTeX
* 支持不同格式的文件读入
* 好像还有云同步，但并没有用过

## 流程图/模型图绘制
写论文或者建模就知道画图的苦，以前一直都羡慕人家的文章中能够画出那么漂亮的图片，因为以往都只知道函数图怎么画，但不知道有什么比较好用的流程图工具
* [draw.io](https://draw.io)<br/>
在线画图，有网格，图形多，使用方便，画什么都容易，不足是对插图的处理不强，原生LaTeX在导出时常常出现问题
* [Microsoft Visio](https://products.office.com/en-us/visio/flowchart-software)<br/>
需要学校账户下载安装，而且还是Office 365版本
* [ipe](http://ipe.otfried.org/)<br/>
下载解压即用，有网格，但自动吸附格点，使用极其麻烦（要记一堆快捷键，有种CAD的感觉），但对LaTeX的支持非常好
* [TikZ-cd](http://ctan.math.washington.edu/tex-archive/graphics/pgf/contrib/tikz-cd/tikz-cd-doc.pdf)<br/>
刚才提到的LaTeX包，用`&`即可实现对齐，绘制简单的流程图非常方便
* [Doxygen](https://www.doxygen.nl/index.html)
	* `doxygen -g`生成初始的配置文件，然后可以修改下列常用项
	```python
	PROJECT_NAME        = "Test"
	OUTPUT_DIRECTORY    = doc/
	RECURSIVE           = YES
	UML_LOOK            = YES
	HAVE_DOT            = YES
	CALL_GRAPH          = YES
	CALLER_GRAPH        = YES
	SOURCE_BROWSER      = YES
	GENERATE_TREEVIEW   = ALL
	```
	* `doxygen Doxyfile`即可生成HTML和TeX文档。

### 有限状态机
* TikZ里有automata的package
* http://madebyevan.com/fsm/

## 数据可视化
这个也是写论文必备
* [Matplotlib](https://matplotlib.org/)<br/>
Python包，功能强大，不过我主要用来画折线图、柱形图；语法还算简单，添加标签标注等等也不会太麻烦，标签可以直接输入LaTeX代码
* [Mathematica(MMA)](https://www.wolfram.com/mathematica/)<br/>
上大学之前就只知道MMA画函数/3D/等高线图，其实用matplotlib画2D函数图会简单很多；而直到这一次建模也才直到MMA这么强大，还可以直接制作有数值的地图，完全是开外挂...
	<!-- > TODO MMA 剑魔 -->
* [Plotly](https://plot.ly/)<br/>
在线网站，可以用Python调用API，功能很强大，但还未自己试过

## 服务器
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

## 编程语言
对的，这里我把各种编程语言也当成工具看待，以后（有时间的话）应该会把这些语言都写一篇Blog的吧。

### 正统语言
* C：学完计组再回看会发现很多底层的细节被忽略了
* C++：各种算法及框架最常用，高效易写
* Python：Python大法好！
	<!-- - pip, Anaconda, numpy, pandas -->
* Haskell：函数式赞歌！
* Wolfram：MMA的编程语言，算半个吧(
* Verilog：传统的硬件描述语言
* [Chisel](https://chisel.eecs.berkeley.edu/)（在学）：UCB造的硬件锤子！

### 其他玩意儿
* Markdown<br/>
不用关心排版，层次化分明
	* [Gitlab Markdown Guide](https://about.gitlab.com/handbook/engineering/ux/technical-writing/markdown-guide/)
	* [Markdown Guide for Jupyter Notebook](https://medium.com/analytics-vidhya/the-ultimate-markdown-guide-for-jupyter-notebook-d5e5abf728fd)
* 正则表达式<br/>
其实掌握常用匹配指令就好了，一开始觉得很复杂，后来觉得也还好，人家还不是图灵完备的(

## 人工智能
当时入深度学习坑时选择TF，折腾了很久连它语法都没搞清楚，对初学者非常不友善，于是就此放弃
* [Pytorch](https://pytorch.org/)<br/>
原生Python语法，动态图，部署网络非常方便
	* CUDA 10.2[下载](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&target_distro=Ubuntu&target_version=1804&target_type=deblocal)及[安装](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)，注意要先[卸载旧版本](https://askubuntu.com/questions/530043/removing-nvidia-cuda-toolkit-and-installing-new-one)
* [Visdom](https://github.com/facebookresearch/visdom)<br/>
Pytorch对应的可视化工具，界面还可以接受，但目前还不够完善
* [Sklearn](https://scikit-learn.org/)：机器学习
* [numpy](http://www.numpy.org/)+[pandas](https://pandas.pydata.org/)：数据挖掘

## 线性规划求解器
因为我目前研究的调度算法需要用整数线性规划(Integer Linear Programming, ILP)解出最优解，所以会用到一些求解器，如下所示。
* [IBM CPLEX](https://ibm.onthehub.com/WebStore/OfferingDetails.aspx?o=733c3d21-0ce1-e711-80fa-000d3af41938&pmv=00000000-0000-0000-0000-000000000000)：学生可以申请免费
* [CBC](https://projects.coin-or.org/Cbc)：免费，有Python支持
* [PuLP](https://pythonhosted.org/PuLP/)：Python包集成了几个求解器，CBC是其中之一

## 性能剖析
* Linux perf
	* [Memory loads](https://stackoverflow.com/questions/44466697/perf-stat-does-not-count-memory-loads-but-counts-memory-stores)
	* [Cache reference](https://stackoverflow.com/questions/55035313/how-does-linux-perf-calculate-the-cache-references-and-cache-misses-events)
* Intel PCM

## 其他东西
* [Github Desktop](https://desktop.github.com/)
* [Github Page](https://pages.github.com)+[Jekyll](https://github.com/jekyll/jekyll)：就是这个博客啦
* [Google Calendar](https://www.google.com/calendar)：有Google账号可以同步，界面非常清爽
* [Gnu Privacy Guard(GPG)](https://www.gnupg.org)：Linux平台下文件加密系统，配合[Mailvelope](https://www.mailvelope.com/en/help)食用更加
	- 原理是用对方的公钥加密，邮件发送给对方后，对方用自己的密钥解密
	- `gpg --version`查看是否有安装
	- `gpg --genkey`生成密钥
	- `gpg -k --keyid-format long`查看公(k)/私(K)钥
	- `gpg --send-keys [ID] --keyserver pgp.mit.edu`上传公钥
	- `gpg --search-keys [ID]`搜索密钥
	- `gpg --export -a "[user]" > [user].pub`导出公钥
	- `gpg --export-secret-keys -a "[user]" > [user].priv`导出私钥
	- `gpg --delete(-secret)-keys [Email]`删除密钥
	- `gpg --import [key].pub`导入公/私钥
	- `gpg --encrypt --armor -r [Email] [file]`生成ASCII码加密文件
	- `gpg -d [file].asc`解密文件
* 查看Github仓库大小，用[API](https://stackoverflow.com/questions/8646517/how-can-i-see-the-size-of-a-github-repository-before-cloning-it)

## 网页样式
* [Bootstrap Alerts](https://getbootstrap.com/docs/4.0/components/alerts/)