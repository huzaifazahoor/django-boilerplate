from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    username = models.CharField(
        _("username"),
        max_length=150,
        blank=True,
        null=True,
        help_text=_(
            "Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        unique=True,
    )
    first_name = models.CharField(
        _("first name"),
        max_length=150,
        blank=False,
        help_text=_("Required. Enter your first name."),
    )
    last_name = models.CharField(
        _("last name"),
        max_length=150,
        blank=False,
        help_text=_("Required. Enter your last name."),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this user should be treated as active."),
    )
    is_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("Designates whether this user has verified their email address."),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
