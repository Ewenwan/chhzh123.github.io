---
layout: summary
title: 并行编程-OpenCL
---

OpenCL提供了主机和加速器设备交互的界面，允许在异构设备上并行(CPU, GPU, FPGA, DSP)

## 平台(platform)模型
ICD(installable client driver)模型，允许不同厂商的平台同时存在，如`libcudart.so`是NVIDIA的，`lib.amdocl64.so`是AMD的，只需对应链接即可
* 一个host，多个设备(devices)
* 一个设备分为多个计算单元
* 一个计算单元分成多个处理元素，每个处理元素有自己的PC

## 程序
* 程序对象(object)提供的源码/二进制文件，选定目标设备
	- OpenCL核的集合，可以是源代码或预编译的二进制文件
	- 还可以包含常量或辅助函数
* 核(kernel)是一个在程序中声明的函数，将会在OpenCL设备上执行

地址空间对象声明
* `__global`：全局地址空间
* `__constant`：只读内存
* `__local`：被work-group共享内存
* `__private`：对于每个work-item私有
* `__read_only/__write_only`：用户图片
* 核的参数必须是全局、常数或局部

```cpp
__kernel void vecadd(__global int* A, __global int* B, __global int* C){
	int tid = get_global_id(0);
	C[tid] = A[tid] + B[tid];
}
```

* 内存对象会被创建并移动到(on and off)设备上
* 请求队列允许host向设备请求操作
* 程序和核包含设备需要执行的代码

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