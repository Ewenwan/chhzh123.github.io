---
layout: post
title: C++ - 类
date: 2018-06-13
tag: [summary]
---
## 基本思想
* 抽象(abstraction) 封装(encapsulation)
	* 抽象：依赖于接口(interface)和实现(implementation)分离的编程技术
	* 封装实现类的接口和实现的分离，隐藏了实现对象
		* 只能用接口，而不能访问实现部分
		* 确保用户代码不会改变封装对象的状态
		* 私有成员改变不需修改用户级别代码
## 基础
* 定义在类内部的函数是隐式的inline函数
* this常量指针 隐式定义
* 一般来说，如果非成员函数是类接口的组成部分，则这些函数的声明应该与类在同一个头文件内
* `=default`C++11要求编译器生成构造函数，要有类内初始值
* 访问说明符(access specifiers)`public` `private`
	* `class` `struct`定义类唯一的区别就是默认的访问权限，前者`private`，后者`public`
* 自定义类型成员`typedef std::string::size_type pos`或`using pos = std::string::size_type`隐藏实现细节
* 可变数据成员`mutable size_t access_ctr`永远不会是`const`；就算函数是`const`成员函数也依然能改变其值
* 类的定义分两步：编译成员的声明，直到类全部可见才编译函数体
* 尽管类成员被隐藏了，但仍可强制加类的名字或显式地使用`this`指针强制访问
* 类的静态成员存在于任何对象之外，对象中不包含任何与静态数据成员有关的数据，不用重复使用关键字`static`
* 构造函数
	* 成员初始化顺序**与它们在类定义中出现的顺序一致**，尽可能避免用某些成员初始化另一些成员
	* 委托构造函数(delegating) 用一个构造函数构造其他构造函数
	* 转换构造函数(converting)
	* `explicit`抑制构造函数隐式转换，只对一个实参的构造函数有效，且只用在类内声明，类外不用；只能用于直接初始化，不能用于拷贝初始化
* 友元
	* 类可以允许其他类或者函数访问它的私有成员，友元`friend`，只能出现在类的内部；一般最好在类定义开始或结束的位置声明友元
	* 友元类`friend class blablabla`或者友元成员函数 注意朋友的朋友不是朋友
	* 友元声明的作用是影响访问权限，本身并非普通意义上的声明，如类内`friend void f(); X() { f(); }`会报错
* 聚合类(aggregate class)
	* 所有成员都是`public`的
	* 没有定义任何构造函数
	* 没有类内初始值
	* 没有基类，没有`virtual`函数
		* 可用一个花括号括起来的成员初始值列表初始化，初始值顺序与声明顺序必须一致

## 拷贝控制(copy control)
* 拷贝构造、拷贝赋值、移动构造、移动赋值、析构
* 合成拷贝函数(synthesized) 编译器给出默认
* 拷贝初始化
	* `string s(dots)`直接初始化 `string s = dots`拷贝初始化
	* 使用情形
		* `=`定义变量
		* 将一个对象作为实参传递给一个非引用类型的形参
		* 从一个返回类型为非引用类型的函数中返回一个对象
		* 用花括号列表初始化一个数组中的元素或一个聚合类中的成员
* 析构函数
	* 成员初始化在函数体执行之前完成，且按照它们在类中出现的次序进行初始化
	* 首先执行函数体，然后销毁成员，成员按照初始化顺序的逆序销毁
* **需要析构函数的类一般需要拷贝赋值操作；需要拷贝操作的类也需要赋值操作，反之亦然**
* `=default`默认内联函数
* `=delete`禁止拷贝/赋值
	* 也可以通过声明（但不定义）私有的拷贝构造函数以禁止外部拷贝
* 赋值运算符好的模式
	* 非常重要！！！避免自赋值出错！
	* **先将右侧运算对象拷贝到一个局部临时对象中，销毁左侧运算对象的资源，再将临时对象的数据拷贝入左侧运算对象**
	* 拷贝并交换技术，异常安全

