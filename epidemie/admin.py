from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX
from import_export.widgets import ForeignKeyWidget
from leaflet.forms.widgets import LeafletWidget

from epidemie.models import HealthRegion, City, EpidemicCase, DistrictSanitaire, Epidemie, Echantillon, Patient, \
    Employee, Symptom, ServiceSanitaire, Commune, CasSynthese, SyntheseDistrict

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


class HealthRegionResource(resources.ModelResource):
    class Meta:
        model = HealthRegion
        fields = ('id', 'name')  # Adjust fields as needed
        export_order = ('id', 'name')


@admin.register(HealthRegion)
class HealthRegionAdmin(ImportExportModelAdmin):
    resource_class = HealthRegionResource
    list_display = ('id', 'name')


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


class DistrictSanitaireResource(resources.ModelResource):
    region__name = fields.Field(
        column_name='region__name',
        attribute='region',
        widget=ForeignKeyWidget(HealthRegion, 'name')
    )

    class Meta:
        model = DistrictSanitaire
        fields = ('id', 'nom', 'region__name')  # Fields to be imported/exported
        export_order = ('id', 'nom', 'region__name')

    def before_import_row(self, row, **kwargs):
        region_name = row.get('region__name')
        if region_name:
            try:
                row['region'] = HealthRegion.objects.get(name=region_name)
            except HealthRegion.DoesNotExist:
                row['region'] = None


@admin.register(DistrictSanitaire)
class DistrictSanitaireAdmin(ImportExportModelAdmin):
    resource_class = DistrictSanitaireResource
    list_display = ('nom', 'region')


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
class CommuneAdmin(admin.ModelAdmin):
    search_fields = ['name', 'place', 'is_in', 'district__nom']
    list_display = ['name', 'place', 'population', 'district']
    list_filter = ['district', 'source']

    # Optionnel: pour personnaliser l'affichage des résultats de recherche
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        # Vous pouvez ajouter des filtres supplémentaires ici si nécessaire
        return queryset, use_distinct


class EchantillonResource(resources.ModelResource):
    class Meta:
        model = Echantillon
        import_id_fields = ('code_echantillon',)
        skip_unchanged = True
        report_skipped = False
        fields = ('patient', 'code_echantillon', 'maladie', 'date_collect', 'resultat')

    def get_import_formats(self):
        formats = (XLSX,)  # Ajoutez ici d'autres formats si nécessaire
        return [fmt for fmt in formats if fmt.is_available()]


@admin.register(CasSynthese)
class CasSyntheseAdmin(ImportExportModelAdmin):
    pass
    # resource_class = EchantillonResource

@admin.register(SyntheseDistrict)
class SyntheseDistrictAdmin(ImportExportModelAdmin):
    pass

@admin.register(Echantillon)
class EchantillonAdmin(ImportExportModelAdmin):
    resource_class = (EchantillonResource)
