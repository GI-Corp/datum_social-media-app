import itertools
from datetime import date, datetime, timezone
import datetime
from django import http
from django.db.models.fields import NullBooleanField
from django.http import request
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.utils import tree
from DatumApp.models import Preference, Profile, Interest, Match
from DatumApp.forms import ProfileForm, PreferenceForm
from django.core.paginator import Paginator

# сделать rest api (done)
# сделать бота тг (starting from 27th May)

def index(request):
    
    if request.user.is_authenticated and Profile.objects.filter(user_id=request.user, birthdate__lte=datetime.datetime.now().date()).exists():

        current_user = get_current_user(request)

        try:
            current_profile = get_current_user_profile(request)
            current_profile_interest = get_current_user_interests(request)
            min_year = datetime.datetime.now().date().year - current_user.user_preference.pref_min_age + 1
            max_year = datetime.datetime.now().date().year - current_user.user_preference.pref_max_age - 1
            min_date = str(min_year) + '-' + '01-01'
            max_date = str(max_year) + '-' + '01-01'

            users_age = Profile.objects.filter(birthdate__lte = min_date, birthdate__gte = max_date).exclude(id=current_profile.id).values_list('user_id', flat=True)

            users_interests = Profile.objects.filter(interest__in=current_profile_interest).exclude(id=current_profile.id).values_list('user_id', flat=True)

            resulting_matches = set(users_interests).intersection(users_age)
            num_users = len(resulting_matches)
            print(f'final matches: {resulting_matches}')

        except Exception as e:
            messages.error(request, f'Nobody suits to your preferences. Error: {e}')
            return redirect('profile')
        else:
            matches = Profile.objects.filter(user_id__in=resulting_matches)
            # LIKE & SKIP METHODS
            if request.method == "POST":
                if request.POST.get('Skip') == 'Skip':
                    status = False
                    matches = matches.exclude(tg_username = request.POST.get('user_id'))
                    your_partner = request.POST.get('user_id')
                    your_matches(request, your_partner, status)
                    messages.warning(request, 'You skipped this person.')
                if request.POST.get('Like') == 'Like':
                    status = True
                    your_partner = request.POST.get('user_id')
                    your_matches(request, your_partner, status)
                    messages.success(request, f'You liked this person.')

            check_for_matches = Match.objects.filter(current_user=request.user, user_requested__in=resulting_matches).values_list('user_requested__username', flat=True)

            num_of_excluded = len(check_for_matches)
            
            print(f'Number of excluded profiles (already exist): {num_of_excluded}')
            print(f'Matches (already exist):  {check_for_matches}')

            if check_for_matches:
                matches = matches.exclude(tg_username__in = check_for_matches)
                context = {'matches': matches, 'user_numbers': num_users-num_of_excluded}
            else:
                context = {'matches': matches, 'user_numbers': num_users}
            return render(request, 'pages/index.html', context)
    else:
        messages.error(request, 'Please update/fill your profile and preference details.')
        redirect('profile')
        return render(request, 'pages/index.html')

def register(request):
    if request.method == 'POST':
        # Get form values
        tg_username = request.POST.get('tg_username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        tg_username = '@' + tg_username 

        # Check if passwords match
        if password == password2:
            # Check tg_username
            if User.objects.filter(username=tg_username).exists():
                messages.error(request, 'That username is already taken')
                return redirect('register')
            else:
                # Success
                user = User.objects.create_user(username=tg_username, password = password, first_name=first_name, last_name=last_name)
                # Login after register
                auth.login(request, user)
                profile = Profile.objects.get_or_create(user_id=request.user, first_name=first_name, last_name=last_name, tg_username=tg_username)
                preference = Preference.objects.get_or_create(p_user=request.user)
                messages.success(request, 'You are now logged in')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, 'pages/register.html')

def login(request):
    if request.method == 'POST':
        tg_username = request.POST.get('tg_username')
        password = request.POST.get('password')

        user = auth.authenticate(username=tg_username, password=password)
        
        print(tg_username)
        print(password)
        if user is not None:
            auth.login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    else:
        return render(request, 'pages/login.html')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return redirect('login')

def dashboard(request):

    mutual_matched_user_ids = check_for_mutual_like(request)
    matches = Match.objects.filter(current_user=request.user, user_requested__in=mutual_matched_user_ids).values_list('user_requested', flat=True)
    print(matches)
    
    if not matches:
        messages.error(request, 'No matches here, sorry :/')
        context = {}
    else:
        requester_profile = Profile.objects.filter(user_id = request.user)
        requester_profiles = Profile.objects.filter(user_id__in=matches).order_by('-first_name')

        paginator = Paginator(requester_profiles, 3) # number of profiles each page
        page = request.GET.get('page')
        page_profiles = paginator.get_page(page)
        page_profiles = paginator.get_page(page)

        context = {'profiles': page_profiles, 'profile': requester_profile, 'matches': matches}

    return render(request, 'pages/dashboard.html', context)

def dashboard_profile(request, profile_id):
    profile = get_object_or_404(Profile, pk=profile_id)
    profile_user_id = profile.user_id
    preference = Preference.objects.get(p_user=profile_user_id)
    if profile:
        context = {'profile': profile, 'preference':preference}
    else:
        messages.error(request, 'No profile details are available')
        return redirect('dasboard')
    return render(request, 'pages/profile_details.html', context)

