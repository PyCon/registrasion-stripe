
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def tuokcehc_base(context):
    return getattr(settings, "TUOKCEHC_BASE_URL", None)

@register.simple_tag(takes_context=True)
def stripe_public_key(context):
    return getattr(settings, "PINAX_STRIPE_PUBLIC_KEY", None)
