---
layout: post
title: C++ - 泛型算法
date: 2018-05-01
tag: [summary]
---

## 概述
* 迭代器令算法不依赖于容器，但算法依赖于元素类型的操作
* 泛型算法本身不会执行容器的操作，它们只会运行于迭代器之上，执行迭代器的操作

## 一些泛型算法
都定义在`<algorithm>`头文件内
* `find(vec.cbegin(),vec.cend(),val)`
* `accumulate(v.cbegin(),v.end(),string(""))`只要定义了加法，就能以第三个参数为初值加
* `fill(b,e,0)`
* 插入迭代器`back_inserter`，如`fill_n(back_inserter(vec),10,0)`
* `copy(b(a1),e(a1),a2)`
* `unique(b,e)`覆盖重复，将不重复的调到前面，返回最后一个不重复元素之后的位置，再执行`c.erase(end_unique,c.end())`删除
* 谓词(predicate)：一元意味着只接受单一参数

```cpp
void elimDups(vector<string> &words)
{
    // sort words alphabetically so we can find the duplicates
    sort(words.begin(), words.end());
    // unique reorders the input range so that each word appears once in the
    // front portion of the range and returns an iterator one past the unique range
    auto end_unique = unique(words.begin(), words.end());
    // erase uses a vector operation to remove the nonunique elements
    words.erase(end_unique, words.end());
}

bool isShorter(const string &s1, const string &s2)
{
    return s1.size() < s2.size();
}
stable_sort(words.begin(),words.end(),isShorter);
```

## lambda表达式
* `[capture list](parameter list) -> return type { function body }`
* `find_if(words.begin(),words.end(),[sz](const string &a) { return a.size() >= sz; });`返回一个迭代器，指向第一个长度不小于给定参数sz的元素
* `for_each(wc,word.end(),[](const string &s) { cout << s << " ";} );`
* 若希望改变捕获变量的值，要加上关键字`mutable`，如`[v1] () mutable { return ++v1; };`
* 尾置返回类型`[] (int i) -> int { if (i<0) return -i; else return i;});`

```cpp
// sz implicitly captured by value
wc = find_if(words.begin(), words.end(),
            [=](const string &s)
                { return s.size() >= sz; });

void biggies(vector<string> &words,
            vector<string>::size_type sz,
            ostream &os = cout, char c = ' ')
{
    // other processing as before
    // os implicitly captured by reference; c explicitly captured by value
    for_each(words.begin(), words.end(),
            [&, c](const string &s) { os << s << c; });
    // os explicitly captured by reference; c implicitly captured by value
    for_each(words.begin(), words.end(),
            [=, &os](const string &s) { os << s << c; });
}
```

| Lambda表达式捕获列表 | 含义 |
| :--: | :--: |
| `[]` | 空捕获列表 |
| `[names]` | 传值，如果跟`&`则传引用 |
| `[&]` | 全部传引用 |
| `[=]` | 全部传值 |
| `[&,identifier_list]` | 传引用，传值 |
| `[=,reference_list]` | 传值，传引用 |

## 参数绑定?
* `bind(isShorter,_2,_1)` _2,_1为占位符
* `placeholder`

## 迭代器
* 插入迭代器
* 反向迭代器
* 移动迭代器
* 流迭代器
```cpp
istream_iterator<int> in(cin),eof;
cout << accumulate(in,eof,0) << endl;
ostream_iterator<int> out_iter(cout," ");
copy(vec.begin(),vec.end(),out_iter);
```