from django import template

register = template.Library()

@register.filter(name='upper_method')
def upper_method(_str):
    return _str.upper()
    