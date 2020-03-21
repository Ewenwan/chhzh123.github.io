---
layout: post
title: TVM - 安装
tags: [dl, tvm]
---

本文记录TVM的安装方式，主要验证[官方教程](https://docs.tvm.ai/install/from_source.html)中从源码安装是否对WSL可行。

<!--more-->

下面代码都在WSL环境中运行，同时用virtualenv创建了Python 3.6的虚拟环境。

```bash
# 1. Clone the project
git clone --recursive https://github.com/apache/incubator-tvm tvm

# 2. Install Linux dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-dev python3-setuptools gcc libtinfo-dev zlib1g-dev build-essential cmake libedit-dev libxml2-dev

# 3. Build the shared library
mkdir build
cp cmake/config.cmake build # change settings in cmake file

# for cpu and gpu, need to install LLVM first
# i) Download LLVM pre-built version 9.0 from http://releases.llvm.org/download.html
# 2) set (USE_LLVM /path/to/llvm/bin/llvm-config) in config.cmake

cd build
cmake ..
make -j4

# 4. Python package installation
# Recommended for developers, no need to call setup!
# It would be better if adding them to ~/.bashrc
export TVM_HOME=/path/to/tvm
export PYTHONPATH=$TVM_HOME/python:$TVM_HOME/topi/python:${PYTHONPATH}

# 5. Install python dependencies
pip install numpy decorator attrs
```

事实证明官方教程讲得很清晰，之后就可以顺利在Python里`import tvm`啦！

可以通过测试[GEMM在CPU上的例子](https://docs.tvm.ai/tutorials/optimize/opt_gemm.html#sphx-glr-tutorials-optimize-opt-gemm-py)看是否能正常编译。