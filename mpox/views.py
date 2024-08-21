from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.


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

