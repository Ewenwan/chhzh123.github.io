---
layout: post
title: LaTeX常用格式调整指南
tag: [configuration]
---

本文记录LaTeX常用的preamble指令。

<!--more-->

## 图片与文字距离
下面这幅图很好展示了浮动体与文字之间的距离怎么进行计算。
![](https://i.stack.imgur.com/qjLqv.png)

```latex
\setlength{\textfloatsep}{5pt}
```

## 参考资料
* <https://tex.stackexchange.com/questions/60477/remove-space-after-figure-and-before-text?rq=1>