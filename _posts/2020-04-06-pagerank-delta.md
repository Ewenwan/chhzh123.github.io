---
layout: post
title: PageRank Delta
tags: [graph]
---

本文记录PageRank Delta的推导过程及在图系统中的实现。

<!--more-->

$$p_v=\frac{1-\gamma}{\vert V\vert}+\gamma\sum_{u\in N^-(v)}\frac{p_u}{\deg^+(u)}$$

考虑算差值
$$
\begin{aligned}
\Delta_v&:=p_v^{(k+1)}-p_v^{(k)}\\
&=\left(\frac{1-\gamma}{\vert V\vert}+\gamma\sum_{u\in N^-(v)}\frac{p_u^{(k+1)}}{\deg^+(u)}\right)-\left(\frac{1-\gamma}{\vert V\vert}+\gamma\sum_{u\in N^-(v)}\frac{p_u^{(k)}}{\deg^+(u)}\right)\\
&=\gamma\sum_{u\in N^-(v)}\frac{\Delta_u}{\deg^+(u)}
\end{aligned}
$$

对于第一轮，初始化为$p_v^{(0)}=1/\vert V\vert$，而
$$p^{(1)}_v=\frac{1-\gamma}{\vert V\vert}+\gamma\sum_{u\in N^-(v)}\frac{1}{\vert V\vert \deg^+(u)}$$

后面的
$$p^{(k+1)}_v=p^{(k)}_v+\gamma\sum_{u\in N^-(v)}\frac{\Delta_u^{(k)}}{\deg^+(u)}
=p_v^{(k)}+\gamma\cdot nghSum_v^{(k)}$$

因此，初始化$p_v^{(0)}=(1-\gamma)/\vert V\vert$，$\Delta_v^{(0)}=1/\vert V\vert$，通过edgeMap可得到$ngh_v^{(0)}$，进而算出$p_v^{(1)}$，但注意要重新计算$\Delta_v^{(0)}$的值，使其等于$p_v^{(1)}-p_v^{(0)}$。

完整实现可参见[Krill-PRDelta](https://github.com/chhzh123/Krill/blob/master/apps/PageRankDelta.h)。