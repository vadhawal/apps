# This is models.py for a new user profile that you would like to create.
 
"""
this gist gets an id from django-social-auth and based on that saves the photo from social networks into your model. This is one of the best ways to extend User model because this way, you don't need to redefine a CustomUser as explained in the doc for django-social-auth. this is a new implementation based on https://gist.github.com/1248728
"""
import os
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
from django_resized import ResizedImageField
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.comments.signals import comment_was_posted
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from mezzanine.blog.models import BlogPost, BlogCategory, BlogParentCategory
from mezzanine.conf import settings as _settings
from mezzanine.generic.fields import CommentsField
from mezzanine.generic.models import ThreadedComment

from cropper.models import Original
from imagestore.models import Album, Image
from actstream import action, actions
from follow.models import Follow

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    from datetime import datetime
    now = datetime.now

import datetime as datetime_
from follow import utils
import uuid


MESSAGE_MAX_LENGTH = getattr(_settings,'MESSAGE_MAX_LENGTH',3000)

def get_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    Path = os.path.join('profiles/', "user_%d/%s" % (instance.user.id, filename))
    return Path

class BroadcastForm(forms.Form):
    message = forms.CharField(max_length=100)
    class Meta:
        app_label = 'userProfile'
        
class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    GENDER_CHOICES = (
        (_('male'), _('Male')),
        (_('female'), _('Female')),
        (_('other'), _('Other')),
        ('', '')
        )
    profile_photo = ResizedImageField(upload_to=get_image_path, max_width=1000, max_height=800, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, choices=GENDER_CHOICES, verbose_name=_("Gender"))
    image_url = models.URLField(blank=True, verbose_name=_("Imageurl"), editable=False)
    description = models.TextField(blank=True, verbose_name=_("Description"), help_text=_("Tell us about yourself!"))
    location = models.CharField(verbose_name=_("Location"), max_length=100, help_text=_("Tell us about your location!"), null=True, blank=True)
    birthday = models.DateField(_("Your Birthday!"), null=True, blank=True)

    def __str__(self):  
        return "%s's profile" % self.user  
    class Meta:
        app_label = 'userProfile'

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends import google
from social_auth.signals import socialauth_registered
from social_auth.signals import pre_update
from social_auth.models import UserSocialAuth

def new_users_handler(sender, user, response, details, **kwargs):
    user.is_new = True
    if user.is_new:
        if "id" in response:
            from urllib2 import urlopen, HTTPError
            from django.template.defaultfilters import slugify
            from django.core.files.base import ContentFile
            
            try:
                #url = None
                #if sender == FacebookBackend:
                #    url = "http://graph.facebook.com/%s/picture?type=large" \
                #                % response["id"]
                #elif sender == TwitterBackend:
                #    url = "https://api.twitter.com/1/users/profile_image?screen_name=twitterapi&size=bigger"

                #elif sender == google.GoogleOAuth2Backend and "picture" in response:
                #    url = response["picture"]
    
                #if url:
                #    avatar = urlopen(url)
                    profile = UserProfile.objects.get(user=user)
                    #profile = user.get_profile()
                    if sender == FacebookBackend:
                        profile.image_url = "http://graph.facebook.com/%s/picture" \
                                % response["id"]
                        user_birthday = user.social_auth.get(provider='facebook').extra_data['birthday']
                        profile.birthday = datetime_.datetime.strptime(user_birthday, '%m/%d/%Y').strftime('%Y-%m-%d')

                        user_location = user.social_auth.get(provider='facebook').extra_data['location']
                        profile.location = user_location['name']
                        profile.gender = user.social_auth.get(provider='facebook').extra_data['gender']
                        #'https://graph.facebook.com/' + user.social_auth.filter(provider="facebook")[0] + '/picture'
                        #profile.profile_photo.save(slugify(user.username + " social") + '.jpg', ContentFile(avatar.read()))              
                    elif sender == TwitterBackend: 
                        profile.image_url = user.social_auth.get(provider='twitter').extra_data['profile_image_url']
                        profile.location = user.social_auth.get(provider='twitter').extra_data['location']
                    profile.save()
    
            except HTTPError:
                pass
    
    return False
 

class BroadcastManager(models.Manager):
    def create_broadcast_object(self, message, user):
        broadcast = self.create(message=message, user=user)
        return broadcast

class Broadcast(models.Model):
    message = models.TextField(_('message'), max_length=MESSAGE_MAX_LENGTH)
    user    = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_messages")

    objects = BroadcastManager()

    def __unicode__(self):
        return self.message 

class GenericWishManager(models.Manager):
    def create_generic_wish_object(self, user, message, content_type, object_id, wishimage, urlPreviewContent):
        broadcast = self.create(user=user, message=message, content_type=content_type, object_id=object_id, wishimage=wishimage, urlPreviewContent=urlPreviewContent)
        return broadcast

class BroadcastWishManager(models.Manager):
    def create_user_wish_object(self, user, blog_category, blog_parentcategory, message, content_type, object_id, wishimage, urlPreviewContent):
        broadcast = self.create(user=user, blog_category=blog_category, blog_parentcategory=blog_parentcategory, message=message, content_type=content_type, object_id=object_id, wishimage=wishimage, urlPreviewContent=urlPreviewContent)
        return broadcast

