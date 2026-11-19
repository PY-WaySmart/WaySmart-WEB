from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": "nombre@empresa.com",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": "Ingresa tu contraseña",
            }
        ),
    )
    remember_me = forms.BooleanField(
        label="Mantener sesión iniciada",
        required=False,
    )