from __future__ import division
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
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
from django.core.files import File
from django.template import Template
from django.db.models import Count

from mezzanine.blog.models import BlogPost, BlogCategory, BlogParentCategory
from mezzanine.generic.models import Review
from mezzanine.generic.models import ThreadedComment, RequiredReviewRating, OptionalReviewRating
from mezzanine.utils.views import paginate
from mezzanine.utils.email import send_mail_template
from mezzanine.generic.models import Keyword

from actstream import models
from actstream.models import Action
from itertools import chain
from mezzanine.conf import settings
from actstream import actions
from follow.models import Follow
from actstream.models import Follow as _Follow
from voting.models import Vote
from cropper.models import Original
from imagestore.models import Album, Image as _Image
from PIL import Image
import datetime
import os
import uuid
import json
from django.core.urlresolvers import reverse
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.views.decorators.csrf import csrf_exempt
from userProfile.forms import SuggestStoreForm, ContactUsForm


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
		broadcast_obj = None

		actor = request.POST.get('actor', None)
		message = request.POST.get('message', '')
		urlPreviewContent = request.POST.get('urlPreviewContent','')
		originalImageObj = None
		if 'wishimage' in request.FILES:
			wishimageobj = request.FILES['wishimage']
			img = Image.open(wishimageobj)
			width, height = img.size

			quality 	= getattr(settings, 'IMAGESTORE_IMAGE_QUALITY', 95)
			MAX_WIDTH 	= getattr(settings, 'MAX_IMAGE_WIDTH', 1000.0)
			MAX_HEIGHT 	= getattr(settings, 'MAX_IMAGE_HEIGHT', 1000.0)
			factor 		= min(MAX_WIDTH/width, MAX_HEIGHT/height)

			resizedImageFile = StringIO.StringIO()
			if width > int(MAX_WIDTH) and height > int(MAX_HEIGHT):
				newwidth 	= width * factor
				newheight 	= height * factor
				img.resize((int(newwidth), int(newheight)), Image.ANTIALIAS).save(resizedImageFile, format="JPEG", qualtiy=quality)
			else:
				img.save(resizedImageFile, format="JPEG", qualtiy=quality)

			resizedImageFile.seek(0)

			convertedFile = InMemoryUploadedFile(resizedImageFile, None, 'temp.jpeg', 'image/jpeg', resizedImageFile.len, None)
			originalImageObj = Original.objects.create(image=convertedFile, image_width=width, image_height=height)

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
					broadcast_obj = BroadcastDeal.objects.create_vendor_deal_object(request.user, message, ctype, blog_post.pk, originalImageObj, urlPreviewContent, deal_expiry_date)
					broadcast_obj.blog_category.add(blog_category)
					for parent_category in blog_category.parent_category.all():
						broadcast_obj.blog_parentcategory.add(parent_category)

					action.send(blog_post, verb=settings.DEAL_POST_VERB, target=broadcast_obj)
					actions.follow(request.user, broadcast_obj, send_action=False, actor_only=False) 
					Follow.objects.get_or_create(request.user, broadcast_obj)
				else:
					broadcast_obj = GenericWish.objects.create_generic_wish_object(request.user, message, ctype, blog_post.pk, originalImageObj, urlPreviewContent)
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

					if blog_category and blog_parentcategory not in blog_category.parent_category.all():
						error_codes.append(settings.WISH_PARENT_CATEGORY_MISMATCH)	

			if error_codes:
				return json_error_response(error_codes)

			else:
				ctype = ContentType.objects.get_for_model(User)
				broadcast_obj = None
				verb_str = ''
				if post_as_wish:
					broadcast_obj = BroadcastWish.objects.create_user_wish_object(request.user, message, ctype, request.user.pk, originalImageObj, urlPreviewContent )
					broadcast_obj.blog_category.add(blog_category)
					for parent_category in blog_category.parent_category.all():
						broadcast_obj.blog_parentcategory.add(parent_category)

					verb_str=settings.WISH_POST_VERB
				else:
					broadcast_obj = GenericWish.objects.create_generic_wish_object(request.user, message, ctype, request.user.pk, originalImageObj, urlPreviewContent)
					verb_str=settings.SAID_VERB
				
				action.send(request.user, verb=verb_str, target=broadcast_obj)
				actions.follow(request.user, broadcast_obj, send_action=False, actor_only=False) 
				Follow.objects.get_or_create(request.user, broadcast_obj)

	if request.is_ajax():
		if broadcast_obj.wishimage:
			return HttpResponse(simplejson.dumps(dict(success=True, crop_url=broadcast_obj.wishimage.get_absolute_url())))
		else:
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

	profile_user = ctype.model_class().objects.get(pk=object_id)

	is_incremental = "false"
	s = (int)(""+sIndex)
	l = (int)(""+lIndex)
	if s > 0:
		is_incremental = "true"

	if wishset:
		wishset = wishset.order_by('-timestamp')[s:l]

	data_href =	reverse('get_wishlist', kwargs={
            'content_type_id': ctype.pk, 'object_id': object_id, 'sIndex':s, 'lIndex':l})


	context = RequestContext(request)
	context.update({'is_incremental':is_incremental,
		'wish_list': wishset,
		'ctype': ctype, 'sIndex':s,
		'data_chunk': settings.MIN_DEALS_HOME_PAGE,
		'data_href': data_href})

	if wishset:
		ret_data = {
			'html': render_to_string('wish/wishlist.html', context_instance=context).strip(),
			'success': True
		}
	elif s == 0:
		template = None
		if (profile_user != request.user):
			username = (profile_user.first_name + " " + profile_user.last_name).title()
			template = Template('<span class="fontTitillium1 fontSize13">' + username + ' is yet to upload any wishes.</span>')
		else:
			template = Template('<span class="fontTitillium1 fontSize13">Do tell your friends and us some of your wishes - that might prove to be the first step to getting it fulfilled</span>')
		ret_data = {
			'html': template.render(context).strip(),
			'success': True
		}
	else:
		ret_data = {
			'success': False
		}		

	return HttpResponse(json.dumps(ret_data), mimetype="application/json")

