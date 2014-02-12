from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from mezzanine.blog.models import BlogPost
from mezzanine.generic.models import ThreadedComment

from django.contrib.contenttypes.models import ContentType
from django.template import Node, TemplateSyntaxError, loader, Context, RequestContext
from django.core.urlresolvers import reverse
from userProfile.models import BroadcastDeal, BroadcastWish, Broadcast
from django.http import HttpResponse
from django.utils import simplejson
from follow.models import Follow
from mezzanine.blog.models import BlogPost, BlogCategory, BlogParentCategory
from mezzanine.conf import settings as _settings
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import slugify
from mezzanine.generic.models import Review
from voting.models import Vote
from actstream.models import Action
import datetime

def json_error_response(error_message):
    return HttpResponse(simplejson.dumps(dict(success=False,
                                              error_message=error_message)))

register = template.Library()

# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.simple_tag
def settings_actstream_verb(name):
    verb_dict = getattr(settings, 'ACTSTREAM_VERB_DICT', dict())
    return verb_dict[name]

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

class GetVendorsUrl(template.Node):
    def __init__(self, subcategory, context_var):
        self.subcategory = template.Variable(subcategory)
        self.context_var = context_var

    def render(self, context):
        subcategory_instance = self.subcategory.resolve(context)
        try:
            parent_categories = subcategory_instance.parent_category.all()
            parent_category = parent_categories[0]
            url = reverse('get_vendors', kwargs={'parent_category_slug':parent_category.slug,'sub_category_slug':subcategory_instance.slug})
            context[self.context_var] = url 
        except:
            context[self.context_var] = '#'
            pass
        return  ''

@register.tag
def get_vendors_url(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return GetVendorsUrl(bits[1], bits[3])

class ReviewsByUser(template.Node):
    def __init__(self, user, context_var):
        self.user = template.Variable(user)
        self.context_var = context_var

    def render(self, context):
        user_instance = self.user.resolve(context)
        ctype = ContentType.objects.get_for_model(BlogPost)
        context[self.context_var] = Review.objects.filter(user=user_instance, content_type=ctype)
        return  ''

@register.tag
def get_reviews_by_user(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return ReviewsByUser(bits[1], bits[3])

class WishesByUser(template.Node):
    def __init__(self, user, context_var):
        self.user = template.Variable(user)
        self.context_var = context_var

    def render(self, context):
        user_instance = self.user.resolve(context)
        content_type = ContentType.objects.get_for_model(user_instance).pk
        context[self.context_var] = BroadcastWish.objects.all().filter(content_type=content_type, object_id=user_instance.pk)
        return  ''

@register.tag
def get_wishes_by_user(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return WishesByUser(bits[1], bits[3])

@register.inclusion_tag("wish/render_post.html", takes_context=True)
def render_post(context, post):
    context.update({
        "post": post,
    })
    return context

@register.inclusion_tag("wish/render_wish.html", takes_context=True)
def render_wish(context, wish):
    context.update({
        "wish": wish,
    })
    return context

@register.inclusion_tag("wish/render_deal.html", takes_context=True)
def render_deal(context, deal):
    context.update({
        "deal": deal,
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

class GetShareObjectUrl(template.Node):
    def __init__(self, object, context_var):
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
            content_type = ContentType.objects.get_for_model(object).pk
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] =  reverse('shareObject', kwargs={'content_type_id': content_type, 'object_id': object.pk })
        return ''

def get_share_object_url(parser, token):
    """
    Retrieves the url to get voting/comment/share info and stores them in a context variable which has
    ``voters`` property.

    Example usage::

        {% get_share_object_url object as share_object_url %}
    """

    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return GetShareObjectUrl(bits[1], bits[3])

class GetDeleteObjectUrl(template.Node):
    def __init__(self, object, context_var):
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
            content_type = ContentType.objects.get_for_model(object).pk
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] =  reverse('deleteObject', kwargs={'content_type_id': content_type, 'object_id': object.pk })
        return ''

def get_delete_object_url(parser, token):
    """
    Retrieves the url to get voting/comment/share info and stores them in a context variable which has
    ``voters`` property.

    Example usage::

        {% get_delete_object_url object as delete_object_url %}
    """

    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return GetDeleteObjectUrl(bits[1], bits[3])

class GetFollowObjectUrl(template.Node):
    def __init__(self, object, context_var):
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
            content_type = ContentType.objects.get_for_model(object).pk
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] =  reverse('followObject', kwargs={'content_type_id': content_type, 'object_id': object.pk })
        return ''

def get_follow_object_url(parser, token):
    """
    Retrieves the url to get voting/comment/share info and stores them in a context variable which has
    ``voters`` property.

    Example usage::

        {% get_follow_object_url object as share_object_url %}
    """

    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return GetFollowObjectUrl(bits[1], bits[3])

class GetUnfollowObjectUrl(template.Node):
    def __init__(self, object, context_var):
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
            content_type = ContentType.objects.get_for_model(object).pk
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] =  reverse('unfollowObject', kwargs={'content_type_id': content_type, 'object_id': object.pk })
        return ''

def get_unfollow_object_url(parser, token):
    """
    Retrieves the url to get voting/comment/share info and stores them in a context variable which has
    ``voters`` property.

    Example usage::

        {% get_unfollow_object_url object as share_object_url %}
    """

    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return GetUnfollowObjectUrl(bits[1], bits[3])

class GetRelDataUrl(template.Node):
    def __init__(self, object, context_var):
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
            content_type = ContentType.objects.get_for_model(object).pk
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] = reverse('get_reldata', kwargs={'content_type_id': content_type, 'object_id': object.pk })
        return ''  

