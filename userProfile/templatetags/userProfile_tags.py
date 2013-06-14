from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from mezzanine.blog.models import BlogPost
from mezzanine.generic.models import ThreadedComment

from django.contrib.contenttypes.models import ContentType
from django.template import Node, TemplateSyntaxError
from django.core.urlresolvers import reverse

register = template.Library()

# settings value
@register.simple_tag
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

register.tag(get_wishlist_url)


