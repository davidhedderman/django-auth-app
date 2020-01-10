from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import ProfileUserCreationForm


class SignUpView(CreateView):
    form_class = ProfileUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


@login_required
def user_admin(request):
    """
    User admin page for viewing/managing users. Not as much access as admin access
    :param request: request object
    :return: redirect to the correct page depending if user is logged in and can view user-admin
    """
    if not request.user.can_access_user_admin:
        return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'profiles/user_admin.html', {})
