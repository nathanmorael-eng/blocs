from django.contrib import admin
from .models import DemandePlaceArkose, BilletArkose

@admin.register(DemandePlaceArkose)
class DemandePlaceArkoseAdmin(admin.ModelAdmin):
    # Les colonnes qui s'afficheront dans le tableau du trésorier
    list_display = ('utilisateur', 'nombre_de_places', 'statut', 'date_demande')
    
    # Ajoute un menu sur la droite pour trier les commandes par statut
    list_filter = ('statut',)
    
    # Ajoute une barre de recherche pour trouver un utilisateur rapidement
    search_fields = ('utilisateur__username',)

@admin.register(BilletArkose)
class BilletArkoseAdmin(admin.ModelAdmin):
    list_display = ('code_secret', 'est_disponible', 'proprietaire')
    list_filter = ('est_disponible',)