import logging
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q, Count, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets, serializers
from rest_framework.response import Response
from tablib import Dataset
from unidecode import unidecode

from epidemie.admin import EchantillonResource
from epidemie.forms import PatientForm
from epidemie.models import HealthRegion, City, EpidemicCase, Patient, ServiceSanitaire, Commune, Epidemie, Echantillon, \
    DistrictSanitaire, SyntheseDistrict
from epidemie.serializers import HealthRegionSerializer, CitySerializer, EpidemicCaseSerializer, CommuneSerializer, \
    PatientSerializer, ServiceSanitaireSerializer


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
                    # Recherche de la région sanitaire en ignorant la casse et les accents
                    region_name = unidecode(row['Region_Sanitaire']).lower()
                    region = HealthRegion.objects.annotate(
                        similarity=TrigramSimilarity('name', region_name)
                    ).filter(similarity__gt=0.3).order_by('-similarity').first()

                    if not region:
                        messages.error(request, f"Région sanitaire '{row['Region_Sanitaire']}' introuvable.")
                        continue

                    # Recherche du district sanitaire en ignorant la casse et les accents
                    district_name = unidecode(row['DistrictSanitaire']).lower()
                    district = DistrictSanitaire.objects.annotate(
                        similarity=TrigramSimilarity('nom', district_name)
                    ).filter(similarity__gt=0.3).order_by('-similarity').first()

                    if not district:
                        messages.error(request, f"District sanitaire '{row['DistrictSanitaire']}' introuvable.")
                        continue

                    # Recherche de la commune sans filtrer par district
                    commune_name = unidecode(row['patient__commune']).lower()
                    commune = Commune.objects.annotate(
                        similarity=TrigramSimilarity('name', commune_name)
                    ).filter(similarity__gt=0.3).order_by('-similarity').first()

                    if not commune:
                        messages.error(request, f"Commune '{row['patient__commune']}' introuvable.")
                        continue

                    maladie_name = row['maladie__nom']
                    maladie, _ = Epidemie.objects.get_or_create(nom=maladie_name)

                    # Création ou mise à jour du patient
                    patient, created = Patient.objects.update_or_create(
                        code_patient=row['code_echantillon'],
                        defaults={
                            'nom': row['patient__nom'],
                            'prenoms': row['patient__prenoms'],
                            'date_naissance': row['patient__datenaissance'],
                            'genre': row['patient_sexe'],
                            'commune': commune,
                            'contact': 'N/A'  # Remplacez par la colonne appropriée si elle existe
                        }
                    )

                    # Création ou mise à jour de l'échantillon
                    Echantillon.objects.update_or_create(
                        code_echantillon=row['code_echantillon'],
                        defaults={
                            'patient': patient,
                            'maladie': maladie,  # Assurez-vous que l'ID de l'épidémie est correct
                            'date_collect': row['date_collect'],
                            'site_collect': row['site_collect'],
                            'resultat': row['resultat'],
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


class LandinguePageView(LoginRequiredMixin, ListView):
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
            Patient.objects.filter(echantillons__resultat='POSITIF')
            .values('commune__name')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        # Passer les données au template
        context['positive_cases'] = positive_cases

        return context


class EpidemieDetailView(LoginRequiredMixin, DetailView):
    model = Epidemie
    template_name = 'global/dashboard.html'
    context_object_name = "epidemiedetail"
    ordering = ['id']

    def get(self, request, pk):
        epidemie = get_object_or_404(Epidemie, pk=pk)

        # Filtrer les échantillons et les patients par épidémie
        echantillons_nbr = Echantillon.objects.filter(maladie=epidemie).count()
        echantillons_nbrP = Echantillon.objects.filter(maladie=epidemie, resultat='POSITIF').count()

        patients = Patient.objects.filter(echantillons__maladie=epidemie).distinct().count()
        patients_gueris = Patient.objects.filter(echantillons__maladie=epidemie, gueris=True).distinct().count()
        patients_decedes = Patient.objects.filter(echantillons__maladie=epidemie, decede=True).distinct().count()

        # Nombre total de patients dont les échantillons ont été positifs
        echantillons_positifs = Echantillon.objects.filter(maladie=epidemie, resultat='POSITIF')
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
            Patient.objects.filter(echantillons__maladie=epidemie, echantillons__resultat='POSITIF')
            .values('commune__district__region__name')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        cases_by_district = (
            Patient.objects.filter(echantillons__maladie=epidemie, echantillons__resultat='POSITIF')
            .values('commune__district__region__name', 'commune__district__nom')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        context = {
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
            'patients_gueris': patients_gueris + total_gueri,
            'patients_decedes': patients_decedes,
            'patients': patients + total_cas_negatif,
            'total_patients_positifs': total_patients_positifs + total_cas_positif ,
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
        }

        return render(request, self.template_name, context)

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
