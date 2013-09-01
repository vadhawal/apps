from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from mezzanine.blog.models import BlogPost
from mezzanine.generic.models import ThreadedComment

from django.contrib.contenttypes.models import ContentType
from django.template import Node, TemplateSyntaxError
from django.core.urlresolvers import reverse
from userProfile.models import UserWishRadio
from django.http import HttpResponse
from django.utils import simplejson
from follow.models import Follow
from mezzanine.blog.models import BlogPost, BlogCategory, BlogParentCategory
from mezzanine.conf import settings as _settings
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import slugify
from mezzanine.generic.models import Review

def json_error_response(error_message):
    return HttpResponse(simplejson.dumps(dict(success=False,
                                              error_message=error_message)))

register = template.Library()

# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.filter
def settings_value(name):
    return getattr(settings, name, "")

def do_get_owned_blog(parser, token):
    """
    Retrieves the blog owned by any user

    Example usage::
        {% get_owned_blog user as blog %}
    """

    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return BlogForUserNode(bits[1], bits[3])

class BlogForUserNode(template.Node):
    def __init__(self, user, context_var):
        self.user = user
        self.context_var = context_var

    def render(self, context):
        try:
			user = template.resolve_variable(self.user, context)
			blog_posts = BlogPost.objects.published(for_user=user).select_related().filter(user=user)
			"""
				For now considering blog_posts as a list.
				Going forward we will restrict the #blogposts to be one per user therefore fetching the first element only is sufficient.
				Remove this loop then.
			"""
			if blog_posts:
				blog_post = blog_posts[0]
				context[self.context_var] = blog_post
			else:
				context[self.context_var] = ''
        except template.VariableDoesNotExist:
            return ''
        
        return ''  

register.tag('get_owned_blog', do_get_owned_blog)

@register.filter
def get_class_name(value):
    return value.__class__.__name__

class ReviewCount(template.Node):
    def __init__(self, user, context_var):
        self.user = template.Variable(user)
        self.context_var = context_var

    def render(self, context):
        user_instance = self.user.resolve(context)
        ctype = ContentType.objects.get_for_model(BlogPost)
        context[self.context_var] = ThreadedComment.objects.filter(user=user_instance, content_type=ctype).count()
        return  ''

