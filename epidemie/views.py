import logging
import os
import pandas as pd
from datetime import datetime, timedelta, date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, Permission
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
from guardian.shortcuts import assign_perm, get_objects_for_user
from rest_framework import viewsets, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rolepermissions.mixins import HasRoleMixin
from tablib import Dataset
from unidecode import unidecode

from epidemie.admin import EchantillonResource
from epidemie.forms import PatientForm, InfoscreateForm
from epidemie.models import HealthRegion, City, EpidemicCase, Patient, ServiceSanitaire, Commune, Epidemie, Echantillon, \
    DistrictSanitaire, SyntheseDistrict, Information
from epidemie.reports import EpidemieReport
from epidemie.serializers import HealthRegionSerializer, CitySerializer, EpidemicCaseSerializer, CommuneSerializer, \
    PatientSerializer, ServiceSanitaireSerializer


def import_synthese_districts(file):
    # Save the file temporarily
    temp_file_name = default_storage.save('temp/' + file.name, ContentFile(file.read()))
    temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_name)

    # Read the Excel file into a DataFrame
    df = pd.read_excel(temp_file_path)

    # Iterate over DataFrame rows and create/update SyntheseDistrict instances
    for index, row in df.iterrows():
        try:
            maladie = Epidemie.objects.get(nom=row['maladie'])
            district_sanitaire = DistrictSanitaire.objects.get(nom=row['district_sanitaire'])

            # Create or update SyntheseDistrict instance
            SyntheseDistrict.objects.update_or_create(
                maladie=maladie,
                district_sanitaire=district_sanitaire,
                defaults={
                    'nbre_cas_suspects': row.get('nbre_cas_suspects', 0),
                    'cas_positif': row.get('cas_positif', 0),
                    'cas_negatif': row.get('cas_negatif', 0),
                    'evacue': row.get('evacue', 0),
                    'decede': row.get('decede', 0),
                    'gueri': row.get('gueri', 0),
                    'suivi_en_cours': row.get('suivi_en_cours', 0),
                    'nbre_sujets_contacts': row.get('nbre_sujets_contacts', 0),
                    'contacts_en_cours_suivi': row.get('contacts_en_cours_suivi', 0),
                    'contacts_sorti_suivi': row.get('contacts_sorti_suivi', 0),
                    'devenu_suspect': row.get('devenu_suspect', 0),
                    'devenu_positif': row.get('devenu_positif', 0)
                }
            )
        except Exception as e:
            print(f"Error processing row {index}: {e}")

    # Clean up the temporary file
    default_storage.delete(temp_file_name)

    return df


def import_synthese_view(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, 'Veuillez sélectionner un fichier à importer.')
            return render(request, 'dingue/import_synthese.html')

        file = request.FILES['file']
        try:
            import_synthese_districts(file)
            messages.success(request, 'Données importées avec succès')
            return redirect('echantillons')  # Replace with your success URL
        except Exception as e:
            messages.error(request, f"Erreur lors de l'importation des données : {e}")
            return render(request, 'dingue/import_synthese.html')

    return render(request, 'dingue/import_synthese.html')


