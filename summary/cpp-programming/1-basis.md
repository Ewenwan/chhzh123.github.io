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
    * 每一行都以星号开头
    * 界定符不可嵌套
* `Ctrl+Z`文件结束
* 算术类型
    * `bool`,`char`,`wchar_t`,`char16_t`,`char32_t`,`short`8,`int`16,`long`32,`long long`64,`float`,`double`,`long double`
    * 给无符号类型一个超出它范围的数，结果时初始值对无符号类型表示数值总数取模后的余数
    * 字面值常量(literal) 0八 0x十六 0e0科学记数法
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

## 字符串、向量和数组
* `<string>`
    * 用等号初始化执行的是**拷贝初始化**，否则执行**直接初始化**
    * 触发getline函数返回的换行符被丢弃掉了，得到的string里并不包含该换行符
    * `string::size_type`类型 无符号整数 `auto len = line.size()`推断 最好不要用int 避免混用int和unsigned带来的问题
    * `+`运算符两侧至少有一为string类型 不能直接将字面值相加`"hello"+","`错误写法（字符串字面值与string是不同的类型）

```cpp
string s1;
string s2(s1);
string s3 = s2; // 与上一行等价
string s4 = "value";
string s5("value");
string s6(n,'c'); // 连续n个字符为c

getline(is,s); // 从is中读取一行赋给s
string line;
while(getline(cin,line))
    cout << line << endl;
s.empty();
s.size();
```

* `<ctype>`
    * 字母数字为真`isalnum(c)` 字母`isalpha(c)` 数字`isdigit(c)` 控制字符`iscntrl(c)`
    * 小写`islower(c)` 小写转大写`toupper(c)`
* 基于范围的`for`语句C++11
    * `for ( declaration : expression )` expression是一个对象，用于表示一个**序列**；declaration负责定义一个变量，用于访问序列中的基础元素
    * 范围for语句体内不应改变其所遍历序列的大小
    * 使用引用就能修改字符的值`for (auto &c : s)`

```cpp
// 统计标点符号个数
string s("Hello world!");
decltype(s.size()) punct_cnt = 0;
for ( auto c : s )
    if (ispunct(c))
       ++punct_cnt;
```

* `<vector>`
    * 不可用下标索引添加元素
    * 数组大小不定时用vector

```cpp
vector<string> v1 {"a","an","the"}; // 注意是花括号 列表初始化
vector<int> v2(10,-1);
vector<int> v3(10);
vector<int> v4{10,-1}; // 区别
v.push_back(var);
v.empty();
v.size();
```

* 迭代器(iterator)
    * `v.begin() v.end()`
    * 注意`end`为尾元素的下一位置(one past the end)
    * 若容器为空begin和end返回同一个迭代器
    * `*iter`返回迭代器所指元素的引用
    * 养成用`!=`的习惯 而不是`<`（可能未定义）
    * `vector<int>::iterator it`
* 数组
    * 数组是复合类型
    * 编译时维度必须已知，维度必须是一个常量表达式`constexpr`
    * 定义数组时必须指定类型，不可用`auto`
    * 不能把一个数组直接赋值给另一个
    * 一些编译器支持数组的赋值，即编译器扩展(compiler extension)，但最好不要用非标准特性
    * **想要理解数组声明的含义，最好就是从数组的名字开始由内往外读**
    * 在使用数组下标时，通常定义为`size_t`类型，其是一种机器相关的无符号类型，被设计得足够大以便表示内存中任意对象的大小，在`<cstddef>`中定义
    * 对于数组`int a[]`，`auto a2(a)`类型为整型指针，而`decltype(a) a3 = {1,2}`则类型为数组
    * vector迭代器支持的运算，数组指针全部支持（如递增）
    * C++11引入`int *beg = begin(a)`和`int *last = end(a)`以实现类似vector迭代器的效果
    * 两个指针相减的结果是`ptrdiff_t`的标准库类型，有符号
    * 内置的下表运算符不是无符号类型，故可以`a[-2]`，前提是指针指向数组中间

```cpp
unsigned cnt = 42; // 不是常量表达式
constexpr unsigned sz = 42 ;
string bad[cnt]; // 非法
string str_s[get_size()]; // 当get_size是constexpr时正确 否则错误
```

* C风格字符串/数组
    * `\0`结尾
    * 尽管C++支持，但最好不要使用，因为不仅麻烦，而且极易引发程序漏洞（目标字符串大小由调用者指定）
    * `const char *str = s.c_str();`实现string到C风格的转换，返回指针，但最好拷贝一份，否则s修改str也会改
    * `vector<int> ivec(begin(int_arr),end(int_arr))`
    * 现代C++应避免使用内置数组和指针，尽量使用string
* 多维数组
    * 严格来说，C++没有多维数组，而是数组的数组
    * `int ia[3][4]`大小为3的数组，每个元素是含有4个整数的数组

```cpp
int ia[3][4] = {0,1,2,3,4,5,6,7,8,9,10,11}; // 与加了内层花括号等价
int ia[3][4] = {{0},{4},{8}}; // 初始化每行首元素
int ix[3][4] = {0,3,6,9}; // 初始化第一行

size_t cnt = 0;
for (auto &row : ia)
    for (auto &col : row){
        col = cnt;
        ++cnt;
    }

for (const auto &row : ia) // 外层循环要用引用，同时避免转为指针类型
    for(auto col : row)
        cout << col << endl;

int ia[3][4];
int (*p)[4] = ia; // 括号不能少，p指向含有4个整数的数组，而不是整型指针的数组
for (auto p = begin(ia); p != end(ia); ++p)
    for (auto q = begin(*p); q != end(*p); ++q)
        cout << *q << ' ';
```


## 其他
* C++primer 第五版中文版
* gcc4.7以后才支持C++11标准
* 西西里OJ gcc4.6.3