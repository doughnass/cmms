from django import template

register = template.Library()

@register.filter
def get_item(mapping, key):
    """Return mapping[key] or None. Safe for template use when mapping may be a dict-like.

    Usage in template: {{ mydict|get_item:key }}
    """
    try:
        if mapping is None:
            return None
        # mapping may be a dict or an object with get
        return mapping.get(key) if hasattr(mapping, 'get') else mapping[key]
    except Exception:
        return None