# def import_echantillons(request):
#     if request.method == 'POST':
#         if 'file' not in request.FILES and 'temp_file_name' not in request.POST:
#             messages.error(request, 'Veuillez sélectionner un fichier à importer.')
#             return render(request, 'dingue/import.html')
#
#         echantillon_resource = EchantillonResource()
#         dataset = Dataset()
#
#         if 'file' in request.FILES:
#             new_echantillons = request.FILES['file']
#             temp_file_name = default_storage.save(os.path.join('temp', new_echantillons.name),
#                                                   ContentFile(new_echantillons.read()))
#             temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_name)
#
#             try:
#                 imported_data = dataset.load(open(temp_file_path, 'rb').read(), format='xlsx')
#
#                 for row in dataset.dict:
#                     # Recherche de la région sanitaire en ignorant la casse et les accents
#                     # region_name = unidecode(row['Region_Sanitaire']).lower()
#                     # region = HealthRegion.objects.annotate(
#                     #     similarity=TrigramSimilarity('name', region_name)
#                     # ).filter(similarity__gt=0.3).order_by('-similarity').first()
#                     #
#                     # if not region:
#                     #     messages.error(request, f"Région sanitaire '{row['Region_Sanitaire']}' introuvable.")
#                     #     continue
#
#                     # Recherche du district sanitaire en ignorant la casse et les accents
#                     district_name = unidecode(row['DistrictSanitaire']).lower()
#                     district = DistrictSanitaire.objects.annotate(
#                         similarity=TrigramSimilarity('nom', district_name)
#                     ).filter(similarity__gt=0.3).order_by('-similarity').first()
#
#                     if not district:
#                         messages.error(request, f"District sanitaire '{row['DistrictSanitaire']}' introuvable.")
#                         continue
#
#                     # Recherche de la commune sans filtrer par district
#                     commune_name = unidecode(row['patient_commune']).lower()
#                     commune = Commune.objects.annotate(
#                         similarity=TrigramSimilarity('name', commune_name)
#                     ).filter(similarity__gt=0.3).order_by('-similarity').first()
#
#                     if not commune:
#                         messages.error(request, f"Commune '{row['patient_commune']}' introuvable.")
#                         continue
#
#                     maladie_name = row['maladie_nom']
#                     maladie, _ = Epidemie.objects.get_or_create(nom=maladie_name)
#
#                     # Calcul de l'âge du patient à partir de la colonne 'patient_age'
#                     # (S'assurer d'avoir une date de naissance cohérente)
#                     if 'patient_age' in row:
#                         birth_date = (datetime.today() - timedelta(
#                             days=365 * int(row.get('patient_age')))).date()  # Approximation avec la date de naissance
#
#                     # Création ou mise à jour du patient
#                     patient, created = Patient.objects.update_or_create(
#                         code_patient=row['code_echantillon'],
#                         defaults={
#                             'nom': row['patient'].split()[0],  # Extraction du nom et prénom
#                             'prenoms': " ".join(row['patient'].split()[1:]),
#                             'date_naissance': birth_date,  # Date approximative basée sur l'âge
#                             'genre': row['patient_sexe'],
#                             'commune': commune,
#                             'decede': bool(int(row['patient_decede'])),  # Conversion 0/1 en booléen
#                             'gueris': bool(int(row['patient_gueris'])),
#                             'contact': 'N/A'  # Remplacez par la colonne appropriée si elle existe
#                         }
#                     )
#
#                     # Création ou mise à jour de l'échantillon
#                     Echantillon.objects.update_or_create(
#                         code_echantillon=row['code_echantillon'],
#                         defaults={
#                             'patient': patient,
#                             'maladie': maladie,
#                             'date_collect': row['echantillon_date_prelevement'],
#                             'site_collect': row['DistrictSanitaire'],
#                             'resultat': bool(int(row['echantillon_resultat'])),  # Résultat comme booléen
#                         }
#                     )
#
#                 result = echantillon_resource.import_data(dataset, dry_run=True)
#
#                 if not result.has_errors():
#                     preview_data = dataset.dict
#                     return render(request, 'dingue/import.html',
#                                   {'preview_data': preview_data, 'temp_file_name': temp_file_name})
#
#                 messages.error(request,
#                                'Erreur lors de l\'importation des données : vérifiez les données et réessayez.')
#
#             except Exception as e:
#                 messages.error(request, f"Erreur lors de l'importation des données : {e}")
#                 return render(request, 'dingue/import.html')
#
#         elif 'temp_file_name' in request.POST:
#             temp_file_name = request.POST['temp_file_name']
#             temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_name)
#
#             if os.path.exists(temp_file_path):
#                 imported_data = dataset.load(open(temp_file_path, 'rb').read(), format='xlsx')
#                 echantillon_resource.import_data(dataset, dry_run=False)
#                 messages.success(request, 'Données importées avec succès')
#                 return redirect('echantillons')
#             else:
#                 messages.error(request, 'Fichier temporaire introuvable.')
#                 return render(request, 'dingue/import.html')
#
#     return render(request, 'dingue/import.html')
def import_echantillons(request):
    if request.method == 'POST':
        if 'file' not in request.FILES and 'temp_file_name' not in request.POST:
            messages.error(request, 'Veuillez sélectionner un fichier à importer.')
            return render(request, 'dingue/import.html')

        echantillon_resource = EchantillonResource()
        dataset = Dataset()

        if 'file' in request.FILES:
            new_echantillons = request.FILES['file']
            temp_file_name = default_storage.save(os.path.join('temp', new_echantillons.name),
                                                  ContentFile(new_echantillons.read()))
            temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_name)

            try:
                imported_data = dataset.load(open(temp_file_path, 'rb').read(), format='xlsx')

                for row in dataset.dict:
                    # Normaliser et nettoyer le nom du district sanitaire (enlever accents, mettre en minuscule)
                    district_name = unidecode(row['DistrictSanitaire']).lower()

                    # Recherche du district sanitaire le plus proche par similarité
                    district = DistrictSanitaire.objects.annotate(
                        similarity=TrigramSimilarity('nom', district_name)
                    ).filter(similarity__gt=0.3).order_by('-similarity').first()

                    if not district:
                        messages.error(request, f"District sanitaire '{row['DistrictSanitaire']}' introuvable.")
                        continue

                    # Normaliser et nettoyer le nom de la commune (enlever accents, mettre en minuscule)
                    commune_name = unidecode(row['patient_commune']).lower()

                    # Recherche de la commune la plus proche par similarité
                    commune = Commune.objects.annotate(
                        similarity=TrigramSimilarity('name', commune_name)
                    ).filter(similarity__gt=0.3).order_by('-similarity').first()

                    if not commune:
                        messages.error(request, f"Commune '{row['patient_commune']}' introuvable.")
                        continue

                    # Recherche ou création de la maladie (épidémie)
                    maladie_name = row['maladie_nom']
                    maladie, _ = Epidemie.objects.get_or_create(nom=maladie_name)

                    # Calcul de l'âge du patient à partir de la colonne 'patient_age'
                    if 'patient_age' in row:
                        birth_date = (datetime.today() - timedelta(
                            days=365 * int(row.get('patient_age')))).date()  # Approximation de la date de naissance

                    # Création ou mise à jour du patient
                    patient, created = Patient.objects.update_or_create(
                        code_patient=row['code_echantillon'],
                        defaults={
                            'nom': row['patient'].split()[0],  # Extraction du nom
                            'prenoms': " ".join(row['patient'].split()[1:]),  # Extraction des prénoms
                            'date_naissance': birth_date,
                            'genre': row['patient_sexe'],
                            'commune': commune,
                            'decede': bool(int(row['patient_decede'])),  # Conversion 0/1 en booléen
                            'gueris': bool(int(row['patient_gueris'])),
                            'contact': 'N/A'  # Remplacer si la colonne existe
                        }
                    )

                    # Création ou mise à jour de l'échantillon
                    Echantillon.objects.update_or_create(
                        code_echantillon=row['code_echantillon'],
                        defaults={
                            'patient': patient,
                            'maladie': maladie,
                            'date_collect': row['echantillon_date_prelevement'],
                            'site_collect': row['DistrictSanitaire'],
                            'resultat': bool(int(row['echantillon_resultat'])),  # Résultat comme booléen
                        }
                    )

                result = echantillon_resource.import_data(dataset, dry_run=True)

                if not result.has_errors():
                    preview_data = dataset.dict
                    return render(request, 'dingue/import.html',
                                  {'preview_data': preview_data, 'temp_file_name': temp_file_name})

                messages.error(request,
                               'Erreur lors de l\'importation des données : vérifiez les données et réessayez.')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'importation des données : {e}")
                return render(request, 'dingue/import.html')

        elif 'temp_file_name' in request.POST:
            temp_file_name = request.POST['temp_file_name']
            temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_name)

            if os.path.exists(temp_file_path):
                imported_data = dataset.load(open(temp_file_path, 'rb').read(), format='xlsx')
                echantillon_resource.import_data(dataset, dry_run=False)
                messages.success(request, 'Données importées avec succès')
                return redirect('echantillons')
            else:
                messages.error(request, 'Fichier temporaire introuvable.')
                return render(request, 'dingue/import.html')

    return render(request, 'dingue/import.html')