def get_reldata_url(parser, token):
    """
    Retrieves the url to get voting/comment/share info and stores them in a context variable which has
    ``voters`` property.

    Example usage::

        {% get_reldata_url object as reldata_url %}
    """

    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return GetRelDataUrl(bits[1], bits[3])

class GetDealListUrl(AsNode):
    def render_result(self, context):
        object_instance = self.args[0].resolve(context)
        sIndex = self.args[1].resolve(context)
        lIndex = self.args[2].resolve(context)
        content_type = ContentType.objects.get_for_model(object_instance).pk
        
        return reverse('get_deallist', kwargs={
            'content_type_id': content_type, 'object_id': object_instance.pk, 'sIndex':sIndex, 'lIndex':lIndex})

def get_deallist_url(parser, token):
    bits = token.split_contents()
    if len(bits) != 6:
        raise TemplateSyntaxError("Accepted format "
                                  "{% get_deallist_url [object_instance] sIndex lIndex as wishlisturl %}")
    else:
        return GetDealListUrl.handle_token(parser, token)

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

class ShareDealUrl(Node):
    def __init__(self, deal):
        self.deal = template.Variable(deal)

    def render(self, context):
        deal_instance = self.deal.resolve(context)
        return reverse('shareDeal', kwargs={
            'deal_id':deal_instance.pk})

def share_deal_url(parser, token):
    bits = token.split_contents()
    return ShareDealUrl(*bits[1:])

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
    today = datetime.datetime.today().date()

    deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype, expiry_date__gte=today)
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
register.tag(share_deal_url)
register.tag(get_wishlist_url)
register.tag(get_share_object_url)
register.tag(get_delete_object_url)
register.tag(get_follow_object_url)
register.tag(get_unfollow_object_url)
register.tag(get_reldata_url)
register.tag(get_deallist_url)

@register.filter
def is_following_post(user, obj):
    return Follow.objects.is_following(user, obj)

@register.simple_tag
def get_full_name(user):
	if user:
		return (user.first_name + " " + user.last_name).title()
	return ""

@register.simple_tag
def get_first_name(user):
    if user:
        return (user.first_name).title()
    return ""

@register.simple_tag
def get_last_name(user):
    if user:
        return (user.last_name).title()
    return ""

