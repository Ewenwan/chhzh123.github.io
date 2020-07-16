---
layout: post
title: Vivado HLS in a Nutshell
tags: [hls]
---

本文将简要介绍Vivado HLS的一些基本用法。

<!--more-->

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

<!-- https://github.com/gettalong/kramdown/issues/155 -->
<!-- https://kramdown.gettalong.org/syntax.html#html-blocks -->

* <details markdown="1">
    <summary markdown="span">
    <code>matrix_mult.h</code>：头文件，包括基本宏定义、类型定义及函数原型
    </summary>

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
    </details>
* <details markdown="1">
    <summary markdown="span">
    <code>matrix_mult.cpp</code>：核心函数实现
    </summary>

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
    </details>
* <details markdown="1">
    <summary markdown="span">
    <code>matrix_mult_test.cpp</code>：测试代码，用于软硬件协同模拟
    </summary>

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
    </details>
* <details markdown="1">
    <summary markdown="span">
    <code>run_hls.tcl</code>：自动化编译运行代码
    </summary>

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
    </details>

通过`vivado_hls -f run_hls.tcl`调用。

{% include image.html fig="FPGA/hls-directory-structure.jpg" width="80" %}

命令行运行的结果如下。

<details markdown="1">
<summary markdown="span">
Command line execution results
</summary>

```
****** Vivado(TM) HLS - High-Level Synthesis from C, C++ and SystemC v2018.1 (64-bit)
  **** SW Build 2188600 on Wed Apr  4 18:40:38 MDT 2018
  **** IP Build 2185939 on Wed Apr  4 20:55:05 MDT 2018
    ** Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
#######
# set up projects
#######

# c simulation
INFO: [SIM 211-2] *************** CSIM start ***************
INFO: [SIM 211-4] CSIM will launch GCC as the compiler.
   Compiling ../../../../matrix_mult_test.cpp in debug mode
   Compiling ../../../../matrix_mult.cpp in debug mode
   Generating csim.exe
Test passed!
INFO: [SIM 211-1] CSim done with 0 errors.
INFO: [SIM 211-3] *************** CSIM finish ***************

# synthesis
INFO: [HLS 200-10] Analyzing design file './matrix_mult.cpp' ...
INFO: [HLS 200-10] Validating synthesis directives ...
INFO: [HLS 200-111] Finished Checking Pragmas Time (s): cpu = 00:00:01 ; elapsed = 00:00:13 . Memory (MB): peak = 101.551 ; gain = 44.590
INFO: [HLS 200-111] Finished Linking Time (s): cpu = 00:00:01 ; elapsed = 00:00:14 . Memory (MB): peak = 101.563 ; gain = 44.602
INFO: [HLS 200-10] Starting code transformations ...
INFO: [HLS 200-111] Finished Standard Transforms Time (s): cpu = 00:00:02 ; elapsed = 00:00:15 . Memory (MB): peak = 102.961 ; gain = 46.000
INFO: [HLS 200-10] Checking synthesizability ...
INFO: [HLS 200-111] Finished Checking Synthesizability Time (s): cpu = 00:00:02 ; elapsed = 00:00:15 . Memory (MB): peak = 103.191 ; gain = 46.230
INFO: [HLS 200-111] Finished Pre-synthesis Time (s): cpu = 00:00:02 ; elapsed = 00:00:16 . Memory (MB): peak = 124.961 ; gain = 68.000
INFO: [HLS 200-111] Finished Architecture Synthesis Time (s): cpu = 00:00:02 ; elapsed = 00:00:17 . Memory (MB): peak = 124.961 ; gain = 68.000
INFO: [HLS 200-10] Starting hardware synthesis ...
INFO: [HLS 200-10] Synthesizing 'matrix_mult' ...
INFO: [HLS 200-10]

----------------------------------------------------------------
INFO: [HLS 200-42] -- Implementing module 'matrix_mult'
INFO: [HLS 200-10] ----------------------------------------------------------------

INFO: [SCHED 204-11] Starting scheduling ...
INFO: [SCHED 204-11] Finished scheduling.
INFO: [HLS 200-111]  Elapsed time: 17.173 seconds; current allocated memory: 75.025 MB.
INFO: [BIND 205-100] Starting micro-architecture generation ...
INFO: [BIND 205-101] Performing variable lifetime analysis.
INFO: [BIND 205-101] Exploring resource sharing.
INFO: [BIND 205-101] Binding ...
INFO: [BIND 205-100] Finished micro-architecture generation.
INFO: [HLS 200-111]  Elapsed time: 0.281 seconds; current allocated memory: 75.202 MB.
INFO: [HLS 200-10]

----------------------------------------------------------------
INFO: [HLS 200-10] -- Generating RTL for module 'matrix_mult'
INFO: [HLS 200-10] ----------------------------------------------------------------

INFO: [RTGEN 206-500] Setting interface mode on port 'matrix_mult/a' to 'ap_memory'.
INFO: [RTGEN 206-500] Setting interface mode on port 'matrix_mult/b' to 'ap_memory'.
INFO: [RTGEN 206-500] Setting interface mode on port 'matrix_mult/prod' to 'ap_memory'.
INFO: [RTGEN 206-500] Setting interface mode on function 'matrix_mult' to 'ap_ctrl_hs'.
INFO: [SYN 201-210] Renamed object name 'matrix_mult_mac_muladd_8s_8s_16ns_16_1_1' to 'matrix_mult_mac_mbkb' due to the length limit 20
INFO: [RTGEN 206-100] Generating core module 'matrix_mult_mac_mbkb': 1 instance(s).
INFO: [RTGEN 206-100] Finished creating RTL model for 'matrix_mult'.
INFO: [HLS 200-111]  Elapsed time: 0.229 seconds; current allocated memory: 75.575 MB.
INFO: [HLS 200-111] Finished generating all RTL models Time (s): cpu = 00:00:03 ; elapsed = 00:00:19 . Memory (MB): peak = 124.961 ; gain = 68.000
INFO: [SYSC 207-301] Generating SystemC RTL for matrix_mult.
INFO: [VHDL 208-304] Generating VHDL RTL for matrix_mult.
INFO: [VLOG 209-307] Generating Verilog RTL for matrix_mult.
INFO: [HLS 200-112] Total elapsed time: 18.761 seconds; peak allocated memory: 75.575 MB.
INFO: [Common 17-206] Exiting vivado_hls at Thu Mar 12 16:38:28 2020...
```
</details>

