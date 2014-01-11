from django import forms
from mezzanine.forms.models import Form
from django.utils.translation import ugettext_lazy as _

class SuggestStoreForm(forms.Form):
    email_from = forms.EmailField()
    email_subject = forms.CharField(max_length=200)
    email_message = forms.CharField()