from django.shortcuts import render_to_response
from django.template import RequestContext
from userProfile.models import BroadcastForm, Broadcast, BroadcastWish, BroadcastDeal, GenericWish
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from actstream import action
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import simplejson
from django.core.exceptions import MultipleObjectsReturned

from mezzanine.blog.models import BlogPost, BlogCategory, BlogParentCategory
from mezzanine.generic.models import Review
from mezzanine.generic.models import ThreadedComment, RequiredReviewRating, OptionalReviewRating

from actstream.models import Action
from itertools import chain
from mezzanine.conf import settings
from actstream import actions
from follow.models import Follow
from actstream.models import Follow as _Follow
from voting.models import Vote
import datetime


def json_error_response(error_codes):
    return HttpResponse(simplejson.dumps(dict(success=False,
    										  error_codes=error_codes)))

def json_success_response():
    return HttpResponse(simplejson.dumps(dict(success=True)))

def close_login_popup(request):
    return render_to_response('close_popup.html', {}, RequestContext(request))

@login_required
def broadcast(request):
	if request.method == "POST":
		if _(request.POST['actor']) == "user":
			broadcast = Broadcast.objects.create_broadcast_object( _(request.POST['message']), request.user)
			action.send(request.user, verb=settings.SAID_VERB, target=broadcast)
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
				action.send(blog_post, verb=settings.SAID_VERB, target=broadcast)

	if request.is_ajax():
		return HttpResponse('ok')
	else:
		return render_to_response('broadcast_success.html', {}, RequestContext(request))

@login_required
def userwish(request):
	if request.method == "POST":
		blog_category = None
		blog_parentcategory = None
		wishimageobj = None
		error_codes = []
		expiry_date_valid = True

		actor = request.POST.get('actor', None)
		message = request.POST.get('message', '')
		urlPreviewContent = request.POST.get('urlPreviewContent','')
		if 'wishimage' in request.FILES:
			wishimageobj = request.FILES['wishimage']
								
		if message == '' and urlPreviewContent == '' and not wishimageobj:
			error_codes.append(settings.POST_DATA_REQUIRED)

		if actor and actor == "vendor":
			post_as_deal = request.POST.get('post-as-deal', False)
			if post_as_deal:
				if not wishimageobj:
					error_codes.append(settings.DEAL_IMAGE_REQUIRED)

				deal_expiry_date = request.POST.get('expiry_date',None)
				if deal_expiry_date:
					try:
						received_date = datetime.datetime.strptime(deal_expiry_date, '%Y-%m-%d')
						if received_date.date() < datetime.datetime.today().date():
							error_codes.append(settings.DEAL_EXPIRY_DATE_INVALID)

					except ValueError:
						error_codes.append(settings.DEAL_EXPIRY_DATE_INVALID)
						pass
				else:
					error_codes.append(settings.DEAL_EXPIRY_DATE_REQUIRED)

				blog_category_slug = request.POST.get('radio_category', None)
				
				if BlogCategory.objects.all().exists() and blog_category_slug:
					try:
						blog_category = BlogCategory.objects.get(slug=slugify(blog_category_slug))
					except:
						error_codes.append(settings.DEAL_SUB_CATEGORY_REQUIRED)
						pass

				if BlogParentCategory.objects.all().exists() and blog_category:
					blog_parentcategory = blog_category.parent_category

			if error_codes:
				return json_error_response(error_codes)

			else:
				blog_posts = BlogPost.objects.published(
                                     for_user=request.user).select_related().filter(user=request.user)
				"""
					For now considering blog_posts as a list.
					Going forward we will restrict the #blogposts to be one per user therefore fetching the first element only is sufficient.
					Remove this loop then.
				"""
				blog_post = blog_posts[0]
				ctype = ContentType.objects.get_for_model(BlogPost)
				broadcast_obj = None
				if post_as_deal:
					broadcast_obj = BroadcastDeal.objects.create_vendor_deal_object(request.user, blog_category, blog_parentcategory, message, ctype, blog_post.pk, wishimageobj, urlPreviewContent, deal_expiry_date)
					action.send(blog_post, verb=settings.DEAL_POST_VERB, target=broadcast_obj)
					actions.follow(request.user, broadcast_obj, send_action=False, actor_only=False) 
					Follow.objects.get_or_create(request.user, broadcast_obj)
				else:
					broadcast_obj = GenericWish.objects.create_generic_wish_object(request.user, message, ctype, blog_post.pk, wishimageobj, urlPreviewContent)
					action.send(blog_post, verb=settings.SAID_VERB, target=broadcast_obj)
					actions.follow(request.user, broadcast_obj, send_action=False, actor_only=False) 
					Follow.objects.get_or_create(request.user, broadcast_obj)

		elif actor and actor == "user":
			post_as_wish = request.POST.get('post-as-wish', False)
			if post_as_wish:
				blog_parentcategory_slug 	= request.POST.get('blog_parentcategories', None)
				blog_category_slug 			= request.POST.get('blog_subcategories', None)

				if blog_parentcategory_slug:
					try:
						blog_parentcategory = BlogParentCategory.objects.get(slug=slugify(blog_parentcategory_slug))
					except:
						error_codes.append(settings.WISH_PARENT_CATEGORY_REQUIRED)
						pass

				if blog_category_slug:
					try:
						blog_category = BlogCategory.objects.get(slug=slugify(blog_category_slug))
					except:
						error_codes.append(settings.WISH_SUB_CATEGORY_REQUIRED)
						pass

					if blog_category and blog_parentcategory != blog_category.parent_category:
						error_codes.append(settings.WISH_PARENT_CATEGORY_MISMATCH)	

			if error_codes:
				return json_error_response(error_codes)

			else:
				ctype = ContentType.objects.get_for_model(User)
				broadcast_obj = None
				verb_str = ''
				if post_as_wish:
					broadcast_obj = BroadcastWish.objects.create_user_wish_object(request.user, blog_category , blog_parentcategory, message, ctype, request.user.pk, wishimageobj, urlPreviewContent )
					verb_str=settings.WISH_POST_VERB
				else:
					broadcast_obj = GenericWish.objects.create_generic_wish_object(request.user, message, ctype, request.user.pk, wishimageobj, urlPreviewContent)
					verb_str=settings.SAID_VERB
				
				action.send(request.user, verb=verb_str, target=broadcast_obj)
				actions.follow(request.user, broadcast_obj, send_action=False, actor_only=False) 
				Follow.objects.get_or_create(request.user, broadcast_obj)

	if request.is_ajax():
		return json_success_response()
	else:
		return render_to_response('broadcast_success.html', {}, RequestContext(request))

