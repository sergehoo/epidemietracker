from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView
from rest_framework import viewsets
from rest_framework.response import Response
from tablib import Dataset

from dingue.admin import EchantillonResource
from epidemie.tasks import sync_health_regions, process_city_data, generate_commune_report, alert_for_epidemic_cases

from epidemie.models import Patient, Echantillon, HealthRegion, City, Commune, EpidemicCase, ServiceSanitaire
from epidemie.serializers import HealthRegionSerializer, CitySerializer, EpidemicCaseSerializer, PatientSerializer, \
    ServiceSanitaireSerializer, CommuneSerializer


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


def import_view(request):
    return render(request, 'dingue/import.html')


def import_echantillons(request):
    if request.method == 'POST':
        # Vérifie si le fichier est bien envoyé
        if 'file' not in request.FILES:
            messages.error(request, 'Veuillez sélectionner un fichier à importer.')
            return render(request, 'dingue/import.html')

        echantillon_resource = EchantillonResource()
        dataset = Dataset()
        new_echantillons = request.FILES['file']

        try:
            imported_data = dataset.load(new_echantillons.read(), format='xlsx')
            result = echantillon_resource.import_data(dataset, dry_run=True)  # Dry run for preview

            if not result.has_errors():
                # Pour afficher un aperçu des données
                preview_data = dataset.dict
                if 'confirm' in request.POST:
                    echantillon_resource.import_data(dataset, dry_run=False)  # Commit the import
                    messages.success(request, 'Données importées avec succès')
                    return redirect('nom_de_votre_vue_suivante')
                return render(request, 'dingue/import.html', {'preview_data': preview_data})

            messages.error(request, 'Erreur lors de l\'importation des données : vérifiez les données et réessayez.')

        except Exception as e:
            messages.error(request, f"Erreur lors de l'importation des données : {e}")
            return render(request, 'dingue/import.html')

    return render(request, 'dingue/import.html')


class HomePageView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    # form_class = LoginForm
    template_name = "dingue/dashboard.html"

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