@register.simple_tag(takes_context=True)
def render_reviews_for_user(context, user, latest=settings.MIN_REVIEWS_FOR_USER, orientation='horizontal'):
    template_name = 'generic/user_reviews.html'
    search_param = ''
    if orientation == 'vertical':
        template_name = 'generic/user_reviews_v.html'
        search_param = '?v=1'

    template = loader.get_template(template_name)
    ctype = ContentType.objects.get_for_model(BlogPost)
    reviews_queryset = Review.objects.filter(user=user, content_type=ctype)
    reviews_list = reviews_queryset[:latest]

    data_href = reverse('getUserReviews', kwargs={'user_id':user.id,
                                                  'sIndex':0,
                                                  'lIndex':latest})
    data_chunk = 5

    return template.render(RequestContext(context['request'], {
        'reviews' : reviews_list,
        'data_href' : data_href + search_param,
        'data_chunk': data_chunk,
        'profile_user': user
    }))


@register.simple_tag(takes_context=True)
def render_deals_for_categories(context, parent_category, sub_category, latest=settings.DEALS_NUM_LATEST, orientation='horizontal'):
        template_name = 'wish/deallist.html'
        search_param = ''
        if orientation == 'vertical':
            template_name = 'wish/deallist_v.html'
            search_param = '?v=1'

        template = loader.get_template(template_name)

        ctype = ContentType.objects.get_for_model(BlogPost)
        deals = []
        blog_parentcategory = None
        deals_queryset = None
        today = datetime.datetime.today().date()

        blog_parentcategory_slug = parent_category
        if blog_parentcategory_slug.lower() != "all" and BlogParentCategory.objects.all().exists():
            blog_parentcategory = get_object_or_404(BlogParentCategory, slug=slugify(blog_parentcategory_slug))

        blog_subcategory = None
        blog_subcategory_slug = sub_category
        if blog_subcategory_slug.lower() != "all" and BlogCategory.objects.all().exists():
            blog_subcategory = get_object_or_404(BlogCategory, slug=slugify(blog_subcategory_slug))

        if blog_parentcategory_slug.lower() == "all" and blog_subcategory_slug.lower() == "all":
            deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype, expiry_date__gte=today)
        elif blog_parentcategory_slug.lower() != "all" and blog_subcategory_slug.lower() == "all":
            if blog_parentcategory:
                blog_subcategories = BlogCategory.objects.all().filter(parent_category=blog_parentcategory).values_list('id', flat=True)
                deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype, blog_category__id__in=blog_subcategories, expiry_date__gte=today).distinct()
        else:
            if blog_subcategory and blog_parentcategory:
                deals_queryset = BroadcastDeal.objects.all().filter(blog_category=blog_subcategory, expiry_date__gte=today)

        model_type = ContentType.objects.get_for_model(BroadcastDeal)
        table_name = Broadcast._meta.db_table

        deals_queryset = deals_queryset.extra(select={
            'score': 'SELECT COALESCE(SUM(vote),0) FROM %s WHERE content_type_id=%d AND object_id=%s.id' % (Vote._meta.db_table, int(model_type.id), table_name),
            'sharecount': "SELECT COALESCE(COUNT(*),0) FROM %s WHERE verb='%s' AND target_content_type_id=%d AND target_object_id::int=%s.id" % (Action._meta.db_table, settings.SHARE_VERB, int(model_type.id), table_name)
        }).order_by('-score', '-sharecount', '-timestamp',)

        deals_list = deals_queryset[:latest]

        data_href = reverse('getTrendingDeals', kwargs={'parent_category':slugify(parent_category),
                                                        'sub_category':slugify(sub_category),
                                                        'sIndex':0,
                                                        'lIndex':latest})
        data_chunk = 5

        return template.render(RequestContext(context['request'], {
            'deal_list' : deals_list,
            'data_href' : data_href + search_param,
            'data_chunk': data_chunk
        }))