```cpp
inline void swap(HasPtr &lhs, HasPtr &rhs)
{
    using std::swap;
    swap(lhs.ps, rhs.ps);
    swap(lhs.i, rhs.i);
}

// 注意rhs是按值传递的，意味着HasPtr的拷贝构造函数
// 将右侧运算对象中的string拷贝到rhs
HasPtr& HasPtr::operator=(HasPtr rhs)
{
    // 交换左侧运算对象和局部变量rhs的内容
    swap(*this,rhs); // rhs 现在指向本对象曾经使用的内存
    return *this; // rhs被销毁，从而delete了rhs中的指针
}
```

* 移动操作
	* 右值引用
		* **一个左值表达式表示的是一个对象的身份，而一个右值表达式表示的是对象的值**
		* 左值表达式：返回左值引用的函数、赋值、下标、解引用、前置递增/递减，左值有持久的状态
		* 右值表达式：返回非引用类型的函数、算术、关系、位及后置递增递减运算符，右值短暂的状态
		* `int i = 42; int&& rr = i * 42;`
	* 不抛出异常的操作标记为`noexcept`，如`StrVec::StrVec(StrVec &&s) noexcept : `
	* 移动右值，拷贝左值；若没有移动构造函数，则右值也被拷贝
	* 移动操作避免额外开销

## 重载运算与类型转换
* `:: .* . ?:`不可被重载，其余如`new delete ~ () -> ->*`等均可被重载
* 只可重载已有的运算符，但是无权发明新的运算符号
* `+ - * &`既是一元运算符，又是二元运算符，通过参数数量推断
* 对重载的运算符来说，优先级和结合律保持不变，但求值顺序可能改变，如无法用逻辑运算的短路特性
* 通常不应重载`, & && ||`
* 输出`ostream &operator<<(ostream &os, const Sales_data &item)` 不可为成员函数
* 赋值运算符、下标运算符必须为成员
* 下标运算符通常定义两个版本，一个返回普通引用，另一个是类的常量成员并返回常量引用；非常量可以赋值，常量不能赋值

```cpp
// 下标运算
std::string& operator[] (std::size_t n)
const std::string& operator[] (std::size_t n) const
// 前置后置递增/递减
StrBlobPtr& StrBlobPtr::operator++() // 前置
StrBlobPtr StrBlobPtr::operator++(int) // 后置
{
    // 记录原来的值
    StrBlobPtr ret = *this;
    ++*this;
    return ret;
}
//显式地调用后置运算符
p.operator++(0);
p.operator++(); // 依然前置
```

* 函数调用运算符
	* `operator()(int val) const`

```cpp
class PrintString{
public:
    PrintString(ostream &o = cout, char c = ' '):
        os(o), sep(c) { }
private:
    ostream &os;
    char sep;
};
PrintString errors (cerr, '\n');
errors(s);
// 函数对象常常作为泛型算法的实参
for_each(vs.begin(), vs.end(), PrintString(cerr, '\n'));
```

* `<functional>`头文件
	* 定义了一组表示算术运算符、关系运算符和逻辑运算符的类
	* `vector<string*> nametable; sort(nametable.begin(), nametable.end(), less<string*>());`
* 调用形式(call signature)
	* 可调用的对象：函数、函数指针、lambda表达式、bind创建的对象、以及重载了函数调用运算符的类
	* 如`int(int,int)` 输入两个int，返回一个int
	* 定义一个函数表(function table)用于存储指向这些可调用对象的指针，用map实现，`map<string, int(*)(int,int)> binops`
	* `int add(int i,int j); binops.insert({"+",add});` pair
	* 用`function`标准库类型

```cpp
function<int(int,int)> f1 = add; // 函数指针
function<int(int,int)> f2 = divide(); // 函数对象类的对象
function<int(int,int)> f3 = [](int i, int j); // lambda
```

* 类类型转换(class-type conversions) / 用户定义的类型转换(user-defined conversions)
	* `operator type() const;`
	* 避免过度使用类型转换函数
	* 显式类型转换`explicit`，则需`static_cast<int>(si) + 3;`
	* 当用作表达式条件，编译器会将显式的类型转换自动应用于它
	* 小心二义性错误
		* 不要令两个类进行相同的类型转换
		* 避免转换目标是内置算术类型的类型转换
* 表达式中运算符的候选函数集既包括成员函数，也包括非成员函数