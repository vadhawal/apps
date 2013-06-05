from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from mezzanine.blog.models import BlogPost
from mezzanine.generic.models import ThreadedComment

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