@register.simple_tag(takes_context=True)
def render_stores_for_categories(context, parent_category, sub_category, latest=settings.STORES_NUM_LATEST, orientation='horizontal'):
        template_name = 'generic/vendor_list.html'
        search_param = ''
        if orientation == 'vertical':
            template_name = 'generic/vendor_list_v.html'
            search_param = '?v=1'

        template = loader.get_template(template_name)

        blog_parentcategory = None
        result = None
        table_name = BlogPost._meta.db_table

        blog_parentcategory_slug = parent_category
        if blog_parentcategory_slug.lower() != "all" and BlogParentCategory.objects.all().exists():
            blog_parentcategory = get_object_or_404(BlogParentCategory, slug=slugify(blog_parentcategory_slug))

        blog_subcategory = None
        blog_subcategory_slug = sub_category
        if blog_subcategory_slug.lower() != "all" and BlogCategory.objects.all().exists():
            blog_subcategory = get_object_or_404(BlogCategory, slug=slugify(blog_subcategory_slug))

        if blog_parentcategory_slug.lower() == "all" and blog_subcategory_slug.lower() == "all":
            result = BlogPost.objects.published()

        elif blog_parentcategory_slug.lower() != "all" and blog_subcategory_slug.lower() == "all":
            if blog_parentcategory:
                blog_subcategories = BlogCategory.objects.all().filter(parent_category=blog_parentcategory).values_list('id', flat=True)
                result = BlogPost.objects.published().filter(categories__id__in=blog_subcategories)
        else:
            if blog_subcategory and blog_parentcategory:
                result = BlogPost.objects.published().filter(categories=blog_subcategory)
        
        result = result.extra(select={'fieldsum':'price_average + website_ex_average + quality_average + service_average',
                                      'followers': 'SELECT COUNT(*) FROM %s WHERE target_blogpost_id=%s.id' % (Follow._meta.db_table, table_name)}, 
                                      order_by=('-overall_average', '-fieldsum', '-comments_count', '-followers',)).distinct()[:latest]

        data_href = reverse('getTrendingStores', kwargs={'parent_category':slugify(parent_category),
                                                        'sub_category':slugify(sub_category),
                                                        'sIndex':0,
                                                        'lIndex':latest})
        data_chunk = 5

        return template.render(RequestContext(context['request'], {
            'vendors' : result,
            'data_href' : data_href + search_param,
            'data_chunk': data_chunk
        }))

@register.simple_tag(takes_context=True)
def render_reviews_for_categories(context, parent_category, sub_category, latest=_settings.REVIEWS_NUM_LATEST, orientation='horizontal'):
        template_name = 'generic/top_reviews.html'
        search_param = ''
        if orientation == 'vertical':
            template_name = 'generic/top_reviews_v.html'
            search_param = '?v=1'

        template = loader.get_template(template_name)

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
                blog_subcategories = BlogCategory.objects.all().filter(parent_category=blog_parentcategory).values_list('id', flat=True)
                reviews = Review.objects.all().filter(bought_category__id__in=blog_subcategories).order_by('-submit_date')[:latest]
        else:
            if blog_subcategory and blog_parentcategory:
                reviews = Review.objects.all().filter(bought_category=blog_subcategory).order_by('-submit_date')[:latest]
            else:
                """
                    raise 404 error, in case categories are not present.
                """
                raise Http404()

        data_href = reverse('getTrendingReviews', kwargs={'parent_category':slugify(parent_category),
                                                          'sub_category':slugify(sub_category),
                                                          'sIndex':0,
                                                          'lIndex':latest})
        data_chunk = 5

        return template.render(RequestContext(context['request'], {
            'comments': reviews,
            'data_href' : data_href + search_param,
            'data_chunk': data_chunk
        }))

