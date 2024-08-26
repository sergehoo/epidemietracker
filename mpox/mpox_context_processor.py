from django.db.models import Count, Q
from django.shortcuts import render

from epidemie.models import Echantillon, Patient, DistrictSanitaire, Epidemie


def mpox_dashboard(request):
    # Filtrer les échantillons et les patients pour la maladie MPOX
    echantillons_mpox = Echantillon.objects.filter(maladie__nom='MPOX')
    patients_mpox = Patient.objects.filter(echantillons__in=echantillons_mpox).distinct()

    echantillons_nbr = echantillons_mpox.count()
    echantillons_nbrP = echantillons_mpox.filter(resultat='POSITIF').count()
    patients = patients_mpox.count()
    patients_gueris = patients_mpox.filter(gueris=True).count()
    patients_decedes = patients_mpox.filter(decede=True).count()

    # Nombre total de patients dont les échantillons ont été positifs
    echantillons_positifs = echantillons_mpox.filter(resultat='POSITIF')
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
        pourcentage_decedes_positifs = 0

    if echantillons_nbr > 0:
        pourcentage_positifs = (echantillons_nbrP / echantillons_nbr) * 100
    else:
        pourcentage_positifs = 0

    last_update = echantillons_mpox.order_by('-created_at').values_list('created_at', flat=True).first()

    top_districts = DistrictSanitaire.objects.annotate(
        num_echantillons=Count('commune__patient__echantillons',
                               filter=Q(commune__patient__echantillons__maladie__nom='MPOX')),
        num_gueris=Count('commune__patient__echantillons',
                         filter=Q(commune__patient__echantillons__maladie__nom='MPOX', commune__patient__gueris=True)),
        num_decedes=Count('commune__patient__echantillons',
                          filter=Q(commune__patient__echantillons__maladie__nom='MPOX', commune__patient__decede=True))
    ).order_by('-num_echantillons')[:5]

    epidemies = Epidemie.objects.filter(nom='MPOX').order_by('id')

    # Passer les données au template
    context = {
        'mpox_top_districts': top_districts,
        'mpox_list_epidemie': epidemies,

        'mpox_last_update': last_update,
        'mpox_echantillons_nbr': echantillons_nbr,
        'mpox_echantillons_nbrP': echantillons_nbrP,
        'mpox_pourcentage_positifs': pourcentage_positifs,
        'mpox_patients_gueris': patients_gueris,
        'mpox_patients_decedes': patients_decedes,
        'mpox_patients': patients,
        'mpox_total_patients_positifs': total_patients_positifs,
        'mpox_patients_gueris_positifs': patients_gueris_positifs,
        'mpox_patients_decede_positifs': patients_decedes_positifs,
        'mpox_pourcentage_gueris_positifs': pourcentage_gueris_positifs,
        'mpox_pourcentage_decedes_positifs': pourcentage_decedes_positifs,
    }

    return render(request, 'global/mpox/dashboard_mpox.html', context)
