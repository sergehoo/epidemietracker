from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from leaflet.forms.widgets import LeafletWidget

from epidemie.models import HealthRegion, City, EpidemicCase, DistrictSanitaire, Epidemie, Echantillon, Patient, \
    Employee, Symptom, ServiceSanitaire, Commune

admin.site.site_header = 'EPIDEMIE BACK-END CONTROLER'
admin.site.site_title = 'EPIDEMIE Super Admin Pannel'
admin.site.site_url = 'http://veillesanitaire.com/'
admin.site.index_title = 'MSHP-CMU'
admin.empty_value_display = '**Empty**'


# admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Patient)
# admin.site.register(Employee)
#

# Register your models here.
#
# class HealthRegionAdmin(ModelAdmin):
#     list_display = (
#         'name',
#         'geom',
#     )
#
#
# admin.site.register(HealthRegion, HealthRegionAdmin)
#
#
# class CityAdmin(ModelAdmin):
#     list_display = (
#         'name',
#         'region',
#         'location',
#     )
#
#
# admin.site.register(City, CityAdmin)
#
#
class EpidemicCaseAdmin(ModelAdmin):
    list_display = (
        'disease_name',
        'city',
        'date_reported',
        'num_cases',
    )


admin.site.register(EpidemicCase, EpidemicCaseAdmin)




class HealthRegionAdminForm(forms.ModelForm):
    class Meta:
        model = HealthRegion
        fields = '__all__'
        widgets = {
            'geom': LeafletWidget(),
        }


class HealthRegionAdmin(admin.ModelAdmin):
    form = HealthRegionAdminForm


admin.site.register(HealthRegion, HealthRegionAdmin)


class CityAdminForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'
        widgets = {
            'location': LeafletWidget(),
        }


class CityAdmin(admin.ModelAdmin):
    form = CityAdminForm


admin.site.register(City, CityAdmin)


@admin.register(DistrictSanitaire)
class DistrictSanitaireAdmin(ModelAdmin):
    pass
    # list_display = (
    #     'disease_name',
    #     'city',
    #     'date_reported',
    #     'num_cases',
    # )


@admin.register(Symptom)
class SymptomAdmin(ModelAdmin):
    pass


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    pass


@admin.register(Patient)
class PatientAdmin(ModelAdmin):
    pass


@admin.register(Epidemie)
class EpidemieAdmin(ModelAdmin):
    pass


@admin.register(ServiceSanitaire)
class ServiceSanitaireAdmin(ModelAdmin):
    pass


@admin.register(Commune)
class CommuneAdmin(ModelAdmin):
    pass
