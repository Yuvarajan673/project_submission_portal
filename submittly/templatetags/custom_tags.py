from django import template

register = template.Library()


# Dictionary Methods
@register.filter
def get_attr(value, arg):
    return getattr(value, arg)

@register.filter
def get_items(dictionary,key):
    return dictionary.get(key)

@register.filter
def get_keys(dictionary):
    return dictionary.keys()


# List Methods
@register.filter
def index(lst,i):
    return lst[i]




# To Get Current Year
@register.simple_tag
def cur_year():
    from datetime import date
    return date.today().year




# To Get Current Month
@register.simple_tag
def cur_month():
    from datetime import date
    return date.today().month