import logging
import os
import tempfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage
from django.db.models import Count, Q
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView
from rest_framework import viewsets
from rest_framework.response import Response
from tablib import Dataset
from unidecode import unidecode
from epidemie.tasks import sync_health_regions, process_city_data, generate_commune_report, alert_for_epidemic_cases

from epidemie.models import Patient, Echantillon, HealthRegion, City, Commune, EpidemicCase, ServiceSanitaire, \
    DistrictSanitaire, Epidemie, CasSynthese, SyntheseDistrict
from epidemie.serializers import HealthRegionSerializer, CitySerializer, EpidemicCaseSerializer, PatientSerializer, \
    ServiceSanitaireSerializer, CommuneSerializer, CasSyntheseSerializer, SyntheseDistrictSerializer


# Create your views here.
class HealthRegionViewSet(viewsets.ModelViewSet):
    queryset = HealthRegion.objects.all()
    serializer_class = HealthRegionSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        sync_health_regions.delay()  # Appel de la tâche en arrière-plan


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        process_city_data.delay(instance.id)  # Appel de la tâche en arrière-plan avec l'ID de la ville


class CommuneViewSet(viewsets.ModelViewSet):
    queryset = Commune.objects.all()
    serializer_class = CommuneSerializer

    def perform_destroy(self, instance):
        instance.delete()
        generate_commune_report.delay()  # Appel de la tâche en arrière-plan après suppression


class EpidemicCaseViewSet(viewsets.ModelViewSet):
    queryset = EpidemicCase.objects.all()
    serializer_class = EpidemicCaseSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        alert_for_epidemic_cases.delay()


# class HealthRegionViewSet(viewsets.ModelViewSet):
#     queryset = HealthRegion.objects.all()
#     serializer_class = HealthRegionSerializer
#
#
# class CityViewSet(viewsets.ModelViewSet):
#     queryset = City.objects.all()
#     serializer_class = CitySerializer
#
#
# class CommuneViewSet(viewsets.ModelViewSet):
#     queryset = Commune.objects.all()
#     serializer_class = CommuneSerializer
#
#
# class EpidemicCaseViewSet(viewsets.ModelViewSet):
#     queryset = EpidemicCase.objects.all()
#     serializer_class = EpidemicCaseSerializer


# class PatientViewSet(viewsets.ModelViewSet):
#     queryset = Patient.objects.all()
#     serializer_class = PatientSerializer

# class PatientViewSet(viewsets.ModelViewSet):
#     queryset = Patient.objects.all()
#     serializer_class = PatientSerializer
#
#     def get_queryset(self):
#         # Filtrer les patients qui ont au moins un échantillon avec un résultat positif
#         queryset = self.queryset.filter(
#             Q(echantillons__resultat='POSITIF')
#         ).distinct()
#
#         # Annoter les informations de région, district et commune pour chaque patient
#         queryset = queryset.select_related(
#             'commune__district__region'
#         )
#         return queryset
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_queryset(self):
        # Obtenez l'ID de l'épidémie à partir des paramètres de l'URL
        epidemie_id = self.request.query_params.get('epidemie_id', None)

        # Filtrer les patients qui ont au moins un échantillon avec un résultat positif
        queryset = self.queryset.filter(
            Q(echantillons__resultat=True)
        ).distinct()

        # Si un ID d'épidémie est fourni, filtrer les patients en fonction de l'épidémie
        if epidemie_id:
            queryset = queryset.filter(
                echantillons__maladie_id=epidemie_id
            )

        # Annoter les informations de région, district et commune pour chaque patient
        queryset = queryset.select_related(
            'commune__district__region'
        )

        return queryset


class ServiceSanitaireViewSet(viewsets.ModelViewSet):
    queryset = ServiceSanitaire.objects.all()
    serializer_class = ServiceSanitaireSerializer


class CommuneAggregatedViewSet(viewsets.ModelViewSet):
    queryset = Commune.objects.all()
    serializer_class = CommuneSerializer

    def list(self, request, *args, **kwargs):
        communes = self.queryset.annotate(
            total_patients=Count('patient', filter=Q(patient__echantillons__resultat='POSITIF'))
        ).select_related('district__region')
        serializer = self.get_serializer(communes, many=True)
        return Response(serializer.data)


# Exemple de mise à jour pour la vue des données agrégées des communes
# class CommuneAggregatedViewSet(viewsets.ModelViewSet):
#     queryset = Commune.objects.all()
#     serializer_class = CommuneSerializer
#
#     def list(self, request, *args, **kwargs):
#         communes = self.queryset.annotate(
#             total_patients=Count('patient', filter=Q(patient__echantillons__resultat='POSITIF'))
#         )
#         serializer = self.get_serializer(communes, many=True)
#         return Response(serializer.data)

# Register the new viewset


