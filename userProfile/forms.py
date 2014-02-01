from django import forms
from mezzanine.forms.models import Form
from django.utils.translation import ugettext_lazy as _

class SuggestStoreForm(forms.Form):
    email_from = forms.EmailField()
    email_subject = forms.CharField(max_length=200)
    email_message = forms.CharField()

class ContactUsForm(forms.Form):
    email_from = forms.EmailField(label=_("From"))
    email_subject = forms.CharField(label=_("Subject"), max_length=200)
    email_message = forms.CharField(label=_("Message"), widget=forms.Textarea(attrs={'size':'40'}))