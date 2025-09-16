import json
import logging
import os
import tempfile
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction, models
from django.db.models import Count, Q, F, Max
from django.db.models.functions import Lower, TruncDate
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView, ListView, CreateView
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from tablib import Dataset
from unidecode import unidecode

from api.serializers import SignalementExterneSerializer
from epidemie.authentication import APIKeyAuthentication
from epidemie.tasks import sync_health_regions, process_city_data, generate_commune_report, alert_for_epidemic_cases

from epidemie.models import Patient, Echantillon, HealthRegion, City, Commune, EpidemicCase, ServiceSanitaire, \
    DistrictSanitaire, Epidemie, CasSynthese, SyntheseDistrict, SignalementJournal, Information
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = SyntheseDistrict.objects.all()
    serializer_class = SyntheseDistrictSerializer

    def get_queryset(self):
        maladie_id = self.request.query_params.get('maladie_id')
        if maladie_id:
            return self.queryset.filter(maladie_id=maladie_id)
        return self.queryset.none()


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


# class RecevoirSignalementAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         serializer = SignalementExterneSerializer(data=request.data)
#         if serializer.is_valid():
#             data = serializer.validated_data
#             maladie_nom = data.get("maladie_detectee")
#
#             # 1. Vérifier si la maladie fait partie des épidémies
#             try:
#                 epidemie = Epidemie.objects.get(nom__iexact=maladie_nom)
#             except Epidemie.DoesNotExist:
#                 return Response({"detail": "Maladie non enregistrée comme épidémie."}, status=400)
#
#             # 2. Chercher ou créer le patient
#             patient, _ = Patient.objects.get_or_create(
#                 code_patient=data["code_patient"],
#                 defaults={
#                     "nom": data["nom"],
#                     "prenoms": data["prenoms"],
#                     "genre": data["genre"],
#                     "date_naissance": data["date_naissance"],
#                     "contact": data["contact"],
#                 }
#             )
#
#             # 3. Associer les infos géographiques
#             commune = Commune.objects.filter(nom__icontains=data["commune"]).first()
#             hopital = ServiceSanitaire.objects.filter(nom__icontains=data["hopital"]).first()
#
#             if commune:
#                 patient.commune = commune
#             if hopital:
#                 patient.hopital = hopital
#             patient.cas_suspects = False
#             patient.gueris = False
#             patient.decede = False
#             patient.save()
#
#             # 4. Ajouter la synthèse district (agrégation)
#             SyntheseDistrict.objects.update_or_create(
#                 maladie=epidemie,
#                 district_sanitaire=hopital.district if hopital else None,
#                 defaults={
#                     "cas_positif": 1
#                 }
#             )
#
#             return Response({"message": "Signalement enregistré avec succès."})
#         return Response(serializer.errors, status=400)
class RecevoirSignalementAPIView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic  # Assure l'intégrité des données
    def post(self, request):
        serializer = SignalementExterneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        maladie_nom = data.get("maladie_detectee")

        # 1. Vérification de l'épidémie avec cache
        epidemie = self._get_epidemie(maladie_nom)
        if not epidemie:
            return Response({"detail": "Maladie non enregistrée comme épidémie."}, status=400)

        # 2. Gestion du patient en une requête
        patient = self._get_or_create_patient(data)

        # 3. Mise à jour des informations géographiques
        self._update_geographic_info(patient, data)

        # 4. Journalisation du signalement
        self._log_signalement(request, patient, epidemie, data)

        # 5. Mise à jour de la synthèse district
        self._update_synthese_district(epidemie, patient)

        self._creer_echantillon(patient, epidemie, data)

        return Response({"message": "Signalement enregistré avec succès."})

    def _get_epidemie(self, maladie_nom):
        """Récupère l'épidémie avec cache pour améliorer les performances"""
        try:
            return Epidemie.objects.get(nom__iexact=maladie_nom)
        except Epidemie.DoesNotExist:
            return None

    def _get_or_create_patient(self, data):
        defaults = {
            "nom": data["nom"],
            "prenoms": data["prenoms"],
            "genre": data["genre"],
            "date_naissance": data["date_naissance"],
            "contact": data["contact"],
            "cas_suspects": False,
            "gueris": False,
            "decede": False,
        }
        patient, created = Patient.objects.get_or_create(
            code_patient=data["code_patient"],
            defaults=defaults
        )
        if not created:
            updated = False
            for key, value in defaults.items():
                if getattr(patient, key) != value:
                    setattr(patient, key, value)
                    updated = True
            if updated:
                patient.save()
        return patient

    def _update_geographic_info(self, patient, data):
        """Met à jour les informations géographiques avec select_related"""
        commune = Commune.objects.filter(name__icontains=data["commune"]).first()
        hopital = ServiceSanitaire.objects.filter(nom__icontains=data["hopital"]).select_related('district').first()

        if commune:
            patient.commune = commune
        if hopital:
            patient.hopital = hopital
        patient.save()

    def _creer_echantillon(self, patient, epidemie, data):
        """Crée ou met à jour un échantillon avec le code donné s’il existe"""

        code = data.get("code_echantillon", None)

        if code:
            echantillon, created = Echantillon.objects.get_or_create(
                code_echantillon=code,
                defaults={
                    "patient": patient,
                    "maladie": epidemie,
                    "date_collect": data.get("date_analyse"),
                    "site_collect": data.get("hopital", ""),
                    "resultat": True,
                    "status_echantillons": "POSITIF",
                }
            )
            if not created:
                print(f"⚠️ Échantillon {code} déjà existant. Aucune mise à jour faite.")
        else:
            echantillon = Echantillon.objects.create(
                patient=patient,
                maladie=epidemie,
                date_collect=data.get("date_analyse"),
                site_collect=data.get("hopital", ""),
                resultat=True,
                status_echantillons="POSITIF"
            )
            print("✅ Échantillon généré automatiquement:", echantillon.code_echantillon)

    def _log_signalement(self, request, patient, epidemie, data):
        """Journalise le signalement pour traçabilité"""
        platform = getattr(request.user, 'platform', None)
        if platform:
            platform.last_connected = timezone.now()
            platform.save()

        SignalementJournal.objects.create(
            patient=patient,
            maladie=epidemie,
            hopital=patient.hopital,
            commune=patient.commune,
            donnees_brutes=json.loads(json.dumps(data, cls=DjangoJSONEncoder)),
            source_ip=self._get_client_ip(request),
            user_api=request.user,
            source_application=platform,
            statut_reception="SUCCES",
            message="Signalement enregistré avec succès"
        )

        # 🔔 Création automatique d'une Information
        titre = f"Alerte : Nouveau cas de {epidemie.nom}"
        message = (
            f"<p>Nouveau cas de <strong>{epidemie.nom}</strong> signalé.</p>"
            f"<ul>"
            f"<li><strong>à :</strong> {patient.commune.name if patient.commune else 'Non renseignée'}</li>"
            f"<li><strong> Hôpital :</strong> {patient.hopital.nom if patient.hopital else 'Non renseigné'}</li>"
            f"<li><strong> le : </strong> {timezone.now().strftime('%d/%m/%Y à %Hh%M')}</li>"
            f"</ul>"
        )

        Information.objects.create(
            titre=titre,
            message=message,
            auteur=request.user.employee if hasattr(request.user, 'employee') else None
        )

    def _update_synthese_district(self, epidemie, patient):
        print("DEBUG: Hôpital=", patient.hopital)
        print("DEBUG: District=", getattr(patient.hopital, "district", None))

        if patient.hopital and getattr(patient.hopital, "district", None):
            SyntheseDistrict.increment_counter(
                epidemie,
                patient.hopital.district,
                "cas_positif"
            )
        else:
            print("⚠️ Aucun district associé à cet hôpital.")

    def _get_client_ip(self, request):
        """Récupère l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


class LandingPageView(LoginRequiredMixin, ListView):
    """
    This view now only handles the initial rendering of the HTML page.
    All dynamic data will be loaded via the API.
    """
    model = Epidemie
    template_name = "global/landingpage.html"
    context_object_name = 'epidemies'  # The initial list can be rendered on first load
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pre-populate symptom data for the modal to avoid an extra API call
        all_epidemies = Epidemie.objects.prefetch_related('symptomes').all()
        symptoms_data = {
            epidemie.id: {
                'nom': epidemie.nom,
                'description': epidemie.description or "Informations détaillées sur les symptômes courants.",
                'symptomes': [
                    {'nom': s.nom, 'description': s.description or "Pas de description.", 'frequence': s.frequence,
                     'gravite': s.gravite}
                    for s in epidemie.symptomes.all()
                ]
            } for epidemie in all_epidemies
        }
        context['symptoms_data_json'] = json.dumps(symptoms_data)
        return context


# @require_GET
# def landing_page_api(request):
#     """
#     This new API view provides all the dashboard data in a single JSON response.
#     It's designed to be called asynchronously by the frontend.
#     """
#     # --- Global Statistics (Cached) ---
#     global_stats = cache.get('global_epidemic_stats_v2')
#     if not global_stats:
#         stats = Patient.objects.aggregate(
#             total_confirmed=Count('id', filter=Q(echantillons__resultat=True), distinct=True),
#             total_recovered=Count('id', filter=Q(gueris=True, echantillons__resultat=True), distinct=True),
#             total_deaths=Count('id', filter=Q(decede=True, echantillons__resultat=True), distinct=True),
#             total_suspects=Count('id', filter=Q(cas_suspects=True)),
#             new_suspects_7d=Count('id', filter=Q(cas_suspects=True, created_at__gte=timezone.now() - timedelta(days=7)))
#         )
#         confirmed = stats.get('total_confirmed', 0)
#         recovered = stats.get('total_recovered', 0)
#         deaths = stats.get('total_deaths', 0)
#
#         global_stats = {
#             'total_cas_actifs': confirmed - recovered - deaths,
#             'total_gueris': recovered,
#             'total_deces': deaths,
#             'total_suspects': stats.get('total_suspects', 0),
#             'nouveaux_suspects_7j': stats.get('new_suspects_7d', 0),
#             'taux_guerison': round((recovered / confirmed) * 100, 1) if confirmed else 0,
#             'taux_mortalite': round((deaths / confirmed) * 100, 1) if confirmed else 0,
#         }
#         cache.set('global_epidemic_stats_v2', global_stats, 60 * 15)
#
#     # --- Epidemics List ---
#     epidemies_qs = Epidemie.objects.annotate(
#         last_activity=Max('echantillon__date_collect', filter=Q(echantillon__resultat=True)),
#         total_cases=Count('echantillon__patient', filter=Q(echantillon__resultat=True), distinct=True),
#         total_deaths=Count('echantillon__patient',
#                            filter=Q(echantillon__resultat=True, echantillon__patient__decede=True), distinct=True),
#         new_cases_7d=Count('echantillon', filter=Q(echantillon__resultat=True,
#                                                    echantillon__date_collect__gte=timezone.now() - timedelta(days=7)))
#     ).order_by(F('last_activity').desc(nulls_last=True))
#
#     epidemies_data = [{
#         'id': e.id,
#         'nom': e.nom,
#         'thumbnails_url': e.thumbnails.url if e.thumbnails else '',
#         'last_activity': e.last_activity.strftime('%d %b %Y') if e.last_activity else 'Aucun',
#         'total_cases': e.total_cases,
#         'total_deaths': e.total_deaths,
#         'new_cases_7d': e.new_cases_7d,
#         'status_display': e.status_display,
#         'status_class': e.status_class,
#     } for e in epidemies_qs]
#
#     # --- Chart Data (Cached) ---
#     chart_data = cache.get('chart_evolution_data_v2')
#     if not chart_data:
#         dates = [(timezone.now() - timedelta(days=i)).date() for i in range(29, -1, -1)]
#         daily_counts = Echantillon.objects.filter(date_collect__date__gte=dates[0]).extra(
#             {"day": "date(date_collect)"}).values("day").annotate(
#             confirmed=Count('id', filter=Q(resultat=True)),
#             deaths=Count('id', filter=Q(resultat=True, patient__decede=True))
#         ).order_by('day')
#         counts_by_date = {item['day'].strftime('%Y-%m-%d'): item for item in daily_counts}
#         chart_data = {
#             'labels': [d.strftime('%d/%m') for d in dates],
#             'confirmed': [counts_by_date.get(d.strftime('%Y-%m-%d'), {}).get('confirmed', 0) for d in dates],
#             'deaths': [counts_by_date.get(d.strftime('%Y-%m-%d'), {}).get('deaths', 0) for d in dates],
#         }
#         cache.set('chart_evolution_data_v2', chart_data, 60 * 15)
#
#     # --- Map & Alerts Data ---
#     # --- Map & Alerts Data ---
#     foyers = SignalementJournal.objects.filter(
#         created_at__gte=timezone.now() - timedelta(days=90),
#         commune__latitude__isnull=False, commune__longitude__isnull=False
#     ).select_related('maladie', 'commune').order_by('commune', '-created_at').distinct('commune')
#
#     foyers_data = [
#         {
#             'lat': f.commune.latitude,
#             'lon': f.commune.longitude,
#             'maladie': f.maladie.nom,
#             'commune': f.commune.nom,
#             'niveau': f.get_niveau_display(),
#             'date': f.created_at.strftime('%d/%m/%Y'),
#         }
#         for f in foyers
#     ]
#
#     # >>> Nouveau: agrégations par commune pour la carte (confirmés/guéris/décès/suspects)
#     # Essaie Patient.commune ; sinon, bascule sur Echantillon.patient__commune
#     try:
#         commune_stats_qs = (
#             Patient.objects.filter(commune__isnull=False)
#             .values('commune__id', 'commune__nom', 'commune__latitude', 'commune__longitude')
#             .annotate(
#                 confirmed=Count('id', filter=Q(echantillons__resultat=True), distinct=True),
#                 recovered=Count('id', filter=Q(gueris=True, echantillons__resultat=True), distinct=True),
#                 deaths=Count('id', filter=Q(decede=True, echantillons__resultat=True), distinct=True),
#                 suspects=Count('id', filter=Q(cas_suspects=True), distinct=True),
#                 last_activity=Max('echantillons__date_collect', filter=Q(echantillons__resultat=True)),
#             )
#         )
#     except Exception:
#         commune_stats_qs = (
#             Echantillon.objects.filter(patient__commune__isnull=False)
#             .values('patient__commune__id', 'patient__commune__nom',
#                     'patient__commune__latitude', 'patient__commune__longitude')
#             .annotate(
#                 confirmed=Count('id', filter=Q(resultat=True)),
#                 deaths=Count('id', filter=Q(resultat=True, patient__decede=True)),
#                 recovered=Count('id', filter=Q(resultat=True, patient__gueris=True)),
#                 suspects=Count('patient', filter=Q(patient__cas_suspects=True), distinct=True),
#                 last_activity=Max('date_collect', filter=Q(resultat=True)),
#             )
#         )
#
#     # Normalisation des champs selon la branche utilisée ci-dessus
#     commune_stats = []
#     for row in commune_stats_qs:
#         # Détecte quelle clé est présente
#         cid = row.get('commune__id') or row.get('patient__commune__id')
#         nom = row.get('commune__nom') or row.get('patient__commune__nom')
#         lat = row.get('commune__latitude') or row.get('patient__commune__latitude')
#         lon = row.get('commune__longitude') or row.get('patient__commune__longitude')
#         last = row.get('last_activity')
#
#         if lat is None or lon is None:
#             continue
#
#         commune_stats.append({
#             'commune_id': cid,
#             'commune': nom,
#             'lat': float(lat),
#             'lon': float(lon),
#             'confirmed': int(row.get('confirmed') or 0),
#             'recovered': int(row.get('recovered') or 0),
#             'deaths': int(row.get('deaths') or 0),
#             'suspects': int(row.get('suspects') or 0),
#             'last_activity': last.strftime('%d/%m/%Y') if last else None,
#         })
#
#     alertes_qs = SignalementJournal.objects.select_related('maladie', 'commune__district__region').order_by(
#         '-created_at')[:5]
#     alertes_data = [{
#         'maladie_nom': a.maladie.nom,
#         'region_nom': a.commune.district.region.nom,
#         'message': a.message,
#         'created_since': f"{a.created_at.strftime('%d %b, %H:%M')}",
#         'niveau_class': 'danger' if a.niveau == 'H' else ('warning' if a.niveau == 'M' else 'primary')
#     } for a in alertes_qs]
#
#     data = {
#         'global_stats': global_stats,
#         'epidemies': epidemies_data,
#         'chart_data': chart_data,
#         'map_data': {
#             'foyers': foyers_data,
#             'regions_touchees': foyers.values('commune__district__region').distinct().count(),
#             'foyers_actifs': foyers.count(),
#             # >>> expose les stats par commune
#             'commune_stats': commune_stats,
#         },
#         'alertes': alertes_data,
#         'last_updated': timezone.now().strftime('%H:%M:%S')
#     }
#
#     return JsonResponse(data)
@require_GET
def landing_page_api(request):
    """
    API renvoyant toutes les données du tableau de bord en un seul JSON.
    Compatible avec Commune.geom (PointField).
    """

    # --- Global Statistics (Cached) ---
    global_stats = cache.get('global_epidemic_stats_v2')
    if not global_stats:
        stats = Patient.objects.aggregate(
            total_confirmed=Count('id', filter=Q(echantillons__resultat=True), distinct=True),
            total_recovered=Count('id', filter=Q(gueris=True, echantillons__resultat=True), distinct=True),
            total_deaths=Count('id', filter=Q(decede=True, echantillons__resultat=True), distinct=True),
            total_suspects=Count('id', filter=Q(cas_suspects=True), distinct=True),
            new_suspects_7d=Count(
                'id',
                filter=Q(cas_suspects=True, created_at__gte=timezone.now() - timedelta(days=7)),
                distinct=True,
            ),
        )
        confirmed = stats.get('total_confirmed') or 0
        recovered = stats.get('total_recovered') or 0
        deaths = stats.get('total_deaths') or 0

        global_stats = {
            'total_cas_actifs': max(0, confirmed - recovered - deaths),
            'total_gueris': recovered,
            'total_deces': deaths,
            'total_suspects': stats.get('total_suspects') or 0,
            'nouveaux_suspects_7j': stats.get('new_suspects_7d') or 0,
            'taux_guerison': round((recovered / confirmed) * 100, 1) if confirmed else 0,
            'taux_mortalite': round((deaths / confirmed) * 100, 1) if confirmed else 0,
        }
        cache.set('global_epidemic_stats_v2', global_stats, 60 * 15)

    # --- Epidemics List (gère echantillon/echantillons) ---
    try:
        epidemies_qs = (
            Epidemie.objects.annotate(
                last_activity=Max('echantillon__date_collect', filter=Q(echantillon__resultat=True)),
                total_cases=Count('echantillon__patient', filter=Q(echantillon__resultat=True), distinct=True),
                total_deaths=Count(
                    'echantillon__patient',
                    filter=Q(echantillon__resultat=True, echantillon__patient__decede=True),
                    distinct=True,
                ),
                new_cases_7d=Count(
                    'echantillon',
                    filter=Q(
                        echantillon__resultat=True,
                        echantillon__date_collect__gte=timezone.now() - timedelta(days=7),
                    ),
                ),
            ).order_by(F('last_activity').desc(nulls_last=True))
        )
    except Exception:
        epidemies_qs = (
            Epidemie.objects.annotate(
                last_activity=Max('echantillons__date_collect', filter=Q(echantillons__resultat=True)),
                total_cases=Count('echantillons__patient', filter=Q(echantillons__resultat=True), distinct=True),
                total_deaths=Count(
                    'echantillons__patient',
                    filter=Q(echantillons__resultat=True, echantillons__patient__decede=True),
                    distinct=True,
                ),
                new_cases_7d=Count(
                    'echantillons',
                    filter=Q(
                        echantillons__resultat=True,
                        echantillons__date_collect__gte=timezone.now() - timedelta(days=7),
                    ),
                ),
            ).order_by(F('last_activity').desc(nulls_last=True))
        )

    epidemies_data = [
        {
            'id': e.id,
            'nom': e.nom,
            'thumbnails_url': e.thumbnails.url if getattr(e, 'thumbnails', None) else '',
            'last_activity': e.last_activity.strftime('%d %b %Y') if e.last_activity else 'Aucun',
            'total_cases': e.total_cases,
            'total_deaths': e.total_deaths,
            'new_cases_7d': e.new_cases_7d,
            'status_display': getattr(e, 'status_display', None),
            'status_class': getattr(e, 'status_class', None),
        }
        for e in epidemies_qs
    ]

    # --- Chart Data (Cached) ---
    chart_data = cache.get('chart_evolution_data_v2')
    if not chart_data:
        start_date = (timezone.now() - timedelta(days=29)).date()
        daily_counts = (
            Echantillon.objects.filter(date_collect__date__gte=start_date)
            .annotate(day=TruncDate('date_collect'))
            .values('day')
            .annotate(
                confirmed=Count('id', filter=Q(resultat=True)),
                deaths=Count('id', filter=Q(resultat=True, patient__decede=True)),
            )
            .order_by('day')
        )
        counts_by_date = {
            item['day'].strftime('%Y-%m-%d'): item for item in daily_counts if item['day'] is not None
        }
        dates = [(timezone.now() - timedelta(days=i)).date() for i in range(29, -1, -1)]
        chart_data = {
            'labels': [d.strftime('%d/%m') for d in dates],
            'confirmed': [counts_by_date.get(d.strftime('%Y-%m-%d'), {}).get('confirmed', 0) for d in dates],
            'deaths': [counts_by_date.get(d.strftime('%Y-%m-%d'), {}).get('deaths', 0) for d in dates],
        }
        cache.set('chart_evolution_data_v2', chart_data, 60 * 15)

    # --- Map & Alerts Data ---

    # Foyers (1 par commune), avec géom présente
    foyers = (
        SignalementJournal.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=90),
            commune__geom__isnull=False,            # ⬅️ filtre corrigé
        )
        .select_related('maladie', 'commune')
        .order_by('commune', '-created_at')
        .distinct('commune')
    )

    foyers_data = []
    for f in foyers:
        # geom est un Point : x=lon, y=lat
        lat = float(f.commune.geom.y)
        lon = float(f.commune.geom.x)
        foyers_data.append({
            'lat': lat,
            'lon': lon,
            'maladie': f.maladie.nom,
            'commune': f.commune.name,   # ⬅️ name (pas nom)
            'niveau': f.get_niveau_display(),
            'date': f.created_at.strftime('%d/%m/%Y'),
        })

    # Agrégations par commune : confirmés / guéris / décès / suspects
    # Branche 1: Patient.commune ; Fallback: Echantillon.patient__commune
    try:
        commune_stats_qs = (
            Patient.objects.filter(commune__isnull=False, commune__geom__isnull=False)
            .values('commune__id', 'commune__name')
            .annotate(
                confirmed=Count('id', filter=Q(echantillons__resultat=True), distinct=True),
                recovered=Count('id', filter=Q(gueris=True, echantillons__resultat=True), distinct=True),
                deaths=Count('id', filter=Q(decede=True, echantillons__resultat=True), distinct=True),
                suspects=Count('id', filter=Q(cas_suspects=True), distinct=True),
                last_activity=Max('echantillons__date_collect', filter=Q(echantillons__resultat=True)),
                geom_json=AsGeoJSON('commune__geom'),   # ⬅️ récupère les coords
            )
        )
        branch = 'patient'
    except Exception:
        commune_stats_qs = (
            Echantillon.objects.filter(patient__commune__isnull=False, patient__commune__geom__isnull=False)
            .values('patient__commune__id', 'patient__commune__name')
            .annotate(
                confirmed=Count('id', filter=Q(resultat=True)),
                deaths=Count('id', filter=Q(resultat=True, patient__decede=True)),
                recovered=Count('id', filter=Q(resultat=True, patient__gueris=True)),
                suspects=Count('patient', filter=Q(patient__cas_suspects=True), distinct=True),
                last_activity=Max('date_collect', filter=Q(resultat=True)),
                geom_json=AsGeoJSON('patient__commune__geom'),
            )
        )
        branch = 'echantillon'

    commune_stats = []
    for row in commune_stats_qs:
        # Récupère l'ID/nom selon la branche
        if branch == 'patient':
            cid = row['commune__id']
            nom = row['commune__name']
        else:
            cid = row['patient__commune__id']
            nom = row['patient__commune__name']

        # Parse AsGeoJSON -> {"type":"Point","coordinates":[lon,lat]}
        coords = [None, None]
        try:
            gj = json.loads(row['geom_json']) if row.get('geom_json') else None
            if isinstance(gj, dict) and isinstance(gj.get('coordinates'), (list, tuple)) and len(gj['coordinates']) >= 2:
                coords = gj['coordinates']
        except Exception:
            pass
        lon, lat = coords[0], coords[1]
        if lon is None or lat is None:
            continue

        last = row.get('last_activity')
        commune_stats.append({
            'commune_id': cid,
            'commune': nom,
            'lat': float(lat),
            'lon': float(lon),
            'confirmed': int(row.get('confirmed') or 0),
            'recovered': int(row.get('recovered') or 0),
            'deaths': int(row.get('deaths') or 0),
            'suspects': int(row.get('suspects') or 0),
            'last_activity': last.strftime('%d/%m/%Y') if last else None,
        })

    alertes_qs = (
        SignalementJournal.objects
        .select_related('maladie', 'commune__district__region')
        .order_by('-created_at')[:5]
    )
    alertes_data = [
        {
            'maladie_nom': a.maladie.nom,
            'region_nom': a.commune.district.region.name if a.commune and a.commune.district else '',
            'message': a.message,
            'created_since': a.created_at.strftime('%d %b, %H:%M'),
            'niveau_class': 'danger' if a.statut_reception == 'H' else ('warning' if a.statut_reception == 'M' else 'primary'),
        }
        for a in alertes_qs
    ]

    return JsonResponse(
        {
            'global_stats': global_stats,
            'epidemies': epidemies_data,
            'chart_data': chart_data,
            'map_data': {
                'foyers': foyers_data,
                'regions_touchees': foyers.values('commune__district__region').distinct().count(),
                'foyers_actifs': foyers.count(),
                'commune_stats': commune_stats,
            },
            'alertes': alertes_data,
            'last_updated': timezone.now().strftime('%H:%M:%S'),
        }
    )