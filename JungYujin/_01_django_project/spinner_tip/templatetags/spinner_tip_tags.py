from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def spinner_loader_box(element_id="spinner-tip-box"):
    """
    스피너 표시 박스 컴포넌트 삽입:
    {% spinner_loader_box "myLoader" %}
    """
    return render_to_string("spinner_tip/loader_box.html", {"id": element_id})