def import_view(request):
    return render(request, 'dingue/import.html')


logger = logging.getLogger(__name__)


def info_banner_view(request):
    infos = Information.objects.all().order_by('-date_added')  # You can filter as needed
    return render(request, 'global/layouts/navhead.html', {'infos': infos})


def import_excel(request):
    if request.method == 'POST':
        if True:
            # Read the uploaded Excel file
            excel_file = request.FILES['file']
            try:
                # Load the Excel file into a pandas DataFrame
                df = pd.read_excel(excel_file, engine='openpyxl')

                # Iterate through each row of the DataFrame and create objects
                for index, row in df.iterrows():
                    # Create or update the Patient object
                    nom = row['Nom'].split(' ')[0]
                    prenoms = ' '.join(row['Nom'].split(' ')[1:10])
                    patient, created = Patient.objects.get_or_create(

                        code_patient=row.get('code_patient'),
                        defaults={
                            'nom': nom,
                            'prenoms': prenoms,
                            'contact': row.get('contact'),
                            'situation_matrimoniale': row.get('situation_matrimoniale'),
                            'lieu_naissance': row.get('lieu_naissance'),
                            'date_naissance': datetime.today() - timedelta(days=365 * int(row.get('date_naissance'))),
                            'genre': 'Femme' if row.get('genre') == 'F' else 'Homme',
                            'nationalite': row.get('nationalite'),
                            'profession': row.get('profession'),
                            'nbr_enfants': row.get('nbr_enfants'),
                            'groupe_sanguin': row.get('groupe_sanguin', 'B+'),
                            'niveau_etude': row.get('niveau_etude', 'Primaire'),
                            'employeur': row.get('employeur', 'Non defini'),
                            'commune_id': row.get('commune_id'),  # Assuming Commune ID is available
                            'hopital_id': row.get('hopital_id'),  # Assuming ServiceSanitaire ID is available
                            'quartier': Commune.filter(nom__contains=row.get('commune'))[0],
                            'status': row.get('cas_positif'),
                            'gueris': bool(row.get('gueris')),
                            'decede': bool(row.get('decede')),
                        }
                    )

                    # Create or update the Echantillon object
                    Echantillon.objects.create(
                        patient=patient,
                        code_echantillon=row.get('code_echantillon'),
                        maladie_id=row.get('maladie_id'),  # Assuming Epidemie ID is available
                        mode_preleve_id=row.get('mode_preleve_id'),  # Assuming PreleveMode ID is available
                        date_collect=row.get('date_collect'),
                        site_collect=row.get('site_collect'),
                        agent_collect_id=row.get('agent_collect_id'),  # Assuming Employee ID is available
                        status_echantillons=row.get('status_echantillons'),
                        resultat=row.get('resultat'),

                    )

                messages.success(request, 'Data imported successfully.')
                return redirect('your-success-url')
            except Exception as e:
                messages.error(request, f'Error occurred: {e}')
    else:
        messages.error(request, 'Fichier  introuvable.')
        return render(request, 'dingue/import.html')

    return render(request, 'dingue/import.html')


