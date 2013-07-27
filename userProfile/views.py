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
from mezzanine.generic.models import Review

from userProfile.models import UserWishRadio
from actstream.models import Action
from itertools import chain
from mezzanine.conf import settings
from actstream import actions
from follow.models import Follow

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
			blog_category = get_object_or_404(BlogCategory, slug=slugify(_(request.POST['radio_category'])))
		wishimgeobj = None
		if 'wishimage' in request.FILES:
			wishimgeobj = request.FILES['wishimage']

		urlPreviewContent = request.POST.get("urlPreviewContent","")

		if _(request.POST['actor']) == "user":
			ctype = ContentType.objects.get_for_model(User)
			broadcast = UserWishRadio.objects.create_user_wishradio_object(request.user, _(request.POST['userwish']), blog_category , _(request.POST['message']), ctype, request.user.pk, wishimgeobj, urlPreviewContent )
			action.send(request.user, verb='said:', action_object=broadcast)
			actions.follow(request.user, broadcast, send_action=False, actor_only=False) 
			Follow.objects.get_or_create(request.user, broadcast)
			#blog_posts = BlogPost.objects.all().filter(categories=blog_category)
			#for blog_post in blog_posts:
			#	actions.follow(blog_post.user, broadcast, send_action=False, actor_only=False)

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
				broadcast = UserWishRadio.objects.create_user_wishradio_object(request.user, _(request.POST['vendorwish']), blog_category, _(request.POST['message']), ctype, request.user.pk, wishimgeobj, urlPreviewContent)
				action.send(blog_post, verb='said:', action_object=broadcast)
				actions.follow(request.user, broadcast, send_action=False, actor_only=False) 
				Follow.objects.get_or_create(request.user, broadcast)
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

def followWish(request, wish_id):
	wishObject = get_object_or_404(UserWishRadio, pk=wish_id)
	ctype = ContentType.objects.get_for_model(wishObject)
	Follow.objects.get_or_create(request.user, wishObject)
	actions.follow(request.user, wishObject, send_action=False, actor_only=False)
	return HttpResponse('ok')

def unfollowWish(request, wish_id):
	wishObject = get_object_or_404(UserWishRadio, pk=wish_id)
	ctype = ContentType.objects.get_for_model(wishObject)
	follow = Follow.objects.get_follows(wishObject).get(user=request.user)
	follow.delete()
	actions.unfollow(request.user, wishObject, send_action=False)
	return HttpResponse('ok')

def getTopReviewsForStoreCategory(request, category_slug):
	import operator
	
	latest = settings.REVIEWS_NUM_LATEST
	
	reviews = Review.objects.all().filter(bought_category=category_slug)[:latest]
	reviews = sorted(reviews, key=operator.attrgetter('submit_date'), reverse=True)

	return render_to_response('generic/top_reviews.html', {
				'comments': reviews
			}, context_instance=RequestContext(request))

def getTopStoresForStoreCategory(request, category_slug):
	import operator
	blog_category = None
	latest = settings.REVIEWS_NUM_LATEST
	if BlogCategory.objects.all().exists():
		blog_category = get_object_or_404(BlogCategory, slug=slugify(category_slug))
	
	vendors = BlogPost.objects.published().filter(categories=blog_category).extra(select={'fieldsum':'price_average + variety_average + quality_average + service_average + exchange_average'},order_by=('-fieldsum',))[:latest]

	return render_to_response('generic/vendor_list.html', {
				'vendors': vendors
			}, context_instance=RequestContext(request))

def getTopDealsForStoreCategory(request, category_slug):
	import operator
	blog_category = None
	if BlogCategory.objects.all().exists():
		blog_category = get_object_or_404(BlogCategory, slug=slugify(category_slug))
	
	deals = []
	latest = settings.REVIEWS_NUM_LATEST
	ctype = ContentType.objects.get_for_model(BlogPost)
	deals_queryset = UserWishRadio.objects.all().filter(content_type=ctype, blog_category=blog_category)[:latest]
	deals_queryset = sorted(deals_queryset, key=operator.attrgetter('timestamp'), reverse=True)
	for deal in deals_queryset:
	    deals.append(deal) 

	return render_to_response('generic/wishlist.html', {
				'wish_list': deals,
				'sIndex':0
			}, context_instance=RequestContext(request))