def view_post(request, post_id, template_name='wish/view_post.html'):
	post = get_object_or_404(GenericWish, id=post_id)

	return render_to_response(template_name, {
		'post': post,
     }, context_instance=RequestContext(request))

def view_wish(request, wish_id, template_name='wish/view_wish.html'):
	wish = get_object_or_404(BroadcastWish, id=wish_id)

	return render_to_response(template_name, {
		'wish': wish,
     }, context_instance=RequestContext(request))

def view_deal(request, deal_id, template_name='wish/view_deal.html'):
	deal = get_object_or_404(BroadcastDeal, id=deal_id)

	return render_to_response(template_name, {
		'deal': deal,
     }, context_instance=RequestContext(request))


def get_wishlist(request, content_type_id, object_id, sIndex, lIndex):

	from itertools import chain
	import operator

	ctype = get_object_or_404(ContentType, pk=content_type_id)
	wishset = BroadcastWish.objects.all().filter(content_type=ctype, object_id=object_id)
	wishlist = list(wishset)

	wishlist =  sorted(wishlist, key=operator.attrgetter('timestamp'), reverse=True)

	s = (int)(""+sIndex)
	l = (int)(""+lIndex)
	wishlist = wishlist[s:l]
	return render_to_response('wish/wishlist.html', {
		'wish_list': wishlist,
		'ctype': ctype, 'sIndex':s
	}, context_instance=RequestContext(request))

def get_deallist(request, content_type_id, object_id, sIndex, lIndex):

	from itertools import chain
	import operator

	ctype = get_object_or_404(ContentType, pk=content_type_id)
	dealset = BroadcastDeal.objects.all().filter(content_type=ctype, object_id=object_id)
	deallist = list(dealset)

	deallist =  sorted(deallist, key=operator.attrgetter('timestamp'), reverse=True)

	s = (int)(""+sIndex)
	l = (int)(""+lIndex)

	deallist = deallist[s:l]
	return render_to_response('wish/deallist.html', {
		'deal_list': deallist,
		'ctype': ctype, 'sIndex':s
	}, context_instance=RequestContext(request))

