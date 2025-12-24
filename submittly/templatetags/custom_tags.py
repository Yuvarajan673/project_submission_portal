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