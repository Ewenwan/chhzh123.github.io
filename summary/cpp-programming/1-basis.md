---
layout: post
title: C++ - 基本类型与数组
date: 2018-07-14
tag: [summary]
---

## 基本语法
* `int main`
* 输出流
    * `cerr`警告 错误信息
    * `clog`一般信息
    * `endl`=`\n`+flushing
* 注释
    * 单行注释和界定符对注释
    * 每一行都以星号开头`/* ... */`
    * 界定符不可嵌套
* `Ctrl+Z`文件结束
* 算术类型
    * `bool`,`char`,`wchar_t`,`char16_t`,`char32_t`,`short`8,`int`16,`long`32,`long long`64,`float`,`double`,`long double`
    * 给无符号类型一个超出它范围的数，结果时初始值对无符号类型表示数值总数取模后的余数
    * 字面值常量(literal) `0`八 `0x`十六 `0e0`科学记数法
    * 若两个字符串字面值位置紧邻且仅由空格缩进换行符分隔，则它们实际上是一个整体
* 列表初始化 `int units_sold{0}`,`int units_sold(0)`
* 声明(declaration)与定义(definition)->分离式(separate compilation)编译
    * 声明使名字为程序所知 声明一个变量而非定义它 `extern int i`
    * 定义负责创建与名字相关联的实体 声明并定义 `int j`
    * **变量只能被定义一次，但是可以被多次声明**
* 复合(compound)类型
    * 引用
        * 引用为对象起了另一个名字，引用类型引用另外一种类型
        * **引用即别名，不是对象，不能定义引用的引用；必须绑定在对象上，而不能与字面值绑定**

```cpp
int ival = 1024;
int &refVal = ival; // refVal指向ival(是ival的另一个名字)
int &refVal2; // 报错：引用必须被初始化
```

> 一般在初始化变量时，初始值会被拷贝到新建的对象中。然而定义引用时，程序把引用和它的初始值绑定在一起，而不是将初始值拷贝给引用。一旦初始化完成，引用将和它的初始化对象一直绑定在一起。因为无法令引用重新绑定到另外一个对象，所以引用必须初始化。

* 指针
    * 指针本身就是一个对象，允许对指针赋值拷贝，且在生命周期内可先后指向不同的对象；无须赋初值
    * 不能定义指向引用的指针
    * `*`解引用符
    * C++11空指针`nullptr`，0，`NULL`的预处理变量(preprocessor variable，在cstdlib定义，值就是0)
    * 把`int`变量直接赋值给指针是错误的操作，即使`int`的值恰好为0也不可
    * `void*`指针，可用于存放任意对象的地址
    * `int* p1,p2;`p1是指向int的指针，p2是int

* `const`
    * 从右往左读规则，遇到`var`转为is a，遇到`*`转为pointer to
        * 常量指针 `const int* p`与`int const* p`相同，指针指向整型常量，内容不能改，但指针可以改
        * 指针常量 `int* const p`，指针为常量指向整型，内容可以改，但指针不能改
    * 默认状态下，const对象仅在文件内有效
    * 要在文件间共享const对象，无论声明还是定义都加`extern`关键字
    * 对常量的引用，与普通引用不同的是，其不可被用作修改它所绑定的对象
    * 对const的引用可能引用一个非const的对象
    * 同样常量不可由非常量指针指向
    * 顶层(top-level)常量-指针是常量`int *const p1 = &i;` 底层常量-指针所指对象是一个常量`const int *p2 = &ci;`
    ```cpp
    const int c = 1;
    const int &r = c;
    r = 42; // 错误：r是对常量的引用
    int &p = c; // 错误：试图让一个非常量引用指向一个常量对象
    const double &p2 = c; // 错误：这样绑定的是临时量temp
    ```

* 常量表达式`constexpr` C++11
    * 值不会改变而且在编译过程就能得到计算结果的表达式
    * 必须是字面值类型（算术类型、引用、指针），但string类就不是
* 类型别名(type alias)
    * `typedef double wages`
    * 别名声明(alias declaration) `using SI = Sales_item;`
    * 注意`typedef char *pstring;`后`const pstring`代表的是`char const*`指针为常量，而不是`const char*`指向常量的指针
* `auto`C++11
    * 编译器替我们分析表达式所属类型 `auto item = val1 + val2;`
    * 一般会忽略掉顶层const，底层const则会保留
* `decltype`C++11
    * 从表达式的类型中推断出要定义的变量的类型，但是不想用该表达式的值初始化变量
    * `decltype(f()) sum = x;`sum的类型就是函数f的返回类型
    * `decltype((var))`双层括号结果是引用
* 自定义数据类型
    * 结构体、类最后都要加`;`
* 预处理器(preprocessor)
    * 确保头文件多次包含仍能正常工作
    * `#include`即在预处理的时候用头文件替代
    * 头文件保护符(header guard)依赖于预处理变量
        * 预处理变量有两种状态：已定义和未定义
        * `#define`把一个名字设定为预处理变量
        * `#ifdef`当且仅当变量已定义时为真
        * `#ifndef`当且仅当变量未定义时为真
        * `#endif`一旦检查为真执行至此
    * 预处理变量无视C++中关于作用域的规则
    ```cpp
    #ifndef DATA_H
    #define DATA_H
    ...
    #endif
    ```
* 命名空间
    * `using std::cin;using std::cout;using std::string;`
    * 头文件不应包含`using`声明
* 基于范围的`for`语句C++11
    * `for ( declaration : expression )` expression是一个对象，用于表示一个**序列**；declaration负责定义一个变量，用于访问序列中的基础元素
    * 范围for语句体内不应改变其所遍历序列的大小
    * 使用引用就能修改字符的值`for (auto &c : s)`