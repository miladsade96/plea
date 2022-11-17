{% extends "mail_templated/base.tpl" %}

{% block subject %}
Password reset
{% endblock %}

{% block html %}
Hello {{full_name}}
<br>
Please click on link below in order to reset your account password:
http://127.0.0.1:8000/accounts/reset-password/confirm/{{token}}
{% endblock %}
