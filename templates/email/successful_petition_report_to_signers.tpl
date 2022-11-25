{% extends "mail_templated/base.tpl" %}

{% block subject %}
Successful petition report
{% endblock %}

{% block html %}
Hello dear signer
<br>
{{ title }} petition owned by {{ owner }} has been reached its goal({{ goal }} signs) and marked as a successful
one. Congratulations.
<br>
Sincerely
<br>
Plea.org
{% endblock %}
