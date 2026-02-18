from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Access dictionary item by key in template."""
    return dictionary.get(key)