可以得到下面的结果（见生成的`matrix_mult_prj\solution\syn\report\matrix_mult_csynth.rpt`文件）

<details markdown="1">
<summary markdown="span">
Performance estimates
</summary>

```
================================================================
== Performance Estimates
================================================================
+ Timing (ns):
    * Summary:
    +--------+-------+----------+------------+
    |  Clock | Target| Estimated| Uncertainty|
    +--------+-------+----------+------------+
    |ap_clk  |  10.00|      8.70|        1.25|
    +--------+-------+----------+------------+

+ Latency (clock cycles):
    * Summary:
    +-----+-----+-----+-----+---------+
    |  Latency  |  Interval | Pipeline|
    | min | max | min | max |   Type  |
    +-----+-----+-----+-----+---------+
    |  311|  311|  311|  311|   none  |
    +-----+-----+-----+-----+---------+

    + Detail:
        * Instance:
        N/A

        * Loop:
        +--------------+-----+-----+----------+-----------+-----------+------+----------+
        |              |  Latency  | Iteration|  Initiation Interval  | Trip |          |
        |   Loop Name  | min | max |  Latency |  achieved |   target  | Count| Pipelined|
        +--------------+-----+-----+----------+-----------+-----------+------+----------+
        |- Row         |  310|  310|        62|          -|          -|     5|    no    |
        | + Col        |   60|   60|        12|          -|          -|     5|    no    |
        |  ++ Product  |   10|   10|         2|          -|          -|     5|    no    |
        +--------------+-----+-----+----------+-----------+-----------+------+----------+
```
</details>

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


重新编译运行可以得到

<details markdown="1">
<summary markdown="span">
Command line execution results (add pipelining)
</summary>

