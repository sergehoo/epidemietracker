from django.db.models import Q, Count
from django.shortcuts import render
from rest_framework import viewsets, serializers
from rest_framework.response import Response

from epidemie.models import HealthRegion, City, EpidemicCase, Patient, ServiceSanitaire, Commune
from epidemie.serializers import HealthRegionSerializer, CitySerializer, EpidemicCaseSerializer, CommuneSerializer, \
    PatientSerializer, ServiceSanitaireSerializer


class HealthRegionViewSet(viewsets.ModelViewSet):
    queryset = HealthRegion.objects.all()
    serializer_class = HealthRegionSerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class CommuneViewSet(viewsets.ModelViewSet):
    queryset = Commune.objects.all()
    serializer_class = CommuneSerializer


class EpidemicCaseViewSet(viewsets.ModelViewSet):
    queryset = EpidemicCase.objects.all()
    serializer_class = EpidemicCaseSerializer


# class PatientViewSet(viewsets.ModelViewSet):
#     queryset = Patient.objects.all()
#     serializer_class = PatientSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()  # Définir le queryset ici
    serializer_class = PatientSerializer

    def get_queryset(self):
        # Filtrer les patients qui ont au moins un échantillon avec un résultat positif
        queryset = self.queryset.filter(
            Q(echantillons__resultat='POSITIF')
        ).distinct()

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
        )
        serializer = self.get_serializer(communes, many=True)
        return Response(serializer.data)


# Register the new viewset


def dashboard_view(request):
    return render(request, 'dingue/home.html')
