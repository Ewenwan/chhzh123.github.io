---
layout: summary
title: 并行计算-离散搜索与负载均衡
---

DFS搜深度为k的树，每个节点遍历一次，时间复杂度为$$O(b^k)$$，空间复杂度为$$\Theta(k)$$

并行DFS关键在于负载：任务分割(splitting)及动态负载均衡
* 捐赠(donor)进程：发送任务(work)的进程
* 接受(recipient)进程：接收任务的进程
* 半分割(half-split)：理想地，一个stack被分为两块等大
* 隔断(cutoff)深度：避免发送太小的任务，在给定深度时就不再发送，自己完成