```
INFO: [HLS 200-10] ----------------------------------------------------------------
INFO: [HLS 200-42] -- Implementing module 'matrix_mult'
INFO: [HLS 200-10] ----------------------------------------------------------------
INFO: [SCHED 204-11] Starting scheduling ...
INFO: [SCHED 204-61] Pipelining loop 'Row_Col'.
WARNING: [SCHED 204-69] Unable to schedule 'load' operation ('a_load_1', ./matrix_mult.cpp:22) on array 'a' due to limited memory ports. Please consider using a memory core with more ports or partitioning the array 'a'.
INFO: [SCHED 204-61] Pipelining result : Target II = 1, Final II = 3, Depth = 5.
WARNING: [SCHED 204-21] Estimated clock period (10.779ns) exceeds the target (target clock period: 10ns, clock uncertainty: 1.25ns, effective delay budget: 8.75ns).
WARNING: [SCHED 204-21] The critical path consists of the following:
        'mul' operation ('tmp_7_2', ./matrix_mult.cpp:22) (3.36 ns)
        'add' operation ('tmp2', ./matrix_mult.cpp:22) (3.02 ns)
        'add' operation ('tmp_8_4', ./matrix_mult.cpp:22) (2.08 ns)
        'store' operation (./matrix_mult.cpp:22) of variable 'tmp_8_4', ./matrix_mult.cpp:22 on array 'prod' (2.32 ns)
INFO: [SCHED 204-11] Finished scheduling.
```
</details>

从下面的性能分析报告中可以看到`Row`和`Col`被合并了，latency大大减少，提升了**近4倍**！（事实上在更大的数据集下，单一的流水线即可提升10+倍）

<details markdown="1">
<summary markdown="span">
Performance estimates (add pipelining)
</summary>

```
================================================================
== Performance Estimates
================================================================
+ Timing (ns):
    * Summary:
    +--------+-------+----------+------------+
    |  Clock | Target| Estimated| Uncertainty|
    +--------+-------+----------+------------+
    |ap_clk  |  10.00|     10.78|        1.25|
    +--------+-------+----------+------------+

+ Latency (clock cycles):
    * Summary:
    +-----+-----+-----+-----+---------+
    |  Latency  |  Interval | Pipeline|
    | min | max | min | max |   Type  |
    +-----+-----+-----+-----+---------+
    |   78|   78|   78|   78|   none  |
    +-----+-----+-----+-----+---------+

    + Detail:
        * Instance:
        N/A

        * Loop:
        +-----------+-----+-----+----------+-----------+-----------+------+----------+
        |           |  Latency  | Iteration|  Initiation Interval  | Trip |          |
        | Loop Name | min | max |  Latency |  achieved |   target  | Count| Pipelined|
        +-----------+-----+-----+----------+-----------+-----------+------+----------+
        |- Row_Col  |   76|   76|         5|          3|          1|    25|    yes   |
        +-----------+-----+-----+----------+-----------+-----------+------+----------+
```
</details>

需要完成循环所需总的时钟周期数为

$$N_{loop}=(J\times N_{body})+N_{control}$$

注意到在上面scheduling的报告中，提到虽然我们的目标II是1，但是最好只能做到3，因为内存端口限制了。因此要提升性能，需要将数组进行划分，以提升IO效率。

```cpp
void matrix_mult(
    mat_a a[IN_A_ROWS][IN_A_COLS],
    mat_b b[IN_B_ROWS][IN_B_COLS],
    mat_prod prod[IN_A_ROWS][IN_B_COLS])
{
    #pragma HLS ARRAY_RESHAPE variable=a complete dim=2
    #pragma HLS ARRAY_RESHAPE variable=b complete dim=1
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

最后可得到结果报告如下，latency降到了29，也即比原始最naive的矩阵乘法已经提升了**10倍**！而我们只需要在原始C++代码中插入3行即可。

<details markdown="1">
<summary markdown="span">
Execution results & performance estimates (add pipelining & array partition)
</summary>

```
INFO: [HLS 200-10] ----------------------------------------------------------------
INFO: [HLS 200-42] -- Implementing module 'matrix_mult'
INFO: [HLS 200-10] ----------------------------------------------------------------
INFO: [SCHED 204-11] Starting scheduling ...
INFO: [SCHED 204-61] Pipelining loop 'Row_Col'.
INFO: [SCHED 204-61] Pipelining result : Target II = 1, Final II = 1, Depth = 4.
WARNING: [SCHED 204-21] Estimated clock period (11.477ns) exceeds the target (target clock period: 10ns, clock uncertainty: 1.25ns, effective delay budget: 8.75ns).
WARNING: [SCHED 204-21] The critical path consists of the following:
	'mul' operation ('tmp_7_4', ./matrix_mult.cpp:25) (3.36 ns)
	'add' operation ('tmp3', ./matrix_mult.cpp:25) (3.02 ns)
	'add' operation ('tmp2', ./matrix_mult.cpp:25) (3.02 ns)
	'add' operation ('tmp_8_4', ./matrix_mult.cpp:25) (2.08 ns)
