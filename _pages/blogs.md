---
layout: archive
permalink: /blogs/
title: "Blog Posts"
author_profile: true
---

{% include base_path %}
{% capture written_year %}'None'{% endcapture %}
{% for post in site.posts %}
  {% assign flag = false %}
  {% for tag in post.tags %}
    {% if tag == "configuration" or tag == "abroad" %}
      {% assign flag = true %}
    {% endif %}
  {% endfor %}
  {% if flag == false %}
    {% capture year %}{{ post.date | date: '%Y' }}{% endcapture %}
    {% include archive-single.html %}
  {% endif %}
{% endfor %}