def get_deallist(request, content_type_id, object_id, sIndex, lIndex):

	from itertools import chain
	import operator

	ctype = get_object_or_404(ContentType, pk=content_type_id)
	today = datetime.datetime.today().date()
	dealset = BroadcastDeal.objects.all().filter(content_type=ctype, object_id=object_id, expiry_date__gte=today)
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

def getUserReviews(request, user_id, sIndex=0, lIndex=0):
	if request.method == "GET" and request.is_ajax():
		try:
			user_instance = User.objects.get(id=user_id)
		except:
			return []

		ctype = ContentType.objects.get_for_model(BlogPost)
		reviews = Review.objects.filter(user=user_instance, content_type=ctype).order_by('-submit_date')

		isVertical = request.GET.get('v', '0')
		template = 'generic/user_reviews.html'
		if isVertical == '1':
			template = 'generic/user_reviews_v.html'

		s = (int)(""+sIndex)
		l = (int)(""+lIndex)
		if l == 0:
			sub_reviews = reviews
		else:
			sub_reviews = reviews[s:l]

		context = RequestContext(request)
		context.update({'reviews': sub_reviews,
						'is_incremental': True})

		if sub_reviews:
			ret_data = {
				'html': render_to_string(template, context_instance=context).strip(),
				'success': True
			}
		elif s == 0:
			template = Template("<div class='color5D fontSize14 halfGutter'>No reviews were found for the selected category. Do write a review if you've shopped for this category.</div>")
			ret_data = {
				'html': template.render(context).strip(),
				'success': True
			}
		else:
			ret_data = {
				'success': False
			}			

		return HttpResponse(json.dumps(ret_data), mimetype="application/json")
	else:
		raise Http404()

