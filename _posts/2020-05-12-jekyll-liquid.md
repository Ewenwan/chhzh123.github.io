---
layout: post
title: Jekyll和Liquid语法速查
tag: [configuration]
---

本文记录部署Jekyll可能用到的一些指令及Liquid的一些相关资料。

<!--more-->

参见一段Blog的生成代码
<div markdown="0">
<pre>
{% raw %}
{% for post in site.posts %}
  {% assign flag = false %}
  {% for tag in post.tags %}
    {% if tag == "test" %}
      {% assign flag = true %}
    {% endif %}
  {% endfor %}
  {% if flag == false %}
    {% capture year %}{{ post.date | date: '%Y' }}{% endcapture %}
    {% include archive-single.html %}
  {% endif %}
{% endfor %}
{% endraw %}
</pre>
</div>

## Resources
* [Jekyll官网](https://jekyllrb.com/)
* [Liquid官方文档](https://shopify.github.io/liquid/)
* [Jekyll Liquid Cheatsheet](https://gist.github.com/JJediny/a466eed62cee30ad45e2)