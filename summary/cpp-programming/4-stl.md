---
layout: post
title: C++ - 标准库
date: 2019-02-22
tag: [summary]
---
## IO库
* IO库类型
	* `<iostream>`：流中读写数据`istream,ostream,iostream`
	* `<fstream>`：文件中读写数据`ifstream,ofstream,fstream`
	* `<sstream>`：字符串读写数据`istringstream,ostringstream,stringstream`
* 刷新输出缓冲区
	* `endl`换行刷新
	* `ends`空字符刷新
	* `flush`刷新
	* 如果程序崩溃，输出缓冲区不会被刷新
	* 输入流读取数据前一定会刷新关联的输出流
* 文件流
	* `fstream`被销毁时，`close`自动被调用
	* `in,out,app,ate,trunc,binary`
	* 用`ostringstream`实现最后才输出

```cpp
ifstream in(ifile);
ofstream out;
out.open("a.out");
out.close();
ofstream out2("file1",ofstream::app) // 保留文件内容，定位到文件末尾

string line, word;
vector<PersonInfo> people;
while (getline(cin,line))
{
	PersonInfo info;
	istringstream record(line); //将记录绑定到刚读入的行
	record >> info.name;
	while (record >> word)
		info.phones.push_back(word);
	people.push_back(info);
}

ostringstream badNums;
badNums << " " << nums;
os << badNums.str() << endl;
```

## 顺序容器
* 不同类型
	* `vector`大小可变数组，支持快速随机访问
	* `deque`双端队列
	* `list`双向链表
	* `forward_list`单向链表
	* `array`固定大小数组，支持快速随机访问，不能添加或删除元素
	* `string`
* 使用迭代器，不使用下标操作，避免随机访问
* 迭代器范围 左闭合区间
* 当不需要写访问时，应用`cbegin`和`cend`
* 只有顺序容器的构造函数才接受大小参数 `vector<int> ivec(10,-1);`
* 固定大小`array<int,42>`
* `swap(l1,l2)` 统一使用非成员函数版本的`swap`更利于泛型编程

```cpp
list<string> names;
vector<const char*> oldstyle;
names = oldstyle; // 错误：容器类型不匹配
names.assign(oldstyle.cbegin(), oldstyle.cend()); // 正确：可以将const char*转为string
```

* 插入
	* 向一个`vector`,`string`,`deque`插入元素会使所有指向容器的迭代器、引用和指针失效（中间插入会重新分配内存），不要缓存迭代器
	* `c.insert(p,il)`il是一个花括号包围的元素值列表，将这些值插入到迭代器p所指的元素之前，返回指向新添加的第一个元素的迭代器
	* `c.insert(p,n,t)`迭代器p前插入n个值为r的元素
	* `c.insert(p,b,e)`将迭代器b,e之间的元素插入到p之前
	* `emplace``emplace_front``emplace_back`函数在容器中直接构造元素，传递给`emplace`函数的参数必须与元素类型的构造函数相匹配
		* `c,push_back(Sales_data("dsf",25,15.99))`等价于`c,emplace_back("dsf",25,15.99)`
* 访问
	* `at`返回下标为n的元素的引用，和下标一样，只适用于`string``vector``deque``array`
	* `c.back()` `c.front()` 注意不要对空容器使用
* 删除
	* `c.clear()`
	* `c.erase(b,e)`返回被删元素后的下一个
* `resize`不适用于`array`
* `forward_list`

```cpp
lst.before_begin() // 首元素之前一个元素
lst.cbefore_begin()
lst.insert_after(p,t) // p后插入，t对象，n数量
lst.insert_after(p,n,t)
lst.insert_after(p,b,e)
lst.insert_after(p,il)
emplace_after(p,args)
lst.erase_after(p)
lst.erase_after(b,e)
```

* 管理容量
	* `c.shrink_to_fit()`C++11退回不需要的内存空间，不一定成功
	* `c.capacity()`不重新分配内存，当前最大可保存元素数目
	* `c.reserve(n)`分配至少能容纳n个元素的空间
* `string`
```cpp
s.substr(pos,n)
s.insert(s.size(),5,'!')
s.erase(s.size() - 5,5)
s.assign(cp,7)
s.insert(0,s2,0,s2.size()) // 在s[0]之前插入s2中从s2[0]开始的s2.size()个字符
s.append("fd") // 结尾加
s.replace(1,3,s2) // 从位置1开始删除3个字符并插入s2
s.find(args) s.rfind(args)
s.find_first_of(args) s.find_last_of(args)
s.find_first_not_of(args) s.find_last_not_of(args)
// args 可以为
// c,pos
// s2,pos
// cp,pos
// cp,pos,n 从s的pos位置搜指针cp指向的数组的前n个字符
s.compare(args)
// s2
// pos1,n1,s2
// pos1,n1,s2,pos2,n2
// cp
// pos1,n1,cp
// pos1,n1,cp,n2
to_string(val)
stoi(s,p,b) stol(s,p,b) stoul(s,p,b) stoll(s,p,b) stoull(s,p,b)
stof(s,p,b) stod(s,p,b) stold(s,p,b)
```