def getTrendingReviews(request, parent_category, sub_category, sIndex=0, lIndex=0):

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
			reviews = Review.objects.all().order_by('-submit_date') #[:latest]
		elif blog_parentcategory_slug.lower() != "all" and blog_subcategory_slug.lower() == "all":
			if blog_parentcategory:
				blog_subcategories = BlogCategory.objects.all().filter(parent_category=blog_parentcategory).values_list('id', flat=True)
				reviews = Review.objects.all().filter(bought_category__id__in=blog_subcategories).order_by('-submit_date') #[:latest]
		else:
			if blog_subcategory and blog_parentcategory:
				reviews = Review.objects.all().filter(bought_category=blog_subcategory).order_by('-submit_date') #[:latest]
			else:
				"""
					raise 404 error, in case categories are not present.
				"""
				raise Http404()
		isVertical = request.GET.get('v', '0')
		template = 'generic/top_reviews.html'
		if isVertical == '1':
			template = 'generic/top_reviews_v.html'

		s = (int)(""+sIndex)
		l = (int)(""+lIndex)
		if l == 0:
			sub_reviews = reviews
		else:
			sub_reviews = reviews[s:l]

		context = RequestContext(request)
		context.update({'comments': sub_reviews,
						'is_incremental': True})
		if sub_reviews:
			ret_data = {
				'html': render_to_string(template, context_instance=context).strip(),
				'success': True
			}
		elif s == 0:
			template = None
			if isVertical == '1':
				template = Template("<div class='color5D fontSize14 halfGutter'>No reviews were found for the selected category. Do write a review if you've shopped for this category.</div>")
			else:
				template = Template("<div class='color5D fontSize14 halfGutter topHalfGutter'>No reviews were found for the selected category. Do write a review if you've shopped for this category.</div>")
			ret_data = {
				'html': template.render(context).strip(),
				'success': True
			}
		else:
			ret_data = {
				'success': False
			}			

		return HttpResponse(json.dumps(ret_data), mimetype="application/json")
	else:
		raise Http404()

def getTrendingDeals(request, parent_category, sub_category, sIndex=0, lIndex=0):
	if request.method == "GET": #and request.is_ajax():
		ctype = ContentType.objects.get_for_model(BlogPost)
		# latest = settings.DEALS_NUM_LATEST
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
			deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype, expiry_date__gte=today) #[:latest]
		elif blog_parentcategory_slug.lower() != "all" and blog_subcategory_slug.lower() == "all":
			if blog_parentcategory:
				blog_subcategories = BlogCategory.objects.all().filter(parent_category=blog_parentcategory).values_list('id', flat=True)
				deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype, blog_category__id__in=blog_subcategories, expiry_date__gte=today).distinct() #[:latest]
		else:
			if blog_subcategory and blog_parentcategory:
				deals_queryset = BroadcastDeal.objects.all().filter(blog_category=blog_subcategory, expiry_date__gte=today)#[:latest]
			else:
				"""
					raise 404 error, in case categories are not present.
				"""
				raise Http404()

		model_type = ContentType.objects.get_for_model(BroadcastDeal)
		table_name = Broadcast._meta.db_table

		deals_queryset = deals_queryset.extra(select={
			'score': 'SELECT COALESCE(SUM(vote),0) FROM %s WHERE content_type_id=%d AND object_id=%s.id' % (Vote._meta.db_table, int(model_type.id), table_name),
			'sharecount': "SELECT COALESCE(COUNT(*),0) FROM %s WHERE verb='%s' AND target_content_type_id=%d AND target_object_id::int=%s.id" % (Action._meta.db_table, settings.SHARE_VERB, int(model_type.id), table_name)
		}).order_by('-score', '-sharecount', '-timestamp',)

		s = (int)(""+sIndex)
		l = (int)(""+lIndex)
		if l == 0:
			deal_chunk = deals_queryset
		else:
			deal_chunk = deals_queryset[s:l]

		isVertical = request.GET.get('v', '0')
		template = 'wish/deallist.html'
		if isVertical == '1':
			template = 'wish/deallist_v.html'

		context = RequestContext(request)
		context.update({'deal_list': deal_chunk,
						'is_incremental': True})
		if deal_chunk:
			ret_data = {
				'html': render_to_string(template, context_instance=context).strip(),
				'success': True,
				'more':True
			}
		elif s == 0:
			template = Template('<div class="color5D fontSize14 halfGutter">This category does not have any Deals currently.</div>')
			ret_data = {
				'html': template.render(context).strip(),
				'success': True
			}
		else:
			ret_data = {
				'success': False
			}			

		return HttpResponse(json.dumps(ret_data), mimetype="application/json")
	else:
	 	raise Http404()

