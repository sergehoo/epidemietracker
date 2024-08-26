from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX

from epidemie.models import Echantillon


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


@admin.register(Echantillon)
class EchantillonAdmin(ImportExportModelAdmin):
    resource_class = EchantillonResource