@login_required
def shareWish(request, wish_id):
	wishObject = get_object_or_404(BroadcastWish, pk=wish_id)
	ctype = ContentType.objects.get_for_model(wishObject)
	actionObject = None
	try:
		actionObject = Action.objects.get(actor_content_type=wishObject.content_type, actor_object_id=wishObject.object_id,verb=settings.WISH_POST_VERB, target_content_type=ctype, target_object_id=wishObject.pk)
	except:
		pass
	if actionObject:
		action.send(request.user, verb=settings.SHARE_VERB, target=actionObject)
	if request.is_ajax():
		return HttpResponse('ok') 
	else:
		return render_to_response(('actstream/detail.html', 'activity/detail.html'), {
				'action': actionObject
			}, context_instance=RequestContext(request)) 

@login_required
def shareDeal(request, deal_id):
	dealObject = get_object_or_404(BroadcastDeal, pk=deal_id)
	ctype = ContentType.objects.get_for_model(dealObject)
	actionObject = None
	try:
		actionObject = Action.objects.get(actor_content_type=dealObject.content_type, actor_object_id=dealObject.object_id,verb=settings.DEAL_POST_VERB, target_content_type=ctype, target_object_id=dealObject.pk)
	except:
		pass

	if actionObject:
		action.send(request.user, verb=settings.SHARE_VERB, target=actionObject)
	
	if request.is_ajax():
		return HttpResponse('ok') 
	else:
		return render_to_response(('actstream/detail.html', 'activity/detail.html'), {
				'action': actionObject
			}, context_instance=RequestContext(request))

@login_required
def shareStore(request, store_id):
	storeObject = get_object_or_404(BlogPost, pk=store_id)

	action.send(request.user, verb=settings.SHARE_VERB, target=storeObject)
	
	if request.is_ajax():
		return HttpResponse(simplejson.dumps(dict(success=True, message="Store is shared")))
	else:
		return render_to_response('blog/blog_post_detail.html', {
				"blog_post": storeObject, 
				"editable_obj": storeObject
			}, context_instance=RequestContext(request))

@login_required
def followObject(request, content_type_id, object_id):
	ctype = get_object_or_404(ContentType, pk=content_type_id)
	object = get_object_or_404(ctype.model_class(), pk=object_id)
	
	Follow.objects.get_or_create(request.user, object)
	actions.follow(request.user, object, send_action=False, actor_only=False)
	return HttpResponse(simplejson.dumps(dict(success=True)))

@login_required
def unfollowObject(request, content_type_id, object_id):
	follow = None
	ctype = get_object_or_404(ContentType, pk=content_type_id)
	object = get_object_or_404(ctype.model_class(), pk=object_id)
	try:
		_follow = Follow.objects.get_follows(object)
		follow = _follow.get(user=request.user)
	except (MultipleObjectsReturned, Follow.DoesNotExist) as e:
		if isinstance(e, MultipleObjectsReturned):
			follow = _follow.filter(user=request.user)[0]
			pass
		else:
			follow = None
			pass

	if follow:
		follow.delete()

	actions.unfollow(request.user, object, send_action=False)
	return HttpResponse(simplejson.dumps(dict(success=True)))


@login_required
def followWish(request, wish_id):
	wishObject = get_object_or_404(BroadcastWish, pk=wish_id)
	ctype = ContentType.objects.get_for_model(wishObject)
	Follow.objects.get_or_create(request.user, wishObject)
	actions.follow(request.user, wishObject, send_action=False, actor_only=False)
	return HttpResponse('ok')

@login_required
def unfollowWish(request, wish_id):
	wishObject = get_object_or_404(BroadcastWish, pk=wish_id)
	ctype = ContentType.objects.get_for_model(wishObject)
	follow = Follow.objects.get_follows(wishObject).get(user=request.user)
	follow.delete()
	actions.unfollow(request.user, wishObject, send_action=False)
	return HttpResponse('ok')

@login_required
def followDeal(request, deal_id):
	wishObject = get_object_or_404(BroadcastDeal, pk=deal_id)
	ctype = ContentType.objects.get_for_model(wishObject)
	Follow.objects.get_or_create(request.user, wishObject)
	actions.follow(request.user, wishObject, send_action=False, actor_only=False)
	return HttpResponse('ok')

@login_required
def unfollowDeal(request, deal_id):
	dealObject = get_object_or_404(BroadcastDeal, pk=deal_id)
	ctype = ContentType.objects.get_for_model(dealObject)
	follow = Follow.objects.get_follows(dealObject).get(user=request.user)
	follow.delete()
	actions.unfollow(request.user, dealObject, send_action=False)
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
		isVertical = request.GET.get('v', '0')
		template = 'generic/top_reviews.html'
		if isVertical == '1':
			template = 'generic/top_reviews_v.html'

		return render_to_response(template, {
				'comments': reviews
			}, context_instance=RequestContext(request))
	else:
		raise Http404()

