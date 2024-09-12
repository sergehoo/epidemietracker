# resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from epidemie.models import Echantillon, Epidemie, DistrictSanitaire, SyntheseDistrict


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


class SyntheseDistrictResource(resources.ModelResource):
    maladie = fields.Field(
        column_name='maladie',
        attribute='maladie',
        widget=ForeignKeyWidget(Epidemie, 'id')  # or use another field like 'nom' if necessary
    )

    district_sanitaire = fields.Field(
        column_name='district_sanitaire',
        attribute='district_sanitaire',
        widget=ForeignKeyWidget(DistrictSanitaire, 'nom')  # assuming the district names match
    )

    class Meta:
        model = SyntheseDistrict
        import_id_fields = ['id']
        fields = (
            'id', 'maladie', 'district_sanitaire', 'nbre_cas_suspects', 'cas_positif', 'cas_negatif', 'evacue', 'decede',
            'gueri', 'suivi_en_cours', 'nbre_sujets_contacts', 'contacts_en_cours_suivi', 'contacts_sorti_suivi',
            'devenu_suspect', 'devenu_positif'
        )