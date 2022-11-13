{% extends "mail_templated/base.tpl" %}

{% block subject %}
Account activation
{% endblock %}

{% block html %}
Hello {{full_name}}
<br>
Please activate your account by link below:
http://127.0.0.1:8000/accounts/activation/confirm/{{token}}
{% endblock %}
