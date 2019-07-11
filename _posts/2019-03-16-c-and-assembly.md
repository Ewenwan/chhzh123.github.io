---
layout: post
title: C与汇编混编
tag: [pl, os]
---

本文主要讲讲如何在C语言中嵌入汇编语言。

<!--more-->

## 为什么要在C中写汇编？
1. 速度快、效率高（但现在编译器技术这么高级，这种情况已经很少见了
2. 实现C语言也无法解决的底层操作，如调入扇区、显存显示等，这是主要原因

## 内联汇编
基本的内联汇编语法是这样的
```cpp
asm ( assembler template 
    : output operands                  /* optional */
    : input operands                   /* optional */
    : list of clobbered registers      /* optional */
    );
```
所谓clobbered寄存器就是指在此段代码段会被使用/修改值的寄存器，在这里声明表示让编译器不要占用（输入输出寄存器可以不用）。

`volatile`表示编译器不要对此段代码进行优化。
`__asm__`和`asm`，`__volatile__`和`volatile`的写法都是可以的。

注意汇编语句均用双引号括起来，同时每行最末要添加`\r\n`以告诉汇编器换行。

常用的限制如下
* 通用寄存器(`r`)，如`asm ("movl %%eax, %0\n" :"=r"(myval));`

| r |    Register(s)     |
|:---:|:---:|
| a |   %eax, %ax, %al   |
| b |   %ebx, %bx, %bl   |
| c |   %ecx, %cx, %cl   |
| d |   %edx, %dx, %dl   |
| S |   %esi, %si        |
| D |   %edi, %di        |

* 内存限制`m`
* 匹配`0`、`1`、...、`9`：表示用它限制的操作数与某个指定的操作数匹配，如用`0`去描述`%1`
* `=`只写的（输出操作数）
* `+`操作数在指令中是读写类型的（输入输出操作数）

## Intel语法解决方案
gcc编译器默认的内联(inline)汇编是AT&T语法，但OS课上我们都采用Intel/nasm的语法，故这里需要做出一点修改，在汇编语句前添加
```cpp
asm (".intel_syntax noprefix");
```
即可，同时注意添加编译选项`-masm=intel`（注意这种方法不能使用`m`限制）。

如果想换回AT&T语法，则输入
```cpp
asm (".att_syntax noprefix");
```

完整可运行的例子如下
```cpp
#include <stdio.h>

#ifdef ATT // -DATT
int att_add(int foo, int bar)
{// ".att_syntax noprefix"
    __asm__ __volatile__("addl  %%ebx,%%eax"
                         :"=a"(foo)
                         :"a"(foo), "b"(bar)
                         );
    return foo;
}
#else // -masm=intel
int intel_add(int foo, int bar)
{
    asm volatile(".intel_syntax noprefix\r\n"
                 "add  eax, ebx\r\n"
                 :"=a"(foo)
                 :"a"(foo), "b"(bar)
                 :);
    return foo;
}
#endif

int main(void)
{
    int foo = 10, bar = 15;
#ifdef ATT
    printf("%d + %d = %d\n", foo, bar, att_add(foo,bar));
#else
    printf("%d + %d = %d\n", foo, bar, intel_add(foo,bar));
#endif
}
```

## 参考资料
* C语言中嵌入汇编代码，<https://blog.csdn.net/zjy900507/article/details/79487605>
* How can i write inline assembler in c code, <https://forum.nasm.us/index.php?topic=2114.0>
* Can I use Intel syntax of x86 assembly with GCC?, <https://stackoverflow.com/questions/9347909/can-i-use-intel-syntax-of-x86-assembly-with-gcc>
* GCC-Inline-Assembly-HOWTO, <https://www.ibiblio.org/gferg/ldp/GCC-Inline-Assembly-HOWTO.html>
* Inline Assembler(Wiki), <https://en.wikipedia.org/wiki/Inline_assembler>
* 内核例子, <https://github.com/embedded2014/rtenv/blob/master/kernel.c>
* GNU C内联汇编介绍，<https://www.cnblogs.com/rain-blog/p/gnu-gcc-insert-asm.html>