## 容器适配器(adaptor)
* `stack`
* `queue`
* `priority_queue`

## 关联容器
* `map`
* `set`

```cpp
c.find(k)
c.count(k)
c.lower_bound(k) // 返回迭代器，第一个关键字不小于k的元素
c.upper_bound(k)
c.equal_range(k)
```

* `pair`
* `multiset`

```cpp
bool compareIsbn(const Sales_data &lhs, const Sales_data &rhs)
{
    return lhs.isbn() < rhs.isbn();
}
multiset<Sales_data, decltype(compareIsbn)*> bookstore(compareIsbn); // 提供函数指针
```

## 无序容器C++11
* 如果关键字类型固有就是无序的，或者性能测试发现问题可以用哈希技术解决，就可以用无序容器

```cpp
// 管理桶接口
c.bucket_count()
c.max_bucket_count()
c.bucket_size(n)
c.bucket(k) // 关键字k在哪个桶
// 桶迭代
local_iterator
const_local_iterator
c.begin(n), c.end(n) // 桶n的迭代器
c.cbegin(n), c.cend(n)
// 哈希策略
c.load_factor // 每个桶的平均元素数量，返回float
c.max_load_factor() // 试图维护平均桶大小
c.rehash(n) // 重新存储为>n个桶
c.reserve(n) // 重新存储，使得c可以保存n个元素且不必rehash
```

## tuple类型
```cpp
tuple<string, vector<double>, int, list<int>>
auto item = make_tuple("fdsa", 3, 20.00); // 标准库定义
auto price = get<2>(item)/cnt;
```
## bitset类型
```cpp
bitset<20> bitvec2(0xbeef);
b.any(); // 是否存在置位的二进制位
b.all(); // 所有位都置位了吗
b.count(); // 置位的位数
b.flip(pos); // 也可通过~实现
b.set(pos,v);
```

## 正则表达式(regex)库
* 正则表达式是在运行时而非编译时编译的，故其编译是一个很慢的操作，应尽量避免创建不必要的regex，如应在循环外创建
```cpp
// i除非在c之后，否则在e之前
string pattern("[^c]ei");
pattern = "[[:alpha:]]*" + pattern + "[[:alpha:]]*";
regex r(pattern); // 构造一个用于查找模式的regex
smatch results; // 定义一个对象保存搜索结果
string test_str = "receipt friend theif receive";
// 用r在test_str中查找与pattern匹配的字串
if (regex_search(test_str, results, r))
    cout << results.str() << endl;
```

## 随机数(random)库
* 一个给定的随机数发生器一直会生成相同的随机数序列，一个函数如果定义了局部的随机数发生器，应将其（引擎和分布对象）定义为`static`
```cpp
// 随机数发生器 = 分布对象 + 引擎对象
uniform_int_distribution<unsigned> u(0,9);
default_random_engine e; // 生成无符号随机整数
for (size_t i = 0; i < 10; ++i)
    // u作为随机数源
    // 每个调用返回在指定范围内并服从均匀分布的值
    cout << u(e) << " ";
// 设置种子
e.seed(32767);
// 生成随机实数
uniform_real_distribution<double> u(0,1);
```

## IO库
* `boolalpha`输出`true`或`false`，恢复用`noboolalpha`
* `oct`、`hex`、`dec`指定整型进制，`showbase`显示进制，`noshowbase`恢复，`hexfloat`C++11
* `uppercase`
* `<iomainp>`操纵`setprecision`，`showpoint`显示小数点
* `left`、`right`左右对齐，`setw`指定数字或字符串值的最小空间，`setfill(' ')`用符号补全空白
* `fixed`定点十进制，`scientific`科学计数法
* `noskipws`可读取空格，`skipws`恢复
* 多字节操作`is.get(sink,size,delim)`、`is.getline(sink,size,delim)`、`is.ignore(size,delim)`
* 随机访问`seek`定位、`tell`告诉当前位置
* <http://www.cnblogs.com/leewiki/archive/2011/12/13/2286168.html>

## 网页链接
* 标准库
	* 简介< http://blog.csdn.net/sxhelijian/article/details/7552499>
	* document <http://classfoo.com/ccby/article/WlfKr>
* 常用容器
	* <https://www.cnblogs.com/pengjun-shanghai/p/5283657.html>
* `string`类
	* <http://blog.csdn.net/yzl_rex/article/details/7839379>
	* doucument< http://www.cplusplus.com/reference/string/string/>
* `stack`
	* <http://blog.csdn.net/chao_xun/article/details/8037420>
* `queue`
	* <https://www.cnblogs.com/hdk1993/p/5809180.html>
* `bitset`
	* <http://blog.csdn.net/qll125596718/article/details/6901935>
* `algorithm`
	* <http://blog.csdn.net/tianshuai1111/article/details/7674327>
	* <https://www.cnblogs.com/lgxZJ/p/6377437.html>
	* document <http://www.cplusplus.com/reference/algorithm/>
* `priority_queue`
	* <https://www.cnblogs.com/Deribs4/p/5657746.html>