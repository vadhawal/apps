from django.shortcuts import render_to_response
from django.template import RequestContext
from userProfile.models import BroadcastForm
from django.http import HttpResponse
from django.shortcuts import render
from actstream import action
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat
from mezzanine.blog.models import BlogPost

def close_login_popup(request):
    return render_to_response('close_popup.html', {}, RequestContext(request))

def broadcast(request):
	if request.method == "POST":
		if _(request.POST['actor']) == "user":
			action.send(request.user, verb=string_concat('said', ': ', _(request.POST['message'])))
		elif _(request.POST['actor']) == "vendor":
			
			blog_posts = BlogPost.objects.published(
                                     for_user=request.user).select_related()
			"""
				For now considering blog_posts as a list.
				Going forward we will restrict the #blogposts to be one per user therefore fetching the first element only is sufficient.
				Remove this loop then.
			"""
			blog_post = blog_posts[:1].get()
			action.send(blog_post, verb=string_concat('said', ': ', _(request.POST['message'])))

	if request.is_ajax():
		return HttpResponse('ok')
	else:
		return render_to_response('broadcast_success.html', {}, RequestContext(request))