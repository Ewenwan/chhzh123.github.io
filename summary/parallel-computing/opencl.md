---
layout: summary
title: 并行编程-OpenCL
---

OpenCL允许在异构设备上并行(CPU, GPU, FPGA, DSP)

## 平台(platform)模型
ICD(installable client driver)模型，允许不同厂商的平台同时存在
* 一个host，多个设备(devices)
* 一个设备分为多个计算单元
* 一个计算单元分成多个处理元素，每个处理元素有自己的PC

## 程序
* 程序对象(object)提供的源码/二进制文件，选定目标设备
* 核(kernel)是一个在程序中声明的函数，将会在OpenCL设备上执行

## 内存模型
* 显性的：需要告诉怎么从设备/主机上移动
* 没有保证的在不同工作组中通信的一致性

## 编程模型
* 数据并行：工作组能够被显式/隐式定义
* 任务并行
* 同步

## 编译运行
```bash
export LD_LIBRARY_PATH=/opt/AMDAPP/lib/x86_64
gcc -o vecadd vecadd.c 0I/opt/AMDAPP/include -l/opt/AMDAPP/lib/x86_64 -lOpenCL
```