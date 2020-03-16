---
layout: post
title: C++ - 表达式、语句与函数
date: 2018-07-13
tag: [summary]
---

## 表达式
* 基础
	* 左值(lvalue)与右值(rvalue)
	* 求值顺序
		* `int i = f1() * f2():`f1,f2一定会在乘法前被调用，但是谁先就不知道了
	* C++11标准 商一律切除小数部分
		* `(-m)/n`和`m/(-n)`都等价于`-(m/n)`，`m%(-n)`等价于`m%n`，`(-m)%n`等价于`-(m%n)`
	* 短路求值(short-circuit evaluation)
	* `int i = 0;`是初始化，而非赋值
	* 赋值运算满足**右结合**律`ival = jval = 0`
	* `cout << *iter++ << endl;`等价于`cout << *iter << endl; ++iter;`
	* 移位运算符（IO运算符）满足**左结合**
	* `sizeof`返回`size_t`类型
	* 逗号运算符 左侧运算完丢掉 常用在`for`循环
	* 类型转换 一般隐式转换 算术转换 整数提升
	* 显示转换
		* 强制类型转换`cast-name<type>(expression)`，`cast-name`是`static_cast`,`dynamic_cast`,`const_cast`,`reinterpret_cast`中的一种
		* 通常用`static_cast`实现原有C类型的转换`(type)expr`
* 运算符优先级 **重载并不会改变运算符的优先级，因而输入输出流运算符优先级位置没有变**
	* `::`
	* `.` `->` `[]` `()`函数调用 类型构造
	* 后`++` 后`--` `typeid` `cast`
	* 前`++` 前`--` `~` `!` `-` `+` `*` `&` `()`类型转换 `sizeof` `new` `delete` `noexcept`
	* `->*` `.*`
	* `*` `/` `%`
	* `+ -`
	* `<< >>`
	* `< <= > >=`
	* `== !=`
	* `&`位与
	* `^`
	* `|`
	* `&&`
	* `||`
	* `? :`
	* `=`
	* `*= /= %= += -= <<= >>= &= |= ^=`
	* `throw`
	* `,`

## 语句
* `goto label;` `label: do something`
* 异常处理
	* `throw runtime_error("Wrong");` 类型`runtime_error`是标准库异常类型的一种，定义在`stdexcept`头文件中
	* `try{ } catch( ){ } catch( ){ }`

```cpp
while (cin >> item1 >> item2){
	try {
		//添加失败抛出runtime_error异常
	} catch (runtime_error err) {
		cout << err.what()
			<< "\nTry Again? Enter y or n" << endl;
		char c;
		cin >> c;
		if (!cin || c == 'n')
			break;
	}
}
```

## 函数
* 基础
	* 实参是形参的初始值
	* `static`局部静态对象实现生命周期贯穿函数调用及之后的时间
	* 函数原型：返回类型、函数名、形参类型
	* 分离式编译产生Windows`.obj` Unix`.o`对象代码
* 参数传递
	* 引用传递(passed by reference)
		* 绑定在对象上，引用形参是它对应的实参的别名
		* 传引用可以避免拷贝
		* 可通过传参方法返回多个值
		* 尽量使用常量引用，如`string::size_type find_char(string &s)`后输入`find_char("hello")`会报错
	* 值传递(passed by value)
		* 形参与实参是两个独立的对象
		* 指针形参：当执行指针拷贝操作时，拷贝的是指针的值，拷贝之后两个指针是不同的指针，因为指针可以间接地访问它所指的对象，故通过指针可以修改它所指对象的值
	* 数组参数传递
		* 最好传首元素和尾后指针`void print(const int *beg, const int *end)`
		* 二维数组`int (*matrix)[10]`指向10个整数的数组的指针
	* `main`处理命令行选项
		* `int main (int argc, char *argv[]) { }`
		* `prog -d -o ofile data0`
	* 含有可变形参的函数C++11
		* `initializer_list`形参
			* 其对象元素永远是常量值，不可改变其中的值
			* `void error_msg(initializer_list<string> il)`
		* `varargs`省略符形参
			* `void foo(parm_list, ...);`
* 无返回值函数
	* 不要求非得有`return`，因最后一句会隐式执行`return`
* 返回值
	* 返回一个值的方式和初始化一个变量或形参的方式完全一样：返回的值用于初始化调用点的一个临时量，该临时量就是函数调用的结果
	* 如返回`string`则意味着返回值被拷贝至调用点
	* 不要返回局部对象的引用或指针
	* 引用返回左值 特别是**赋值**要返回引用
		* `get_val(s,0) = 'A'` 左边函数返回了`char&`
	* 列表初始化返回值 `return{"functionX",expected,actual};`
* main函数不能调用自己 不能重载
* 函数重载
	* 可以省略形参名字 `Record lookup(const Account&)`
	* 函数匹配/重载确定
	* 可能出现 最佳匹配(类型越相近越好) 无匹配 二义性调用(ambiguous call,如double与int类型间转换)
	* 名字查找发生在类型检查之前
	* 在局部作用域声明函数会导致全局函数隐藏

```cpp
Record lookup(Phone);
Record lookup(const Phone); // 重复声明
Record lookup(Phone*);
Record lookup(Phone* const); // 重复声明
Record lookup(Account&); // 函数作用于Account的引用
Record lookup(const Account&); // 新函数，作用于常量引用
Record lookup(Account*); // 新函数，作用于指向Account的指针
Record lookup(const Account*); // 新函数，作用于指向常量的指针

const string &shorterString(const string &s1, const string &s2)
{
    return s1.size() <= s2.size() ? s1 : s2;
}
string &shorterString(string &s1, string &s2)
{
    auto &r = shorterString(const_cast<const string&>(s1),const_cast<const string&>(s2));
    return const_cast<string&>(r);
}
```

* 特殊用途语言特性
	* 默认实参
		* `string screen(sz ht = 24, sz wid = 80, char bg = ' ')`
		* 可以为一个或多个形参定义默认值，但一旦某个形参被赋予了默认值，后面均得有
		* `screen( , , '?')` 错误，只能省略尾部实参
		* `string screen(sz ht = 24, sz wid = 80, char bg); string screen(sz ht, sz wid, char bg = ' ')` 正确，不是重复声明，但只能给没赋值的实参赋值，不能重新赋
	* 内联函数(inline)
		* 内联说明只是向编译器发出的一个请求，编译器可以选择忽略
		* 内联机制用于优化规模较小、流程直接、频繁调用的函数
		* 内联函数和`constexpr`通常放在头文件中
* 函数指针
	* `using PF = int (*)(int*, int); PF f1(int);` 返回指向函数的指针

```cpp
bool lengthCompare(const string & , const string &);
bool (*pf)(const string &, const string &);
pf = lengthCompare;
pf = &lengthCompare; // 取地址符可选
bool b = pf("hello","goodbye"); // 可以不用*
```