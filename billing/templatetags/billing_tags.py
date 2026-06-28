from django import template

register = template.Library()


@register.filter
def feature_label(labels, key):
    if isinstance(labels, dict):
        return labels.get(key, key)
    return key
