from DatumApp.api_test import ProfileDelete
from rest_framework import exceptions, generics
from rest_framework.exceptions import ValidationError
from django.db.models import manager, query
from rest_framework import serializers
from DatumApp.models import Match, Profile, Preference
from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
from django.shortcuts import render
from django.http import JsonResponse, response
from rest_framework import status

from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import reverse
from .serializers import ProfileSerializer, PreferenceSerializer, MatchSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'profiles': reverse('profile-list', request=request, format=format)
    })

from rest_framework import renderers
from rest_framework.response import Response

class ProfileTelegram(generics.GenericAPIView):
    queryset = Profile.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        return Response(profile.tg_username)

class MatchedProfiles(generics.GenericAPIView):
    queryset = Match.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]

    def get(self, request, *args, **kwargs):
        match = self.get_object()
        return Response(f'{match.current_user} matches {match.user_requested}')

@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'List': 'profile-list, preference-list, match-list, user-list',
        'Detail view': 'profile-detail/<int:id>, preference-detail/<int:id>, match-detail/<int:match_id>',
        'Create': 'profile-create, preference-create, match-create, user-create',
        'Update': 'profile-update/<int:id>, preference-update/<int:id>, match-update/<int:id>',
        'Delete': 'profile-delete/<int:id>, preference-delete/<int:id>, match-delete/<int:id>, user-delete/<int:id>',
    }
    return Response(api_urls)

# profile api
@api_view(['GET'])
def profileList(request):
    profiles = Profile.objects.all()
    serializer = ProfileSerializer(profiles, many=True)
    return Response(serializer.data)

@csrf_exempt
@api_view(['GET'])
def profileDetail(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    serializer = ProfileSerializer(profile, many=False)
    return Response(serializer.data)

@csrf_exempt
@api_view(['POST'])
def profileCreate(request):
    serializer = ProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@csrf_exempt
@api_view(['PUT'])
def profileUpdate(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    serializer = ProfileSerializer(instance=profile, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def profileDelete(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    profile.delete()
    return Response('Profile is successfully deleted.')

# preference api
@api_view(['GET'])
def preferenceList(request):
    preference = Preference.objects.all()
    serializer = PreferenceSerializer(preference, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def preferenceDetail(request, preference_id):
    preference = Preference.objects.get(id=preference_id)
    serializer = PreferenceSerializer(preference, many=False)
    return Response(serializer.data)

@csrf_exempt
@api_view(['POST'])
def preferenceCreate(request):
    serializer = PreferenceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@csrf_exempt
@api_view(['PUT'])
def preferenceUpdate(request, preference_id):
    preference = Preference.objects.get(id=preference_id)
    serializer = PreferenceSerializer(instance=preference, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def preferenceDelete(request, preference_id):
    preference = Preference.objects.get(id=preference_id)
    preference.delete()
    return Response('Preference is successfully deleted.')

# match api
@api_view(['GET'])
def matchList(request):
    match = Match.objects.all()
    serializer = MatchSerializer(match, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def matchDetail(request, match_id, format=None):
    match = Match.objects.get(id=match_id)
    serializer = MatchSerializer(match, many=False)
    return Response(serializer.data)

@csrf_exempt
@api_view(['POST'])
def matchCreate(request):
    serializer = MatchSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@csrf_exempt
@api_view(['PUT'])
def matchUpdate(request, match_id):
    match = Match.objects.get(id=match_id)
    serializer = MatchSerializer(instance=match, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def matchDelete(request, match_id):
    try:
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        match.delete()
        return Response('Preference is successfully deleted.')

# endpoints
