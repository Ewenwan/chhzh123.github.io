---
layout: post
title: gprof性能分析器
tag: [tools]
---

上一篇[文章]({% post_url 2019-02-19-pcm %})讲述了内存、CPU**实时监视器**的使用，而本文则着重于更高层的**性能分析器**(profiler)。

<!--more-->

## 性能分析器
所谓性能分析器，就是分析程序运行中究竟什么函数运行次数最多，什么地方存在瓶颈(bottleneck)。
而实时监视器也可以算是一种性能分析器，都是用来进行性能分析(profiling)，只是返回的内容不同。

Linux环境下GNU内置了一个性能分析器，称为gprof。

## gprof使用指南
gprof的使用和[gdb]({% post_url 2019-03-16-gdb %})一样简明易懂。

* 编译添加指令`-pg`
* 运行程序，会自动生成`gmon.out`文件
* 用`gprof <exe> gmon.out > analysis.txt`将性能分析结果写出
	- 注意如果`<exe>`执行文件带指令，只需在第一次运行时添加即可，第二次运行`gprof`只用告诉其文件名

最终可以得到如下结果，详细说明每个函数的使用情况
```
Each sample counts as 0.01 seconds.
%    cumulative self          self   total
time seconds    seconds calls s/call s/call name
33.86 15.52     15.52    1    15.52  15.52  func2
33.82 31.02     15.50    1    15.50  15.50  new_func1
33.29 46.27     15.26    1    15.26  30.75  func1
0.07  46.30     0.03                        main
```

## 参考资料
* 官网，<https://sourceware.org/binutils/docs/gprof/>
* GPROF Tutorial, <https://www.thegeekstuff.com/2012/08/gprof-tutorial/>