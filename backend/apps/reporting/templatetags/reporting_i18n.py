from django import template
from apps.reporting.itaukei import localize_text
register=template.Library()
@register.filter
def itaukei(value):
    return localize_text(value)
