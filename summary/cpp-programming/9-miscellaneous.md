---
layout: post
title: C++ - 大型项目工具
date: 2018-06-14
tag: [summary]
---
## 异常处理(exception handling)
* 通过抛出一条表达式来引发一个异常
* 栈展开(stack unwinding)：当抛出一个异常后，程序暂停当前函数的执行并立即寻找与异常匹配的`catch`子句
* 一个单独的catch不能完整地处理某个异常，则重新抛出，直接`throw;`
* 捕获所有异常`catch(...)`
* 不抛出说明`noexcept`跟在函数参数列表后，也可以作为运算符，与异常说明的bool实参一起出现

```cpp
while (cin >> item1 >> item2) {
    try{
        if (item1.isbn() != item2.isbn())
            throw (runtime_error("Data must refer to same ISBN");
    } catch (runtime_error err) {
        cout << err.what()
                << "\nTry Again? Enter Y or N" << endl;
    }
}
```

## 命名空间
* `namespace`命名空间结束后无需分号
* 全局命名空间没有名字，即`::member_name`
* 命名空间可以嵌套
* C++11内联命名空间(inline)，其内部名字可被外层命名空间直接使用
* 使用未命名的命名空间取代文件中的静态声明
* 名字空间的别名(alias)`namespace primer = cplusplus_primer;`
* `using`一次只引入命名空间的一个成员

## 多重继承与虚继承
* 虚继承可以保证虚基类在继承体系中出现了多少次，在派生类中都只包含唯一一个共享的虚基类子对象
* `public`和`virtual`的顺序随意

## 特殊工具与技术
* 定位(placement) new
	* `new (place_address) type [size] { braced initializer list}`
	* 调用析构函数会销毁对象，但不会释放内存
* 运行时类型识别(runtime type identification, RTTI)
	* `typeid`
	* `dynamic_cast`
* `type_info`定义在`<typeinfo>`头文件中
	* `t1==t2`、`t1!=t2`、`t.name()`
* 枚举类型
	* 不限定作用域 `enum color {red, yellow, green}`，之后再定义这三者会报错
	* 限定作用域C++11 `enum class peppers {red, yellow, green}`
	* 默认情况下，枚举值从0开始，依次加1，但也能直接赋值
	* C++11可以 `enum intValues : unsigned long long`定义类型
* 嵌套类(nested)
* union：节省空间的类
	* 在任意时刻只有一个数据成员可以有值
	* 不能含引用类型的成员，默认公有，可以有构造函数、析构函数等成员函数，但不能继承、作为基类、含有虚函数
* 固有的不可移植特性(nonportable)
	* 位域(bit-field)
	* `volatile`
		* 直接处理硬件的程序常常包含这样的数据元素，它们的值由程序直接控制之外的过程控制，如程序可能含一个由系统时钟定时更新的变量
	* 链接指示(linkage directive) `extern "C"`调用其他语言编写的函数