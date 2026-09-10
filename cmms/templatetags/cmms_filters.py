"""
Custom template filters for cmms app
"""

from django import template

register = template.Library()


@register.filter(name="get_item")
def get_item(dictionary, key):
    """
    Template filter to safely get a value from a dictionary or object.

    Usage in template:
        {{ item.meta|get_item:"floor" }}
        {{ some_dict|get_item:field.name }}

    Returns empty string if key not found or dictionary is None.
    """
    if dictionary is None:
        return ""

    # Handle dict-like objects
    if hasattr(dictionary, "get"):
        return dictionary.get(key, "")

    # Handle objects with attributes
    if hasattr(dictionary, key):
        return getattr(dictionary, key, "")

    return ""


@register.filter(name="get_item_default")
def get_item_default(dictionary, key_default):
    """
    Template filter to get a value from dictionary with a custom default.

    Usage:
        {{ item.meta|get_item_default:"floor,N/A" }}

    Args:
        dictionary: dict or dict-like object
        key_default: string in format "key,default_value"
    """
    if "," not in key_default:
        # fallback to get_item if no default provided
        return get_item(dictionary, key_default)

    key, default = key_default.split(",", 1)
    key = key.strip()
    default = default.strip()

    if dictionary is None:
        return default

    if hasattr(dictionary, "get"):
        value = dictionary.get(key)
        return value if value is not None else default

    if hasattr(dictionary, key):
        value = getattr(dictionary, key, None)
        return value if value is not None else default

    return default


@register.filter(name="remove_required")
def remove_required(field_html):
    """
    Remove the 'required' attribute from form field HTML.
    
    Usage:
        {{ form.field|remove_required }}
    """
    import re
    # Remove required attribute from input tags
    field_html = re.sub(r'\s+required(?:="[^"]*")?', '', str(field_html))
    field_html = re.sub(r'\s+required(?=\s|>)', '', field_html)
    return field_html
