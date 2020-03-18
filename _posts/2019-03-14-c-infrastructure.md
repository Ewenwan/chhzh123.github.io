---
layout: post
title: C语言常用操作
tag: [pl]
---

由于本学期计算机网络和OS课都要大量使用到C语言编程，而当时入学时对C的了解并没有这么深刻，所以这个学期相当于重新学习，在此记录。

<!--more-->

## 系统函数
* `assert`：`<assert.h>`头文件，当assert内容不为真时停止报错
* `atoi`是windows才有的函数，Linux下直接用`sprintf`
* `strchr`：匹配字符串中首次出现的指定字符
    * 原型：`char* strchr(const *s, int c)`
    * 功能：用来找出参数`s`字符串中第一个出现参数`c`的地址，然后将该字符出现的地址返回
    * 返回值：如果找到指定的字符，则返回该字符所在地址，否则返回`0`
* `strstr`：字符串匹配，在一个字符串中查找指定的字符串
    * 原型：`char* strstr(const char *haystack, const char *needle)`
    * 功能：`strstr()`会从字符串`haystack`中搜寻字符串`needle`，并将第一次出现的地址返回
    * 返回值：返回指定字符串第一次出现的地址，否则返回0
* `strtok`：字符串分割函数
    * 原型：`char *strtok(char *s, const char *delim);`
    * 功能：分解字符串为一组字符串。`s`为要分解的字符串，`delim`为分隔符字符串
    * 说明：`strtok()`用来将字符串分割成一个个片段。参数`s`指向欲分割的字符串，参数`delim`则为分割字符串中包含的所有字符。当`strtok()`在参数`s`的字符串中发现参数`delim`中包含的分割字符时，则会将该字符改为`\0`字符。在第一次调用时，`strtok()`必须给予参数`s`字符串，往后的调用则将参数`s`设置成`NULL`。每次调用成功则返回指向被分割出片段的指针，如无从分割则返回`NULL`。
* `strsep`: https://www.cnblogs.com/wkfvawl/p/9042695.html

## 获取系统时间
这是非常常用的操作。

```cpp
// #include <time.h>
time_t t;
struct tm* lt;
time (&t);
lt = localtime (&t); // get current time
// lt->tm_year+1900, lt->tm_mon, lt->tm_mday
// lt->tm_hour, lt->tm_min, lt->tm_sec
```

通过[`strftime`](http://www.cplusplus.com/reference/ctime/strftime/)可以格式化时间字符串。

## C文件输入输出
已包含于头文件`<stdio.h>`中，可参见[一文](https://stackoverflow.com/questions/17598572/read-write-to-binary-files-in-c)。

```cpp
unsigned char buffer[10];
FILE *ptr;
ptr = fopen("test.bin","rb");  // r for read, b for binary
fread(buffer,sizeof(buffer),1,ptr); // read 10 bytes to our buffer

FILE *write_ptr;
write_ptr = fopen("test.bin","wb");  // w for write, b for binary
fwrite(buffer,sizeof(buffer),1,write_ptr); // write 10 bytes from our buffer
```

## C++文件输入输出
详情见[官方参考文档](http://www.cplusplus.com/doc/tutorial/files/)