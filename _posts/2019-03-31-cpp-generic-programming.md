---
layout: post
title: C++泛型编程
tag: [pl]
---

这次做图系统进行系统层级代码的编写，才发现C++中的诸多问题，以前并未思考过，现在查阅了大量资料才大致了解应该怎么做，仅以本文作为记录。

<!--more-->

C++很大一个问题在于泛型编程与面向对象的耦合问题。

用数组存储类的继承，多态性就会被消除（这是因为不同继承类的大小不同，无法统一），因而必须以指针形式存储。
```cpp
class Base;
Base** bases = new Base* [10];
vector<Base*> bases[10]; // or
```

注意C++是静态类型的语言，工厂模式(factory pattern)比较难实现。
函数返回不同的类型不是最麻烦的，最麻烦的是函数返回不同的泛型的特例，此时这些类型都是不同的，没有共同的基类，无法简单用基类指针解决。
```cpp
what_type factory(int i){
	if (i == 1)
		return vector<int> (10,0);
	else
		return vector<bool> (10,0);
}

int main()
{
	what_type fac = factory(1);
}
```

为了避免出现新建的变量出了作用域会被消除的情况，如下
```cpp
A* instance = NULL;
if ( condition = true )
   instance = new A(1);
else
   instance = new A(2);

// or use ternary operator
A* instance = new A( condition ? 1 : 2 );

// factory patter
class A; // abstract
class B : public A;
class C : public A;

class AFactory
{
public:
   A* create(int x)
   {
      if ( x == 0 )
         return new B;
      if ( x == 1 )
         return new C;
      return NULL;
   }
};
```

C++17中引入了`std::variant`来存储多种类型，是类似于`union`的东西，通过`get`、`visit`等方法来访问元素
```cpp
std::variant<int, double, std::string> x, y;

// assign value
x = 1;
y = "1.0";

// overwrite value
x = 2.0;
```

## 参考资料
* Virtual member function overriding, <http://www.cplusplus.com/forum/general/61557/>
* Scope of variables in if statements, <https://stackoverflow.com/questions/8543167/scope-of-variables-in-if-statements>
* C++17更通用的union: variant，<https://kheresy.wordpress.com/2017/10/16/cpp17-variant/>