def get_filtered_deallist(request, store_id, sub_category, sIndex, lIndex):
	deals_queryset = None
	blog_subcategory = None
	today = datetime.datetime.today().date()
	ctype = ContentType.objects.get_for_model(BlogPost)
	if sub_category.lower() != "all" and sub_category.lower() != '':
		try:
			blog_subcategory = BlogCategory.objects.get(slug=slugify(sub_category))
			deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype, object_id=store_id, blog_category=blog_subcategory, expiry_date__gte=today)
		except:
			raise Http404()

	elif sub_category.lower() == "all" or sub_category.lower() == '':
		deals_queryset = BroadcastDeal.objects.all().filter(content_type=ctype, object_id=store_id, expiry_date__gte=today)

	s = (int)(""+sIndex)
	l = (int)(""+lIndex)

	if deals_queryset:
		model_type = ContentType.objects.get_for_model(BroadcastDeal)
		table_name = Broadcast._meta.db_table

		deals_queryset = deals_queryset.extra(select={
			'score': 'SELECT COALESCE(SUM(vote),0) FROM %s WHERE content_type_id=%d AND object_id=%s.id' % (Vote._meta.db_table, int(model_type.id), table_name),
			'sharecount': "SELECT COALESCE(COUNT(*),0) FROM %s WHERE verb='%s' AND target_content_type_id=%d AND target_object_id::int=%s.id" % (Action._meta.db_table, settings.SHARE_VERB, int(model_type.id), table_name)
		}).order_by('-score', '-sharecount', '-timestamp',)

		deals_queryset = deals_queryset[s:l]

	isVertical = request.GET.get('v', '0')
	template = 'wish/deallist.html'
	if isVertical == '1':
		template = 'wish/deallist_v.html'

	context = RequestContext(request)
	context.update({'deal_list': deals_queryset})

	if s == 0:
		data_href = reverse('get_filtered_deallist', kwargs={'store_id':store_id,
															'sub_category':sub_category,
															'sIndex':s,
															'lIndex':l})
		data_chunk = settings.DEALS_NUM_LATEST

		context.update({'is_incremental': False,
						'data_href' : data_href,
						'data_chunk': data_chunk})

	else:
		context.update({'is_incremental': True})


	if deals_queryset:
		ret_data = {
			'html': render_to_string(template, context_instance=context).strip(),
			'success': True
		}
	elif s == 0:
		template = Template('<div class="color5D fontSize14 halfGutter">This category does not have any Deals currently.</div>')
		ret_data = {
			'html': template.render(context).strip(),
			'success': True
		}
	else:
		ret_data = {
			'success': False
		}		

	return HttpResponse(json.dumps(ret_data), mimetype="application/json")


def getTrendingStores(request, parent_category, sub_category, sIndex=0, lIndex=0):
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
		table_name = BlogPost._meta.db_table

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
			else:
				"""
					raise 404 error, in case categories are not present.
				"""
				ret_data = {
					'success': False
				}
				return HttpResponse(json.dumps(ret_data), mimetype="application/json")

		result = result.extra(select={'fieldsum':'price_average + website_ex_average + quality_average + service_average',
									  'followers': 'SELECT COUNT(*) FROM %s WHERE target_blogpost_id=%s.id' % (Follow._meta.db_table, table_name)},
									  order_by=( '-overall_average', '-fieldsum', '-comments_count', '-followers',)).distinct() #[:latest]

		isVertical = request.GET.get('v', '0')
		template = 'generic/vendor_list.html'
		if isVertical == '1':
			template = 'generic/vendor_list_v.html'

		s = (int)(""+sIndex)
		l = (int)(""+lIndex)
		if l == 0:
			sub_result = result
		else:
			sub_result = result[s:l]

		context = RequestContext(request)
		context.update({'vendors': sub_result,
						'is_incremental': True})
		if sub_result:
			ret_data = {
				'html': render_to_string(template, context_instance=context).strip(),
				'success': True
			}
		elif s == 0:
			template = None
			if isVertical == '1':
				template = Template('<div class="color5D fontSize14 halfGutter">No stores were found for the selected category. Do suggest a store, if you know of one.</div>')
			else:
				template = Template('<div class="color5D fontSize14 halfGutter topHalfGutter">No stores were found for the selected category. Do suggest a store, if you know of one.</div>')
			ret_data = {
				'html': template.render(context).strip(),
				'success': True
			}
		else:
			ret_data = {
				'success': False
			}			
		return HttpResponse(json.dumps(ret_data), mimetype="application/json")

	else:
		raise Http404()

