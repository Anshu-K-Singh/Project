from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def dividedby(value, arg):
    try:
        return value / arg
    except (ValueError, ZeroDivisionError):
        return 0
