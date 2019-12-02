---
layout: archive
permalink: /blogs/
title: "Blog Posts"
author_profile: true
---

{% include base_path %}
{% capture written_year %}'None'{% endcapture %}
{% for post in site.posts %}
  {% capture year %}{{ post.date | date: '%Y' }}{% endcapture %}
  {% include archive-single.html %}
{% endfor %}