@register.tag
def get_review_count(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return ReviewCount(bits[1], bits[3])

class ReviewsByUser(template.Node):
    def __init__(self, user, context_var):
        self.user = template.Variable(user)
        self.context_var = context_var

    def render(self, context):
        user_instance = self.user.resolve(context)
        ctype = ContentType.objects.get_for_model(BlogPost)
        context[self.context_var] = ThreadedComment.objects.filter(user=user_instance, content_type=ctype)
        return  ''

@register.tag
def get_reviews_by_user(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return ReviewsByUser(bits[1], bits[3])

@register.inclusion_tag("wish/render_wish.html", takes_context=True)
def render_wish(context, wish):
    context.update({
        "wish": wish,
    })
    return context

class AsNode(Node):
    """
    Base template Node class for template tags that takes a predefined number
    of arguments, ending in an optional 'as var' section.
    """
    args_count = 3

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse and return a Node.
        """
        bits = token.split_contents()
        args_count = len(bits) - 1
        if args_count >= 2 and bits[-2] == 'as':
            as_var = bits[-1]
            args_count -= 2
        else:
            as_var = None
        if args_count != cls.args_count:
            arg_list = ' '.join(['[arg]' * cls.args_count])
            raise TemplateSyntaxError("Accepted formats {%% %(tagname)s "
                "%(args)s %%} or {%% %(tagname)s %(args)s as [var] %%}" %
                {'tagname': bits[0], 'args': arg_list})
        args = [parser.compile_filter(token) for token in
            bits[1:args_count + 1]]
        return cls(args, varname=as_var)

    def __init__(self, args, varname=None):
        self.args = args
        self.varname = varname

    def render(self, context):
        result = self.render_result(context)
        if self.varname is not None:
            context[self.varname] = result
            return ''
        return result

    def render_result(self, context):
        raise NotImplementedError("Must be implemented by a subclass")

class GetWishListUrl(AsNode):
    def render_result(self, context):
        object_instance = self.args[0].resolve(context)
        sIndex = self.args[1].resolve(context)
        lIndex = self.args[2].resolve(context)
        content_type = ContentType.objects.get_for_model(object_instance).pk
        
        return reverse('get_wishlist', kwargs={
            'content_type_id': content_type, 'object_id': object_instance.pk, 'sIndex':sIndex, 'lIndex':lIndex})

def get_wishlist_url(parser, token):
    bits = token.split_contents()
    if len(bits) != 6:
        raise TemplateSyntaxError("Accepted format "
                                  "{% get_wishlist_url [object_instance] sIndex lIndex as wishlisturl %}")
    else:
        return GetWishListUrl.handle_token(parser, token)

class ShareWishUrl(Node):
    def __init__(self, wish):
        self.wish = template.Variable(wish)

    def render(self, context):
        wish_instance = self.wish.resolve(context)
        return reverse('shareWish', kwargs={
            'wish_id':wish_instance.pk})

def share_wish_url(parser, token):
    bits = token.split_contents()
    return ShareWishUrl(*bits[1:])

@register.inclusion_tag("wish/wishlist.html",
    takes_context=True)
def recent_deals(context):
    """
    Dashboard widget for displaying recent deals.
    """
    import operator
    deals = []
    latest = context["settings"].COMMENTS_NUM_LATEST
    ctype = ContentType.objects.get_for_model(BlogPost)
    deals_queryset = UserWishRadio.objects.all().filter(content_type=ctype)
    deals_queryset = sorted(deals_queryset, key=operator.attrgetter('timestamp'), reverse=True)
    for deal in deals_queryset:
        deals.append(deal) 
    context["wish_list"] = deals
    context["sIndex"] = 0
    return context

@register.tag
def get_wish_owner(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return DealsOwner(bits[1], bits[3])

class DealsOwner(template.Node):
    def __init__(self, wish, context_var):
        self.wish = template.Variable(wish)
        self.context_var = context_var

    def render(self, context):
        wish_instance = self.wish.resolve(context)
        obj = wish_instance.content_type.get_object_for_this_type(pk=wish_instance.object_id)
        context[self.context_var] = obj
        return ''

register.tag(share_wish_url)
register.tag(get_wishlist_url)

@register.filter
def is_following_post(user, obj):
    return Follow.objects.is_following(user, obj)

@register.simple_tag
def get_full_name(user):
	if user:
		return (user.first_name + " " + user.last_name).title()
	return ""

@register.inclusion_tag("generic/wishlist.html", takes_context=True)
def render_deals_for_categories(context, parent_category, sub_category, latest=settings.DEALS_NUM_LATEST):
        ctype = ContentType.objects.get_for_model(BlogPost)
        deals = []
        blog_parentcategory = None
        deals_queryset = None
        
        blog_parentcategory_slug = parent_category
        if blog_parentcategory_slug.lower() != "all" and BlogParentCategory.objects.all().exists():
            blog_parentcategory = get_object_or_404(BlogParentCategory, slug=slugify(blog_parentcategory_slug))

        blog_subcategory = None
        blog_subcategory_slug = sub_category
        if blog_subcategory_slug.lower() != "all" and BlogCategory.objects.all().exists():
            blog_subcategory = get_object_or_404(BlogCategory, slug=slugify(blog_subcategory_slug))

        if blog_parentcategory_slug.lower() == "all" and blog_subcategory_slug.lower() == "all":
            deals_queryset = UserWishRadio.objects.all().filter(content_type=ctype).order_by('-timestamp')[:latest]
        elif blog_parentcategory_slug.lower() != "all" and blog_subcategory_slug.lower() == "all":
            if blog_parentcategory:
                blog_subcategories = list(BlogCategory.objects.all().filter(parent_category=blog_parentcategory))
                deals_queryset = UserWishRadio.objects.all().filter(content_type=ctype, blog_category__in=blog_subcategories).order_by('-timestamp').distinct()[:latest]
        else:
            if blog_subcategory and blog_parentcategory:
                deals_queryset = UserWishRadio.objects.all().filter(blog_category=blog_subcategory).order_by('-timestamp')[:latest]

        context.update({
            'wish_list': deals_queryset,
            'sIndex':0
        })
        return context

@register.inclusion_tag("generic/vendor_list.html", takes_context=True)
def render_stores_for_categories(context, parent_category, sub_category, latest=settings.STORES_NUM_LATEST):
        blog_parentcategory = None
        result = None

        blog_parentcategory_slug = parent_category
        if blog_parentcategory_slug.lower() != "all" and BlogParentCategory.objects.all().exists():
            blog_parentcategory = get_object_or_404(BlogParentCategory, slug=slugify(blog_parentcategory_slug))

        blog_subcategory = None
        blog_subcategory_slug = sub_category
        if blog_subcategory_slug.lower() != "all" and BlogCategory.objects.all().exists():
            blog_subcategory = get_object_or_404(BlogCategory, slug=slugify(blog_subcategory_slug))

        if blog_parentcategory_slug.lower() == "all" and blog_subcategory_slug.lower() == "all":
            result = BlogPost.objects.published().extra(select={'fieldsum':'price_average + variety_average + quality_average + service_average + exchange_average + overall_average'},order_by=('-fieldsum',))[:latest]
        elif blog_parentcategory_slug.lower() != "all" and blog_subcategory_slug.lower() == "all":
            if blog_parentcategory:
                blog_subcategories = list(BlogCategory.objects.all().filter(parent_category=blog_parentcategory))
                result = BlogPost.objects.published().filter(categories__in=blog_subcategories).extra(select={'fieldsum':'price_average + variety_average + quality_average + service_average + exchange_average + overall_average'},order_by=('-fieldsum',)).distinct()[:latest]
        else:
            if blog_subcategory and blog_parentcategory:
                result = BlogPost.objects.published().filter(categories=blog_subcategory).extra(select={'fieldsum':'price_average + variety_average + quality_average + service_average + exchange_average + overall_average'},order_by=('-fieldsum',))[:latest]

        context.update({
            'vendors': result,
            'sIndex':0
        })
        return context

@register.inclusion_tag("generic/top_reviews.html", takes_context=True)
def render_reviews_for_categories(context, parent_category, sub_category, latest=_settings.REVIEWS_NUM_LATEST):
        blog_parentcategory = None
        
        blog_parentcategory_slug = parent_category
        if blog_parentcategory_slug.lower() != "all" and BlogParentCategory.objects.all().exists():
            blog_parentcategory = get_object_or_404(BlogParentCategory, slug=slugify(blog_parentcategory_slug))

        blog_subcategory = None
        blog_subcategory_slug = sub_category
        if blog_subcategory_slug.lower() != "all" and BlogCategory.objects.all().exists():
            blog_subcategory = get_object_or_404(BlogCategory, slug=slugify(blog_subcategory_slug))

        if blog_parentcategory_slug.lower() == "all" and blog_subcategory_slug.lower() == "all":
            reviews = Review.objects.all().order_by('-submit_date')[:latest]
        elif blog_parentcategory_slug.lower() != "all" and blog_subcategory_slug.lower() == "all":
            if blog_parentcategory:
                blog_subcategories = list(BlogCategory.objects.all().filter(parent_category=blog_parentcategory))
                reviews = Review.objects.all().filter(bought_category__in=blog_subcategories).order_by('-submit_date')[:latest]
        else:
            if blog_subcategory and blog_parentcategory:
                reviews = Review.objects.all().filter(bought_category=blog_subcategory).order_by('-submit_date')[:latest]
            else:
                """
                    raise 404 error, in case categories are not present.
                """
                raise Http404()
        context.update({
            'comments': reviews,
        })
        return context	




