---
layout: archive
title: Catalog
---

<section class="catalog">

{% for tag in site.tags %}
	<h3>{{ tag[0] }}</h3>
	{% for post in tag[1] %}
	<li><a href="{{ post.url }}"><span>{{ post.date | date: "%B %-d, %Y" }}</span> - {{ post.title }}</a></li>
	{% endfor %}
{% endfor %}

</section>