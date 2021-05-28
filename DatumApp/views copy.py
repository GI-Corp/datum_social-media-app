import itertools
from datetime import date, datetime, timezone
import datetime
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.utils import tree
from DatumApp.models import Preference, Profile, Interest, Match
from DatumApp.forms import ProfileForm, PreferenceForm
from django.core.paginator import Paginator


def index(request):

    if request.user.is_authenticated:

        # Конечный set юзеров для отправки в template
        resulting_matches = set()
        your_matches_by_age = set()
        your_matches_by_interest = set()

        user = request.user
        current_profile = user.user_profile

        profiles = Profile.objects.all()

        current_age = timezone.now().date().year - current_profile.birthdate.year
        preferences = Preference.objects.filter(pref_min_age__lte=current_age, pref_max_age__gte=current_age)
        preference_profile_ids = preferences.values_list('profile_id', flat=True)
        ineterest_profile_ids = Profile.objects.filter(interests__contains=current_profile.interests).exclude(id=current_profile.id).values_list('id', flat=True)

        profile_ids = set(preference_profile_ids).intersection(set(ineterest_profile_ids))
        profiles = Profile.objects.filter(id__in=profile_ids)
                    

        # отлично, теперь у нас есть совпадения в age и interest, как out мы имеем dict
        # а еще лучше, если просто сохранить user_id с age и interest и сравнить их, если совпадают, то отправить в template
        if current_profile.user_id in resulting_matches:
            resulting_matches.remove(current_profile.user_id)

        resulting_matches = list(resulting_matches)

        print(f'Here is your final matches {request.user.first_name}: {resulting_matches}')
        num_users = len(resulting_matches)
        # matches_list = []
        # for i in range(0, num_users):
        #     matches_list.append(Profile.objects.all().filter(user_id=your_matches[i]))

        matches = Profile.objects.filter(user_id__in=resulting_matches)
        

        # почти закончил matching (like, skip functions, matched list), осталось поработать с jquery, доделать restapi и бота тг

        # LIKE & SKIP FUNCTIONS
        # if liked, status to true.
        status = True
        your_matches(request, matches, num_users, status)
        

        context = {'matches': matches, 'user_numbers': num_users}
        return render(request, 'pages/index.html', context)

        # if you like -> create Match model and add current user id, and match user id. If you skipp, do nothing. (or save id of skipped users somewhere so that they will not show up again.)
    else:
        messages.error(request, 'Please login, to access a page.')
        redirect('login')
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

    matches = Match.objects.filter(current_user=request.user, user_accepted=True)
    
    if not matches:
        messages.error(request, 'No matches here, sorry :/')
        context = {}
    else:
        requester_profile = request.user.profile
        user_requested_ids = matches.values_list('user_requested_id', flat=True)
        requester_profiles = Profile.objects.filter(user_id__in=user_requested_ids).order_by('-registered_date')

        paginator = Paginator(requester_profiles, 3) # number of profiles each page
        page = request.GET.get('page')
        page_profiles = paginator.get_page(page)
        page_profiles = paginator.get_page(page)

        context = {'profiles': page_profiles, 'profile': requester_profile, 'matches': matches}

    return render(request, 'pages/dashboard.html', context)


def dashboard_profile(request, profile_id):
    profile = get_object_or_404(Profile, pk=profile_id)    
    if profile:
        context = {'profile': profile}
    else:
        messages.error(request, 'No profile details are available')
        return redirect('dasboard')
    return render(request, 'pages/profile_details.html', context)

def profile(request):
    user = User.objects.get(username=request.user.username)
    username = user.username
    try:
        profile = get_object_or_404(Profile, tg_username=username)
        preference = get_object_or_404(Preference, p_user=user)

        profiles = Profile.objects.all().filter(tg_username=username)
        preferences = Preference.objects.all().filter(p_user=user)

    except Exception:
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
        context = {'profiles': profiles, 'profile': profile, 'preference': preference, 'preferences': preferences,'profile_does_not_exists': profile_does_not_exists, 'preference_does_not_exists': preference_does_not_exists}
        return render(request, 'pages/profile.html', context)
    
def profile_details(request, profile_id):
    user = User.objects.get(username=request.user.username)
    try:
        profile = get_object_or_404(Profile, pk=profile_id)
        preferences = get_object_or_404(Preference, p_user=user)
    except Exception:
        messages.error(request, 'No profile details are available')
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

def your_matches(request, user, quantity, status):
    user_profile = []
    print(f'{request.user.username} matches, ')
    for i in range(0, quantity):
        print(f'{i}:{user[i].first_name} {user[i].last_name}')
        user_profile.append(User.objects.get(username = user[i].tg_username))

    print(user_profile)

    accepted_matches_ids = []
    for i in range(0, quantity):
        match_exists = Match.objects.all().filter(current_user=request.user, user_requested=user_profile[i]).exists()

        if match_exists == False: # проверяем, если match уже есть, то пропускаем
            if status == True:
                match_established = Match.objects.get_or_create(current_user=request.user, user_requested=user_profile[i], user_accepted=True)
                accepted_matches_ids.append(match_established)
            else:
                match_established = Match.objects.get_or_create(current_user=request.user, user_requested=user_profile[i], user_accepted=False)
                # здесь, user_accepted = False, потому что второй юзер пока не принял запрос

            print(match_established)
        print(f'Accepted matches ids: {accepted_matches_ids}')
    # if match_exists == True:
    #     dashboard(request, match_established)

def feed(request):
    user = User.objects.get(username=request.user.username)
    username = user.username
    try:
        profile = get_object_or_404(Profile, tg_username=username)
        preferences = get_object_or_404(Preference, p_user=user)

        profiles = Profile.objects.all()
        preferences = Preference.objects.all()

        print(profiles)
        print(preferences)

    except Exception:
        messages.error(request, 'No profile details are available')
        return redirect('dasboard')
    else:
        context = {'profile': profile, 'preferences': preferences}
        return render(request, 'pages/index.html', context)