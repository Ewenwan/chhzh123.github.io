---
layout: post
title: Vivado HLS in a Nutshell
tags: [hls]
---

本文将简要介绍Vivado HLS的一些基本用法。

<!--more-->

<font color="red">注意本文并未完结！！！</font>

C-HLS可以简单理解为C/C++语言的扩展，即提供了一些硬件编译指示，从而使得高层的规范(specification)可以被映射到RTL层级的电路描述。

## 快速入门
C/C++中的设施与硬件设施有如下对应。

| C/C++ | 硬件 |
| :--: | :--: |
| 函数 | 模块(module) |
| 参数 | 输入/输出端口(port) |
| 算子 | 函数单元 |
| 标量 | 线(wire)或寄存器 |
| 数组 | 内存(memory) |
| 控制流 | 控制逻辑 |

通常情况下RTL代码/硬件模块层次与原始C/C++代码层次一致。

{% include image.html fig="FPGA/hls-function-hierarchy.jpg" width="80" %}

下面以矩阵乘法为例（摘自[Zynq Book Tutorials](http://www.zynqbook.com/download-tuts.html) Exercise 3），需要写下列4个程序。

<ul>
<li><details>
<summary><code>matrix_mult.h</code>：头文件，包括基本宏定义、类型定义及函数原型</summary>

```cpp
#ifndef __MATRIXMUL_H__
#define __MATRIXMUL_H__

#include <cmath>
using namespace std;

// Compare TB vs HW C-model and/or RTL
#define HW_COSIM

#define IN_A_ROWS 5
#define IN_A_COLS 5
#define IN_B_ROWS 5
#define IN_B_COLS 5

typedef char mat_a;
typedef char mat_b;
typedef short mat_prod;

// Prototype of top level function for C-synthesis
void matrix_mult(
      mat_a a[IN_A_ROWS][IN_A_COLS],
      mat_b b[IN_B_ROWS][IN_B_COLS],
      mat_prod prod[IN_A_ROWS][IN_B_COLS]);

#endif // __MATRIXMUL_H__ not defined
```

</details></li>

<li><details>
<summary><code>matrix_mult.cpp</code>：核心函数实现</summary>

```cpp
#include "matrix_mult.h"

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
</details></li>


<li><details>
<summary><code>matrix_mult_test.cpp</code>：测试代码，用于软硬件协同模拟</summary>

```cpp
#include <iostream>
#include "matrix_mult.h"

using namespace std;

int main(int argc, char **argv)
{
    mat_a in_mat_a[5][5] = {
        {0, 0, 0, 0, 1},
        {0, 0, 0, 1, 0},
        {0, 0, 1, 0, 0},
        {0, 1, 0, 0, 0},
        {1, 0, 0, 0, 0}};
    mat_b in_mat_b[5][5] = {
        {1, 1, 1, 1, 1},
        {0, 1, 1, 1, 1},
        {0, 0, 1, 1, 1},
        {0, 0, 0, 1, 1},
        {0, 0, 0, 0, 1}};
    mat_prod hw_result[5][5], sw_result[5][5];
    int error_count = 0;

    // Generate the expected result
    // Iterate over the rows of the A matrix
    for (int i = 0; i < IN_A_ROWS; i++)
    {
        for (int j = 0; j < IN_B_COLS; j++)
        {
            // Iterate over the columns of the B matrix
            sw_result[i][j] = 0;
            // Do the inner product of a row of A and col of B
            for (int k = 0; k < IN_B_ROWS; k++)
            {
                sw_result[i][j] += in_mat_a[i][k] * in_mat_b[k][j];
            }
        }
    }

#ifdef HW_COSIM
    // Run the Vivado HLS matrix multiplier
    matrix_mult(in_mat_a, in_mat_b, hw_result);
#endif

    // Print product matrix
    for (int i = 0; i < IN_A_ROWS; i++)
    {
        for (int j = 0; j < IN_B_COLS; j++)
        {
#ifdef HW_COSIM
            // Check result of HLS vs. expected
            if (hw_result[i][j] != sw_result[i][j])
            {
                error_count++;
            }
#else
            cout << sw_result[i][j];
#endif
        }
    }

#ifdef HW_COSIM
    if (error_count)
        cout << "TEST FAIL: " << error_count << "Results do not match!" << endl;
    else
        cout << "Test passed!" << endl;
#endif
    return error_count;
}
```
</details></li>

<li><details>
<summary><code>run_hls.tcl</code>：自动化编译运行代码</summary>

```bash
# run.tcl

# open the HLS project mm.prj
set src_dir "."
open_project -reset matrix_mult_prj

# set the top-level function of the design
set_top mmult_hw

# add design and testbench files
add_files $src_dir/matrix_mult.h
add_files $src_dir/matrix_mult.cpp
add_files -tb $src_dir/matrix_mult_test.cpp

open_solution "solution"

# use Zynq device
set_part {xc7z020clg484-1}

# target clock period is 10 ns
create_clock -period 10 -name default

# do a c simulation
csim_design -clean

# synthesize the design
csynth_design

# do a co-simulation
#cosim_design

# close project and quit
close_project
exit
```
</details></li>
</ul>


通过流水线方式，降低初始间隔(initial interval, II)，提升并行度，提升吞吐率。

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
        #pragma HLS PIPELINE II=1
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

需要完成循环所需总的时钟周期数为

$$N_{loop}=(J\times N_{body})+N_{control}$$

最后一步则是将数组进行划分，以提升IO效率。

```cpp
void matrix_mult(
    mat_a a[IN_A_ROWS][IN_A_COLS],
    mat_b b[IN_B_ROWS][IN_B_COLS],
    mat_prod prod[IN_A_ROWS][IN_B_COLS])
{
    #pragma HLS ARRAY RESHAPE variable=a complete dim=2
    #pragma HLS ARRAY RESHAPE variable=b complete dim=2
    // Iterate over the rows of the A matrix
Row:
    for (int i = 0; i < IN_A_ROWS; i++)
    {
    // Iterate over the columns of the B matrix
    Col:
        for (int j = 0; j < IN_B_COLS; j++)
        {
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

## 编译运行
通过`vivado_hls -f run_hls.tcl`调用。

{% include image.html fig="FPGA/hls-directory-structure.jpg" width="80" %}

## C HLS pragma
* `#pragma HLS pipeline II=<int>`
* `#pragma HLS array_reshape variable=<name> <type> factor=<int> dim=<int>`
* `#pragma HLS dataflow`
* `#pragma HLS unroll factor=<N>`

## 数据类型
任意精度整数(Arbitrary Precision, AP)
* `#include "ap_int.h"`
* `ap_int`有符号，`ap_uint`无符号
* 用模板类声明，如`ap_uint<24>`代表24位无符号整数

定点数
* `#include "ap_fixed.h"`
* `ap_fixed`和`ap_ufixed`
* `ap_fixed<W,I,Q,O>`
    * `W`：总字长
    * `I`：整数字长
    * `Q`：量化(quantization)模式
    * `O`：上溢(overflow)模式

如`ap_ufixed<11,8,AP_TRN,AP_WRAP>`代表
* 11位长度定点数，8位整数位，3位小数位
* `AP_TRN`表示量化时采用截断(truncation)
* `AP_WRAP`表示用wrapping来处理上溢（即直接丢除最高位，这会导致循环）；另外一种是浸润模式`AP_SAT`，高于最大值都当最大值，低于最小值都当最小值

{% include image.html fig="FPGA/ap_fixed_overflow.jpg" width="80" %}

## 需要注意的点
* HLS不支持递归、系统调用（文件读取）、动态内存分配
* 默认情况下，循环都不展开(rolled)
* 当外层循环用了`pipeline`或者`unroll`时，内层循环默认展开
* HLS默认优化面积，即用最小的资源实现目标（串行架构），因此时延可能非常慢，吞吐率低

## 参考资料说明
本文主要参照以下资料进行整理，特别向这些课程/书籍/资料的作者和老师致以感谢。

* [^1]是非常好的关于Xilinx Zynq和SoC/异构系统入门的书籍，其中第14章介绍了高层次综合(HLS)的基本概念，第15章则非常清晰明了地介绍了Vivado HLS的常用指令及相关规范，该书特别适合初学者入门——简练而突出重点，同时也有免费的中文版可以下载。
* [^3]讲述了高层次综合的整体流程及原理，第2课简要介绍了Vivado HLS的使用，同时以FIR (Finite Impulse Response)为例讲解HLS的优化指令，也是十分简明扼要；第3课关于FPGA的硬件结构也非常有必要了解。
* [^2]是U Washington研究生体系结构课程中的一个实验项目，算是一个非常非常非常详细的Vivado HLS的入门教程了，基本上能够调到他预期的加速比就算达成任务了。本文中矩阵乘的例子就来源于此。
* [^4]可作为速查手册，提供了所有C HLS #pragma
* [^5]和[^6]是官方说明手册，前者是完整的HLS说明书，后者则是Vivado HLS的一些实验范例（但比较侧重于图形化界面）
* [^7]给出了大量应用加速的例子，算是HLS的高阶应用教程
* [^8]收录了大量FPGA的学习资料，上述很多链接也从该项目中获取

## Resources
[^1]: The Zynq Book, <http://www.zynqbook.com/>, [Chinese edition](http://www.zynqbook.com/download-book-chinese.php)
[^2]: Thierry Moreau, [UW CSE548](https://courses.cs.washington.edu/courses/cse548/17sp/) [Lab 3: Custom Acceleration with FPGAs](https://github.com/uwsampa/cse548-labs), Spring 2017
[^3]: Zhiru Zhang, [Cornell ECE 5775](http://www.csl.cornell.edu/courses/ece5775/schedule.html): High-Level Digital Design Automation, Fall 2018
[^4]: [SDAccel HLS Pragmas](https://www.xilinx.com/html_docs/xilinx2018_3/sdaccel_doc/hls-pragmas-okr1504034364623.html#okr1504034364623)
[^5]: [Xilinx Vivado HLS User Guide](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2017_1/ug902-vivado-high-level-synthesis.pdf)
[^6]: [Xilinx Vivado HLS Tutorial](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2017_1/ug871-vivado-high-level-synthesis-tutorial.pdf)
[^7]: Ryan Kastner, Janarbek Matai, and Stephen Neuendorffer (UCSB), *[Parallel Programming for FPGAs](https://arxiv.org/abs/1805.03648)*, 2018
[^8]: Yizhou Shan, [Cook FPGA](https://github.com/lastweek/fpga_readings)