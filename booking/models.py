from django.db import models
from django.contrib.auth.models import User # Permet de lier la commande à un compte

class DemandePlaceArkose(models.Model):
    # Les différents états possibles pour la commande
    STATUTS = [
        ('ATTENTE', 'En attente de virement'),
        ('VALIDE', 'Payé - Place validée'),
    ]
    
    # ForeignKey relie cette demande au compte de la personne connectée
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_de_places = models.PositiveIntegerField(default=1)
    date_demande = models.DateTimeField(auto_now_add=True) # Se remplit tout seul
    statut = models.CharField(max_length=10, choices=STATUTS, default='ATTENTE')

    def __str__(self):
        # C'est le texte qui s'affichera dans l'interface d'administration
        return f"Demande de {self.utilisateur.email} - {self.nombre_de_places} place(s)"
    
class Profil(models.Model):
    # Relie ce profil à un compte utilisateur unique
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    justification = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profil de {self.user.email}"
    
class BilletArkose(models.Model):
    code_secret = models.CharField(max_length=50, unique=True)
    est_disponible = models.BooleanField(default=True)
    est_reserve = models.BooleanField(default=False)  # NOUVEAU
    proprietaire = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    commande = models.ForeignKey(  # NOUVEAU
        'DemandePlaceArkose',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billets_reserves'
    )

    def __str__(self):
        if not self.est_disponible:
            return f"Billet [{self.code_secret}] - Attribué à {self.proprietaire.username}"
        elif self.est_reserve:
            return f"Billet [{self.code_secret}] - Réservé"
        else:
            return f"Billet [{self.code_secret}] - Libre"