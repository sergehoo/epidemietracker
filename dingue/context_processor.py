from epidemie.models import Echantillon, Patient


def dashboard(request):
    echantillons_nbr = Echantillon.objects.all().count()
    echantillons_nbrP = Echantillon.objects.filter(resultat='POSITIF').count()
    patients = Patient.objects.all().count()
    patients_gueris = Patient.objects.filter(gueris=True).count()
    patients_decedes= Patient.objects.filter(decede=True).count()

    # Nombre total de patients dont les échantillons ont été positifs
    echantillons_positifs = Echantillon.objects.filter(resultat='POSITIF')
    patients_avec_echantillons_positifs = Patient.objects.filter(echantillons__in=echantillons_positifs).distinct()

    total_patients_positifs = patients_avec_echantillons_positifs.count()

    # Nombre de patients guéris parmi ceux dont les échantillons ont été positifs
    patients_gueris_positifs = patients_avec_echantillons_positifs.filter(gueris=True).count()
    patients_decedes_positifs = patients_avec_echantillons_positifs.filter(decede=True).count()

    # Calculer le pourcentage de patients guéris parmi les patients avec des échantillons positifs
    if total_patients_positifs > 0:
        pourcentage_gueris_positifs = (patients_gueris_positifs / total_patients_positifs) * 100
        pourcentage_decedes_positifs = (patients_decedes_positifs / total_patients_positifs) * 100
    else:
        pourcentage_gueris_positifs = 0




    if echantillons_nbr > 0:
        pourcentage_positifs = (echantillons_nbrP / echantillons_nbr) * 100
    else:
        pourcentage_positifs = 0

        # Passer les données au template
    context = {
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
        'patients_decedes_positifs': patients_decedes_positifs,

    }

    return context
