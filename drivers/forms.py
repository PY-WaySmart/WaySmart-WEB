import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Repartidor

User = get_user_model()

MAX_PDF_SIZE = 5 * 1024 * 1024  # 5 MB


class RegistroRepartidorForm(forms.Form):
    nombres = forms.CharField(
        label="Nombres",
        max_length=100,
        error_messages={
            "required": "Los nombres son obligatorios.",
            "max_length": "Los nombres no pueden superar 100 caracteres.",
        },
    )
    apellidos = forms.CharField(
        label="Apellidos",
        max_length=100,
        error_messages={
            "required": "Los apellidos son obligatorios.",
            "max_length": "Los apellidos no pueden superar 100 caracteres.",
        },
    )
    email = forms.EmailField(
        label="Correo electrónico",
        error_messages={
            "required": "El correo es obligatorio.",
            "invalid": "Ingresa un correo válido.",
        },
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=20,
        error_messages={
            "required": "El teléfono es obligatorio.",
            "max_length": "El teléfono no puede superar 20 caracteres.",
        },
    )
    nro_identificacion = forms.CharField(
        label="Número de documento de identidad",
        max_length=30,
        error_messages={
            "required": "El número de documento es obligatorio.",
            "max_length": "El documento no puede superar 30 caracteres.",
        },
    )
    archivo_documento = forms.FileField(
        label="Documento de identidad (PDF)",
        help_text="Solo archivos PDF (máx. 5 MB).",
        widget=forms.FileInput(attrs={"accept": "application/pdf,.pdf"}),
        error_messages={"required": "Debes subir el PDF de tu documento de identidad."},
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        error_messages={"required": "La contraseña es obligatoria."},
    )
    password_confirmacion = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
        error_messages={"required": "Debes confirmar la contraseña."},
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo ya está registrado.")
        return email

    def clean_nro_identificacion(self):
        documento = self.cleaned_data["nro_identificacion"].strip()
        if not re.fullmatch(r"[0-9A-Za-z\-]{5,30}", documento):
            raise ValidationError(
                "El documento debe tener entre 5 y 30 caracteres (letras, números o guion)."
            )
        if Repartidor.objects.filter(nro_identificacion__iexact=documento).exists():
            raise ValidationError("Este documento ya está registrado.")
        return documento

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        if not re.fullmatch(r"[0-9+\-\s]{7,20}", telefono):
            raise ValidationError(
                "Ingresa un teléfono válido (7 a 20 caracteres; se permiten +, - y espacios)."
            )
        return telefono

    def clean_archivo_documento(self):
        archivo = self.cleaned_data["archivo_documento"]
        nombre = (archivo.name or "").strip().lower()
        content_type = (getattr(archivo, "content_type", "") or "").lower()

        # 1) Extensión .pdf obligatoria
        if not nombre.endswith(".pdf"):
            raise ValidationError("Solo se permiten archivos con extensión .pdf.")

        # 2) Tipo MIME (si el navegador lo envía)
        tipos_permitidos = {"application/pdf", "application/x-pdf"}
        if content_type and content_type not in tipos_permitidos:
            raise ValidationError("El archivo debe ser un PDF válido.")

        # 3) Tamaño máximo
        if archivo.size > MAX_PDF_SIZE:
            raise ValidationError("El PDF no puede superar 5 MB.")

        # 4) Cabecera real del PDF (%PDF)
        try:
            firma = archivo.read(5)
            archivo.seek(0)
        except Exception:
            raise ValidationError("No se pudo leer el archivo. Intenta con otro PDF.")

        if firma != b"%PDF-":
            raise ValidationError(
                "El archivo no es un PDF válido. Sube el documento en formato PDF."
            )

        return archivo

    def clean_password(self):
        password = self.cleaned_data["password"]
        try:
            validate_password(password)
        except ValidationError as exc:
            raise ValidationError(list(exc.messages))
        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirmacion = cleaned.get("password_confirmacion")
        if password and confirmacion and password != confirmacion:
            self.add_error("password_confirmacion", "Las contraseñas no coinciden.")
        return cleaned


class PerfilRepartidorForm(forms.ModelForm):
    class Meta:
        model = Repartidor
        fields = ("nombres", "apellidos", "nro_identificacion", "telefono")
        widgets = {
            "nombres": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "nro_identificacion": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "telefono": forms.TextInput(attrs={"class": "ws-input form-control"}),
        }