def profile(request):
    user = User.objects.get(username=request.user.username)
    try:
        profile = get_object_or_404(Profile, user_id=user)
        preference = get_object_or_404(Preference, p_user=user)

        profiles = Profile.objects.all().filter(user_id=user)
        preferences = Preference.objects.all().filter(p_user=user)

    except Exception as e:
        print(e)
        profile_does_not_exists = True
        preference_does_not_exists = True
        context = {
            'profile_does_not_exists': profile_does_not_exists, 
            'preference_does_not_exists': preference_does_not_exists
        }
        return render(request, 'pages/profile.html', context)

    else:
        profile_does_not_exists = False
        preference_does_not_exists = False
        context = {
            'profiles': profiles, 
            'profile': profile, 
            'preference': preference, 
            'preferences': preferences,
            'profile_does_not_exists': profile_does_not_exists, 
            'preference_does_not_exists': preference_does_not_exists
            }
        return render(request, 'pages/profile.html', context)
    
def profile_details(request, profile_id):
    user = User.objects.get(username=request.user.username)
    try:
        profile = get_object_or_404(Profile, pk=profile_id)
        preferences = get_object_or_404(Preference, p_user=user)
    except Exception as e:
        messages.error(request, f'No profile details are available, error: {e}')
        return redirect('dasboard')
    else:
        context = {'profile': profile, 'preferences': preferences}
        return render(request, 'pages/profile_details.html', context)

def create_profile(request):

    form = ProfileForm()

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            telegram_username = request.user.username
            first_name = request.user.first_name
            last_name = request.user.last_name
            last_update_date = datetime.datetime.now()

            add = form.save(commit=False)
            add.user_id = User.objects.get(id=request.user.id)
            add.first_name = first_name
            add.last_name = last_name
            add.registered_date = request.user.date_joined
            add.last_update_date = last_update_date
            form.save()
            messages.success(request, 'Profile is updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = ProfileForm()

    context = {'form': form}
    return render(request, 'pages/create_profile.html', context)

def create_prefs(request):

    form = PreferenceForm()
    if request.method == "POST":
        if request.user.is_authenticated:
            form = PreferenceForm(request.POST, request.FILES)
            if form.is_valid():
                prefs = form.save(commit=False)
                prefs.p_user = User.objects.get(id=request.user.id)
                prefs.save()
                messages.success(request, 'Preferences are updated.')
            else:
                messages.error(request, 'Form is not valid.')
    else:
        form = PreferenceForm()

    context = {
        'form': form
    }
    return render(request, 'pages/create_prefs.html', context)

def update_profile(request, profile_id):

    profile = get_object_or_404(Profile, pk=profile_id)
    form = ProfileForm(instance=profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            telegram_username = request.user.username
            first_name = request.user.first_name
            last_name = request.user.last_name
            last_update_date = datetime.datetime.now()

            add = form.save(commit=False)
            add.user_id = User.objects.get(id=request.user.id)
            add.tg_username = telegram_username
            add.first_name = first_name
            add.last_name = last_name
            add.registered_date = request.user.date_joined
            add.last_update_date = last_update_date
            form.save()
            messages.success(request, 'Profile is updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = ProfileForm(instance=profile)

    context = {'form': form, 'profile': profile}
    return render(request, 'pages/update_profile.html', context)

def update_prefs(request, preference_id):
    
    preference = get_object_or_404(Preference, pk=preference_id)
    form = PreferenceForm(instance=preference)
    if request.method == "POST":
        if request.user.is_authenticated:
            form = PreferenceForm(request.POST, request.FILES, instance=preference)
            if form.is_valid():
                prefs = form.save(commit=False)
                prefs.p_user = User.objects.get(id=request.user.id)
                prefs.save()
                messages.success(request, 'Preferences are updated.')
            else:
                messages.error(request, 'Form is not valid.')
    else:
        form = PreferenceForm(instance=preference)

    context = {'form': form, 'preference': preference}
    return render(request, 'pages/update_prefs.html', context)

def your_matches(request, your_partner, status):

    partner = User.objects.get(username=your_partner)

    match_exists = Match.objects.filter(current_user=request.user, user_requested=partner).exists()
    if not match_exists: # проверяем, если match уже есть, то пропускаем
        if status == True:
            match_established = Match.objects.get_or_create(current_user=request.user, user_requested=partner, user_accepted=True)
        else:
            match_established = Match.objects.get_or_create(current_user=request.user, user_requested=partner, user_accepted=False)
            # здесь, user_accepted = False, потому что второй юзер пока не принял запрос, скипаем этого юзера и больше не показываем в homepage

            print(match_established)

def get_current_user_matches(request):
    my_matches = Match.objects.filter(current_user = request.user)
    return my_matches

def get_current_user_profile(request):
    current_user_profile = get_object_or_404(Profile, pk=request.user.user_profile.id)    
    return current_user_profile

def get_current_user(request):
    current_user = User.objects.get(username = request.user.username)
    return current_user

def get_current_user_preference(request):
    my_preference = Preference.objects.filter(p_user = request.user)
    return my_preference

def get_current_user_interests(request):
    my_interests = Profile.objects.filter(user_id = request.user).values_list('interest', flat=True)
    return my_interests

def check_for_mutual_like(request):
    current_user_like = Match.objects.filter(current_user=request.user, user_accepted=True).values_list('user_requested', flat=True)
    other_user_like = Match.objects.filter(current_user__in=current_user_like, user_accepted=True).values_list('current_user', flat=True).exclude(current_user=request.user)
    mutual_user_ids = set(current_user_like).intersection(set(other_user_like))
    return list(mutual_user_ids)