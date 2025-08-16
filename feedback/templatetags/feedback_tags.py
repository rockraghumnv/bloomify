from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Template filter to look up a value in a dictionary by key
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, None)
    return None

@register.filter
def yesno(value, arg):
    """
    Enhanced yesno filter for more conditions
    """
    try:
        yes, no, maybe, other = arg.split(',')
    except ValueError:
        return value
    
    if value == 'excellent':
        return yes
    elif value == 'advanced':
        return no
    elif value == 'intermediate':
        return maybe
    else:
        return other
