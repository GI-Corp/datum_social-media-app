from django.db import models
import datetime
from datetime import datetime, timezone, time
from django.contrib.auth.models import User
from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms.widgets import DateInput

# Create your models here.

class Interest(models.Model):

    interest_title = models.CharField(max_length=300, null=True)
    is_available = models.BooleanField(default=True, null=True)

    class Meta:
        verbose_name = "Interest"
        verbose_name_plural = "Interests"

    def __str__(self):
        return self.interest_title

class Profile(models.Model):

    male = "Male"
    female = "Female"

    GENDER = [
        (male, "Male"),
        (female, "Female"),
    ]
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, default=None, related_name='user_profile')
    first_name = models.CharField(max_length=300, null=True)
    last_name = models.CharField(max_length=300, null=True)
    birthdate = models.DateField(null=True, help_text='format: YYYY-MM-DD')
    gender = models.CharField(max_length=100, null=True, choices=GENDER)
    tg_username = models.CharField(max_length=300, null=True, unique=True, help_text='format: @gi_corp')
    interest = models.ManyToManyField(Interest, blank=True, related_name='profile_interests')
    photo = models.ImageField(upload_to='user_photos/%Y/', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True)
    registered_date = models.DateTimeField(default=datetime.now, null=True)
    last_update_date = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return str(self.tg_username)

    def full_name(self):
        return str(self.first_name + self.last_name)

    def display_interests(self):
        return ', '.join([a.interest_title for a in self.interest.all()])

    def get_age(self):
        return datetime.now().date().year - self.birthdate.year


class Preference(models.Model):
    p_user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, related_name='user_preference')
    pref_min_age = models.IntegerField(null=True)
    pref_max_age = models.IntegerField(null=True)
    def __str__(self):
        return str(self.p_user)

class Match(models.Model):
    current_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, help_text='current user', related_name='user_match')
    user_requested = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None, help_text='whom you liked', related_name='user_match_you')
    user_accepted = models.BooleanField(default=False, null=True, help_text='if user accepts your match then, this switches to True')

    is_active = models.BooleanField(default=True, null=True, help_text='used to remove match connection')

    def __str__(self):
        return str(self.current_user)

    def get_match(self):
        return str(self.current_user + self.user_requested)

    def get_curret_user(self):
        return str(self.current_user)

    def get_user_you_liked(self):
        return str(self.user_requested)

    class Meta:
        verbose_name_plural = 'Matches'
