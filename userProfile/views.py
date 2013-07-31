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
from mezzanine.blog.models import BlogPost, BlogCategory, BlogParentCategory
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
		blog_parentcategory = None
		if BlogCategory.objects.all().exists():
			blog_category = get_object_or_404(BlogCategory, slug=slugify(_(request.POST['radio_category'])))
		if BlogParentCategory.objects.all().exists():
			blog_parentcategory = blog_category.parent_category
		wishimgeobj = None
		if 'wishimage' in request.FILES:
			wishimgeobj = request.FILES['wishimage']

		urlPreviewContent = request.POST.get("urlPreviewContent","")

		if _(request.POST['actor']) == "user":
			ctype = ContentType.objects.get_for_model(User)
			broadcast = UserWishRadio.objects.create_user_wishradio_object(request.user, _(request.POST['userwish']), blog_category , blog_parentcategory, _(request.POST['message']), ctype, request.user.pk, wishimgeobj, urlPreviewContent )
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
				broadcast = UserWishRadio.objects.create_user_wishradio_object(request.user, _(request.POST['vendorwish']), blog_category, blog_parentcategory, _(request.POST['message']), ctype, request.user.pk, wishimgeobj, urlPreviewContent)
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

def getTrendingReviews(request, parent_category, sub_category):

	if request.method == "GET" and request.is_ajax():
		latest = settings.REVIEWS_NUM_LATEST
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
				blog_subcategories = BlogCategory.objects.all().filter(parent_category=blog_parentcategory)
				reviews = Review.objects.all().filter(bought_category__in=blog_subcategories).order_by('-submit_date')[:latest]
		else:
			if blog_subcategory and blog_parentcategory:
				reviews = Review.objects.all().filter(bought_category=blog_subcategory).order_by('-submit_date')[:latest]
			else:
				"""
					raise 404 error, in case categories are not present.
				"""
				raise Http404()

		return render_to_response('generic/top_reviews.html', {
				'comments': reviews
			}, context_instance=RequestContext(request))
	else:
		raise Http404()

def getTrendingDeals(request, parent_category, sub_category):
	if request.method == "GET" and request.is_ajax():
		ctype = ContentType.objects.get_for_model(BlogPost)
		latest = settings.REVIEWS_NUM_LATEST
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
				blog_subcategories = BlogCategory.objects.all().filter(parent_category=blog_parentcategory)
				deals_queryset = UserWishRadio.objects.all().filter(content_type=ctype, blog_category__in=blog_subcategories).order_by('-timestamp').distinct()[:latest]
		else:
			if blog_subcategory and blog_parentcategory:
				deals_queryset = UserWishRadio.objects.all().filter(blog_category=blog_subcategory).order_by('-timestamp')[:latest]
			else:
				"""
					raise 404 error, in case categories are not present.
				"""
				raise Http404()

		return render_to_response('generic/wishlist.html', {
					'wish_list': deals_queryset,
					'sIndex':0
				}, context_instance=RequestContext(request))
	else:
		raise Http404()

def getTrendingStores(request, parent_category, sub_category):
	if request.method == "GET" and request.is_ajax():
		latest = settings.REVIEWS_NUM_LATEST
		blog_parentcategory = None
		result = None
		"""
		/xyz/abc/ will return a list ["","xyz",abc",""] after parsing.
		2nd and 3rd element from last will be sub_category and parent_category respectively.
		"""
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
				blog_subcategories = BlogCategory.objects.all().filter(parent_category=blog_parentcategory)
				result = BlogPost.objects.published().filter(categories__in=blog_subcategories).extra(select={'fieldsum':'price_average + variety_average + quality_average + service_average + exchange_average + overall_average'},order_by=('-fieldsum',)).distinct()[:latest]
		else:
			if blog_subcategory and blog_parentcategory:
				result = BlogPost.objects.published().filter(categories=blog_subcategory).extra(select={'fieldsum':'price_average + variety_average + quality_average + service_average + exchange_average + overall_average'},order_by=('-fieldsum',))[:latest]
			else:
				"""
					raise 404 error, in case categories are not present.
				"""
				raise Http404()

		return render_to_response('generic/vendor_list.html', {
				'vendors': result
			}, context_instance=RequestContext(request))
	else:
		raise Http404()