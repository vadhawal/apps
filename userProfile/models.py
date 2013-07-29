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

from mezzanine.blog.models import BlogCategory, BlogParentCategory
from mezzanine.conf import settings
from mezzanine.generic.fields import CommentsField
from django.contrib.contenttypes.models import ContentType
try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    from datetime import datetime
    now = datetime.now

from follow import utils

MESSAGE_MAX_LENGTH = getattr(settings,'MESSAGE_MAX_LENGTH',3000)
PREFIX_MESSAGE_MAX_LENGTH = getattr(settings,'PREFIX_MESSAGE_MAX_LENGTH',256)

def get_image_path(instance, filename):
    return os.path.join('users', str(instance.id), filename)

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
    profile_photo = ResizedImageField(upload_to="users/", max_width=100, max_height=80, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, choices=GENDER_CHOICES, verbose_name=_("Gender"))
    image_url = models.URLField(blank=True, verbose_name=_("Imageurl"), editable=False)
    description = models.TextField(blank=True, verbose_name=_("Description"), help_text=_("Tell us about yourself!"))
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
                        #'https://graph.facebook.com/' + user.social_auth.filter(provider="facebook")[0] + '/picture'
                        #profile.profile_photo.save(slugify(user.username + " social") + '.jpg', ContentFile(avatar.read()))              
                    elif sender == TwitterBackend: 
                        profile.image_url = user.social_auth.get(provider='twitter').extra_data['profile_image_url'] 
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

class UserWishRadioManager(models.Manager):
    def create_user_wishradio_object(self, user, prefix_message, blog_category, blog_parentcategory, message, content_type, object_id, wishimage, urlPreviewContent ):
        broadcast = self.create(user=user, prefix_message=prefix_message, blog_category=blog_category, blog_parentcategory=blog_parentcategory, message=message, content_type=content_type, object_id=object_id, wishimage=wishimage, urlPreviewContent=urlPreviewContent)
        return broadcast

def get_wishimage_upload_path(instance, filename):
    return os.path.join(
      "users/user_%d/" % instance.user.id, filename)

class UserWishRadio(Broadcast):
    prefix_message = models.TextField(_('message'), max_length=PREFIX_MESSAGE_MAX_LENGTH)
    blog_category = models.ForeignKey(BlogCategory,
                                        verbose_name=_("Category"),
                                        blank=True, related_name="broadcast_blogcategory", null=True)
    blog_parentcategory = models.ForeignKey(BlogParentCategory,
                                        verbose_name=_("ParentCategory"),
                                        blank=True, related_name="broadcast_blogparentcategory", null=True)
    comments = CommentsField(verbose_name=_("Comments"))
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=now)
    wishimage = ResizedImageField(upload_to=get_wishimage_upload_path, blank=True, null=True)
    urlPreviewContent = models.TextField(blank=True, verbose_name=_("UrlPreview"))

    objects = UserWishRadioManager()

    def __unicode__(self):
        message = self.prefix_message
        if self.blog_category:
            message += " " + self.blog_category.slug
        message += " "+self.message
        return message

    def get_absolute_url(self):
        return ('view_wish', [self.id])
    get_absolute_url = models.permalink(get_absolute_url)  

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0]) 
pre_update.connect(new_users_handler, sender=FacebookBackend)
pre_update.connect(new_users_handler, sender=TwitterBackend)

utils.register(UserWishRadio)
