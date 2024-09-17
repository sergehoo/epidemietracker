from datetime import date

from django.db.models import Sum, Count
from slick_reporting.fields import ComputationField, SlickReportField
from slick_reporting.generator import Chart
from slick_reporting.views import ReportView, SlickReportView
from django.utils.translation import gettext_lazy as _

from epidemie.models import Epidemie, Patient, Echantillon, SyntheseDistrict


class EpidemieReport(ReportView):
    def generate(self, epidemie_id):
        # Récupération de l'épidémie
        epidemie = Epidemie.objects.get(pk=epidemie_id)

        # Données pour le rapport
        total_cases = Patient.objects.filter(echantillons__maladie=epidemie, echantillons__resultat=True).count()
        male_cases = Patient.objects.filter(echantillons__maladie=epidemie, genre='M',
                                            echantillons__resultat=True).count()
        female_cases = Patient.objects.filter(echantillons__maladie=epidemie, genre='F',
                                              echantillons__resultat=True).count()

        # Calcul des pourcentages
        if total_cases > 0:
            male_percentage = round((male_cases / total_cases) * 100)
            female_percentage = round((female_cases / total_cases) * 100)
        else:
            male_percentage = 0
            female_percentage = 0

        echantillons_nbr = Echantillon.objects.filter(maladie=epidemie).count()
        echantillons_nbrP = Echantillon.objects.filter(maladie=epidemie, resultat=True).count()

        patients = Patient.objects.filter(echantillons__maladie=epidemie).distinct().count()
        patients_gueris = Patient.objects.filter(echantillons__maladie=epidemie, gueris=True).distinct().count()
        patients_decedes = Patient.objects.filter(echantillons__maladie=epidemie, decede=True).distinct().count()

        echantillons_positifs = Echantillon.objects.filter(maladie=epidemie, resultat=True)
        patients_avec_echantillons_positifs = Patient.objects.filter(echantillons__in=echantillons_positifs).distinct()
        total_patients_positifs = patients_avec_echantillons_positifs.count()

        patients_gueris_positifs = patients_avec_echantillons_positifs.filter(gueris=True).count()
        patients_decedes_positifs = patients_avec_echantillons_positifs.filter(decede=True).count()

        synthesedistrict = SyntheseDistrict.objects.filter(maladie_id=epidemie.pk)

        total_cas_suspects = synthesedistrict.aggregate(Sum('nbre_cas_suspects'))['nbre_cas_suspects__sum'] or 0
        total_cas_positif = synthesedistrict.aggregate(Sum('cas_positif'))['cas_positif__sum'] or 0
        total_cas_negatif = synthesedistrict.aggregate(Sum('cas_negatif'))['cas_negatif__sum'] or 0
        total_evacue = synthesedistrict.aggregate(Sum('evacue'))['evacue__sum'] or 0
        total_decede = synthesedistrict.aggregate(Sum('decede'))['decede__sum'] or 0
        total_gueri = synthesedistrict.aggregate(Sum('gueri'))['gueri__sum'] or 0
        total_suivi_en_cours = synthesedistrict.aggregate(Sum('suivi_en_cours'))['suivi_en_cours__sum'] or 0
        total_sujets_contacts = synthesedistrict.aggregate(Sum('nbre_sujets_contacts'))[
                                    'nbre_sujets_contacts__sum'] or 0
        total_contacts_en_cours_suivi = synthesedistrict.aggregate(Sum('contacts_en_cours_suivi'))[
                                            'contacts_en_cours_suivi__sum'] or 0
        total_contacts_sorti_suivi = synthesedistrict.aggregate(Sum('contacts_sorti_suivi'))[
                                         'contacts_sorti_suivi__sum'] or 0
        total_devenu_suspect = synthesedistrict.aggregate(Sum('devenu_suspect'))['devenu_suspect__sum'] or 0
        total_devenu_positif = synthesedistrict.aggregate(Sum('devenu_positif'))['devenu_positif__sum'] or 0

        pourcentage_gueris_positifs = (
                patients_gueris_positifs / total_patients_positifs * 100) if total_patients_positifs > 0 else 0
        pourcentage_decedes_positifs = (
                patients_decedes_positifs / total_patients_positifs * 100) if total_patients_positifs > 0 else 0
        pourcentage_positifs = (echantillons_nbrP / echantillons_nbr * 100) if echantillons_nbr > 0 else 0

        context = {
            'male_cases': male_percentage,
            'female_cases': female_percentage,
            'echantillons_nbr': echantillons_nbr,
            'echantillons_nbrP': echantillons_nbrP,
            'patients': patients,
            'patients_gueris': patients_gueris,
            'patients_decedes': patients_decedes,
            'total_patients_positifs': total_patients_positifs,
            'patients_gueris_positifs': patients_gueris_positifs,
            'patients_decedes_positifs': patients_decedes_positifs,
            'pourcentage_gueris_positifs': pourcentage_gueris_positifs,
            'pourcentage_decedes_positifs': pourcentage_decedes_positifs,
            'pourcentage_positifs': pourcentage_positifs,
            'total_cas_suspects': total_cas_suspects,
            'total_cas_positif': total_cas_positif,
            'total_cas_negatif': total_cas_negatif,
            'total_evacue': total_evacue,
            'total_decede': total_decede,
            'total_gueri': total_gueri,
            'total_suivi_en_cours': total_suivi_en_cours,
            'total_sujets_contacts': total_sujets_contacts,
            'total_contacts_en_cours_suivi': total_contacts_en_cours_suivi,
            'total_contacts_sorti_suivi': total_contacts_sorti_suivi,
            'total_devenu_suspect': total_devenu_suspect,
            'total_devenu_positif': total_devenu_positif,
        }

        return context


# def group_by_age_tranches(date_naissance):
#     if date_naissance:  # Vérifier que la date de naissance n'est pas None
#         # Calcul de l'âge
#         age = date.today().year - date_naissance.year - (
#                 (date.today().month, date.today().day) < (date_naissance.month, date_naissance.day)
#         )
#         if age < 18:
#             return '0-17 ans'
#         elif 18 <= age < 30:
#             return '18-29 ans'
#         elif 30 <= age < 45:
#             return '30-44 ans'
#         elif 45 <= age < 60:
#             return '45-59 ans'
#         else:
#             return '60 ans et plus'
#     else:
#         return 'Inconnu'  # Si la date de naissance est None
#
#
# class PatientInfecteAgeReportView(ReportView):
#     report_model = Echantillon
#     date_field = 'date_collect'  # Utilisation de la date de collecte
#
#     # Groupement personnalisé par tranche d'âge
#     group_by = 'patient__date_naissance'
#
#     # Définition des colonnes
#     columns = [
#         SlickReportField(
#             field='patient__date_naissance',
#             custom_grouping=group_by_age_tranches,
#             name='tranche_age',  # Ajout du nom du champ
#             verbose_name="Tranches d'âge"
#         ),
#         SlickReportField(
#             field='id',  # Ajout du nom du champ
#             aggregation=Count('id'),
#             name='nombre_patients',  # Ajout du nom du champ
#             verbose_name='Nombre de patients infectés'
#         )
#     ]

# Fonction pour définir les tranches d'âge
