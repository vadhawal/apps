from mezzanine import template

register = template.Library()

@register.inclusion_tag("generic/includes/reviewrating.html", takes_context=True)
def reviewrating_for(context, obj):
    """
    Provides a generic context variable name for the object that
    ratings are being rendered for, and the rating form.
    """
    context["reviewrating_object"] = context["reviewrating_obj"] = obj
    for f in ("average", "count", "sum"):
        context["overall_" + f] = getattr(obj, "%s_%s" % ("overall", f))
    context["overall_excellentR"] = getattr(obj, "overall_excellentR")
    context["overall_verygoodR"] = getattr(obj, "overall_verygoodR")
    context["overall_averageR"] = getattr(obj, "overall_averageR")
    context["overall_poorR"] = getattr(obj, "overall_poorR")
    context["overall_terribleR"] = getattr(obj, "overall_terribleR")
    for f in ("average", "count", "sum"):
        context["price_" + f] = getattr(obj, "%s_%s" % ("price", f))
    for f in ("average", "count", "sum"):
        context["variety_" + f] = getattr(obj, "%s_%s" % ("variety", f))
    for f in ("average", "count", "sum"):
        context["quality_" + f] = getattr(obj, "%s_%s" % ("quality", f))
    for f in ("average", "count", "sum"):
        context["service_" + f] = getattr(obj, "%s_%s" % ("service", f))
    for f in ("average", "count", "sum"):
        context["exchange_" + f] = getattr(obj, "%s_%s" % ("exchange", f))
    return context
