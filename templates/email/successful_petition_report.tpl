{% extends "mail_templated/base.tpl" %}

{% block subject %}
Successful petition report
{% endblock %}

{% block html %}
Hello dear {{ recipient_name }}
<br>
{{ title }} petition owned by {{ owner }} has been reached its goal({{ goal }} signs) and marked as a successful
one. {{ owner }} submitted your email as its recipient.
Full report of this petition signers attached to this email. Please check it out.
<br>
Sincerely
<br>
Plea.org
{% endblock %}
