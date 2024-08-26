from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response

from epidemie.models import HealthRegion, City, Commune, EpidemicCase, ServiceSanitaire, Epidemie, Echantillon, Patient, \
    DistrictSanitaire
from epidemie.serializers import HealthRegionSerializer, CitySerializer, CommuneSerializer, EpidemicCaseSerializer, \
    ServiceSanitaireSerializer, PatientSerializer
from epidemie.tasks import sync_health_regions, process_city_data, generate_commune_report, alert_for_epidemic_cases


# Create your views here.


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


# class PatientViewSet(viewsets.ModelViewSet):
#     queryset = Patient.objects.all()
#     serializer_class = PatientSerializer
#
#     def get_queryset(self):
#         # Filtrer les patients qui ont au moins un échantillon avec un résultat positif
#         queryset = self.queryset.filter(
#             Q(echantillons__resultat='POSITIF', echantillons__maladie='MPOX')
#         ).distinct()
#
#         # Annoter les informations de région, district et commune pour chaque patient
#         queryset = queryset.select_related(
#             'commune__district__region'
#         )
#         return queryset
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()  # Définir le queryset par défaut
    serializer_class = PatientSerializer

    def get_queryset(self):
        # Obtenez l'ID de l'épidémie pour 'MPOX'
        try:
            moxp_epidemie = Epidemie.objects.get(nom='MPOX')
        except Epidemie.DoesNotExist:
            return Patient.objects.none()  # Retourne une queryset vide

        # Filtrer les patients qui ont au moins un échantillon avec un résultat positif pour MPOX
        queryset = Patient.objects.filter(
            echantillons__resultat='POSITIF',
            echantillons__maladie=moxp_epidemie
        ).distinct()

        # Annoter les informations de région, district et commune pour chaque patient
        queryset = queryset.select_related(
            'commune__district__region'
        )
        return queryset


class MpoxHomeDash(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    # form_class = LoginForm
    template_name = "global/mpox/dashboard_mpox.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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
                             filter=Q(commune__patient__echantillons__maladie__nom='MPOX',
                                      commune__patient__gueris=True)),
            num_decedes=Count('commune__patient__echantillons',
                              filter=Q(commune__patient__echantillons__maladie__nom='MPOX',
                                       commune__patient__decede=True))
        ).order_by('-num_echantillons')[:5]

        epidemies = Epidemie.objects.filter(nom='MPOX').order_by('id')

        # Ajouter les données au contexte
        context.update({
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
        })

        return context


class ServiceSanitaireViewSet(viewsets.ModelViewSet):
    queryset = ServiceSanitaire.objects.all()
    serializer_class = ServiceSanitaireSerializer


class CommuneAggregatedViewSet(viewsets.ModelViewSet):
    queryset = Commune.objects.all()
    serializer_class = CommuneSerializer

    def list(self, request, *args, **kwargs):
        communes = self.queryset.annotate(
            total_patients=Count('patient', filter=Q(patient__echantillons__resultat='POSITIF'))
        )
        serializer = self.get_serializer(communes, many=True)
        return Response(serializer.data)
