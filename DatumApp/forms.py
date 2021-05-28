from django.db import models
from django.db.models import fields
from DatumApp.models import Interest, Profile, Preference, Match
from django.forms import ModelForm
from django import forms

class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ['interest_title']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ('user_id', 'first_name', 'last_name', 'tg_username', 'registered_date', 'last_update_date',)

class PreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = '__all__'
        exclude = ('p_user',)




