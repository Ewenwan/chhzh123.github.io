---
layout: post
title: Python高级指南
date: 2020-03-16
tag: [summary]
---

## 迭代 - 生成器函数
```python
def gensquares(n):
    for i in range(n):
        yield i ** 2

for i in gensquares(5):
    print(i, end=" : ")

x = gensquares(4)
next(x)

G = (x ** 2 for x in range(4)) # this is an iterator
```

## 模块
Python的`import`和C/C++的`#include`有着巨大区别，导入并非只是把一个文件文本插入另一个文件而已，Python的导入是运行时的运算，程序**第一次导入**指定文件会执行三个步骤：（只导入**一次**）
1. 找到模块文件
2. 编译成位码
3. 执行模块的代码来创建其所定义的对象

可以用`from imp import reload; reload(...)`重新加载。

Python与Java类似，以操作系统的文件结构进行组织，每个文件夹即称为包，并且为了跨平台，以点号`.`分隔。

文件组织如下，注意子文件夹要添加`__init__.py`文件，该文件可以包含Python代码作为声明，或者完全是空的。作为声明，这些文件可以防止有相同名称的目录不小心隐藏在模块搜索路径中，而之后才出现真正需要的模块。
```
dir0\dir1\dir2\mod.py

import dir1.dir2.mod

dir0\
    dir1\
        __init__.py
        dir2\
            __init__.py
            mod.py
```

Python首次导入某个目录时，会自动执行该目录下`__init__.py`文件中的所有程序代码。可以在`__init__.py`文件中声明`__all__`列表，用于声明`from *`导入的子模块名称，如

```python
__all__ = ["Error", "encode", "decode"] # export these only
```

或者通过把下划线放在最前面`_X`，防止该变量被`from *`复制出去。但它不是“私有”声明，依然可以通过比如`import`导入。

* 绝对导入：导入位于模块导入搜索路径上某处的模块
* 相对导入：导入位于**同一包**中的模块（只适用于`from`语句）

```python
from . import spam # relative to this package
from .spam import name

# now code at A.B.C
from .D import X # import A.B.D.X
from ..E import X # import A.E.X
```

注意`from`其实是在导入者的作用域内对变量名的赋值语句，也就是**变量名拷贝**运算，而不是变量名别名机制。

可以通过`sys.path.append`来添加模块搜索路径。

要开启以后的语言特性，可以通过`from __future__ import featurename`导入。

每个模块都有名为`__name__`的内置属性，Python会自动设置该属性：
* 如果文件以顶层程序执行，在启动时，`__name__`就会设置为字符串`__main__`
* 如果文件被导入，`__name__`就会被改为客户端的模块名

因此下列代码就可以通过检测自己的`__name__`来判断是在执行还是导入，这点非常有用。
```python
def tester():
    print("Hello!")

if __name__ == "__main__": # only when run
    tester()               # not when imported
```


## 类与OOP
调用超类构造函数
```python
class Super:
    def __init__(self,x):
        # default code

    def action(self): # abstact base class method
        raise NotImplementedError("Actions must be defined!")

class Sub(Super): # inherent
    def __init__(self,x,y):
        Super.__init__(self,x) # run superclass __init__
        # custom code
```

