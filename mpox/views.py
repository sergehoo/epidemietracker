from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response

from epidemie.models import HealthRegion, City, Commune, EpidemicCase, ServiceSanitaire
from epidemie.serializers import HealthRegionSerializer, CitySerializer, CommuneSerializer, EpidemicCaseSerializer, \
    ServiceSanitaireSerializer
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


class MpoxHomeDash(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    # form_class = LoginForm
    template_name = "global/mpox/dashboard_mpox.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #
    #     # Filtrer les patients ayant au moins un échantillon avec un résultat positif
    #     positive_cases = (
    #         Patient.objects.filter(echantillons__resultat='POSITIF')
    #         .values('commune__name')
    #         .annotate(total=Count('id'))
    #         .order_by('-total')
    #     )
    #
    #     # Passer les données au template
    #     context['positive_cases'] = positive_cases
    #
    #     return context

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


# class PatientViewSet(viewsets.ModelViewSet):
#     queryset = Patient.objects.all()  # Définir le queryset ici
#     serializer_class = PatientSerializer
#
#     def get_queryset(self):
#         # Filtrer les patients qui ont au moins un échantillon avec un résultat positif
#         queryset = self.queryset.filter(
#             Q(echantillons__resultat='POSITIF')
#         ).distinct()
#
#         return queryset
#

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
