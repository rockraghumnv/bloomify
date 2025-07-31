from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter
def dict_get(d, key):
    if d and key in d:
        return d[key]
    return ''
