from django import template

register = template.Library()


# @register.filter
# def get_item(dictionary, key):
#     return dictionary.get(key, [])


@register.filter
def dict_key(dictionary, key):
    """Returns the value from a dictionary safely"""
    return dictionary.get(key, None)