def getTrendingStores_v2(request, sub_category):
	#if request.method == "GET" and request.is_ajax():
		result = None
		"""
		/xyz/abc/ will return a list ["","xyz",abc",""] after parsing.
		2nd and 3rd element from last will be sub_category and parent_category respectively.
		"""
		blog_subcategory = None
		blog_subcategory_slug = sub_category
		table_name = BlogPost._meta.db_table

		blog_subcategory = get_object_or_404(BlogCategory, slug=slugify(blog_subcategory_slug))
		parent_category = blog_subcategory.parent_category.all()[0]

		if blog_subcategory and parent_category:
			stores = settings.CATEGORY_STORE_MAP.get(sub_category, [])
			if len(stores) > 0:
				result = BlogPost.objects.published().filter(title__in=stores)
		else:
			"""
				raise 404 error, in case categories are not present.
			"""
			ret_data = {
				'success': False
			}
			return HttpResponse(json.dumps(ret_data), mimetype="application/json")

		if result:
			result = result.extra(select={'fieldsum':'price_average + website_ex_average + quality_average + service_average',
									  'followers': 'SELECT COUNT(*) FROM %s WHERE target_blogpost_id=%s.id' % (Follow._meta.db_table, table_name)},
									  order_by=( '-overall_average', '-fieldsum', '-comments_count', '-followers',)).distinct() #[:latest]

		isVertical = request.GET.get('v', '0')
		template = 'generic/new_vendor_list.html'


		context = RequestContext(request)
		context.update({'vendors': result,
						'is_incremental': True})

		category_search_url = reverse('get_vendors', kwargs={'parent_category_slug':parent_category,
																'sub_category_slug': sub_category})
		if result:
			ret_data = {
				'html': render_to_string(template, context_instance=context).strip(),
				'search_url': category_search_url,
				'success': True
			}
		elif s == 0:
			template = None
			if isVertical == '1':
				template = Template('<div class="color5D fontSize14 halfGutter">No stores were found for the selected category. Do suggest a store, if you know of one.</div>')
			else:
				template = Template('<div class="color5D fontSize14 halfGutter topHalfGutter">No stores were found for the selected category. Do suggest a store, if you know of one.</div>')
			ret_data = {
				'html': template.render(context).strip(),
				'category' : parent_category,
				'search_url': category_search_url,
				'success': True
			}
		else:
			ret_data = {
				'success': False
			}			
		return HttpResponse(json.dumps(ret_data), mimetype="application/json")

	# else:
	# 	raise Http404()

