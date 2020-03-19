---
layout: post
title: 再谈DSL
tags: pl
---

看看这几年领域特定编程语言(Domain Specific Language, DSL)的发展，会发现**算法和调度的解耦**越来越明显，同时**编译和综合的边界**越来越模糊。

<!--more-->

这些年涌现了一大批DSL，它们算是软件2.0时代的产物，也是编译3.0时代的推进者。

其中的先锋者即[Halide](https://halide-lang.org/)[^1]，最早提出要将算法(algorithm)和调度(schedule)相分离。
之后的[TVM](https://tvm.apache.org/)[^2]、[HeteroCL](http://heterocl.csl.cornell.edu/web/index.html)[^3]、[GraphIt](https://graphit-lang.org/)[^4]、[Taichi](http://taichi.graphics/)[^5]等DSL无不在践行这一准则。

事实上调度的思想在HLS的发展中一直存在，毕竟HLS就是以综合作为根基的。但是HLS的问题在于它太过将算法和调度**紧耦合**了，导致代码十分的难写（也即所谓的混合软硬件特性）。还是举经典的GEMM的例子

```cpp
void matrix_mult(
    mat_a a[IN_A_ROWS][IN_A_COLS],
    mat_b b[IN_B_ROWS][IN_B_COLS],
    mat_prod prod[IN_A_ROWS][IN_B_COLS])
{
    // Iterate over the rows of the A matrix
Row:
    for (int i = 0; i < IN_A_ROWS; i++)
    {
    // Iterate over the columns of the B matrix
    Col:
        for (int j = 0; j < IN_B_COLS; j++)
        {
        #pragma HLS PIPELINE II=1 // here!!!
            prod[i][j] = 0;
        // Do the inner product of a row of A and col of B
        Product:
            for (int k = 0; k < IN_B_ROWS; k++)
            {
                prod[i][j] += a[i][k] * b[k][j];
            }
        }
    }
}
```

其中实现流水最好是将编译指示插在中间层循环，但是对于没有经验的人来说，可能就需要在三层循环体分别进行尝试，然后选出最优性能的插入。

我们会发现，事实上无论你的编译指示插在哪，对最终计算的结果是不会有影响的，而影响的只是它的计算速度。除了<u>流水线</u>，对于循环的优化还有<u>调换顺序、循环展开(unrolling)、铺砖(tiling)</u>等等，这些都不会对运算结果产生影响。

因此如果我们将算法（也即GEMM）抽象出来，然后要做的优化（也即所谓的调度）又另外进行抽象，那我们就可以采用一些自动化的方法对整体程序进行优化。

所以当`#pragma HLS PIPELINE II=1`这种语句写成`GEMM.schedule("PIPELINE",1)`的形式，那我们就实现了**算法和调度的分离**。更一般化地来说，我们可将调度表示成

```cpp
<algorithm>.schedule(<optimization>,<args>)
```

从而程序员可以更加focus在算法的核心部分，而其余的优化则交由编译器来做。

这种方法能行得通的原因很大程度上也依赖于现在硬件的发展，因为硬件的速度越来越快，因而我们也开始有办法去处理这些庞大的搜索空间，而不再需要程序员手工去优化。无论是启发式方法抑或是机器学习方法，都能实现很高程度的自动化，进而实现自动调优的功能，这也是现在为什么这些DSL的编译器基本都集成了综合的功能。只要spec定义得好，那么剩下的事情就交给机器了，既然是有限的搜索空间（`<opt>`和`<args>`都是有限的），那就一定能搜出最优解（至于搜多长时间就涉及到搜索算法的效率问题了）。

## References
[^1]: Jonathan Ragan-Kelley (MIT), Connelly Barnes, Andrew Adams, Sylvain Paris, Frédo Durand, and Saman Amarasinghe, *Halide: A Language and Compiler for Optimizing Parallelism, Locality, and Recomputation in Image Processing Pipelines*, PLDI, 2013
[^2]: Tianqi Chen (UW), Thierry Moreau, Ziheng Jiang, Lianmin Zheng, Eddie Yan, Arvind Krishnamurthy, et al., *TVM: An Automated End-to-End Optimizing Compiler for Deep Learning*, OSDI, 2018
[^3]: Yi-Hsiang Lai (Cornell), Yuze Chi, Yuwei Hu, Jie Wang, Cody Hao Yu, Yuan Zhou, Jason Cong, Zhiru Zhang, *HeteroCL: A Multi-Paradigm Programming Infrastructure for Software-Defined Reconfigurable Computing*, FPGA, 2019
[^4]: Yunming Zhang (MIT), Mengjiao Yang, Riyadh Baghdadi, Shoaib Kamil, Julian Shun, Saman Amarasinghe, *GraphIt: A High-Performance Graph DSL*, OOPSLA, 2018
[^5]: Yuanming Hu (MIT), Tzu-Mao Li, Luke Anderson, Jonathan Ragan-Kelley, Frédo Durand, *Taichi: A Language for High-Performance Computation on Spatially Sparse Data Structures*, SIGGRAPH Asia, 2019