class BroadcastDealManager(models.Manager):
    def create_vendor_deal_object(self, user, blog_category, blog_parentcategory, message, content_type, object_id, wishimage, urlPreviewContent, expiry_date=None ):
        broadcast = self.create(user=user, blog_category=blog_category, blog_parentcategory=blog_parentcategory, message=message, content_type=content_type, object_id=object_id, wishimage=wishimage, urlPreviewContent=urlPreviewContent, expiry_date=expiry_date)
        return broadcast

def get_wishimage_upload_path(instance, filename):
    return os.path.join(
      "users/user_%d/" % instance.user.id, filename)


class GenericWish(Broadcast):
    comments = CommentsField(verbose_name=_("Comments"))
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=now)
    wishimage = models.OneToOneField(Original, null=True, blank=True)
    urlPreviewContent = models.TextField(blank=True, verbose_name=_("UrlPreview"))

    objects = GenericWishManager()

    def get_absolute_url(self):
        return ('view_post', [self.id])
    get_absolute_url = models.permalink(get_absolute_url)

    def __unicode__(self):
        return self.message

class BroadcastWish(GenericWish):
    blog_category = models.ForeignKey(BlogCategory,
                                        verbose_name=_("Category_wish"),
                                        blank=True, related_name="broadcast_blogcategory_wish", null=True)
    blog_parentcategory = models.ForeignKey(BlogParentCategory,
                                        verbose_name=_("ParentCategory"),
                                        blank=True, related_name="broadcast_blogparentcategory_wish", null=True)
    objects = BroadcastWishManager()

    def get_absolute_url(self):
        return ('view_wish', [self.id])
    get_absolute_url = models.permalink(get_absolute_url)

class BroadcastDeal(GenericWish):
    blog_category = models.ForeignKey(BlogCategory,
                                        verbose_name=_("Category_deal"),
                                        blank=True, related_name="broadcast_blogcategory_deal", null=True)
    blog_parentcategory = models.ForeignKey(BlogParentCategory,
                                        verbose_name=_("ParentCategory"),
                                        blank=True, related_name="broadcast_blogparentcategory_deal", null=True)

    expiry_date = models.DateField(_("expiry_date"), default=datetime_.date.today)

    objects = BroadcastDealManager()

    def get_absolute_url(self):
        return ('view_deal', [self.id])
    get_absolute_url = models.permalink(get_absolute_url)


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0]) 
pre_update.connect(new_users_handler, sender=FacebookBackend)
pre_update.connect(new_users_handler, sender=TwitterBackend)

utils.register(GenericWish)
utils.register(BroadcastWish)
utils.register(BroadcastDeal)


def comment_action(sender, comment=None, target=None, **kwargs):
    if comment.user:
        if isinstance(comment.content_object, BlogPost):
            action.send(comment.user, verb=settings.REVIEW_POST_VERB, action_object=comment.content_object, 
                target=comment)
            Follow.objects.get_or_create(comment.user, comment)
            actions.follow(comment.user, comment, send_action=False, actor_only=False) 
        elif isinstance(comment.content_object, ThreadedComment):
            action.send(comment.user, verb=settings.REVIEW_COMMENT_VERB, action_object=comment, 
                target=comment.content_object, batch_time_minutes=30, is_batchable=True)
        elif isinstance(comment.content_object, Album):
            action.send(comment.user, verb=settings.ALBUM_COMMENT_VERB, action_object=comment, 
                target=comment.content_object, batch_time_minutes=30, is_batchable=True)
        elif isinstance(comment.content_object, Image):
            action.send(comment.user, verb=settings.IMAGE_COMMENT_VERB, action_object=comment, 
                target=comment.content_object, batch_time_minutes=30, is_batchable=True)
        elif isinstance(comment.content_object, BroadcastWish):
            action.send(comment.user, verb=settings.WISH_COMMENT_VERB, action_object=comment, 
                target=comment.content_object, batch_time_minutes=30, is_batchable=True)
            Follow.objects.get_or_create(comment.user, comment.content_object)
            actions.follow(comment.user, comment.content_object, send_action=False, actor_only=False)
        elif isinstance(comment.content_object, BroadcastDeal):
            action.send(comment.user, verb=settings.DEAL_COMMENT_VERB, action_object=comment, 
                target=comment.content_object, batch_time_minutes=30, is_batchable=True)
            Follow.objects.get_or_create(comment.user, comment.content_object)
            actions.follow(comment.user, comment.content_object, send_action=False, actor_only=False)
        elif isinstance(comment.content_object, GenericWish):
            action.send(comment.user, verb=settings.POST_COMMENT_VERB, action_object=comment, 
                    target=comment.content_object, batch_time_minutes=30, is_batchable=True)
    
            Follow.objects.get_or_create(comment.user, comment.content_object)
            actions.follow(comment.user, comment.content_object, send_action=False, actor_only=False) 

comment_was_posted.connect(comment_action)