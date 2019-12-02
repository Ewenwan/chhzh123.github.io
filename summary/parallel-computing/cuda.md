---
layout: post
title: 并行编程-CUDA
tag: [summary, parallel]
---

CUDA(Compute Unified Device Architecture)主要用于GPU上的编程，让SIMD能够对应用更加通用

## GPU与CUDA简介
GPU利用Moore定律
* 增加片上并行性及DRAM带宽
* 为图形应用提升灵活性和性能
* 加速通用数据并行任务

CUDA的目标：
* 可扩展性：任意顺序执行的独立块，线性加速比
* SIMD编程性：充分利用硬件架构，但CPU的SIMD往往很难使用，CUDA抽象提供编程性

CUDA GPU是流多处理器(streaming multiprocessors, SM)的集合，每一个SM都是一个SIMD执行流水的集合(scalar processors)，共享控制逻辑、寄存器堆、L1 cache。

## 安装
* <https://developer.nvidia.com/cuda-downloads>
* <https://docs.nvidia.com/cuda/cuda-quick-start-guide/index.html>

注意：现在WSL还不支持GPU！

## Hello World
由于GPU一般作为协处理器，故CPU与GPU常构成异构系统，其中CPU为host，GPU为device。

典型CUDA程序执行流程如下：
1. 分配host内存，并进行数据初始化；
2. 分配device内存，并从host将数据拷贝到device上；
3. 调用CUDA的核函数在device上完成指定的运算；
4. 将device上的运算结果拷贝到host上；
5. 释放device和host上分配的内存。

```cpp
#include <iostream>
#include <math.h>
// Kernel function to add the elements of two arrays
__global__
void add(int n, float *x, float *y)
{
  for (int i = 0; i < n; i++)
    y[i] = x[i] + y[i];
}

int main(void)
{
  int N = 1<<20;
  float *x, *y;

  // Allocate Unified Memory – accessible from CPU or GPU
  cudaMallocManaged(&x, N*sizeof(float));
  cudaMallocManaged(&y, N*sizeof(float));

  // initialize x and y arrays on the host
  for (int i = 0; i < N; i++) {
    x[i] = 1.0f;
    y[i] = 2.0f;
  }

  // Run kernel on 1M elements on the GPU
  add<<<1, 1>>>(N, x, y);

  // Wait for GPU to finish before accessing on host
  cudaDeviceSynchronize();

  // Check for errors (all values should be 3.0f)
  float maxError = 0.0f;
  for (int i = 0; i < N; i++)
    maxError = fmax(maxError, fabs(y[i]-3.0f));
  std::cout << "Max error: " << maxError << std::endl;

  // Free memory
  cudaFree(x);
  cudaFree(y);

  return 0;
}
```

## 基本语法
* `__global__`：核函数，在device上线程中并行执行的函数，从host中调用（一些特定的GPU也可以从device上调用），返回类型必须是void，不支持可变参数参数，不能成为类成员函数。注意用`__global__`定义的kernel是异步的，这意味着host不会等待kernel执行完就执行下一步
* `__device__`：在device上执行，单仅可以从device中调用，不可以和`__global__`同时用
* `__host__`：在host上执行，仅可以从host上调用，一般省略不写，不可以和`__global__`同时用，但可和`__device__`，此时函数会在device和host都编译

内存操作
* `cudaError_t cudaMalloc(void** devPtr, size_t size);`
* `cudaFree(void*)`
* `cudaError_t cudaMemcpy(void* dst, const void* src, size_t count, cudaMemcpyKind kind)`：kind控制复制的方向cudaMemcpyHostToHost, cudaMemcpyHostToDevice, cudaMemcpyDeviceToHost及cudaMemcpyDeviceToDevice
* `cudaError_t cudaMallocManaged(void **devPtr, size_t size, unsigned int flag=0)`：自CUDA 6.0开始，统一管理内存，自动进行数据传输

## 层次结构
CUDA编程模型分为4级层次结构（同样可以map到其他硬件上）
* Stream = list of grids (whole GPU)
* Grid = $$2^32$$ thread blocks
* Thread Block = up to 1024 cuda threads
* Cuda Thread: SIMD lane
* Warps: logical SIMD width

每一个cuda线程都有自己的**控制流、PC、寄存器、堆栈**，能够访问GPU任意全局内存地址
```
threadIdx.{x,y,z}
blockIdx.{x,y}
```

Kernel上的两层线程组织结构如下(2-dim)
![thread hierarchy](https://pic1.zhimg.com/v2-aa6aa453ff39aa7078dde59b59b512d8_b.jpg)

一个线程需要两个内置的坐标变量`(blockIdx,threadIdx)`来唯一标识，都是`dim3`变量。`<<<grid,block>>>`代表网格、线程块数目。

关于`dim3`的结构类型
* `dim3`是基于`uint3`定义的矢量类型，相当于由3个`unsigned int`型组成的结构体。`uint3`类型有三个数据成员`unsigned int x; unsigned int y; unsigned int z;`
* 可使用于一维、二维或三维的索引来标识线程，构成一维、二维或三维线程块(block)。
* 相关的几个内置变量
	- `threadIdx`，顾名思义获取线程`thread`的ID索引；如果线程是一维的那么就取`threadIdx.x`，二维的还可以多取到一个值`threadIdx.y`，以此类推到三维`threadIdx.z`。
	- `blockIdx`，线程块的ID索引；同样有`blockIdx.x`，`blockIdx.y`，`blockIdx.z`。
	- `blockDim`，线程块的维度，同样有`blockDim.x`，`blockDim.y`，`blockDim.z`。
	- `gridDim`，线程格的维度，同样有`gridDim.x`，`gridDim.y`，`gridDim.z`。
* 对于一维的`block`，线程的`threadID = threadIdx.x`
* 对于大小为`(blockDim.x, blockDim.y)`的二维`block`
	- `int i = blockIdx.x * blockDim.x + threadIdx.x;`
	- `int j = blockIdx.y * blockDim.y + threadIdx.y;`
* 对于大小为`(blockDim.x, blockDim.y, blockDim.z)`的三维`block`，线程的`threadID = threadIdx.x+threadIdx.y*blockDim.x+threadIdx.z*blockDim.x*blockDim.y`
* 对于计算线程索引偏移增量为已启动线程的总数，如`stride = blockDim.x * gridDim.x; threadId += stride`

```cpp
dim3 grid(3, 2);
dim3 block(5, 3);
kernel_fun<<< grid, block >>>(prams...);
// Thread(1,1)
// threadIdx.x = 1
// threadIdx.y = 1
// blockIdx.x = 1
// blockIdx.y = 1
```

* 每一个线程都有私有的寄存器，64/128KB的寄存器堆会划分到每一个线程上
* 每一个线程块都有一块共用内存(on-chip)
* 每一个网格共用一块大的**全局共享**内存（同时有一个768KB的共享L2）

![memory hierarchy](https://pic2.zhimg.com/v2-6456af75530956da6bc5bab7418ff9e5_b.jpg)

内存访问也是SIMD，尽可能稠密存储

## 编译运行
* 编译器`nvcc`
* 性能分析器`nvprof`
* 查看GPU信息`nvidia-smi`

## 参考资料
* An Even Easier Introduction to CUDA, <https://devblogs.nvidia.com/even-easier-introduction-cuda/>
* CUDA Education, <https://developer.nvidia.com/cuda-education>
* CUDA编程入门极简教程 - 小小将的文章 - 知乎，<https://zhuanlan.zhihu.com/p/34587739>
* CUDA-“从入门到放弃”，<https://www.jianshu.com/p/34a504af8d51>