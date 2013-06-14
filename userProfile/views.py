from django.shortcuts import render_to_response
from django.template import RequestContext
from userProfile.models import BroadcastForm, Broadcast, UserWishRadio
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from actstream import action
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from mezzanine.blog.models import BlogPost, BlogCategory

from userProfile.models import UserWishRadio

def close_login_popup(request):
    return render_to_response('close_popup.html', {}, RequestContext(request))

def broadcast(request):
	if request.method == "POST":
		if _(request.POST['actor']) == "user":
			broadcast = Broadcast.objects.create_broadcast_object( _(request.POST['message']), request.user)
			action.send(request.user, verb='said:', action_object=broadcast)
		elif _(request.POST['actor']) == "vendor":
			
			blog_posts = BlogPost.objects.published(
                                     for_user=request.user).select_related().filter(user=request.user)
			"""
				For now considering blog_posts as a list.
				Going forward we will restrict the #blogposts to be one per user therefore fetching the first element only is sufficient.
				Remove this loop then.
			"""
			if blog_posts:
				blog_post = blog_posts[0]
				broadcast = Broadcast.objects.create_broadcast_object( _(request.POST['message']), request.user)
				action.send(blog_post, verb='said:', action_object=broadcast)

	if request.is_ajax():
		return HttpResponse('ok')
	else:
		return render_to_response('broadcast_success.html', {}, RequestContext(request))

def userwish(request):
	if request.method == "POST":
		blog_category = get_object_or_404(BlogCategory, slug=slugify(_(request.POST['blog_category'])))
		if _(request.POST['actor']) == "user":
			broadcast = UserWishRadio.objects.create_user_wishradio_object(request.user, _(request.POST['userwish']), blog_category , _(request.POST['message']) )
			action.send(request.user, verb='said:', action_object=broadcast)
		elif _(request.POST['actor']) == "vendor":
			
			blog_posts = BlogPost.objects.published(
                                     for_user=request.user).select_related().filter(user=request.user)
			"""
				For now considering blog_posts as a list.
				Going forward we will restrict the #blogposts to be one per user therefore fetching the first element only is sufficient.
				Remove this loop then.
			"""
			if blog_posts:
				blog_post = blog_posts[0]
				broadcast = UserWishRadio.objects.create_user_wishradio_object(request.user, _(request.POST['vendorwish']), blog_category, _(request.POST['message']) )
				action.send(blog_post, verb='said:', action_object=broadcast)

	if request.is_ajax():
		return HttpResponse('ok')
	else:
		return render_to_response('broadcast_success.html', {}, RequestContext(request))

def view_wish(request, wish_id, template_name='wish/view_wish.html'):
    wish = get_object_or_404(UserWishRadio, id=wish_id)

    return render_to_response(template_name, {
        'wish': wish,
    }, context_instance=RequestContext(request))
view_wish = login_required(view_wish)
