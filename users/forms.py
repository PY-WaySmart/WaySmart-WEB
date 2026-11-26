from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError

from .models import Perfil

User = get_user_model()


class WaySmartPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {
                "class": "ws-input form-control",
                "placeholder": "nombre@empresa.com",
                "autocomplete": "email",
            }
        )


class WaySmartSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "ws-input form-control",
                    "autocomplete": "new-password",
                }
            )


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": "nombre@empresa.com",
                "class": "ws-input form-control",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": "Ingresa tu contraseña",
                "class": "ws-input form-control",
            }
        ),
    )
    remember_me = forms.BooleanField(
        label="Mantener sesión iniciada",
        required=False,
    )


class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "ws-input form-control", "placeholder": "Tu nombre"}),
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "ws-input form-control", "placeholder": "Tus apellidos"}),
    )
    username = forms.CharField(
        label="Nombre de usuario",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "ws-input form-control", "placeholder": "nombre_usuario"}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "ws-input form-control", "placeholder": "nombre@empresa.com"}),
    )
    role = forms.ChoiceField(
        label="Tipo de cuenta",
        choices=(
            (Perfil.Rol.EMPRESA, "Empresa"),
            (Perfil.Rol.REPARTIDOR, "Repartidor"),
        ),
        widget=forms.Select(attrs={"class": "ws-input form-select"}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "ws-input form-control", "autocomplete": "new-password"}),
    )
    password_confirmation = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "ws-input form-control", "autocomplete": "new-password"}),
    )
    terms = forms.BooleanField(
        label="Acepto los términos y condiciones",
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está registrado.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmation = cleaned_data.get("password_confirmation")
        if password and confirmation and password != confirmation:
            self.add_error("password_confirmation", "Las contraseñas no coinciden.")
        if password:
            try:
                validate_password(password)
            except ValidationError as error:
                self.add_error("password", error)
        return cleaned_data