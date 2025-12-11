from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.generic import FormView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .forms import AppPasswordResetForm
from .models import UserLoginAttempt, User

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')
        user = authenticate(username=username, password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return redirect('core:home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return render(request, 'core/logout_done.html')
    return render(request, 'core/logout_confirm.html')

class AppPasswordResetView(FormView):
    template_name = 'core/password_reset.html'
    form_class = AppPasswordResetForm
    success_url = '/accounts/login/'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = User.objects.get(email=email)
        if user:
            subject = 'Password Reset Requested'
            email_template_name = 'core/password_reset_email.txt'
            context = {
                'email': user.email,
                'domain': get_current_site(self.request).domain,
                'site_name': 'Website',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if self.request.is_secure() else 'http',
            }
            email = EmailMultiAlternatives(
                subject,
                render_to_string(email_template_name, context),
                'noreply@yourdomain.com',
                [user.email],
            )
            email.send(fail_silently=False)
        return super().form_valid(form)

@login_required
def delete_account_view(request):
    user = request.user
    if request.method == 'POST':
        # Perform account deletion logic
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('core:home')
    return render(request, 'core/delete_account.html', {'user': user})
