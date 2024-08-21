from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView

from epidemie.models import Patient, Echantillon


# Create your views here.


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