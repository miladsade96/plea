{% extends "mail_templated/base.tpl" %}

{% block subject %}
Signature verification
{% endblock %}

{% block html %}
Hello {{full_name}}
<br>
Please verify your email in order to submit your signature on petition.
http://127.0.0.1:8000/signature/verification/confirm/{{token}}
{% endblock %}
