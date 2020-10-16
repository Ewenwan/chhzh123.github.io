---
layout: post
title: Jekyll/Liquid使用指南
tag: [configuration]
---

本文记录部署Jekyll可能用到的一些指令、第三方包及Liquid的一些相关资料。

<!--more-->

# Liquid
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

用`%raw% %endraw%`可以实现liquid代码的escape，前后要加大括号。

## Resources
* [Jekyll官网](https://jekyllrb.com/)
* [Liquid官方文档](https://shopify.github.io/liquid/)
* [Liquid官方Wiki](https://github.com/Shopify/liquid/wiki)
* [Jekyll Liquid Cheatsheet](https://gist.github.com/JJediny/a466eed62cee30ad45e2)

# Valine
[Valine](https://valine.js.org/)是基于[LeanCloud](https://leancloud.cn/)非常轻量级的评论系统
* [Valine-Admin](https://github.com/DesertsP/Valine-Admin)：用来管理评论数据
* [Valine Admin 配置手册](https://deserts.io/valine-admin-document/)
* [Valine-1.4.4新版本尝鲜+个性制定](https://cungudafa.gitee.io/post/8202.html)

# 网页样式
* [Bootstrap Alerts](https://getbootstrap.com/docs/4.0/components/alerts/)