INFO: [SCHED 204-11] Finished scheduling.

================================================================
== Performance Estimates
================================================================
+ Timing (ns):
    * Summary:
    +--------+-------+----------+------------+
    |  Clock | Target| Estimated| Uncertainty|
    +--------+-------+----------+------------+
    |ap_clk  |  10.00|     11.48|        1.25|
    +--------+-------+----------+------------+

+ Latency (clock cycles):
    * Summary:
    +-----+-----+-----+-----+---------+
    |  Latency  |  Interval | Pipeline|
    | min | max | min | max |   Type  |
    +-----+-----+-----+-----+---------+
    |   29|   29|   29|   29|   none  |
    +-----+-----+-----+-----+---------+

    + Detail:
        * Instance:
        N/A

        * Loop:
        +-----------+-----+-----+----------+-----------+-----------+------+----------+
        |           |  Latency  | Iteration|  Initiation Interval  | Trip |          |
        | Loop Name | min | max |  Latency |  achieved |   target  | Count| Pipelined|
        +-----------+-----+-----+----------+-----------+-----------+------+----------+
        |- Row_Col  |   27|   27|         4|          1|          1|    25|    yes   |
        +-----------+-----+-----+----------+-----------+-----------+------+----------+
```
</details>

当然在报告中还有更加详细的内存、资源占用信息，这里就没有再贴出来。

## C HLS pragma
* `#pragma HLS pipeline II=<int>`
* `#pragma HLS array_partition variable=<variable> <block, cyclic, complete> factor=<int> dim=<int>`
* `#pragma HLS array_reshape variable=<variable> <block, cyclic, complete> factor=<int> dim=<int>`
    * 区别参见[此文](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2015_2/sdsoc_doc/topics/calling-coding-guidelines/concept_increasing_local_memory_bandwidth.html)
* `#pragma HLS dataflow`
* `#pragma HLS unroll factor=<N>`

### pipeline
详情见[UG P331](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2014_1/ug902-vivado-high-level-synthesis.pdf)
```cpp
dout_t loop_pipeline(din_t A[N]) {
  int i, j;
  static dout_t acc;
  LOOP_I: for(i = 0; i < 20; i++){
    LOOP_J: for(j = 0; j < 20; j++){
      acc += A[i] * j;
    }
  }
  return acc;
}
```

* 如果不加`pipeline`，那么全部代码串行执行
    * 延迟为$20\times 20\times T_{mac}$
* 如果对内层循环添加`pipeline`，则`LOOP_J`在硬件上只有1份拷贝（单一的乘法器）
    * 延迟为$(20\times 20-1)\times II + T_{mac}$，若II(initial interval)为1，则总时延大约是400 cycles（相当于乘法的延迟被掩盖了），只需小于100 LUTs和寄存器
* 如果对外层循环添加`pipeline`，则`LOOP_J`会被`unroll`产生20份拷贝，会有20个乘法器和20个数组访问需要被调度
    * 延迟只有$(20-1)\times II + T_{mac}$ cycles（如果乘法器能够同时完成操作）
* 如果对整个函数进行`pipeline`，则一共产生数千个LUT和寄存器
    * 延迟只有10（20个双端口访问），但需要大量硬件资源

### HLS Video Library
需要包含头文件`<hls_video.h>`，其中最有用的是LineBuffer和WindowBuffer。

