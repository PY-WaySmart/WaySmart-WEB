from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError

from companies.models import Empresa
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
    business_name = forms.CharField(
        label="Razón social",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
    )
    nit = forms.CharField(
        label="NIT",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
    )
    business_address = forms.CharField(
        label="Dirección de la empresa",
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
    )
    business_phone = forms.CharField(
        label="Teléfono de contacto",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
    )
    legal_name = forms.CharField(
        label="Nombre del representante legal",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
    )
    legal_phone = forms.CharField(
        label="Teléfono del representante",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
    )
    legal_email = forms.EmailField(
        label="Correo del representante",
        required=False,
        widget=forms.EmailInput(attrs={"class": "ws-input form-control"}),
    )
    tipo_colaboracion = forms.ChoiceField(
        label="Tipo de colaboración",
        required=False,
        choices=Empresa.TipoColaboracion.choices,
        widget=forms.Select(attrs={"class": "ws-input form-select"}),
    )
    identification = forms.CharField(
        label="Número de identificación",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
    )
    phone = forms.CharField(
        label="Teléfono",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
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

    def clean_nit(self):
        nit = self.cleaned_data["nit"].strip()
        if nit and Empresa.objects.filter(nit__iexact=nit).exists():
            raise forms.ValidationError("Ya existe una empresa registrada con este NIT.")
        return nit

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        role_fields = (
            {
                "business_name": "La razón social es obligatoria.",
                "nit": "El NIT es obligatorio.",
                "business_address": "La dirección de la empresa es obligatoria.",
                "business_phone": "El teléfono de contacto es obligatorio.",
                "legal_name": "El nombre del representante es obligatorio.",
                "legal_phone": "El teléfono del representante es obligatorio.",
                "legal_email": "El correo del representante es obligatorio.",
                "tipo_colaboracion": "Selecciona un tipo de colaboración.",
            }
            if role == Perfil.Rol.EMPRESA
            else {
                "identification": "El número de identificación es obligatorio.",
                "phone": "El teléfono es obligatorio.",
            }
        )
        for field, error in role_fields.items():
            if not cleaned_data.get(field):
                self.add_error(field, error)

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