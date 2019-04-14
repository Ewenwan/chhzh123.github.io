---
layout: post
title: C/C++多线程
tag: [pl]
---

本文主要介绍C/C++中多线程编程的方法。

<!--more-->

## 传统方法
```cpp
#include <pthread.h>
int pthread_create(pthread_t * thread, const pthread_arrt_t* attr, void*(*start_routine)(void *), void* arg);
void pthread_exit(void * retval);
void pthread_join(pthread_t thread,void ** retval);
pthread_mutex_init(&mutex1,NULL); // 初始化互斥锁
pthread_mutex_destroy(&mutex1); // 释放锁资源
pthread_mutex_lock(&mutex1); // 加锁
pthread_mutex_unlock(&mutex1); // 去锁
```

实例如下
```cpp
#include <pthread.h>
#include <stdio.h>

pthread_mutex_t mutex1;

void *foo(void *arg)
{
	int* id = (int*) arg;
	pthread_mutex_lock(&mutex1);
	for (int i = 0; i < 5; ++i){
		sleep(1);
		printf("Myid %d\n", *id);
	}
	pthread_mutex_unlock(&mutex1);
}

int main()
{
	pthread_t id[4];
	pthread_mutex_init(&mutex1,NULL);

	for (int i = 0; i < 4; ++i)
		pthread_create(&id[i],NULL,foo,&i);
	for (int i = 0; i < 4; ++i)
		pthread_join(&id[i],NULL);

	for (int i = 0; i < 4; ++i)
		pthread_exit(&id1);

	pthread_mutex_destroy(&mutex1);
}
```

编译指令添加`-lpthread`

## C++11
C++11中添加了标准库的多线程支持

```cpp
#include <iostream>
#include <thread>
using namespace std;

void exec(int n){
	cout << "thread" << n << endl;
}

int main(){
	thread myThread[4];
	for (int i = 0; i < 4; ++i)
		myThread = thread(exec,i);
	for (int i = 0; i < 4; ++i)
		myThread[i].join();
}
```

当要传共享变量/引用时采用`std::ref()`实现。

加互斥锁(mutex)需要添加头文件`<mutex>`，然后在**全局变量**声明一个锁，在函数内部打开`lock_guard`。
```cpp
std::mutex g_display_mutex;
thread_function()
{
    std::lock_guard<std::mutex> guard(g_display_mutex);
    std::thread::id this_id = std::this_thread::get_id();
    std::cout << "From thread " << this_id  << endl;
}
```

这是C++11比较支持的方式，`lock_guard`的作用域即为它的生存期。

对于多线程程序，编译时还是要添加`-pthread`指令

## 参考资料
* C++ 11 多线程--线程管理，<https://www.cnblogs.com/wangguchangqing/p/6134635.html>
* Learn C++ Multi-Threading in 5 Minutes, <https://hackernoon.com/learn-c-multi-threading-in-5-minutes-8b881c92941f>