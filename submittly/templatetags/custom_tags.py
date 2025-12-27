from datetime import date
from django import template

register = template.Library()

@register.filter
def get_attr(value, arg):
    return getattr(value, arg)

@register.filter
def get_items(dictionary,key):
    return dictionary.get(key)

@register.filter
def index(lst,i):
    return lst[i]

@register.filter
def cur_year(val):
    return date.today().year


@register.filter
def cur_month(val):
    return date.today().month