@register.simple_tag(takes_context=True)
def render_deals_for_stores(context, store_id, sub_category, latest=settings.DEALS_NUM_LATEST, orientation='horizontal'):
        template_name = 'wish/deallist.html'
        search_param = ''
        if orientation == 'vertical':
            template_name = 'wish/deallist_v.html'
            search_param = '?v=1'

        template = loader.get_template(template_name)
        try:
            blog_post = BlogPost.objects.get(id=store_id)
        except:
            return ''
        
        ctype = ContentType.objects.get_for_model(BlogPost)
        deals_queryset = None
        blog_subcategory = None
        blog_subcategory_slug = sub_category
        today = datetime.datetime.today().date()
        if blog_subcategory_slug.lower() != "all" and blog_subcategory_slug.lower() != '':
            try:
                blog_subcategory = BlogCategory.objects.get(slug=slugify(blog_subcategory_slug))
                deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype, object_id=store_id, blog_category=blog_subcategory, expiry_date__gte=today)
            except:
                blog_subcategory = None
                pass

        elif blog_subcategory_slug.lower() == "all" or blog_subcategory_slug.lower() == '':
            deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype, object_id=store_id, expiry_date__gte=today)
        else:
            return ''

        model_type = ContentType.objects.get_for_model(BroadcastDeal)
        table_name = Broadcast._meta.db_table

        deals_queryset = deals_queryset.extra(select={
            'score': 'SELECT COALESCE(SUM(vote),0) FROM %s WHERE content_type_id=%d AND object_id=%s.id' % (Vote._meta.db_table, int(model_type.id), table_name),
            'sharecount': "SELECT COALESCE(COUNT(*),0) FROM %s WHERE verb='%s' AND target_content_type_id=%d AND target_object_id::int=%s.id" % (Action._meta.db_table, settings.SHARE_VERB, int(model_type.id), table_name)
        }).order_by('-score', '-sharecount', '-timestamp',)

        deals_list = deals_queryset[:latest]
        data_href = reverse('get_filtered_deallist', kwargs={'store_id':store_id,
                                                             'sub_category':sub_category,
                                                             'sIndex':0,
                                                             'lIndex':latest})
        data_chunk = 5

        return template.render(RequestContext(context['request'], {
            'deal_list': deals_list,
            'data_href' : data_href + search_param,
            'data_chunk': data_chunk,
            'blog_post': blog_post
        }))

@register.simple_tag(takes_context=True)
def render_related_stores(context, store_id, sub_category, latest=settings.STORES_NUM_LATEST, orientation='horizontal'):
    template_name = 'generic/vendor_list.html'
    search_param = ''

    if orientation == 'vertical':
        template_name = 'generic/vendor_list_v.html'
        search_param = '?v=1'

    template = loader.get_template(template_name)

    if sub_category.lower() != "all" and sub_category.lower() != '':
        try:
            blog_subcategory = BlogCategory.objects.get(slug=slugify(sub_category))
            blogPostQueryset = BlogPost.objects.published().filter(categories=blog_subcategory).exclude(id=store_id).extra(select={'fieldsum':'price_average + website_ex_average + quality_average + service_average'},order_by=('-overall_average', '-fieldsum', )).distinct()[:latest]
        except:
            blogPostQueryset = None
            pass

    elif sub_category.lower() == "all" or sub_category.lower() == '':
        try:
            blog_post = BlogPost.objects.get(id=store_id)
            categories = blog_post.categories.all().values_list('id', flat=True)
            blogPostQueryset = BlogPost.objects.published().filter(categories__id__in=categories).exclude(id=store_id).extra(select={'fieldsum':'price_average + website_ex_average + quality_average + service_average'},order_by=('-overall_average', '-fieldsum',)).distinct()[:latest]
        except:
            blogPostQueryset = None
            pass

    data_href = reverse('get_related_stores', kwargs={'store_id':store_id,
                                                      'sub_category':sub_category,
                                                      'sIndex':0,
                                                      'lIndex':latest})
    data_chunk = 5

    return template.render(RequestContext(context['request'], {
        'vendors': blogPostQueryset,
        'data_href' : data_href + search_param,
        'data_chunk': data_chunk
    }))


 



