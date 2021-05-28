from django.contrib import admin
from DatumApp.models import Profile, Interest, Preference, Match
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'birthdate', 'gender', 'tg_username')
    list_display_links = ('id', 'first_name', 'last_name')
    list_filter = ('tg_username',)
    search_fields = ('first_name', 'last_name', 'tg_username')
    list_per_page = 30

class MatchAdmin(admin.ModelAdmin):
    list_display = ('current_user', 'user_requested', 'user_accepted')
    list_display_links = ('current_user', 'user_requested')
    list_per_page = 15

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Interest)
admin.site.register(Preference)
admin.site.register(Match, MatchAdmin)