def dashboard_view(request):
    return render(request, 'dingue/home.html')


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
#             temp_file_name = default_storage.save(
#                 os.path.join('temp', new_echantillons.name),
#                 ContentFile(new_echantillons.read())
#             )
#             temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_name)
#
#             try:
#                 imported_data = dataset.load(open(temp_file_path, 'rb').read(), format='xlsx')
#                 result = echantillon_resource.import_data(dataset, dry_run=True)
#
#                 if not result.has_errors():
#                     preview_data = dataset.dict
#                     return render(request, 'dingue/import.html', {
#                         'preview_data': preview_data,
#                         'temp_file_name': temp_file_name
#                     })
#
#                 messages.error(request, 'Erreur lors de l\'importation des données : vérifiez les données et réessayez.')
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
#
#                 # Commencez par parcourir les données pour effectuer les recherches insensibles à la casse et aux accents
#                 for row in dataset.dict:
#                     # Recherche de la région sanitaire
#                     region_name = row['Region_Sanitaire'].strip().lower()
#                     region = HealthRegion.objects.annotate(
#                         similarity=TrigramSimilarity(Lower('name'), region_name)
#                     ).filter(similarity__gt=0.3).order_by('-similarity').first()
#
#                     if not region:
#                         messages.error(request, f"Région sanitaire '{row['Region_Sanitaire']}' introuvable.")
#                         continue
#
#                     # Recherche du district sanitaire
#                     district_name = row['DistrictSanitaire'].strip().lower()
#                     district = DistrictSanitaire.objects.filter(region=region).annotate(
#                         similarity=TrigramSimilarity(Lower('nom'), district_name)
#                     ).filter(similarity__gt=0.3).order_by('-similarity').first()
#
#                     if not district:
#                         messages.error(request, f"District sanitaire '{row['DistrictSanitaire']}' introuvable.")
#                         continue
#
#                     # Recherche de la commune
#                     commune_name = row['patient__commune'].strip().lower()
#                     commune = Commune.objects.filter(district=district).annotate(
#                         similarity=TrigramSimilarity(Lower('name'), commune_name)
#                     ).filter(similarity__gt=0.3).order_by('-similarity').first()
#
#                     if not commune:
#                         messages.error(request, f"Commune '{row['patient__commune']}' introuvable.")
#                         continue
#
#                     maladie_name = row['maladie__nom']
#                     maladie, _ = Epidemie.objects.get_or_create(nom=maladie_name)
#
#                     # Mise à jour ou création du patient
#                     patient, created = Patient.objects.update_or_create(
#                         code_patient=row['code_echantillon'],
#                         defaults={
#                             'nom': row['patient__nom'],
#                             'prenoms': row['patient__prenoms'],
#                             'date_naissance': row['patient__datenaissance'],
#                             'commune': commune,
#                             'contact': 'N/A'
#                         }
#                     )
#
#                     # Mise à jour ou création de l'échantillon
#                     Echantillon.objects.update_or_create(
#                         code_echantillon=row['code_echantillon'],
#                         defaults={
#                             'patient': patient,
#                             'maladie': maladie,
#                             'date_collect': row['date_collect'],
#                             'site_collect': row['site_collect'],
#                             'resultat': row['resultat'],
#                         }
#                     )
#
#                 # Importation finale des données
#                 echantillon_resource.import_data(dataset, dry_run=False)
#                 messages.success(request, 'Données importées avec succès')
#                 return redirect('echantillons')
#             else:
#                 messages.error(request, 'Fichier temporaire introuvable.')
#                 return render(request, 'dingue/import.html')
#
#     return render(request, 'dingue/import.html')


# class PatientCreateView(LoginRequiredMixin, CreateView):
#     model = Patient
#     form_class = PatientCreateForm
#     template_name = "pages/patient_create.html"
#     success_url = reverse_lazy(
#         'glogal_search')  # Assurez-vous de remplacer 'nom_de_la_vue_de_liste_des_factures' par le nom correct de votre vue de liste des factures
#
#     def form_valid(self, form):
#         nom = form.cleaned_data['nom'].upper()
#         prenoms = form.cleaned_data['prenoms'].upper()
#         date_naissance = form.cleaned_data['date_naissance']
#         contact = form.cleaned_data['contact']
#
#         # Vérification des doublons
#         if Patient.objects.filter(nom__iexact=nom, prenoms__iexact=prenoms, date_naissance=date_naissance).exists():
#             messages.error(self.request, 'Ce patient existe déjà.')
#             return self.form_invalid(form)
#
#         if Patient.objects.filter(contact=contact).exists():
#             messages.error(self.request, 'Un patient avec ce contact existe déjà.')
#             return self.form_invalid(form)
#
#         # Sauvegarder l'objet Patient
#         self.object = form.save()
#
#         # Gérer les informations de localisation
#         localite_data = {
#             'contry': form.cleaned_data['pays'],
#             'ville': form.cleaned_data['ville'],
#             'commune': form.cleaned_data['commune']
#         }
#         localite, created = Location.objects.get_or_create(**localite_data)
#         self.object.localite = localite
#         self.object.save()
#
#         messages.success(self.request, 'Patient créé avec succès!')
#         return redirect(self.success_url)

class CasSyntheseViewSet(viewsets.ModelViewSet):
    queryset = CasSynthese.objects.all()
    serializer_class = CasSyntheseSerializer


class SyntheseDistrictViewSet(viewsets.ModelViewSet):
    queryset = SyntheseDistrict.objects.all()
    serializer_class = SyntheseDistrictSerializer

    def get_queryset(self):
        return self.queryset.filter(maladie_id=self.request.query_params.get('maladie_id'))


def get_infected_cases_data(request, epidemie_id):
    epidemie = get_object_or_404(Epidemie, pk=epidemie_id)

    # Count male and female cases
    male_cases = Patient.objects.filter(echantillons__maladie=epidemie, echantillons__resultat=True,
                                        genre='Male').count()
    female_cases = Patient.objects.filter(echantillons__maladie=epidemie, echantillons__resultat=True,
                                          genre='Female').count()

    data = {
        'male_cases': male_cases,
        'female_cases': female_cases,
    }

    return JsonResponse(data)