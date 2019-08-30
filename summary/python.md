---
layout: summary
title: Python
date: 2019-08-30
---

本文记录下Python的一些常用标准库的使用。

<!--more-->

## 数据结构
```python
import queue
q = queue.Queue()
q.put(1)
q.get()
pq = queue.PriorityQueue()
pq.put((priority,val))# the smaller value, the higher priority, and will pop out first
```

## 字符串
### 字符串匹配
```python
re.findall("\[.*?\]","[all]sf[that]")
```

### 格式化字符串
```python
L = [1,2,3]
print(*L, sep=" ")
>>> 1 2 3

s1 = "so much depends upon {}".format("a red wheel barrow")
s2 = "glazed with {} water beside the {} chickens".format("rain", "white")

s1 = " {0} is better than {1} ".format("emacs", "vim")
s2 = " {1} is better than {0} ".format("emacs", "vim")
s3 = " {0} is the same as {0} ".format("emacs")

madlib = " I {verb} the {object} off the {place} ".format(verb="took", object="cheese", place="table")

print("{0:d} - {0:x} - {0:o} - {0:b} ".format(21))
>>> 21 - 15 - 25 - 10101
```

| 数字 | 格式 | 输出 | 描述 |
| 3.1415926 | {:.2f} | 3.14 | 保留小数点后两位 |
| -3.1415926 | {:+.2f} | -3.14 | 带符号保留小数点后两位 |
| 2.71828 | {:.0f} | 3 | 不带小数 |
| 5 | {:0>2d} | 05 | 数字补零（填充左边, 宽度为2） |
| 5 | {:x<4d} | 5xxx | 数字补x（填充右边, 宽度为4） |
| 1000000 | {:,} | 1,000,000 | 以逗号分隔的数字格式 |
| 0.25 | {:.2%} | 25.00% | 百分比格式 |
| 1000000000 | {:.2e} | 1.00e+09 | 指数记法 |
| 13 | {:4d}  | __13 | 右对齐（宽度为4） |
| 13 | {:<4d} | 13__ | 左对齐（宽度为4） |
| 13 | {:^4d} | \_13\_ | 中间对齐（宽度为4） |

## 时间
```python
import time
localtime = time.localtime(time.time())
struct = time.strptime("201901010000","%Y%m%d%H%M") # read from string
time.strftime("%Y%m%d%H%M",localtime)

import datetime
today = datetime.date.today()
today.weekday() # get weekday, Monday is 0
today.replace(2019,8,30)
anotherday = datetime.date(1999,1,1)
today - anotherday # return a datetime.timedelta

import calendar
Cal = calendar.Calendar() # calendar.Calendar(firstweekday=0)
Cal.itermonthdates(2019,8)
calendar.isleap(2019)
calendar.weekday(2019,9,1) # 0 is Monday
calendar.monthrange(2019,9) # Returns weekday of first day of the month and number of days in month
calendar.monthcalendar(2019,9)
calendar.day_name
calendar.day_abbr
calendar.month_name
calendar.month_abbr
```

`time.struct_time`如下

| 序号 | 属性 | 值 |
| :--: | :--: | :--: |
| 0 | tm_year | 2008 |
| 1 | tm_mon | 1 到 12 |
| 2 | tm_mday | 1 到 31 |
| 3 | tm_hour | 0 到 23 |
| 4 | tm_min | 0 到 59 |
| 5 | tm_sec | 0 到 61（60或61是闰秒） |
| 6 | tm_wday | 0到6（0是**周一**） |
| 7 | tm_yday | 1 到 366（儒略历） |
| 8 | tm_isdst | -1, 0, 1, -1决定是否为夏令时 |

`time.strptime`的格式如下

| 指令 | 意义 |
| :--: | :--: |
| %a | 本地化的缩写星期中每日的名称 |
| %A | 本地化的星期中每日的完整名称 |
| %b | 本地化的月缩写名称 |
| %B | 本地化的月完整名称 |
| %c | 本地化的适当日期和时间表示 |
| %d | 十进制数 [01,31] 表示的月中日 |
| %H | 十进制数 [00,23] 表示的小时（24小时制） |
| %I | 十进制数 [01,12] 表示的小时（12小时制） |
| %j | 十进制数 [001,366] 表示的年中日 |
| %m | 十进制数 [01,12] 表示的月 |
| %M | 十进制数 [00,59] 表示的分钟 |
| %p | 本地化的 AM 或 PM 
| %S | 十进制数 [00,61] 表示的秒 |
| %U | 十进制数 [00,53] 表示的一年中的周数（星期日作为一周的第一天）作为在第一个星期日之前的新年中的所有日子都被认为是在第0周 |
| %w | 十进制数 [0(星期日),6] 表示的周中日 |
| %W | 十进制数 [00,53] 表示的一年中的周数（星期一作为一周的第一天）作为在第一个星期一之前的新年中的所有日子被认为是在第0周 |
| %x | 本地化的适当日期表示 |
| %X | 本地化的适当时间表示 |
| %y | 十进制数 [00,99] 表示的没有世纪的年份 |
| %Y | 十进制数表示的带世纪的年份 |
| %z | 时区偏移以格式 +HHMM 或 -HHMM 形式的 UTC/GMT 的正或负时差指示，其中H表示十进制小时数字，M表示小数分钟数字 [-23:59, +23:59]  |
| %Z | 时区名称（如果不存在时区，则不包含字符） |
| %% | 字面的 '%' 字符 |

## 参考资料
* Python格式字符串（译），<http://blog.xiayf.cn/2013/01/26/python-string-format/>
* time, <https://docs.python.org/zh-cn/3/library/time.html>
* datetime, <https://docs.python.org/3/library/datetime.html>