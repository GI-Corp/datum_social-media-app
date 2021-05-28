from os import pathsep, utime
from Datum.settings import AUTH_PASSWORD_VALIDATORS
from django.urls import path, include

from DatumApp import api_test
from . import views
from . import api
from DatumApp.api_test import ProfileList, UserCreate
from django.contrib import admin
from django.conf.urls import include, re_path
from rest_framework.urlpatterns import format_suffix_patterns



# router = DefaultRouter()
# router.register(match, MatchViewSet, base_name='match')

urlpatterns = [
    path('', views.index, name='index'),
    
    path('profile', views.profile, name='profile'),
    path('profile_details/<int:profile_id>', views.profile_details, name='profile_details'),

    path('create_profile', views.create_profile, name='create_profile'),
    path('create_prefs', views.create_prefs, name='create_prefs'),
    path('update_profile/<int:profile_id>', views.update_profile, name='update_profile'),
    path('update_prefs/<int:preference_id>', views.update_prefs, name='update_prefs'),

    path('dashboard_profile/<int:profile_id>', views.dashboard_profile, name='dashboard_profile'),
    path('dashboard', views.dashboard, name='dashboard'),

    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    # APIs
    path('api', api.apiOverview, name='apiOverview'),
    # User API
    path('user-list/', api_test.UserList.as_view()),
    path('user-detail/<int:pk>', api_test.UserDetail.as_view()),
    path('user-create/', api_test.UserCreate.as_view()),
    path('user-delete/<int:pk>', api_test.UserDelete.as_view()),
    # Profile API
    path('profile-list/', api_test.ProfileList.as_view()),
    path('profile-detail/<int:pk>', api_test.ProfileDetail.as_view()),
    path('profile-create/', api_test.ProfileCreate.as_view()),
    path('profile-update/<int:pk>', api_test.ProfileUpdate.as_view()),
    path('profile-delete/<int:pk>', api_test.ProfileDelete.as_view()),
    # Preference API
    path('preference-list/', api.preferenceList, name='preference-list'),
    path('preference-detail/<int:pk>', api.preferenceDetail, name='preference-detail'),
    path('preference-create/', api.preferenceCreate, name='preference-create'),
    path('preference-update/<int:pk>', api.preferenceUpdate, name='preference-update'),
    path('preference-delete/<int:pk>', api.preferenceDelete, name='preference-delete'),
    # Match API
    path('match-list/', api.matchList, name='match-list'),
    path('match-detail/<int:pk>', api.matchDetail, name='match-detail'),
    path('match-create/', api.matchCreate, name='match-create'),
    path('match-update/<int:pk>', api.matchUpdate, name='match-update'),
    path('match-delete/<int:pk>', api.matchDelete, name='match-delete'),

    # endpoints
    path("api-root", api.api_root, name="api-root"),
    path("profile/<int:pk>/tg-username", api.ProfileTelegram.as_view()),
    path("match/<int:pk>/profiles", api.MatchedProfiles.as_view()),
    

]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]