#### LineBuffer
```cpp
// hls::LineBuffer<rows, columns, type> variable;
hls::LineBuffer<3,5,char> Buff_A;
Buff_A.shift_pixels_down(2);
Buff_A.insert_top_row(100,2);
Value = Buff_A.getval(1,3); // 9
```

| Row   | Column 0 | Column 1 | Column 2 | Column 3 | Column 4 |
| :--: | :--: | :--: | :--: | :--: | :--: |
| Row 0 | 1 | 2 | 3 | 4 | 5 |
| Row 1 | 6 | 7 | 8 | 9 | 10 |
| Row 2 | 11 | 12 | 13 | 14 | 15 |

经过上述操作变成

| Row   | Column 0 | Column 1 | Column 2 | Column 3 | Column 4 |
| :--: | :--: | :--: | :--: | :--: | :--: |
| Row 0 | 1 | 2 | 100 | 4 | 5 |
| Row 1 | 6 | 7 | 3 | 9 | 10 |
| Row 2 | 11 | 12 | 8 | 14 | 15 |

其他API包括
* `shift_pixels_up()`
* `shift_pixels_down()`
* `insert_bottom_row()`
* `insert_top_row()`
* `getval(row,column)`

#### WindowBuffer
```cpp
// hls::Window<row, column, type> variable;
hls::Window<3,3,char> Buff_B;
```
* `shift_pixels_up()`
* `shift_pixels_down()`
* `shift_pixels_left()`
* `shift_pixels_right()`
* `insert_pixel(value,row,colum)`：直接覆盖
* `insert_row()`
* `insert_bottom_row()`
* `insert_top_row()`
* `insert_col()`
* `insert_left_col()`
* `insert_right_col()`
* `getval(row, column)`

| Column 0 | Column 1 | Column 2 | Row |
| :--: | :--: | :--: | :--: |
| 1 | 2 | 3 | Row 0 |
| 6 | 7 | 8 | Row 1 |
| 11 | 12 | 13 | Row 2 |

经过`Buff_B.shift_pixels_up()`可得到

| Column 0 | Column 1 | Column 2 | Row |
| :--: | :--: | :--: | :--: |
| 6 | 7 | 8 | Row 0 |
| 11 | 12 | 13 | Row 1 |
| New | New | New | Row 2 |

可以看到这种模式对**卷积**的实现是非常高效的。

经过`char C[3] = {50, 50, 50}; Buff_B.insert_row(C,1);`会得到

| Column 0 | Column 1 | Column 2 | Row |
| :--: | :--: | :--: | :--: |
| 1 | 2 | 3 | Row 0 |
| 50 | 50 | 50 | Row 1 |
| 11 | 12 | 13 | Row 2 |

可以看到WindowBuffer通常都是对一整块内存进行操作，而LineBuffer更多针对单一元素。

