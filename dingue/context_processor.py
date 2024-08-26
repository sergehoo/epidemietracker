from django.db.models import Count, Q
from django.shortcuts import render

from epidemie.models import Echantillon, Patient, DistrictSanitaire, Epidemie


# def dashboard(request):
#     # Récupérer la maladie à partir des paramètres de la requête, par exemple ?maladie=DENGUE
#     maladie = request.GET.get('maladie', None)
#
#     if maladie:
#         # Filtrer les échantillons et les patients en fonction de la maladie sélectionnée
#         echantillons_nbr = Echantillon.objects.filter(maladie__nom=maladie).count()
#         echantillons_nbrP = Echantillon.objects.filter(resultat='POSITIF', maladie__nom=maladie).count()
#         patients = Patient.objects.filter(echantillons__maladie__nom=maladie).count()
#         patients_gueris = Patient.objects.filter(gueris=True, echantillons__maladie__nom=maladie).count()
#         patients_decedes = Patient.objects.filter(decede=True, echantillons__maladie__nom=maladie).count()
#
#         # Nombre total de patients dont les échantillons ont été positifs
#         echantillons_positifs = Echantillon.objects.filter(resultat='POSITIF', maladie__nom=maladie)
#         patients_avec_echantillons_positifs = Patient.objects.filter(echantillons__in=echantillons_positifs).distinct()
#
#         total_patients_positifs = patients_avec_echantillons_positifs.count()
#
#         # Nombre de patients guéris et décédés parmi ceux dont les échantillons ont été positifs
#         patients_gueris_positifs = patients_avec_echantillons_positifs.filter(gueris=True).count()
#         patients_decedes_positifs = patients_avec_echantillons_positifs.filter(decede=True).count()
#
#         # Calculer le pourcentage de patients guéris et décédés parmi les patients avec des échantillons positifs
#         if total_patients_positifs > 0:
#             pourcentage_gueris_positifs = (patients_gueris_positifs / total_patients_positifs) * 100
#             pourcentage_decedes_positifs = (patients_decedes_positifs / total_patients_positifs) * 100
#         else:
#             pourcentage_gueris_positifs = 0
#             pourcentage_decedes_positifs = 0  # Définir la variable même si le total est 0
#
#         if echantillons_nbr > 0:
#             pourcentage_positifs = (echantillons_nbrP / echantillons_nbr) * 100
#         else:
#             pourcentage_positifs = 0
#
#         last_update = Echantillon.objects.filter(maladie__nom=maladie).order_by('-created_at').values_list('created_at',
#                                                                                                            flat=True).first()
#
#         top_districts = DistrictSanitaire.objects.annotate(
#             num_echantillons=Count('commune__patient__echantillons',
#                                    filter=Q(commune__patient__echantillons__maladie__nom=maladie)),
#             num_gueris=Count('commune__patient__echantillons',
#                              filter=Q(commune__patient__echantillons__maladie__nom=maladie,
#                                       commune__patient__gueris=True)),
#             num_decedes=Count('commune__patient__echantillons',
#                               filter=Q(commune__patient__echantillons__maladie__nom=maladie,
#                                        commune__patient__decede=True))
#         ).order_by('-num_echantillons')[:5]
#     else:
#         # Si aucune maladie n'est sélectionnée, afficher les totaux globaux
#         echantillons_nbr = Echantillon.objects.all().count()
#         echantillons_nbrP = Echantillon.objects.filter(resultat='POSITIF').count()
#         patients = Patient.objects.all().count()
#         patients_gueris = Patient.objects.filter(gueris=True).count()
#         patients_decedes = Patient.objects.filter(decede=True).count()
#
#         # Nombre total de patients dont les échantillons ont été positifs
#         echantillons_positifs = Echantillon.objects.filter(resultat='POSITIF')
#         patients_avec_echantillons_positifs = Patient.objects.filter(echantillons__in=echantillons_positifs).distinct()
#
#         total_patients_positifs = patients_avec_echantillons_positifs.count()
#
#         # Nombre de patients guéris et décédés parmi ceux dont les échantillons ont été positifs
#         patients_gueris_positifs = patients_avec_echantillons_positifs.filter(gueris=True).count()
#         patients_decedes_positifs = patients_avec_echantillons_positifs.filter(decede=True).count()
#
#         # Calculer le pourcentage de patients guéris et décédés parmi les patients avec des échantillons positifs
#         if total_patients_positifs > 0:
#             pourcentage_gueris_positifs = (patients_gueris_positifs / total_patients_positifs) * 100
#             pourcentage_decedes_positifs = (patients_decedes_positifs / total_patients_positifs) * 100
#         else:
#             pourcentage_gueris_positifs = 0
#             pourcentage_decedes_positifs = 0  # Définir la variable même si le total est 0
#
#         if echantillons_nbr > 0:
#             pourcentage_positifs = (echantillons_nbrP / echantillons_nbr) * 100
#         else:
#             pourcentage_positifs = 0
#
#         last_update = Echantillon.objects.order_by('-created_at').values_list('created_at', flat=True).first()
#
#         top_districts = DistrictSanitaire.objects.annotate(
#             num_echantillons=Count('commune__patient__echantillons'),
#             num_gueris=Count('commune__patient__echantillons', filter=Q(commune__patient__gueris=True)),
#             num_decedes=Count('commune__patient__echantillons', filter=Q(commune__patient__decede=True))
#         ).order_by('-num_echantillons')[:5]
#
#     epidemies = Epidemie.objects.all().order_by('id')
#
#     # Passer les données au template
#     context = {
#         'top_districts': top_districts,
#         'list_epidemie': epidemies,
#
#         'last_update': last_update,
#         'echantillons_nbr': echantillons_nbr,
#         'echantillons_nbrP': echantillons_nbrP,
#         'pourcentage_positifs': pourcentage_positifs,
#         'patients_gueris': patients_gueris,
#         'patients_decedes': patients_decedes,
#         'patients': patients,
#         'total_patients_positifs': total_patients_positifs,
#         'patients_gueris_positifs': patients_gueris_positifs,
#         'patients_decede_positifs': patients_decedes_positifs,
#         'pourcentage_gueris_positifs': pourcentage_gueris_positifs,
#         'pourcentage_decedes_positifs': pourcentage_decedes_positifs,
#     }
#
#     return context
def dashboard(request):
    echantillons_nbr = Echantillon.objects.all().count()
    echantillons_nbrP = Echantillon.objects.filter(resultat='POSITIF').count()
    patients = Patient.objects.all().count()
    patients_gueris = Patient.objects.filter(gueris=True).count()
    patients_decedes = Patient.objects.filter(decede=True).count()

    # Nombre total de patients dont les échantillons ont été positifs
    echantillons_positifs = Echantillon.objects.filter(resultat='POSITIF')
    patients_avec_echantillons_positifs = Patient.objects.filter(echantillons__in=echantillons_positifs).distinct()

    total_patients_positifs = patients_avec_echantillons_positifs.count()

    # Nombre de patients guéris et décédés parmi ceux dont les échantillons ont été positifs
    patients_gueris_positifs = patients_avec_echantillons_positifs.filter(gueris=True).count()
    patients_decedes_positifs = patients_avec_echantillons_positifs.filter(decede=True).count()

    # Calculer le pourcentage de patients guéris et décédés parmi les patients avec des échantillons positifs
    if total_patients_positifs > 0:
        pourcentage_gueris_positifs = (patients_gueris_positifs / total_patients_positifs) * 100
        pourcentage_decedes_positifs = (patients_decedes_positifs / total_patients_positifs) * 100
    else:
        pourcentage_gueris_positifs = 0
        pourcentage_decedes_positifs = 0  # Définir la variable même si le total est 0

    if echantillons_nbr > 0:
        pourcentage_positifs = (echantillons_nbrP / echantillons_nbr) * 100
    else:
        pourcentage_positifs = 0

    last_update = Echantillon.objects.order_by('-created_at').values_list('created_at', flat=True).first()

    top_districts = DistrictSanitaire.objects.annotate(
        num_echantillons=Count('commune__patient__echantillons'),
        num_gueris=Count('commune__patient__echantillons', filter=Q(commune__patient__gueris=True)),
        num_decedes=Count('commune__patient__echantillons', filter=Q(commune__patient__decede=True))
    ).order_by('-num_echantillons')[:5]

    epidemies = Epidemie.objects.all().order_by('id')

    # Passer les données au template
    context = {
        'top_districts': top_districts,
        'list_epidemie': epidemies,

        'last_update': last_update,
        'echantillons_nbr': echantillons_nbr,
        'echantillons_nbrP': echantillons_nbrP,
        'pourcentage_positifs': pourcentage_positifs,
        'patients_gueris': patients_gueris,
        'patients_decedes': patients_decedes,
        'patients': patients,
        'total_patients_positifs': total_patients_positifs,
        'patients_gueris_positifs': patients_gueris_positifs,
        'patients_decede_positifs': patients_decedes_positifs,
        'pourcentage_gueris_positifs': pourcentage_gueris_positifs,
        'pourcentage_decedes_positifs': pourcentage_decedes_positifs,
    }

    return context