def getTrendingDeals(request, parent_category, sub_category):
	if request.method == "GET" and request.is_ajax():
		ctype = ContentType.objects.get_for_model(BlogPost)
		latest = settings.DEALS_NUM_LATEST
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
			deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype).order_by('-timestamp')[:latest]
		elif blog_parentcategory_slug.lower() != "all" and blog_subcategory_slug.lower() == "all":
			if blog_parentcategory:
				blog_subcategories = list(BlogCategory.objects.all().filter(parent_category=blog_parentcategory))
				deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype, blog_category__in=blog_subcategories).order_by('-timestamp').distinct()[:latest]
		else:
			if blog_subcategory and blog_parentcategory:
				deals_queryset = BroadcastDeal.objects.all().filter(blog_category=blog_subcategory).order_by('-timestamp')[:latest]
			else:
				"""
					raise 404 error, in case categories are not present.
				"""
				raise Http404()

		isVertical = request.GET.get('v', '0')
		template = 'wish/deallist.html'
		if isVertical == '1':
			template = 'wish/deallist_v.html'

		return render_to_response(template, {
					'deal_list': deals_queryset,
				}, context_instance=RequestContext(request))
	else:
		raise Http404()

def getTrendingStores(request, parent_category, sub_category):
	if request.method == "GET" and request.is_ajax():
		latest = settings.STORES_NUM_LATEST
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
				blog_subcategories = list(BlogCategory.objects.all().filter(parent_category=blog_parentcategory))
				result = BlogPost.objects.published().filter(categories__in=blog_subcategories).extra(select={'fieldsum':'price_average + variety_average + quality_average + service_average + exchange_average + overall_average'},order_by=('-fieldsum',)).distinct()[:latest]
		else:
			if blog_subcategory and blog_parentcategory:
				result = BlogPost.objects.published().filter(categories=blog_subcategory).extra(select={'fieldsum':'price_average + variety_average + quality_average + service_average + exchange_average + overall_average'},order_by=('-fieldsum',))[:latest]
			else:
				"""
					raise 404 error, in case categories are not present.
				"""
				raise Http404()

		isVertical = request.GET.get('v', '0')
		template = 'generic/vendor_list.html'
		if isVertical == '1':
			template = 'generic/vendor_list_v.html'

		return render_to_response(template, {
				'vendors': result
			}, context_instance=RequestContext(request))
	else:
		raise Http404()

def get_profile_image(request, username=None):
	user = None

	if username:
		try:
			user = User.objects.get(username=username)
		except:
			raise Http404()
		if user.get_profile().profile_photo:
			return HttpResponseRedirect(user.get_profile().profile_photo.url)
		elif user.get_profile().image_url:
			return HttpResponseRedirect(user.get_profile().image_url)
	raise Http404()

def render_wish(request, wish_id, template="wish/wish_template.html"):
    """
    renders the wish in a page with dedicated url. Can be used to share in social networks.
    """
    wish =  BroadcastWish.objects.get(id=wish_id)
    context = RequestContext(request)

    return render_to_response('wish/wish_template.html', {
       'wish': wish, 
    }, context_instance=context)

def render_deal(request, deal_id, template="wish/deal_template.html"):
    """
    renders the wish in a page with dedicated url. Can be used to share in social networks.
    """
    deal =  BroadcastDeal.objects.get(id=deal_id)
    context = RequestContext(request)

    return render_to_response('wish/deal_template.html', {
       'deal': deal, 
    }, context_instance=context)

def get_reldata(request, content_type_id, object_id):
	ctype = get_object_or_404(ContentType, pk=content_type_id)
	obj = get_object_or_404(ctype.model_class(), pk=object_id)

	if isinstance(obj, BroadcastDeal):
		return render_to_response('generic/rel_data_deal.html', {
			'deal': obj, 
		}, context_instance=RequestContext(request))
	else:
		return render_to_response('generic/rel_data.html', {
			'object': obj, 
		}, context_instance=RequestContext(request))

