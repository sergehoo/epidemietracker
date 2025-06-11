import secrets

from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX
from import_export.widgets import ForeignKeyWidget
from leaflet.forms.widgets import LeafletWidget

from epidemie.models import HealthRegion, City, EpidemicCase, DistrictSanitaire, Epidemie, Echantillon, Patient, \
    Employee, Symptom, ServiceSanitaire, Commune, CasSynthese, SyntheseDistrict, Information, Alert, PolesRegionaux, \
    StructureProvenance, SignalementJournal, Platform
from epidemie.ressources import SyntheseDistrictResource

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


@admin.register(PolesRegionaux)
class PolesRegionauxAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name')
    list_filter = ('id', 'name')
    search_fields = ('id', 'name')


@admin.register(HealthRegion)
class HealthRegionAdmin(ImportExportModelAdmin):
    resource_class = HealthRegionResource
    list_display = ('id', 'name', 'poles')


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
        fields = ('id', 'nom', 'region__name', 'geojson')  # Fields to be imported/exported
        export_order = ('id', 'nom', 'region__name', 'geojson')

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
    list_display = ('nom', 'region', 'geojson')


@admin.register(Symptom)
class SymptomAdmin(ModelAdmin):
    pass


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
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


# @admin.register(SyntheseDistrict)
# class SyntheseDistrictAdmin(ImportExportModelAdmin):
#     pass

@admin.register(SyntheseDistrict)
class SyntheseDistrictAdmin(ImportExportModelAdmin):
    resource_class = SyntheseDistrictResource
    list_display = ('district_sanitaire', 'maladie', 'nbre_cas_suspects', 'cas_positif', 'cas_negatif', 'evacue')


@admin.register(Echantillon)
class EchantillonAdmin(ImportExportModelAdmin):
    resource_class = EchantillonResource
    # form = DistrictSanitaireForm
    list_display = ('maladie', 'code_echantillon', 'patient', 'resultat')
    search_fields = ['patient', 'patient__commune']
    list_filter = ['resultat']


@admin.register(Patient)
class PatientAdmin(ImportExportModelAdmin):
    # resource_class = EchantillonResource
    # form = DistrictSanitaireForm
    list_display = ('nom', 'prenoms', 'commune', 'status')
    search_fields = ['status', 'nom']
    list_filter = ['status', 'gueris', 'decede']


@admin.register(Information)
class InformationAdmin(ImportExportModelAdmin):
    pass


@admin.register(Alert)
class AlertAdmin(ImportExportModelAdmin):
    pass
    # resource_class = (EchantillonResource)


@admin.register(SignalementJournal)
class SignalementJournalAdmin(admin.ModelAdmin):
    list_display = ('id', 'maladie', 'patient', 'commune', 'statut_reception', 'created_at', 'source_application')
    list_filter = ('statut_reception', 'maladie', 'commune', 'created_at')
    search_fields = ('patient__nom', 'patient__prenom', 'maladie__nom', 'commune__name', 'message')
    list_select_related = ('maladie', 'patient', 'commune')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'source_ip', 'user_api')
    fieldsets = (
        ('Information de base', {
            'fields': ('maladie', 'patient', 'commune', 'hopital')
        }),
        ('Détails du signalement', {
            'fields': ('date_analyse', 'statut_reception', 'message')
        }),
        ('Métadonnées', {
            'fields': ('donnees_brutes', 'source_application', 'source_ip', 'user_api', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('maladie', 'patient', 'commune', 'hopital', 'user_api')


@admin.register(StructureProvenance)
class StructureProvenanceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'district')
    list_filter = ('district',)
    search_fields = ('nom', 'district__name')
    list_select_related = ('district',)
    ordering = ('nom',)


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "is_active", "last_connected", "api_key")
    readonly_fields = ("api_key",)
# @admin.register(Platform)
# class PlatformAdmin(admin.ModelAdmin):
#     """
#     Interface d'administration personnalisée pour le modèle Platform.
#     """
#
#     # --- Configuration de l'affichage dans la liste ---
#     list_display = (
#         'name',
#         'user',
#         'is_active',
#         'last_connected',
#         'api_key_preview'
#     )
#
#     list_filter = (
#         'is_active',
#         'last_connected'
#     )
#
#     search_fields = (
#         'name',
#         'user__username',  # Permet de rechercher par le nom d'utilisateur associé
#         'user__email'
#     )
#
#     # --- Configuration du formulaire d'édition ---
#
#     # Organise les champs en sections pour plus de clarté
#     fieldsets = (
#         ('Informations Générales', {
#             'fields': ('name', 'user', 'is_active')
#         }),
#
#     )
#
#     # --- Sécurité et Automatisation ---
#
#     def get_readonly_fields(self, request, obj=None):
#         """
#         Rend la clé API non-modifiable après la création de l'objet.
#         """
#         if obj:  # Si l'objet existe déjà (formulaire de modification)
#             return self.readonly_fields + ('api_key', 'last_connected')
#         # Pour un nouvel objet (formulaire de création), les champs ne sont pas en lecture seule
#         return self.readonly_fields
#
#     def save_model(self, request, obj, form, change):
#         """
#         Génère automatiquement une clé API sécurisée si c'est un nouvel objet.
#         """
#         if not obj.pk:  # Si l'objet n'a pas encore d'ID, c'est une création
#             # Génère un token hexadécimal de 64 caractères (32 octets)
#             obj.api_key = secrets.token_hex(32)
#
#         super().save_model(request, obj, form, change)
#
#     @admin.display(description='Aperçu Clé API')
#     def api_key_preview(self, obj):
#         """
#         Affiche seulement les 8 premiers caractères de la clé API dans la liste
#         pour ne pas surcharger l'affichage et pour la sécurité.
#         """
#         if obj.api_key:
#             return f"{obj.api_key}..."
#         return "Non générée"
