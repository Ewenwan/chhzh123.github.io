---
layout: post
title: C++ - 模板与泛型编程
date: 2019-08-26
tag: [summary]
---

## 定义模板
* `template <typename T, class U> calc (const T&, const U&)`
* 非类型模板参数
	* `template<unsigned N,unsigned M> int compare (const char (&p1)[N], const char (&p2)[M])`给出数组长度
* `inline`与`constexpr`放在模板参数列表之后，返回类型之前
* 模板程序应该尽量减少对实参类型的要求，如用`less`代替`<`，且不用`>`
* 类模板
	* `template<typename T> class Blob`
	* 实例化类模板必须提供额外信息，即显式模板实参`Blob<int> ia`
	* 如果在类外定义成员函数要加上`template`，如`template<typename T> BlobPtr<T> BlobPtr<T>::operator++(int);`
	* 为类模板定义类型别名`template<typename T> using twin = pair<T,T>; twin<string> authors;`
* 当希望通知编译器一个名字表示类型时，必须使用关键字`typename`，而不能使用`class`
* 可以提供默认模板实参`template<typename T = less<T>>`，之后声明时可用空<>来代表使用默认类型
* 可以有成员模板，但不能是虚函数
* `extern template class Blob<string>`实例化声明，在程序某个位置必须有其显式的实例化定义
## 模板实参推断
* 类型转换
	* 将实参传递给带模板类型的函数形参时，能够自动应用的类型转换只有`const`转换和数组或函数到指针的转换
	* 使用相同模板参数类型的函数形参，如模板是`<T,T>`，则不能实例化为`<long,int>`，必须定义两个模板`<U,T>`才可
	* 如果函数参数类型不是模板参数，则对实参进行正常的类型转换
* 显式模板实参

```cpp
template<typename T1, typename T2, typename T3>
T1 sum(T2, T3);
// T1 显式指定，T2 T3从函数实参类型推断而来
auto val3 = sum<long long>(i, lng); // long long sum(int, long)
// 糟糕的设计
template<typename T1, typename T2, typename T3>
T3 sum(T2, T1);
// 则需要指定所有实参
auto val3 = sum<long long, int, long>(i,lng);
```

* 尾置返回类型

```cpp
template<typename It>
auto fcn(It beg, It end) -> decltype(*beg)
// 标准库类型转换模板 <type_traits> 包含模板元程序设计
// 下面的函数可返回具体的值
template<typename It>
auto fcn(It beg, It end) ->
    typename remove_reference<decltype(*beg)>::type
```

* 引用折叠
	* `X& &`、`X& &&`、`X&& &`都折叠成`X&`
	* `X&& &&`折叠成`X&&`

```cpp
// 标准库的move
template<typename T>
typename remove_reference<T>::type&& move(T&& t)
{
    return static_cast<typename remove_reference<T>::type&&>(t);
}
// 通过引用折叠可实现给move左值也可给其右值
```

## 可变参数模板(variadic)
* 可变数目的参数称为参数包(parameter packet)：模板参数包、函数参数包
* 用省略号指出接受一个包
* 可以递归，但需要同时给出非可变参数的模板

```cpp
template <typename T, typename... Args>
void foo(const T& t, const Args&... rest);
// sizeof可获得元素数目
sizeof...(Args)
```

## 模板特例化(specialization)
* 特例化本质是实例化一个模板，而非重载它，因此特例化不影响函数匹配

```cpp
template<typename T> int compare(const T&, const T&);
// compare的特殊版本，处理字符数组指针
template<>
int compare(const char* const& p1, const char* const &p2)
```

## 其他
* Type erasure
	* <https://www.modernescpp.com/index.php/c-core-guidelines-type-erasure>
	* with template, <https://www.modernescpp.com/index.php/c-core-guidelines-type-erasure-with-templates>
* Virtual function performance
	* <https://stackoverflow.com/questions/449827/virtual-functions-and-performance-c>