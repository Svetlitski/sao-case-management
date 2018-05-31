from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse


# Caseworker login page
class OfficeLoginView(LoginView):
    template_name = 'login.html'


# Used for logout button, simply redirects to login page
def logout_view(request):
    logout(request)
    return redirect(settings.LOGIN_REDIRECT_URL)


@login_required
def home_view(request):
    return redirect(reverse('cases:case_list'))
