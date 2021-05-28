from django.contrib.auth import models
from django.db.models import fields
from rest_framework import serializers
from .models import Profile, Preference, Match 
from django.contrib.auth.models import User

# class UserSerializer(serializers.ModelSerializer):
#     user_id = serializers.PrimaryKeyRelatedField(many=True, queryset=Profile.objects.all())
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'user_id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user_id.username')
    class Meta:
        model = Profile
        fields = '__all__'

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'