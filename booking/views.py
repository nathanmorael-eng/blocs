from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import CommandeForm, InscriptionAssosForm
from .models import DemandePlaceArkose, Profil, BilletArkose
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from .forms import CommandeForm, InscriptionAssosForm, ConnexionEmailForm
from django.core.mail import send_mail

# 1. Page d'accueil (Publique)
def accueil(request):
    return render(request, 'accueil.html')

# 2. Page d'inscription / Connexion
def inscription(request):
    if request.method == 'POST':
        form = InscriptionAssosForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data.get('email', '')
            justification = form.cleaned_data.get('justification', '')

            # Username généré automatiquement depuis l'email (ex: prenom.nom@... → prenom.nom)
            username_base = email.split('@')[0]
            username = username_base
            # Si le username existe déjà, on ajoute un numéro
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1

            user.username = username
            user.email = email

            if email.endswith('@student-cs.fr') or email.endswith('@centralesupelec.fr'):
                user.is_active = True
            else:
                user.is_active = False

            user.save()
            Profil.objects.create(user=user, justification=justification)

            if user.is_active:
                login(request, user)
                return redirect('achat')
            else:
                return redirect('accueil')
    else:
        form = InscriptionAssosForm()

    return render(request, 'inscription.html', {'form': form})

# 3. Page d'achat (Privée)
@login_required(login_url='/connexion/')
def achat(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            nb_places = form.cleaned_data['nombre_de_places']

            # Vérifie le stock disponible (ni réservé, ni attribué)
            billets_disponibles = BilletArkose.objects.filter(
                est_disponible=True,
                est_reserve=False
            )

            if billets_disponibles.count() < nb_places:
                return render(request, 'achat.html', {
                    'form': form,
                    'erreur': f"Stock insuffisant. Il ne reste que {billets_disponibles.count()} place(s) disponible(s)."
                })

            # Crée la commande
            commande = form.save(commit=False)
            commande.utilisateur = request.user
            commande.save()

            # Réserve les billets
            billets_a_reserver = billets_disponibles[:nb_places]
            for billet in billets_a_reserver:
                billet.est_reserve = True
                billet.commande = commande
                billet.save()

            return render(request, 'achat.html', {
                'message': "Commande enregistrée ! Vos places sont réservées en attente de votre virement."
            })
    else:
        form = CommandeForm()

    return render(request, 'achat.html', {'form': form})

def connexion(request):
    if request.method == 'POST':
        form = ConnexionEmailForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('achat')
    else:
        form = ConnexionEmailForm()

    return render(request, 'connexion.html', {'form': form})

# 1. Le test de sécurité : Est-ce que la personne est le trésorier ?
def est_tresorier(user):
    return user.is_superuser

# 2. La page principale du trésorier
@user_passes_test(est_tresorier)
def dashboard_tresorier(request):
    comptes_en_attente = User.objects.filter(is_active=False)
    commandes_en_attente = DemandePlaceArkose.objects.filter(statut='ATTENTE')
    
    # Compte combien de billets ont la case "est_disponible" cochée
    stock = BilletArkose.objects.filter(est_disponible=True, est_reserve=False).count()
    
    return render(request, 'dashboard_tresorier.html', {
        'comptes': comptes_en_attente,
        'commandes': commandes_en_attente,
        'stock_disponible': stock # On envoie le chiffre au HTML
    })

# 3. L'action invisible pour valider un compte
@user_passes_test(est_tresorier)
def valider_compte(request, user_id):
    user = get_object_or_404(User, id=user_id) # Trouve l'utilisateur
    user.is_active = True # L'active
    user.save()
    return redirect('dashboard_tresorier') # Recharge la page

# 4. L'action invisible pour valider une commande
@user_passes_test(est_tresorier)
def valider_commande(request, commande_id):
    commande = get_object_or_404(DemandePlaceArkose, id=commande_id)
    
    # Attribue définitivement les billets réservés à l'utilisateur
    billets = commande.billets_reserves.all()
    codes = []
    for billet in billets:
        billet.est_disponible = False
        billet.est_reserve = False
        billet.proprietaire = commande.utilisateur
        billet.commande = None
        billet.save()
        codes.append(billet.code_secret)

    commande.statut = 'VALIDE'
    commande.save()

    # Construction de l'email
    nb = commande.nombre_de_places
    codes_texte = "\n".join([f"- {code}" for code in codes])
    message = f"""Bonjour,

Votre paiement a été validé. Vous avez reçu {nb} place(s) Arkose.

Vos code(s) :
{codes_texte}

Présentez ce(s) code(s) à l'accueil d'Arkose pour accéder à la salle.

À bientôt !
"""

    send_mail(
        subject="Vos places Arkose sont confirmées !",
        message=message,
        from_email='gars4196@gmail.com',
        recipient_list=[commande.utilisateur.email],
        fail_silently=False,
    )

    return redirect('dashboard_tresorier')

# 1. Refuser (supprimer) un compte
@user_passes_test(est_tresorier)
def refuser_compte(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete() # Supprime l'utilisateur et son profil associé
    return redirect('dashboard_tresorier')

# 2. Refuser (supprimer) une commande
@user_passes_test(est_tresorier)
def refuser_commande(request, commande_id):
    commande = get_object_or_404(DemandePlaceArkose, id=commande_id)

    # Remet les billets réservés dans le stock
    for billet in commande.billets_reserves.all():
        billet.est_reserve = False
        billet.commande = None
        billet.save()

    commande.delete()
    return redirect('dashboard_tresorier')