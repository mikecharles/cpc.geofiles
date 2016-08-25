---
layout: default
---

<h1>API Documentation</h1>

<ul>
    {% for page in site.pages %}
        {% if page.type == 'apidoc' %}
            <li>
                <a href="{{site.baseurl}}{{page.url}}">{{page.title}}</a>
            </li>
        {% endif %}
    {% endfor %}
</ul>
