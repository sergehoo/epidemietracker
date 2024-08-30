# resources.py
from import_export import resources

from epidemie.models import Echantillon


class EchantillonResource(resources.ModelResource):
    class Meta:
        model = Echantillon
        fields = ('code_echantillon', 'patient__nom', 'patient__prenoms', 'maladie__nom', 'date_collect', 'site_collect', 'resultat')
        import_id_fields = ('code_echantillon',)  # Utiliser le code_echantillon comme identifiant unique
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        # Modifier cette fonction si vous devez transformer ou valider des données avant l'importation
        pass

    def import_row(self, row, **kwargs):
        # Vous pouvez également effectuer des actions spécifiques lors de l'importation de chaque ligne
        return super().import_row(row, **kwargs)

    def get_or_init_instance(self, instance_loader, row, **kwargs):
        # Modifier cette méthode si vous devez adapter la manière dont les instances sont chargées ou initialisées
        return super().get_or_init_instance(instance_loader, row, **kwargs)