def get_related_stores(request, store_id, sub_category, sIndex, lIndex):
	if sub_category.lower() != "all" and sub_category.lower() != '':
		try:
			blog_subcategory = BlogCategory.objects.get(slug=slugify(sub_category))
			blogPostQueryset = BlogPost.objects.published().filter(categories=blog_subcategory).exclude(id=store_id)
		except:
			blogPostQueryset = None
			pass	
	elif sub_category.lower() == "all" or sub_category.lower() == '':
		try:
			blog_post = BlogPost.objects.get(id=store_id)
			categories = blog_post.categories.all() 
			blogPostQueryset = BlogPost.objects.published().filter(categories__in=categories).exclude(id=store_id)
		except:
			blogPostQueryset = None
			pass

	table_name = BlogPost._meta.db_table
	if blogPostQueryset:
		blogPostQueryset = blogPostQueryset.extra(select={'fieldsum':'price_average + website_ex_average + quality_average + service_average',
														  'followers': 'SELECT COUNT(*) FROM %s WHERE target_blogpost_id=%s.id' % (Follow._meta.db_table, table_name)},
														  order_by=('-overall_average', '-fieldsum', '-comments_count', '-followers',)).distinct()
		s = (int)(""+sIndex)
		l = (int)(""+lIndex)
		blogPostQueryset = blogPostQueryset[s:l]

		isVertical = request.GET.get('v', '0')
		template = 'generic/vendor_list.html'
		if isVertical == '1':
			template = 'generic/vendor_list_v.html'

		context = RequestContext(request)
		context.update({'vendors': blogPostQueryset})

		if s == 0:
			data_href = reverse('get_related_stores', kwargs={'store_id':store_id,
																'sub_category':sub_category,
																'sIndex':s,
																'lIndex':l})
			data_chunk = settings.STORES_NUM_LATEST

			context.update({'is_incremental': False,
							'data_href' : data_href,
							'data_chunk': data_chunk})

		if blogPostQueryset:
			ret_data = {
				'html': render_to_string(template, context_instance=context).strip(),
				'success': True
			}
		elif s == 0:
			template = Template('<span>No related stores found</span>')
			ret_data = {
				'html': template.render(context).strip(),
				'success': True
			}
		else:
			ret_data = {
				'success': False
			}
	else:
		ret_data = {
			'success': False
		}			

	return HttpResponse(json.dumps(ret_data), mimetype="application/json")

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
    reviews = Review.objects.filter(user=user_instance, content_type=ctype).order_by('-submit_date')

    page = request.GET.get("page", 1)
    per_page = settings.REVIEWS_PER_PAGE
    max_paging_links = settings.MAX_PAGING_LINKS

    paginated = paginate(reviews, page, per_page, max_paging_links)

    return render_to_response('generic/includes/reviews_page.html', {
       'reviews': paginated,
       'user': user_instance
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

def deleteFile(file):
    storage, path = file.storage, file.path
    storage.delete(path)

def deleteObject(request, content_type_id, object_id ):
    error_codes = []
    #if not request.is_ajax():
    #   error_codes.append(settings.AJAX_ONLY_SUPPORT)
    #   return json_error_response(error_codes)

    try:
        ctype = ContentType.objects.get(pk=content_type_id)
        object = ctype.model_class().objects.get(pk=object_id)
    except:
        error_codes.append(settings.OBJECT_DOES_NOT_EXIST)
        return json_error_response(error_codes)

    owner = get_object_owner_helper(content_type_id, object_id)

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
        stream = models.action_object_stream(object)
        activity = stream 
        stream = models.target_stream(object)
        activity = activity | stream 
            
        if activity:
            activity.delete()

        _followList = _Follow.objects.filter(content_type=ctype, object_id=str(object_id))
        for _followObj in _followList:
            _followObj.delete()

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
           Delete comments associated with the object.
        """
        comments_queryset = object.comments.all()
        for comment in comments_queryset:
        	ctype_id = ContentType.objects.get_for_model(comment).pk
        	deleteObject(request, ctype_id, comment.pk)
            #comments_queryset.delete()

        """
            Delete related objects for Reviews.
        """

        if isinstance(object, Review):
            try:
                requiredReviewRatingObj = RequiredReviewRating.objects.get(commentid=object._get_pk_val())
            except:
                requiredReviewRatingObj = None
                pass

            if requiredReviewRatingObj:
                requiredReviewRatingCtype = ContentType.objects.get_for_model(requiredReviewRatingObj)
                requiredReviewRatingVoteObjects = Vote.objects.filter(content_type=requiredReviewRatingCtype,
                                                                      object_id=requiredReviewRatingObj._get_pk_val() )
        
                if requiredReviewRatingVoteObjects:
                    requiredReviewRatingVoteObjects.delete()
                requiredReviewRatingObj.delete()
            try:
                OptionalReviewRatingObj = OptionalReviewRating.objects.get(commentid=object._get_pk_val())
            except:
                OptionalReviewRatingObj = None
                pass

            if OptionalReviewRatingObj:
                OptionalReviewRatingObj.delete()

        elif isinstance(object, GenericWish):
            if object.wishimage:
                try:
                    deleteFile(object.wishimage.image)
                except:
                    pass
                object.wishimage.delete()

        """
            Finally nuke the actual object.
        """
        object.delete()           

        return json_success_response()

def get_object_owner_helper(content_type_id, object_id):
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
	if isinstance(object, Review) or isinstance(object, BlogPost) or isinstance(object, Album) or isinstance(object, _Image) or isinstance(object, ThreadedComment):
		owner = object.user

	elif isinstance(object, BroadcastDeal):
		owner_ctype = object.content_type
		owner_id   = object.object_id
		owner_blog_post = owner_ctype.model_class().objects.get(pk=owner_id)
		owner = owner_blog_post.user

	elif isinstance(object, BroadcastWish) or isinstance(object, GenericWish):
		owner_ctype = object.content_type
		owner_id   = object.object_id
		owner = owner_ctype.model_class().objects.get(pk=owner_id)
		if isinstance(owner, BlogPost):
			owner = owner.user
			
	return owner

def save_file(file, path=''):
    ''' Little helper to save a file
    '''
    filename = file._get_name()
    new_filename =  u'{name}.{ext}'.format(  name=uuid.uuid4().hex,
                                             ext=os.path.splitext(filename)[1].strip('.'))

    dir_path =  '%s/%s' % (settings.MEDIA_ROOT, str(path))

    if not os.path.exists(dir_path):
    	os.makedirs(dir_path)

    save_path = os.path.join(dir_path, new_filename)

    with open(save_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return os.path.join(path, new_filename)

@login_required
def edit_blog_image(request, blogpost_id):
	if request.method == "POST":
		error_codes = []
		try:
			blogpost = BlogPost.objects.get(id=blogpost_id)
		except:
			error_codes.append(settings.OBJECT_DOES_NOT_EXIST)
			return json_error_response(error_codes)

		ctype = ContentType.objects.get_for_model(BlogPost)
		owner = get_object_owner_helper(ctype.pk, blogpost_id)

		if owner != request.user:
			if request.is_ajax():
				error_codes.append(settings.UNAUTHORIZED_OPERATION)
				return json_error_response(error_codes)
			else:
				raise Http404()
		else:
			if 'featured_image' in request.FILES:
				featuredImageObj = request.FILES['featured_image']
				if featuredImageObj:
					new_file_rel_path = 'users/store/%s/images/' % (blogpost.id)
					new_file_path = save_file(featuredImageObj, new_file_rel_path)
					if blogpost.featured_image:
						old_file_path = '%s/%s' % (settings.MEDIA_ROOT, str(blogpost.featured_image.path))
						if os.path.exists(old_file_path):
							os.remove(old_file_path)

					blogpost.featured_image = new_file_path
					blogpost.save()

				if request.is_ajax():
					return HttpResponse(simplejson.dumps(dict(success=True, image_url=blogpost.featured_image.url)))
				else:
					return HttpResponseRedirect(blogpost.get_absolute_url())
				
			else:
				error_codes.append(settings.INSUFFICIENT_DATA)
				return json_error_response(error_codes)
	else:
		if request.is_ajax():
			error_codes.append(settings.AJAX_ONLY_SUPPORT)
			return json_error_response(error_codes)
		else:
			return HttpResponseRedirect(request.get_full_path())

def getShopTalk(request, template_name='shoptalk.html'):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/")
		
	return render_to_response(template_name, {
		}, context_instance=RequestContext(request))

@csrf_exempt
def facebook_view(request):
    return HttpResponseRedirect('/')

def suggest_store(request, template="blog/suggest_store.html"):
	if request.is_ajax():
		if request.method == 'POST':
			form = SuggestStoreForm(request.POST)
			if form.is_valid():
				data = json.dumps({'success':True})
				response_kwargs = {"content_type": 'application/json'}
				email_from = settings.DEFAULT_FROM_EMAIL
				email_to = settings.SUGGEST_STORE_EMAIL_TO
				subject = form.cleaned_data['email_subject']
				message = form.cleaned_data['email_message']
				sender_email = "Anonymous"
				if request.user.is_authenticated(): 
					sender_email = request.user.email

				context = {
					"message": message,
					"request": request,
					"from_email": sender_email
				}
				if email_to and email_from:
					send_mail_template(subject, "email/suggest_store_response", email_from,
						email_to, context, fail_silently=settings.DEBUG)

				return HttpResponse(data, **response_kwargs)
			elif form.errors:
				data = json.dumps(form.errors)
				response_kwargs = {"content_type": 'application/json', "status": 400}
				return HttpResponse(data, **response_kwargs)
		else:
			form = SuggestStoreForm()
			if request.user.is_authenticated():
				form.fields['email_from'].initial = request.user.email
			else:
				form.fields['email_from'].initial = settings.SERVER_EMAIL
			form.fields['email_subject'].initial = settings.SUGGEST_STORE_EMAIL_SUBJECT
			form.fields['email_from'].label = ''
			form.fields['email_subject'].label = ''
			form.fields['email_message'].label = 'Store Name or Link'

			form.fields['email_from'].widget.attrs['style'] = 'display:none'
			form.fields['email_subject'].widget.attrs['style'] = 'display:none'
			context = {"form": form, "action_url": reverse("suggest_store")}
			response = render(request, template, context)
			return response
	else:
		raise Http404()

def contact_us(request, template="generic/contact_us.html"):
	if request.is_ajax():
		if request.method == 'POST':
			form = ContactUsForm(request.POST)
			if form.is_valid():
				data = json.dumps({'success':True})
				response_kwargs = {"content_type": 'application/json'}
				
				email_from = settings.DEFAULT_FROM_EMAIL
				email_to = settings.CONTACT_US_EMAIL_TO

				subject = form.cleaned_data['email_subject']
				message = form.cleaned_data['email_contact_message']
				sender_email = "Anonymous"
				if request.user.is_authenticated(): 
					sender_email = request.user.email

				context = {
					"message": message,
					"request": request,
					"from_email": sender_email
				}
				if email_to and email_from:
					send_mail_template(subject, "email/contact_us", email_from,
						email_to, context, fail_silently=settings.DEBUG)

				return HttpResponse(data, **response_kwargs)
			elif form.errors:
				data = json.dumps(form.errors)
				response_kwargs = {"content_type": 'application/json', "status": 400}
				return HttpResponse(data, **response_kwargs)
		else:
			form = ContactUsForm()
			form.fields['email_contact_message'].widget.attrs['style'] = 'resize:none;'
			if request.user.is_authenticated():
				form.fields['email_from'].initial = request.user.email
			else:
				form.fields['email_from'].initial = settings.SERVER_EMAIL
				form.fields['email_from'].widget.attrs['style'] = 'display:none'

			context = {"form": form, "action_url": reverse("contact_us")}
			response = render(request, template, context)
			return response
	else:
		raise Http404()

def autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('query', '')
		keywords = Keyword.objects.filter(title__icontains=query).values_list('title', flat=True)
		context = {
					'query':	query,
					'suggestions': [w.capitalize() for w in keywords]
				}
		return HttpResponse(json.dumps(context), 'application/json')
	else:
		raise Http404()

def autocomplete_stores(request):
	query = request.GET.get('query', '')
	stores = BlogPost.objects.published().filter(title__icontains=query).values_list('title', flat=True)
	context = {
				'query':	query,
				'suggestions': [w.capitalize() for w in stores]
			}
	return HttpResponse(json.dumps(context), 'application/json')

def privacy_policy(request, template_name='generic/privacy_policy.html'):
	return render_to_response(template_name, {
     }, context_instance=RequestContext(request))

def terms_and_conditions(request, template_name='generic/terms_and_conditions.html'):
	return render_to_response(template_name, {
     }, context_instance=RequestContext(request))

def about_us(request, template_name='generic/about_us.html'):
	return render_to_response(template_name, {
     }, context_instance=RequestContext(request))