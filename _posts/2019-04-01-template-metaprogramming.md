---
layout: post
title: C++模板元编程
tag: [pl]
---

最近才稍微了解现代C++中非常重要的技术，即模板元编程，本文作为记录。

<!--more-->

## 模板元编程(template metaprogramming)
C++ 模板最初是为实现泛型编程设计的，但人们发现模板的能力远远不止于那些设计的功能，一个重要的理论结论就是：C++ 模板是**图灵完备**的(Turing-complete)，理论上说 C++ 模板可以执行任何计算任务，但实际上因为模板是**编译期计算**，其能力受到具体编译器实现的限制（如递归嵌套深度，C++11 要求至少1024，C++98要求至少 17）。C++模板元编程（所谓元编程，就是用来编写程序的程序）是“意外”功能，而不是设计的功能，这也是C++模板元编程**语法丑陋**的根源。

C++模板是图灵完备的，这使得C++成为两层次语言(two-level languages)，其中，执行编译计算的代码称为静态代码(static code)，执行运行期计算的代码称为动态代码(dynamic code)。
![two-level language](https://images0.cnblogs.com/blog/528205/201501/131303575117915.png)

具体来说 C++ 模板可以做以下事情：
* 编译期数值计算
* 类型计算
* 代码计算（如循环展开）
其中数值计算实际不太有意义，而类型计算和代码计算可以使得代码更加通用，更加易用，性能更好（也更难阅读，更难调试，有时也会有代码膨胀问题）。

从编程范型(programming paradigm)上来说，C++模板是**函数式编程**(functional programming)，它的主要特点是：函数调用不产生任何副作用（没有可变的存储），用递归形式实现循环结构的功能。C++模板的特例化提供了条件判断能力，而模板递归嵌套提供了循环的能力，这两点使得其具有和普通语言一样通用的能力（图灵完备性）。

```cpp
#include <iostream>

template<typename T, int i=1>
class someComputing {
public:
    typedef volatile T* retType; // 类型计算
    enum { retValume = i + someComputing<T, i-1>::retValume }; // 数值计算，递归
    static void f() { std::cout << "someComputing: i=" << i << '\n'; }
};

template<typename T> // 模板特例，递归终止条件
class someComputing<T, 0> {
public:
    enum { retValume = 0 };
};

template<typename T>
class codeComputing {
public:
    static void f() { T::f(); } // 根据类型调用函数，代码计算
};

int main(){
    someComputing<int>::retType a=0;
    std::cout << sizeof(a) << '\n'; // 64-bit 程序指针
    // VS2013 默认最大递归深度500，GCC4.8 默认最大递归深度900（-ftemplate-depth=n）
    std::cout << someComputing<int, 500>::retValume << '\n'; // 1+2+...+500
    codeComputing<someComputing<int, 99>>::f();
    std::cin.get(); return 0;
}
```

## 特性(traits)
先说作用：当函数，类或者一些封装的通用算法中的某些部分会因为数据类型不同而导致处理或逻辑不同（而我们又不希望因为数据类型的差异而修改算法本身的封装时），traits会是一种很好的解决方案。

模板特化(specialization)，如下段代码使得`TraitHelper<void>::isVoid`的值为真，进而可以在编译器进行类型运算。
```cpp
template<typename T>
struct TraitHelper{
	static const bool isVoid = false;
};

template<>
struct TraitHelper<void>{
	static const bool isVoid = true;
}
```

偏特化(partial specialization)，下面的例子使得输入为指针类型时返回值为真
```cpp
template<typename T>
struct TraitHelper{
	static const bool isPointer = false;
};

template<typename T>
struct TraitHelper<T*>{
	static const bool isPointer = true;
}
```

注意`typename`和`class`的区别，当要用到类型时一定要加`typename`声明
```cpp
template<typename T>
typename T::value_type test(const T& c);
```

实现不同类型参数传递，及不同返回类型
```cpp
template <typename T>
class Test {
public:
    TraitsHelper<T>::ret_type Compute(TraitsHelper<T>::par_type d);
private:
    T mData;
};
```

实现不同算法
```cpp
template< bool b > 
struct algorithm_selector { 
  template< typename T > 
  static void implementation( T& object ) 
  { 
//implement the alorithm operating on "object" here 
  } 
};

template<> 
struct algorithm_selector< true > { 
  template< typename T > 
  static void implementation( T& object )   { 
    object.optimised_implementation(); 
  } 
};

template< typename T > 
void algorithm( T& object ) { 
  algorithm_selector< supports_optimised_implementation< T >::value >::implementation(object); 
}

class ObjectB { 
public: 
  void optimised_implementation() { 
//... 
  } 
};

template<> 
struct supports_optimised_implementation< ObjectB > { 
  static const bool value = true; 
};

int main(int argc, char* argv[]) { 
  ObjectA a; 
  algorithm( a ); 
// calls default implementation 
  ObjectB b; 
  algorithm( b ); 
// calls 
// ObjectB::optimised_implementation(); 
  return 0; 
}
```

特性类(traits class)
```cpp
template<class IterT>
struct my_iterator_traits {
    typedef typename IterT::value_type value_type;
};

my_iterator_traits<vector<int>::iterator>::value_type a;
```

## 模板特化
谓模板特例化即对于通例中的某种或某些情况做单独专门实现，最简单的情况是对每个模板参数指定一个具体值，这成为完全特例化（full specialization），另外，可以限制模板参数在一个范围取值或满足一定关系等，这称为部分特例化（partial specialization），用数学上集合的概念，通例模板参数所有可取的值组合构成全集U，完全特例化对U中某个元素进行专门定义，部分特例化对U的某个真子集进行专门定义。
```cpp
// 实现一个向量类
template<typename T, int N>
class Vec{
    T _v[N];
    // ... // 模板通例（primary template），具体实现
};
template<>
class Vec<float, 4>{
    float _v[4];
    // ... // 对 Vec<float, 4> 进行专门实现，如利用向量指令进行加速
};
template<int N>
class Vec<bool, N>{
    char _v[(N+sizeof(char)-1)/sizeof(char)];
    // ... // 对 Vec<bool, N> 进行专门实现，如用一个比特位表示一个bool
};
```

## [enable_if](https://en.wikibooks.org/wiki/More_C%2B%2B_Idioms/enable-if)
`enable_if`常用于需要根据不同类型的条件实例化不同模板的时候
```cpp
template <bool, class T = void> 
struct enable_if 
{};

template <class T> 
struct enable_if<true, T> 
{ 
  typedef T type; 
};
```
“替代失败不是错误”原则(Substitution Failure Is Not An Error, SFINAE)


## 编译期多态
奇异递归模板(curiously recurring template pattern, CRTP)
```cpp
#include <iostream>
using namespace std;

template <typename Child>
struct Base
{
    void interface()
    {
        static_cast<Child*>(this)->implementation();
    }
};

struct Derived : Base<Derived>
{
    void implementation()
    {
        cerr << "Derived implementation\n";
    }
};

int main()
{
    Derived d;
    d.interface();  // Prints "Derived implementation"
}
```

## Duck Typing
> When I see a bird that walks like a duck and swims like a duck and quacks like a duck, I call that bird a duck. --- James Whitcomb Riley

```cpp
template <typename T> 
void f(const T& object) 
{ 
  object.f(0); // 要求类型 T 必须有一个可让此语句编译通过的函数。
} 

struct C1 
{
  void f(int); 
};
 
struct C2 
{ 
  int f(char); 
};
 
struct C3 
{ 
  int f(unsigned short, bool isValid = true); 
}; 
 
struct C4
{
  Foo* f(Object*);
};
```

## 一些实际的例子
* rapidjson, <https://github.com/Tencent/rapidjson/blob/master/include/rapidjson/document.h>
* Factory pattern, <https://gist.github.com/sacko87/3359911>

## 参考资料
* C++模板元编程（C++ template metaprogramming），<http://www.cnblogs.com/liangliangh/p/4219879.html>
* 【C++模版之旅】神奇的Traits，<https://blog.csdn.net/my_business/article/details/7891687>
* An introduction to C++ Traits, <https://accu.org/index.php/journals/442>
* C++ enable_if的使用，<http://www.fuzihao.org/blog/2016/07/14/C-enable-if%E7%9A%84%E4%BD%BF%E7%94%A8/>
* Polymorphism Without Virtual Functions, <https://stackoverflow.com/questions/48550968/polymorphism-without-virtual-functions>
* C++ Runtime Polymorphism without Virtual Functions, <https://www.codeproject.com/Articles/603818/Cplusplus-Runtime-Polymorphism-without-Virtual-Fun>
* The cost of dynamic (virtual calls) vs. static (CRTP) dispatch in C++, <https://eli.thegreenplace.net/2013/12/05/the-cost-of-dynamic-virtual-calls-vs-static-crtp-dispatch-in-c/>
* The Curiously Recurring Template Pattern in C++, <https://eli.thegreenplace.net/2011/05/17/the-curiously-recurring-template-pattern-in-c/>
* C++ is Lazy: CRTP, <http://www.modernescpp.com/index.php/c-is-still-lazy>
* Combining Static and Dynamic Polymorphism with C++ Mixin classes, <https://michael-afanasiev.github.io/2016/08/03/Combining-Static-and-Dynamic-Polymorphism-with-C++-Template-Mixins.html>