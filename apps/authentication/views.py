from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from .forms import CustomUserCreationForm
from .models import CustomUser
from .tokens import email_verification_token


class CustomLoginView(LoginView):
    template_name = "authentication/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_verified:
            messages.warning(
                self.request,
                _(
                    "Please verify your email first. Need a new verification email? "
                    '<a href="{}">Click here</a>.'.format(
                        reverse("resend_verification_email")
                    )
                ),
            )
            return self.form_invalid(form)
        return super().form_valid(form)


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False
            user.save()

            # Send verification email
            send_verification_email(request, user)

            messages.success(
                request,
                _(
                    "Please check your email to verify your account. "
                    "This helps ensure accurate data and improves your experience."
                ),
            )
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "authentication/signup.html", {"form": form})


def send_verification_email(request, user):
    """Helper function to send verification email"""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    verification_link = request.build_absolute_uri(
        reverse("verify_email", args=[uid, token])
    )

    # Use HTML email template
    html_message = render_to_string(
        "authentication/email/verification_email.html",
        {"user": user, "verification_link": verification_link},
    )

    # Plain text version
    plain_message = (
        f"Hi {user.first_name},\n\n"
        f"Please click this link to verify your email: {verification_link}\n\n"
        "If you didn't request this, you can safely ignore this email."
    )

    send_mail(
        _("Verify your email address"),
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


@require_http_methods(["GET"])
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        if user.is_verified:
            messages.info(request, _("Your email was already verified."))
        else:
            user.is_verified = True
            user.save()
            login(request, user)
            messages.success(request, _("Your email has been verified. Welcome!"))
        return redirect("home")

    messages.error(
        request,
        _(
            "The verification link was invalid or has expired. "
            '<a href="{}">Request a new one</a>.'.format(
                reverse("resend_verification_email")
            )
        ),
    )
    return redirect("login")


@login_required
@require_http_methods(["GET"])
def resend_verification_email(request):
    user = request.user

    if user.is_verified:  # Note: changed from is_verify
        messages.info(request, _("Your account is already verified."))
    else:
        # Implement rate limiting
        if should_throttle_email(user):
            messages.error(
                request, _("Please wait before requesting another verification email.")
            )
        else:
            send_verification_email(request, user)
            messages.success(
                request,
                _("Verification email has been resent. Please check your inbox."),
            )

    return redirect("home")


def should_throttle_email(user):
    """
    Implement rate limiting for email sending.
    You can use cache or database to store the last email sent timestamp.
    """
    # Implementation example using cache:
    from datetime import datetime, timedelta

    from django.core.cache import cache

    THROTTLE_MINUTES = 2
    cache_key = f"last_verification_email_{user.pk}"
    last_sent = cache.get(cache_key)

    if last_sent:
        time_passed = datetime.now() - last_sent
        if time_passed < timedelta(minutes=THROTTLE_MINUTES):
            return True

    cache.set(cache_key, datetime.now(), timeout=300)
    return False