def get_reviews_by_user(request, user_id, template="generic/includes/reviews_page.html"):
    """
    Return a list of child comments for the given parent, storing all
    comments in a dict in the context when first called, using parents
    as keys for retrieval on subsequent recursive calls from the
    comments template.
    """
    user_instance = User.objects.get(id=user_id)
    ctype = ContentType.objects.get_for_model(BlogPost)
    reviews = ThreadedComment.objects.filter(user=user_instance, content_type=ctype)

    return render_to_response('generic/includes/reviews_page.html', {
       'reviews': reviews, 
    }, context_instance=RequestContext(request))


def shareObject(request, content_type_id, object_id, ):
	if request.is_ajax():
		ctype = get_object_or_404(ContentType, pk=content_type_id)
		object = get_object_or_404(ctype.model_class(), pk=object_id)

		action.send(request.user, verb=settings.SHARE_VERB, target=object)
		shareCount = Action.objects.filter(verb=settings.SHARE_VERB, target_content_type=ctype, target_object_id = object_id).count()
		return HttpResponse(simplejson.dumps(dict(success=True, count=shareCount)))
	else:
		raise Http404();

def deleteObject(request, content_type_id, object_id ):
    error_codes = []
    if not request.is_ajax():
        error_codes.append(settings.AJAX_ONLY_SUPPORT)
        return json_error_response(error_codes)

    try:
		ctype = ContentType.objects.get(pk=content_type_id)
		object = ctype.model_class().objects.get(pk=object_id)
    except:
        error_codes.append(settings.OBJECT_DOES_NOT_EXIST)
        return json_error_response(error_codes)

    owner = get_object_owner(request, content_type_id, object_id)

    """
    	Check whehter use is authorized to delete the object.
    """
    if request.user != owner:
        error_codes.append(settings.UNAUTHORIZED_OPERATION)
        return json_error_response(error_codes)

    if object:
    	"""
    		Delete related activities and actstream follow objects.
    	"""
        _follow = None
        try:
            _follow = _Follow.objects.get(follow_object=object)
        except:
            pass

        if _follow:
            stream = models.action_object_stream(_follow)
            activity = stream 
            stream = models.target_stream(_follow)
            activity = activity | stream 
            
            if activity: 
            	activity.delete()
            
            _follow.delete()

    	"""
    		Delete django-follow objects.
    	"""
        follow = None
        try:
        	follow = Follow.objects.get_follows(object)
        except:
        	pass

        if follow:
            follow.delete() 

    	"""
    		Delete voting objects.
    	"""
        voteObjects = Vote.objects.filter(content_type=ctype,
                         object_id=object._get_pk_val() )
        if voteObjects:
            voteObjects.delete()

    	"""
    		Delete related objects for Reviews.
    	"""
        if isinstance(object, Review):
        	requiredReviewRatingObj = RequiredReviewRating.objects.get(commentid=object._get_pk_val())
        	if requiredReviewRatingObj:
        		requiredReviewRatingCtype = ContentType.objects.get_for_model(requiredReviewRatingObj)
        		requiredReviewRatingVoteObjects = Vote.objects.filter(content_type=requiredReviewRatingCtype,
                         								object_id=requiredReviewRatingObj._get_pk_val() )
        	
        		if requiredReviewRatingVoteObjects:
        			requiredReviewRatingVoteObjects.delete()
        		requiredReviewRatingObj.delete()

        	OptionalReviewRatingObj = OptionalReviewRating.objects.get(commentid=object._get_pk_val())
        	if OptionalReviewRatingObj:
        		OptionalReviewRatingObj.delete()

    	"""
    		Finally nuke the actual object.
    	"""
        object.delete()           

        return json_success_response()

def get_object_owner(request, content_type_id, object_id):
	owner = None
	try:
		ctype = ContentType.objects.get(pk=content_type_id)
		object = ctype.model_class().objects.get(pk=object_id)
	except:
		return owner

	"""
		This API get owners which are instanceof User Model.
		Currently supports only Review, BroadcastWish, BroadcastDeal, GenericWish models.
		Enhance for other models as and when required.
	"""
	if isinstance(object, Review):
		owner = object.user

	elif isinstance(object, BroadcastWish) or isinstance(object, GenericWish):
		owner_ctype = object.content_type
		owner_id   = object.object_id
		owner = owner_ctype.model_class().objects.get(pk=owner_id)

	elif isinstance(object, BroadcastDeal):
		owner_ctype = object.content_type
		owner_id   = object.object_id
		owner_blog_post = owner_ctype.model_class().objects.get(pk=owner_id)
		owner = owner_blog_post.user

	return owner
