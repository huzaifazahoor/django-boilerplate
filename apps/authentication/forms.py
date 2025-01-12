from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "you@example.com",
            }
        ),
    )
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "username",
            }
        ),
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "John",
            }
        ),
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Doe",
            }
        ),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "*********",
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "*********",
            }
        )
    )

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError(_("This email address is already in use."))
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            if CustomUser.objects.filter(username=username).exists():
                raise forms.ValidationError(_("This username is already in use."))
            if (
                not username.replace("_", "")
                .replace("-", "")
                .replace(".", "")
                .replace("@", "")
                .replace("+", "")
                .isalnum()
            ):
                raise forms.ValidationError(
                    _("Username can only contain letters, digits and @/./+/-/_")
                )
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data.get("username")
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    password = None

    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    username = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    first_name = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = CustomUser
        fields = ("email", "username", "first_name", "last_name")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            if (
                CustomUser.objects.exclude(pk=self.instance.pk)
                .filter(username=username)
                .exists()
            ):
                raise forms.ValidationError(_("This username is already in use."))
            if (
                not username.replace("_", "")
                .replace("-", "")
                .replace(".", "")
                .replace("@", "")
                .replace("+", "")
                .isalnum()
            ):
                raise forms.ValidationError(
                    _("Username can only contain letters, digits and @/./+/-/_")
                )
        return username
