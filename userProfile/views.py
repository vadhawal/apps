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
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from mezzanine.blog.models import BlogPost, BlogCategory

from userProfile.models import UserWishRadio
from actstream.models import Action
from itertools import chain
from mezzanine.conf import settings

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
		blog_category = None
		if BlogCategory.objects.all().exists():
			blog_category = get_object_or_404(BlogCategory, slug=slugify(_(request.POST['blog_category'])))
		wishimgeobj = None
		if 'wishimage' in request.FILES:
			wishimgeobj = request.FILES['wishimage']
		if _(request.POST['actor']) == "user":
			ctype = ContentType.objects.get_for_model(User)
			broadcast = UserWishRadio.objects.create_user_wishradio_object(request.user, _(request.POST['userwish']), blog_category , _(request.POST['message']), ctype, request.user.pk, wishimgeobj )
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
				ctype = ContentType.objects.get_for_model(BlogPost)
				broadcast = UserWishRadio.objects.create_user_wishradio_object(request.user, _(request.POST['vendorwish']), blog_category, _(request.POST['message']), ctype, request.user.pk, wishimgeobj)
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

from django.utils import simplejson
from django.http import Http404, HttpResponse

def json_error_response(error_message):
    return HttpResponse(simplejson.dumps(dict(success=False,
                                              error_message=error_message)))
def get_wishlist(request, content_type_id, object_id, sIndex, lIndex):

	from itertools import chain
	import operator

	ctype = get_object_or_404(ContentType, pk=content_type_id)
	wishset = UserWishRadio.objects.all().filter(content_type=ctype, object_id=object_id)
	wishlist = list(wishset)

	wishlist =  sorted(wishlist, key=operator.attrgetter('timestamp'), reverse=True)

	s = (int)(""+sIndex)
	l = (int)(""+lIndex)
	wishlist = wishlist[s:l]
	return render_to_response('wish/wishlist.html', {
		'wish_list': wishlist,
		'ctype': ctype, 'sIndex':s
	}, context_instance=RequestContext(request))

def shareWish(request, wish_id):
	wishObject = get_object_or_404(UserWishRadio, pk=wish_id)
	ctype = ContentType.objects.get_for_model(wishObject)

	actionObject = Action.objects.get(actor_content_type=wishObject.content_type, actor_object_id=wishObject.object_id,verb=u'said:', action_object_content_type=ctype, action_object_object_id=wishObject.pk)

	action.send(request.user, verb=_('shared'), target=actionObject)
	if request.is_ajax():
		return HttpResponse('ok') 
	else:
		return render_to_response(('actstream/detail.html', 'activity/detail.html'), {
				'action': actionObject
			}, context_instance=RequestContext(request)) 

def getTopReviewsForBlogCategory(request, category_slug):
	import operator
	blog_category = None
	if BlogCategory.objects.all().exists():
		blog_category = get_object_or_404(BlogCategory, slug=slugify(category_slug))
	
	blog_posts = BlogPost.objects.published().filter(categories=blog_category)
	
	reviews = []
	latest = settings.REVIEWS_NUM_LATEST

	for blog_post in blog_posts:
		comments_queryset = blog_post.comments.visible().order_by('-id')[:latest]
		reviews = list(chain(reviews, list(comments_queryset)))

	reviews = sorted(reviews, key=operator.attrgetter('submit_date'), reverse=True)
	latestReviews = reviews[:latest]

	return render_to_response('generic/top_reviews.html', {
				'comments': latestReviews
			}, context_instance=RequestContext(request))
