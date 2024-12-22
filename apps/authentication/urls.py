from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from . import views

app_name = "authentication"

urlpatterns = [
    path(
        "login/",
        never_cache(csrf_protect(views.CustomLoginView.as_view())),
        name="login",
    ),
    path(
        "logout/",
        never_cache(auth_views.LogoutView.as_view(next_page="authentication:login")),
        name="logout",
    ),
    path("signup/", never_cache(csrf_protect(views.signup)), name="signup"),
    path(
        "password_reset/",
        never_cache(
            csrf_protect(
                auth_views.PasswordResetView.as_view(
                    template_name="authentication/password_reset.html",
                    email_template_name="authentication/password_reset_email.html",
                    html_email_template_name="authentication/password_reset_email.html",
                    subject_template_name="authentication/password_reset_subject.txt",
                )
            )
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="authentication/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="authentication/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="authentication/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "verify-email/<str:uidb64>/<str:token>/",
        views.verify_email,
        name="verify_email",
    ),
    path(
        "resend-verification-email/",
        views.resend_verification_email,
        name="resend_verification_email",
    ),
]