class InformationDetailView(DetailView):
    model = Information
    template_name = 'global/infosdetails.html'
    context_object_name = "infodetail"


class InformationCreateView(CreateView):
    model = Information
    template_name = 'global/infoscreate.html'
    form_class = InfoscreateForm
    success_url = reverse_lazy('landing')


class LandinguePageView(LoginRequiredMixin, ListView):
    allowed_roles = ['RegionalRole', 'NationalRole']  # Accès pour les utilisateurs régionaux et nationaux
    model = Epidemie
    login_url = '/accounts/login/'
    template_name = "global/landingpage.html"
    context_object_name = 'list_epidemie'

    # paginate_by = 5

    def get_queryset(self):
        epidemies = Epidemie.objects.all()

        # Trier les épidémies en fonction de la propriété nombre_patients_positifs_ce_mois
        sorted_epidemies = sorted(epidemies, key=lambda e: e.nombre_patients_positifs_ce_mois, reverse=True)

        return sorted_epidemies

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtrer les patients ayant au moins un échantillon avec un résultat positif
        positive_cases = (
            Patient.objects.filter(echantillons__resultat=True)
            .values('commune__name')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        # Passer les données au template
        context['positive_cases'] = positive_cases

        return context


class EpidemieDetailView(LoginRequiredMixin, DetailView):
    allowed_roles = ['NationalRole']
    model = Epidemie
    template_name = 'global/dashboard.html'
    context_object_name = "epidemiedetail"
    ordering = ['id']

    def get(self, request, pk):

        epidemie = get_object_or_404(Epidemie, pk=pk)

        # Calcul des tranches d'âge pour les patients infectés par cette épidémie
        tranches_age = self.get_infected_by_age_tranche(epidemie)

        # Ajouter les données au contexte


        # Générer le rapport
        report = EpidemieReport()
        report_data = report.generate(epidemie_id=epidemie.pk)

        # Filter patients by gender and epidemic
        male_cases = Patient.objects.filter(echantillons__maladie=epidemie, genre='Male').count()
        female_cases = Patient.objects.filter(echantillons__maladie=epidemie, genre='Female').count()

        # Récupérer les données mensuelles d'évolution de l'épidémie
        monthly_data = Echantillon.objects.filter(maladie=epidemie).annotate(
            month=TruncMonth('date_collect')
        ).values('month').annotate(
            total_cases=Count('id')
        ).order_by('month')

        months = [data['month'].strftime('%b %Y') for data in monthly_data]
        cases = [data['total_cases'] for data in monthly_data]

        # Filtrer les échantillons et les patients par épidémie
        echantillons_nbr = Echantillon.objects.filter(maladie=epidemie).count()
        echantillons_nbrP = Echantillon.objects.filter(maladie=epidemie, resultat=True).count()

        patients = Patient.objects.filter(echantillons__maladie=epidemie).distinct().count()
        patients_gueris = Patient.objects.filter(echantillons__maladie=epidemie, gueris=True).distinct().count()
        patients_decedes = Patient.objects.filter(echantillons__maladie=epidemie, decede=True).distinct().count()

        # Nombre total de patients dont les échantillons ont été positifs
        echantillons_positifs = Echantillon.objects.filter(maladie=epidemie, resultat=True)
        patients_avec_echantillons_positifs = Patient.objects.filter(echantillons__in=echantillons_positifs).distinct()
        total_patients_positifs = patients_avec_echantillons_positifs.count()

        # Nombre de patients guéris et décédés parmi ceux dont les échantillons ont été positifs
        patients_gueris_positifs = patients_avec_echantillons_positifs.filter(gueris=True).count()
        patients_decedes_positifs = patients_avec_echantillons_positifs.filter(decede=True).count()

        # Récupérer les données de synthèse des districts pour l'épidémie en cours
        synthesedistrict = SyntheseDistrict.objects.filter(maladie_id=epidemie.pk)

        # Calculer les statistiques de SyntheseDistrict
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

        # Calculer les pourcentages
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

        last_update = Echantillon.objects.filter(maladie=epidemie).order_by('-created_at').values_list('created_at',
                                                                                                       flat=True).first()

        top_districts = DistrictSanitaire.objects.annotate(
            num_echantillons=Count('commune__patient__echantillons',
                                   filter=Q(commune__patient__echantillons__maladie=epidemie)),
            num_gueris=Count('commune__patient__echantillons',
                             filter=Q(commune__patient__gueris=True, commune__patient__echantillons__maladie=epidemie)),
            num_decedes=Count('commune__patient__echantillons',
                              filter=Q(commune__patient__decede=True, commune__patient__echantillons__maladie=epidemie))
        ).order_by('-num_echantillons')[:5]

        cases_by_region = (
            Patient.objects.filter(echantillons__maladie=epidemie, echantillons__resultat=True)
            .values('commune__district__region__name')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        cases_by_district = (
            Patient.objects.filter(echantillons__maladie=epidemie, echantillons__resultat=True)
            .values('commune__district__region__name', 'commune__district__nom')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        context = {
            'tranches_age': tranches_age,
            # 'tranches_age_ratios': tranches_age_ratios,
            'epidemierep': epidemie,
            'report_data': report_data,

            'male_cases': male_cases,
            'female_cases': female_cases,

            'cases_by_region': cases_by_region,
            'cases_by_district': cases_by_district,
            'epidemie': epidemie,
            'epidemie_id': epidemie.pk,
            'epidemie_nom': epidemie.nom,
            'top_districts': top_districts,
            'last_update': last_update,
            'echantillons_nbr': echantillons_nbr,
            'echantillons_nbrP': echantillons_nbrP,
            'pourcentage_positifs': pourcentage_positifs,
            'patients_gueris': patients_gueris,
            'patients_decedes': patients_decedes,
            'patients': patients + total_cas_negatif,
            'total_patients_positifs': total_patients_positifs,
            'patients_gueris_positifs': patients_gueris_positifs,
            'patients_decedes_positifs': patients_decedes_positifs,
            'pourcentage_gueris_positifs': pourcentage_gueris_positifs,
            'pourcentage_decedes_positifs': pourcentage_decedes_positifs,

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

            'monthly_data': {
                'months': months,
                'cases': cases
            }
        }

        return render(request, self.template_name, context)

    def get_infected_by_age_tranche(self, epidemie):
        """Calcule le nombre de patients infectés par tranche d'âge et leurs ratios pour une épidémie donnée."""
        patients_infectes = Echantillon.objects.filter(
            maladie=epidemie, resultat=True
        ).select_related('patient')

        # Dictionnaire pour stocker les résultats par tranche d'âge
        tranches_age_data = {
            '0-17 ans': 0,
            '18-29 ans': 0,
            '30-44 ans': 0,
            '45-59 ans': 0,
            '60 ans et plus': 0,
        }

        # Compter les patients par tranche d'âge
        total_patients = 0
        for echantillon in patients_infectes:
            patient = echantillon.patient
            age = self.calcul_age(patient.date_naissance)

            if age is not None:
                total_patients += 1
                if age < 18:
                    tranches_age_data['0-17 ans'] += 1
                elif 18 <= age < 30:
                    tranches_age_data['18-29 ans'] += 1
                elif 30 <= age < 45:
                    tranches_age_data['30-44 ans'] += 1
                elif 45 <= age < 60:
                    tranches_age_data['45-59 ans'] += 1
                else:
                    tranches_age_data['60 ans et plus'] += 1

        # Calcul des ratios et création d'une liste de tuples (tranche, nombre, ratio)
        tranches_age_list = []
        for tranche, count in tranches_age_data.items():
            if total_patients > 0:
                ratio = round((count / total_patients) * 100, 2)
            else:
                ratio = 0
            tranches_age_list.append((tranche, count, ratio))

        return tranches_age_list

    def calcul_age(self, date_naissance):
        """Calcule l'âge d'une personne à partir de sa date de naissance."""
        if date_naissance:
            today = date.today()
            return today.year - date_naissance.year - (
                    (today.month, today.day) < (date_naissance.month, date_naissance.day)
            )
        return None

    # def get(self, request, pk):
    #     epidemie = get_object_or_404(Epidemie, pk=pk)
    #
    #     # Filtrer les échantillons et les patients par épidémie
    #     echantillons_nbr = Echantillon.objects.filter(maladie=epidemie).count()
    #     echantillons_nbrP = Echantillon.objects.filter(maladie=epidemie, resultat='POSITIF').count()
    #
    #     patients = Patient.objects.filter(echantillons__maladie=epidemie).distinct().count()
    #     patients_gueris = Patient.objects.filter(echantillons__maladie=epidemie, gueris=True).distinct().count()
    #     patients_decedes = Patient.objects.filter(echantillons__maladie=epidemie, decede=True).distinct().count()
    #
    #     # Nombre total de patients dont les échantillons ont été positifs
    #     echantillons_positifs = Echantillon.objects.filter(maladie=epidemie, resultat='POSITIF')
    #     patients_avec_echantillons_positifs = Patient.objects.filter(echantillons__in=echantillons_positifs).distinct()
    #
    #     total_patients_positifs = patients_avec_echantillons_positifs.count()
    #
    #     # Nombre de patients guéris et décédés parmi ceux dont les échantillons ont été positifs
    #     patients_gueris_positifs = patients_avec_echantillons_positifs.filter(gueris=True).count()
    #     patients_decedes_positifs = patients_avec_echantillons_positifs.filter(decede=True).count()
    #
    #     synthesedistrict = SyntheseDistrict.objects.filter(maladie_id=epidemie.pk).annotate(
    #         tcas_positif=Sum('cas_positif')
    #     )
    #
    #     # Calculer le pourcentage de patients guéris et décédés parmi les patients avec des échantillons positifs
    #     if total_patients_positifs > 0:
    #         pourcentage_gueris_positifs = (patients_gueris_positifs / total_patients_positifs) * 100
    #         pourcentage_decedes_positifs = (patients_decedes_positifs / total_patients_positifs) * 100
    #     else:
    #         pourcentage_gueris_positifs = 0
    #         pourcentage_decedes_positifs = 0
    #
    #     if echantillons_nbr > 0:
    #         pourcentage_positifs = (echantillons_nbrP / echantillons_nbr) * 100
    #     else:
    #         pourcentage_positifs = 0
    #
    #     last_update = Echantillon.objects.filter(maladie=epidemie).order_by('-created_at').values_list('created_at',
    #                                                                                                    flat=True).first()
    #
    #     top_districts = DistrictSanitaire.objects.annotate(
    #         num_echantillons=Count('commune__patient__echantillons',
    #                                filter=Q(commune__patient__echantillons__maladie=epidemie)),
    #         num_gueris=Count('commune__patient__echantillons',
    #                          filter=Q(commune__patient__gueris=True, commune__patient__echantillons__maladie=epidemie)),
    #         num_decedes=Count('commune__patient__echantillons',
    #                           filter=Q(commune__patient__decede=True, commune__patient__echantillons__maladie=epidemie))
    #     ).order_by('-num_echantillons')[:5] + SyntheseDistrict
    #
    #     cases_by_region = (
    #         Patient.objects.filter(echantillons__maladie=epidemie, echantillons__resultat='POSITIF')
    #         .values('commune__district__region__name')
    #         .annotate(total=Count('id'))
    #         .order_by('-total')
    #     )
    #
    #     # Obtenez le nombre de cas par district
    #     cases_by_district = (
    #         Patient.objects.filter(echantillons__maladie=epidemie, echantillons__resultat='POSITIF')
    #         .values('commune__district__region__name', 'commune__district__nom')
    #         .annotate(total=Count('id'))
    #         .order_by('-total')
    #     )
    #
    #     # Passer les données au template
    #
    #     # Passer les données au template
    #     context = {
    #         'cases_by_region': cases_by_region,
    #         'cases_by_district': cases_by_district,
    #
    #         'epidemie': epidemie,
    #         'epidemie_id': epidemie.pk,  # Passer l'ID de l'épidémie
    #         'epidemie_nom': epidemie.nom,  # Passer le nom de l'épidémie
    #
    #         'top_districts': top_districts,
    #         'last_update': last_update,
    #         'echantillons_nbr': echantillons_nbr,
    #         'echantillons_nbrP': echantillons_nbrP,
    #         'pourcentage_positifs': pourcentage_positifs,
    #         'patients_gueris': patients_gueris,
    #         'patients_decedes': patients_decedes,
    #         'patients': patients,
    #         'total_patients_positifs': total_patients_positifs,
    #         'patients_gueris_positifs': patients_gueris_positifs,
    #         'patients_decedes_positifs': patients_decedes_positifs,
    #         'pourcentage_gueris_positifs': pourcentage_gueris_positifs,
    #         'pourcentage_decedes_positifs': pourcentage_decedes_positifs,
    #     }
    #
    #     return render(request, self.template_name, context)



class HomePageView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    # form_class = LoginForm
    template_name = "dingue/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtenez le nombre de cas par région
        cases_by_region = (
            Patient.objects.filter(echantillons__resultat='POSITIF')
            .values('commune__district__region__name')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        # Obtenez le nombre de cas par district
        cases_by_district = (
            Patient.objects.filter(echantillons__resultat='POSITIF')
            .values('commune__district__region__name', 'commune__district__nom')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        # Passer les données au template
        context['cases_by_region'] = cases_by_region
        context['cases_by_district'] = cases_by_district

        return context

    # # Call the parent class's dispatch method for normal view processing.
    #     return super().dispatch(request, *args, **kwargs)
    #
    # def dispatch(self, request, *args, **kwargs):
    #     # Call the parent class's dispatch method for normal view processing.
    #     response = super().dispatch(request, *args, **kwargs)
    #
    #     # Check if the user is authenticated. If not, redirect to the login page.
    #     if not request.user.is_authenticated:
    #         return redirect('login')
    #
    #     # Check if the user is a member of the RH Managers group
    #     if request.user.groups.filter(name='ressources_humaines').exists():
    #         # Redirect the user to the RH Managers dashboard
    #         return redirect('rhdash')
    #
    #     # Check if the user is a member of the RH Employees group
    #     elif request.user.groups.filter(name='project').exists():
    #         # Redirect the user to the RH Employees dashboard
    #         return redirect('rh_employee_dashboard')
    #
    #     # If the user is not a member of any specific group, return a forbidden response
    #     else:
    #         return redirect('page_not_found')
    #         # return HttpResponseForbidden("You don't have permission to access this page.")


class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = "dingue/patientlist.html"
    context_object_name = "patients"
    paginate_by = 10
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_nbr = Patient.objects.all().count()
        context['patient_nbr'] = patient_nbr

        return context


class PatientCreateView(CreateView):
    model = Patient
    template_name = 'global/patient/create_patient_form.html'  # Template pour afficher le formulaire de création
    form_class = PatientForm
    success_url = reverse_lazy('patientlist')  # URL de redirection après la création


class PatientUpdateView(UpdateView):
    model = Patient
    template_name = 'patient_form.html'  # Réutilisation du même template que pour la création
    fields = '__all__'
    success_url = reverse_lazy('patient-list')


class PatientDeleteView(DeleteView):
    model = Patient
    template_name = 'patient_confirm_delete.html'  # Template pour confirmer la suppression
    success_url = reverse_lazy('patient-list')


class EchantillonListView(LoginRequiredMixin, ListView):
    model = Echantillon
    template_name = "dingue/echantillonlist.html"
    context_object_name = "echantillons"
    paginate_by = 1000
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_nbr = Patient.objects.all().count()
        context['patient_nbr'] = patient_nbr

        return context


class EchantillonCreateView(CreateView):
    model = Echantillon
    template_name = 'echantillon_form.html'  # Template pour afficher le formulaire de création
    fields = '__all__'
    success_url = reverse_lazy('echantillon-list')


class EchantillonUpdateView(UpdateView):
    model = Echantillon
    template_name = 'echantillon_form.html'
    fields = '__all__'
    success_url = reverse_lazy('echantillon-list')


class EchantillonDeleteView(DeleteView):
    model = Echantillon
    template_name = 'echantillon_confirm_delete.html'
    success_url = reverse_lazy('echantillon-list')


@api_view(['POST'])
def import_data(request):
    data = request.data

    for row in data:
        try:
            # Gestion des données du modèle Patient
            patient, created = Patient.objects.get_or_create(
                code_patient=row.get('code_patient', ''),
                defaults={
                    'nom': row.get('nom', ''),
                    'prenoms': row.get('prenoms', ''),
                    'contact': row.get('contact', ''),
                    'date_naissance': row.get('date_naissance', None),
                    # Mappez d'autres champs nécessaires
                }
            )
            # Gestion des données du modèle Echantillon
            Echantillon.objects.create(
                patient=patient,
                code_echantillon=row.get('code_echantillon', ''),
                resultat=row.get('resultat', 'NEGATIF'),  # Valeur par défaut ou dynamique
                # Mappez d'autres champs nécessaires
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"status": "success"}, status=200)
