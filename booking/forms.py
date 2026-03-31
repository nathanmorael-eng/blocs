from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import DemandePlaceArkose

class CommandeForm(forms.ModelForm):
    class Meta:
        model = DemandePlaceArkose
        fields = ['nombre_de_places']
        labels = {
            'nombre_de_places': 'Combien de places souhaitez-vous ?'
        }

class InscriptionAssosForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Utilisez votre adresse @student-cs.fr ou @centralesupelec.fr."
    )
    justification = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Remplissez ce champ si vous n'avez pas d'adresse CentraleSupélec."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Plus de champ username — seulement email + mots de passe
        fields = ('email', 'password1', 'password2')

class ConnexionEmailForm(forms.Form):
    email = forms.EmailField(label="Adresse email")
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # On cherche l'utilisateur par email
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("Aucun compte trouvé avec cet email.")

            # On vérifie le mot de passe
            user = authenticate(username=user_obj.username, password=password)
            if user is None:
                raise forms.ValidationError("Mot de passe incorrect.")
            if not user.is_active:
                raise forms.ValidationError("Votre compte est en attente de validation.")

            # On stocke l'utilisateur pour le récupérer dans la vue
            self.user = user

        return cleaned_data

    def get_user(self):
        return self.user