重载运算符：[Python中的魔法方法(magic method)](https://rszalski.github.io/magicmethods/)
* `__init__`、`__del__`
* `__add__`
* `__str__`、`__repr__`
* `__len__`
* `__getitem__`
* `__call__`

有时候程序需要处理与类而不是与实例相关的数据，考虑要记录由一个类创建的实例数目，或者维护当前内存中一个类的所有实例的列表。这种类型的信息与类相关，而不是与其实例相关，即这种信息通常存储在类自身上，不需要任何实例也可以处理，这时就可以使用**特殊方法**。


## 异常处理
```python
try:
    main-action
except Exception1:
    handler1
except Exception2:
    handler2
...
else: # no exceptions happen
    else-block
finally: # all exceptions have been handled
    finally-block
```

`with ... as ...`可以用来管理环境，处理异常，实际工作过程如下：
1. 环境管理器的`__enter__`方法会被调用，如果有`as`子句则赋值给子句中的变量
2. 代码块中的代码执行
3. 若`with`代码块引发异常，`__exit__(type,value,traceback)`就会被调用
4. 若`with`代码块没有引发异常，则`__exit__`方法依然会被调用，其`type`、`value`及`traceback`参数都会以`None`传递


## 装饰器
函数装饰器(decorator)替函数明确了特定的运算模式，也就是将函数包裹了另一层，在另一函数的逻辑内实现。

```python
class C:
    @staticmethod # decoration syntax
    def cal():
        # do something

# the same as
cal = staticmethod(cal) # rebind name
```

装饰器自身是一个**返回可调用对象的可调用对象**
* 函数装饰器在**函数调用**时进行处理
* 类装饰器在**实例创建调用**时处理

```python
import time
class timer:
    def __init__(self, func):
        self.func = func
        self.alltime = 0

    def __call__(self, *args, **kargs):
        start = time.clock()
        result = self.func(*args, **kargs)
        elapsed = time.clock() - start
        self.alltime += elapsed
        print('%s: %.5f, %.5f' % (self.func.__name__, elapsed, self.alltime))
        return result

@timer
def listcomp(N):
    return [x * 2 for x in range(N)]

@timer
def mapcall(N):
    return map((lambda x: x * 2), range(N))

result = listcomp(5) # Time for this call, all calls, return value
listcomp(50000)
listcomp(500000)
listcomp(1000000)
print(result)
print('allTime = %s' % listcomp.alltime) # Total time for all listcomp calls

print('')
result = mapcall(5)
mapcall(50000)
mapcall(500000)
mapcall(1000000)
print(result)
print('allTime = %s' % mapcall.alltime) # Total time for all mapcall calls
print('map/comp = %s' % round(mapcall.alltime / listcomp.alltime, 3))
```

假设你需要被另一个应用程序使用的方法或类注册到一个API，以便随后处理（可能该API随后将会调用该对象，以响应事件）。尽管你可能提供一个注册函数，在对象定义之后手动地调用该函数，但装饰器使得你的意图更为明显。
事实上这种设计在TVM Relay的算子中也出现了，可以参见其[源码](https://github.com/apache/incubator-tvm)。

```python
# Registering decorated objects to an API
registry = {}
def register(obj): # Both class and func decorator
    registry[obj.__name__] = obj # Add to registry
    return obj # Return obj itself, not a wrapper

@register
def spam(x):
    return(x ** 2) # spam = register(spam)

@register
def ham(x):
    return(x ** 3)

@register
class Eggs: # Eggs = register(Eggs)
    def __init__(self, x):
        self.data = x ** 4
    def __str__(self):
        return str(self.data)

print('Registry:')
for name in registry:
    print(name, '=>', registry[name], type(registry[name]))

print('\nManual calls:')
print(spam(2)) # Invoke objects manually
print(ham(2)) # Later calls not intercepted

X = Eggs(2)
print(X)

print('\nRegistry calls:')
for name in registry:
    print(name, '=>', registry[name](3)) # Invoke from registry
```

一个有意思的事情在于，在Python 3.0中，用户定义的类对象是名为`type`的对象的实例，`type`本身是一个类（元类metaclass）。
```python
>>> type([]) # In 3.0 list is instance of list type
<class 'list'>
>>> type(type([])) # Type of list is type class
<class 'type'>
>>> type(list) # Same, but with type names
<class 'type'>
>>> type(type) # Type of type is type: top of hierarchy
<class 'type'>
```

即实例创建自类，而类创建自`type`，在Python 3.0中，“类型”的概念与“类”的概念合并了，**类是类型，类型也是类**。
* 类型由派生自`type`的类定义
* 用户定义的类是类型类的实例
* 用户定义的类是产生它们自己实例的类型

## 参考资料
* 《Python学习手册》（第四版）