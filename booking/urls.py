from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('achat/', views.achat, name='achat'),
    path('connexion/', views.connexion, name='connexion'),
    path('tresorier/', views.dashboard_tresorier, name='dashboard_tresorier'),
    path('tresorier/valider-compte/<int:user_id>/', views.valider_compte, name='valider_compte'),
    path('tresorier/valider-commande/<int:commande_id>/', views.valider_commande, name='valider_commande'),
    path('tresorier/refuser-compte/<int:user_id>/', views.refuser_compte, name='refuser_compte'),
    path('tresorier/refuser-commande/<int:commande_id>/', views.refuser_commande, name='refuser_commande'),
    path('tresorier/importer/', views.importer_billets, name='importer_billets'),
    path('deconnexion/', LogoutView.as_view(next_page='/'), name='logout'),
]