## 数据类型
任意精度整数(Arbitrary Precision, AP)，具体实现可参见[HLS Arbitrary Precision Types](https://github.com/Xilinx/HLS_arbitrary_Precision_Types)，其实都是C++的模板类。

### 整数
* `#include "ap_int.h"`
* `ap_int`有符号，`ap_uint`无符号
* 用模板类声明，如`ap_uint<24>`代表24位无符号整数

### 定点数
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

### 类成员操作
相关类成员操作如下：（在UG C++ Arbitrary Precision Types一节）
* 基本的运算符均已被重载
* `length`
* `to_int`, `to_double`, `to_string`
* Concat
    * `ap_concat_ref ap_(u)int::concat (ap_(u)int low)`
    * `ap_concat_ref ap_(u)int::operator , (ap_(u)int high, ap_(u)int low)`
    ```cpp
    ap_uint<10> Rslt;
    ap_int<3> Val1 = -3;
    ap_int<7> Val2 = 54;
    Rslt = (Val2, Val1); // Yields: 0x1B5
    Rslt = Val1.concat(Val2); // Yields: 0x2B6
    (Val1, Val2) = 0xAB; // Yields: Val1 == 1, Val2 == 43
    ```
* Bit selection
    * `ap_bit_ref ap_(u)int::operator [] (int bit)`
    * 注意返回是一个引用，意味着可以直接赋值修改
* Range selection
    * `ap_range_ref ap_(u)int::range (unsigned Hi, unsigned Lo)`
    * `ap_range_ref ap_(u)int::operator () (unsigned Hi, unsigned Lo)`
    ```cpp
    ap_uint<4> Rslt;
    ap_uint<8> Val1 = 0x5f;
    ap_uint<8> Val2 = 0xaa;
    Rslt = Val1.range(3, 0); // Yields: 0xF
    Val1(3,0) = Val2(3, 0); // Yields: 0x5A
    Val1(4,1) = Val2(4, 1); // Yields: 0x55
    Rslt = Val1.range(7, 4); // Yields: 0xA; bit-reversed!
    ```
* Reduce
    * `bool ap_(u)int::and_reduce ()`
    * and, or, xor, nand, nor, xnor
* `set`, `clear`, `invert`

## 需要注意的点
* HLS不支持递归、系统调用（文件读取）、动态内存分配
* 默认情况下，循环都不展开(rolled)
* 当外层循环用了`pipeline`或者`unroll`时，内层循环默认展开
* HLS默认优化面积，即用最小的资源实现目标（串行架构），因此时延可能非常慢，吞吐率低

## 编译综合模式
* csim：C语言层面进行模拟
* csyn：C综合生成RTL代码
* cosim：在RTL层进行模拟，与C结果输出进行比对
* impl：将RTL打包成IP核

对应的Tcl如下
```bash
# Simulate the C++ design
csim_design
# Synthesize the design
csynth_design
# Co-simulate the design
cosim_design
# Implement the design
export_design -flow impl
```

## 工具安装
* Xilinx的[下载页面](https://www.xilinx.com/support/download.html)下载最新版本的Vivado Design Suite - HLx Edition（最新版v2020的安装包已经达到了35.5G，而且必须全部下载并安装，Xilinx并不提供单独安装HLS的方式）

如果要在WSL内使用`vivado_hls`，其实还是相当麻烦的。之前通过大量的尝试，才得到了一个比较好的解决方案。由于Vivado在Linux下的安装一定要图形界面，因此尝试在WSL内安装了图形桌面后，调用`xsetup`安装，但似乎安装界面Java虚拟机的大量解释开销，一直都没法进入正常的安装界面，故此方法最后还是放弃。

最后试出来的方法是在Windows环境下安装好Vivado套件后，在WSL内通过两层封装进行调用。

首先需要拷贝一份`Xilinx\Vivado\2020.1\bin\vivado_hls.bat`（不妨命名拷贝为`my_vivado_hls.bat`），然后修改文件内容。将弹出新窗口的`%COMSPEC%`指令移除，直接换成`vivado_hls`的调用。完整的bat文件如下，这里可以通过`%1 %2`进行命令行指令的传递。
```bat
@echo off

set PATH=%~dp0;%PATH%;%~dp0..\tps\win64\msys64\usr\bin;%~dp0..\tps\win64\msys64\mingw64\bin

set AUTOESL_HOME=%~dp0..
set VIVADO_HLS_HOME=%~dp0..

echo ===============================
echo == Vivado HLS Command Prompt 
echo == Available commands:
echo == vivado_hls,apcc,gcc,g++,make
echo ===============================


set RDI_OS_ARCH=32
if [%PROCESSOR_ARCHITECTURE%] == [x86] (
  if defined PROCESSOR_ARCHITEW6432 (
    set RDI_OS_ARCH=64
  )
) else (
  if defined PROCESSOR_ARCHITECTURE (
    set RDI_OS_ARCH=64
  )
)
 
if not "%RDI_OS_ARCH%" == "64" goto _NotX64
set COMSPEC=%WINDIR%\SysWOW64\cmd.exe
rem %COMSPEC% 
vivado_hls %1 %2
goto EOF

:_NotX64
set COMSPEC=%WINDIR%\System32\cmd.exe
rem %COMSPEC% /c %0 %1 %2 %3 %4 %5 %6 %7 %8 %9 
vivado_hls %1 %2
 
:EOF
```

这是Windows端的封装，这样弄完后就可以直接在PowerShell里通过`.\my_vivado_hls -f run.tcl`执行综合过程，而不会弹出新的窗口。

至于WSL端的封装则是创建一个bash文件，里面通过`cmd.exe`执行上述指令，脚本如下。
```bash
#!/bin/bash
cmd.exe /c <path_to_xilinx>/Xilinx/Vivado/2020.1/bin/my_vivado_hls $1 $2
```

这里同样通过`$1 $2`传递参数，同时将此脚本保存为`vivado_hls`，假装它就是一个可执行文件，同时放在可被Linux的PATH搜索到的地方。这样执行`which vivado_hls`也能正常执行（这是`alias`所做不到的）。

最终就可以愉快地在WSL里调用`vivado_hls -f run.tcl`进行综合啦！

## 参考资料说明
本文主要参照以下资料进行整理，特别向这些课程/书籍/资料的作者和老师致以感谢。

* [^1]是非常好的关于Xilinx Zynq和SoC/异构系统入门的书籍，其中第14章介绍了高层次综合(HLS)的基本概念，第15章则非常清晰明了地介绍了Vivado HLS的常用指令及相关规范，该书特别适合初学者入门——简练而突出重点，同时也有免费的中文版可以下载。
* [^3]讲述了高层次综合的整体流程及原理，第2课简要介绍了Vivado HLS的使用，同时以FIR (Finite Impulse Response)为例讲解HLS的优化指令，也是十分简明扼要；第3课关于FPGA的硬件结构也非常有必要了解。
* [^2]是U Washington研究生体系结构课程中的一个实验项目，算是一个非常非常非常详细的Vivado HLS的入门教程了，基本上能够调到他预期的加速比就算达成任务了。本文中矩阵乘的例子就来源于此。
* [^4]可作为速查手册，提供了所有C HLS #pragma，[^9]是非常简洁的HLS优化API及完整流程的查询帮助网页
* [^5]和[^6]是官方说明手册，前者是完整的HLS说明书，后者则是Vivado HLS的一些实验范例（但比较侧重于图形化界面），但可以下载[对应源码](https://www.xilinx.com/cgi-bin/docs/ctdoc?cid=4eafd485-f496-45ca-9d97-6be22cfedc4b;d=ug871-design-files.zip)进行学习（需要Xilinx账户）。比较不好的是，这两者都以pdf的形式呈现，而没有简易版的网页帮助，因此要查找相关API其实还挺麻烦的。
* [^7]给出了大量应用加速的例子，算是HLS的高阶应用教程
* [^8]收录了大量FPGA的学习资料，上述很多链接也从该项目中获取

## Resources
[^1]: The Zynq Book, <http://www.zynqbook.com/>, [Chinese edition](http://www.zynqbook.com/download-book-chinese.php)
[^2]: Thierry Moreau, [UW CSE548](https://courses.cs.washington.edu/courses/cse548/17sp/) [Lab 3: Custom Acceleration with FPGAs](https://github.com/uwsampa/cse548-labs), Spring 2017
[^3]: Zhiru Zhang, [Cornell ECE 5775](http://www.csl.cornell.edu/courses/ece5775/schedule.html): High-Level Digital Design Automation, Fall 2018
[^4]: [SDAccel HLS Pragmas](https://www.xilinx.com/html_docs/xilinx2018_3/sdaccel_doc/hls-pragmas-okr1504034364623.html#okr1504034364623)
[^9]: [Xilinx SDAccel Development Environment Help for 2018.2 XDF](https://www.xilinx.com/html_docs/xilinx2018_2_xdf/sdaccel_doc/index.html)
[^5]: [Xilinx Vivado HLS User Guide](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2017_1/ug902-vivado-high-level-synthesis.pdf)
[^6]: [Xilinx Vivado HLS Tutorial](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2017_1/ug871-vivado-high-level-synthesis-tutorial.pdf)
[^7]: Ryan Kastner, Janarbek Matai, and Stephen Neuendorffer (UCSB), *[Parallel Programming for FPGAs](https://arxiv.org/abs/1805.03648)*, 2018
[^8]: Yizhou Shan, [Cook FPGA](https://github.com/lastweek/fpga_readings)