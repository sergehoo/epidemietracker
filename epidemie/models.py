import datetime
import random
import secrets
import string
import uuid

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.timezone import now
from djgeojson.fields import PointField
from simple_history.models import HistoricalRecords
from tinymce.models import HTMLField

Sexe_choices = [
    ('Homme', 'Homme'),
    ('Femme', 'Femme'),

]
Resultat_choices = [
    ('POSITIF', 'POSITIF'),
    ('NEGATIF', 'NEGATIF'),

]
situation_matrimoniales_choices = [
    ('Celibataire', 'Celibataire'),
    ('Concubinage', 'Concubinage'),
    ('Marie', 'Marié'),
    ('Divorce', 'Divorcé'),
    ('Veuf', 'Veuf'),
    ('Autre', 'Autre'),
]
Goupe_sanguin_choices = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
]
Patient_statut_choices = [
    ('Admis', 'Admis'),
    ('Sorti', 'Sorti'),
    ('Transféré', 'Transféré'),
    ('Décédé', 'Décédé'),
    ('Sous observation', 'Sous observation'),
    ('Sous traitement', 'Sous traitement'),
    ('Chirurgie programmée', 'Chirurgie programmée'),
    ('En chirurgie', 'En chirurgie'),
    ('Récupération post-opératoire', 'Récupération post-opératoire'),
    ('USI', 'Unité de soins intensifs (USI)'),
    ('Urgence', 'Urgence'),
    ('Consultation externe', 'Consultation externe'),
    ('Réhabilitation', 'Réhabilitation'),
    ('En attente de diagnostic', 'En attente de diagnostic'),
    ('Traitement en cours', 'Traitement en cours'),
    ('Suivi programmé', 'Suivi programmé'),
    ('Consultation', 'Consultation'),
    ('Sortie en attente', 'Sortie en attente'),
    ('Isolement', 'Isolement'),
    ('Ambulantoire', 'Ambulantoire'),
    ('Aucun', 'Aucun')
]


class Information(models.Model):
    titre = models.CharField(max_length=255)
    message = HTMLField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    auteur = models.ForeignKey('Employee', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.titre


class PolesRegionaux(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Pole"


# Modèle des Régions Sanitaires
class HealthRegion(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    poles = models.ForeignKey(PolesRegionaux, on_delete=models.SET_NULL, null=True, blank=True, related_name='regions')

    def __str__(self):
        return f"{self.name}-{self.poles}"


class DistrictSanitaire(models.Model):
    nom = models.CharField(max_length=100, null=True, blank=True, )
    region = models.ForeignKey(HealthRegion, on_delete=models.CASCADE, null=True, blank=True, )
    geom = models.PointField(null=True, blank=True, )
    geojson = models.JSONField(null=True, blank=True, )

    def __str__(self):
        return f'{self.nom}---->{self.region}'


class Commune(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)
    population = models.CharField(max_length=100, null=True, blank=True)
    is_in = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    osm_id = models.BigIntegerField(null=True, blank=True)
    osm_type = models.CharField(max_length=50, null=True, blank=True)
    district = models.ForeignKey(DistrictSanitaire, on_delete=models.CASCADE, null=True, blank=True, )
    geom = models.PointField()

    def __str__(self):
        return f"{self.name} - {self.district} ({self.geom})"


class ServiceSanitaire(models.Model):
    nom = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    district = models.ForeignKey(DistrictSanitaire, on_delete=models.CASCADE, null=True, blank=True, )
    geom = models.PointField(srid=4326, null=True, blank=True)
    upstream = models.CharField(max_length=255, null=True, blank=True)
    date_modified = models.DateTimeField(null=True, blank=True)
    source_url = models.URLField(max_length=500, null=True, blank=True)
    completeness = models.CharField(max_length=100, null=True, blank=True)
    uuid = models.UUIDField(null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    what3words = models.CharField(max_length=255, null=True, blank=True)
    version = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom}- {self.district} {self.geom}"


ROLE_CHOICES = (
    ('National', 'National'),
    ('Region', 'Region'),
    ('District', 'District'),
)


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee", )
    gender = models.CharField(choices=Sexe_choices, max_length=100, null=True, blank=True, )
    situation_matrimoniale = models.CharField(choices=situation_matrimoniales_choices, max_length=100, null=True,
                                              blank=True, )
    phone = models.CharField(null=True, blank=True, max_length=20, default='+22507070707')
    birthdate = models.DateField(null=True, blank=True)
    # dpt = models.ForeignKey('Service', on_delete=models.CASCADE, verbose_name="service", blank=True, null=True)
    district = models.ForeignKey('DistrictSanitaire', on_delete=models.CASCADE, verbose_name="District Sanitaire",
                                 blank=True, null=True)
    service = models.ForeignKey('ServiceSanitaire', on_delete=models.CASCADE, verbose_name="Service Sanitaire",
                                blank=True, null=True)
    job_title = models.CharField(null=True, blank=True, max_length=50, verbose_name="Titre du poste")

    slug = models.SlugField(null=True, blank=True, help_text="slug field", verbose_name="slug ", unique=True,
                            editable=False)

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='District')
    created_at = models.DateTimeField(auto_now_add=now, )

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user.username}- {self.user.first_name} {self.user.last_name}"

    class Meta:
        permissions = (
            ("access_all", "access all"),
            ("access_region", "access region"),
            ("access_district", "access district"),
            # ("can_view_district", "Can view district"),
            # ("can_view_region", "Can view region"),
            # ("can_view_national", "Can view national"),
            # ("can_edit_employee", "Can edit employee details"),
            # ("can_delete_employee", "Can delete employee"),
            ("can_assign_roles", "Can assign roles to employees"),
        )


class Patient(models.Model):
    code_patient = models.CharField(max_length=225, blank=True, unique=True, editable=False)
    nom = models.CharField(max_length=225, blank=True)
    prenoms = models.CharField(max_length=225, blank=True)
    contact = models.CharField(max_length=225, blank=True)
    situation_matrimoniale = models.CharField(max_length=225, choices=situation_matrimoniales_choices, blank=True)
    lieu_naissance = models.CharField(max_length=200, blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    genre = models.CharField(max_length=10, choices=Sexe_choices, blank=True, )
    nationalite = models.CharField(max_length=200, blank=True, )
    profession = models.CharField(max_length=200, null=True, blank=True)
    nbr_enfants = models.PositiveIntegerField(default=0, blank=True)
    groupe_sanguin = models.CharField(choices=Goupe_sanguin_choices, max_length=20, blank=True, null=True)
    niveau_etude = models.CharField(max_length=500, null=True, blank=True)
    employeur = models.CharField(max_length=500, null=True, blank=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=now)
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True, blank=True)
    hopital = models.ForeignKey(ServiceSanitaire, on_delete=models.SET_NULL, null=True, blank=True)
    quartier = models.CharField(max_length=500, null=True, blank=True)
    # ville = models.ForeignKey('City', on_delete=models.SET_NULL, null=True)
    status = models.CharField(choices=Patient_statut_choices, max_length=100, default='Aucun', null=True, blank=True)
    gueris = models.BooleanField(default=False)
    cas_suspects = models.BooleanField(default=False)
    decede = models.BooleanField(default=False)
    cascontact = models.ManyToManyField('self', blank=True)
    history = HistoricalRecords()

    class Meta:
        indexes = [
            models.Index(fields=['code_patient']),  # Pour les recherches fréquentes
        ]
        ordering = ['-created_at']
        permissions = (('voir_patient', 'Peut voir patient'),)

    def save(self, *args, **kwargs):
        # Générer un code_patient unique constitué de chiffres et de caractères alphabétiques
        if not self.code_patient:
            # Générer 16 chiffres à partir de l'UUID
            digits = ''.join(filter(str.isdigit, str(uuid.uuid4().int)))[:8]
            # Générer 4 caractères alphabétiques aléatoires
            letters = ''.join(random.choices(string.ascii_uppercase, k=4))
            # Combiner les chiffres et les lettres pour former le code_patient
            self.code_patient = digits + letters

        super(Patient, self).save(*args, **kwargs)

    @property
    def calculate_age(self):
        if self.date_naissance:
            today = datetime.date.today()
            age = today.year - self.date_naissance.year - (
                    (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
            return age
        else:
            return None

    @property
    def latest_constante(self):
        return self.constantes.order_by('-created_at').first()

    def __str__(self):
        return f'{self.prenoms} {self.nom} -- {self.commune}--{self.genre}'


class Symptom(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.nom}'


class Typeepidemie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self): return self.nom


class Epidemie(models.Model):
    nom = models.CharField(max_length=100)
    type = models.ForeignKey('Typeepidemie', null=True, blank=True, on_delete=models.CASCADE)
    description = HTMLField(blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    thumbnails = models.ImageField(null=True, blank=True, upload_to='epidemie/thumbnails')
    symptomes = models.ManyToManyField(Symptom, related_name='épidémies')

    class Meta:
        permissions = (('voir_epidemie', 'peut voir epidemie'),)

    @property
    def regions_impactees(self):
        # Récupère toutes les régions impactées par cette épidémie
        regions = HealthRegion.objects.filter(city__commune__echantillons__maladie=self).distinct().count()
        return regions

    @property
    def personnes_touchees(self):
        # Compte le nombre de personnes ayant des échantillons positifs pour cette épidémie
        nombre_personnes_touchees = Patient.objects.filter(
            echantillons__maladie=self,
            echantillons__resultat=True
        ).distinct().count()
        return nombre_personnes_touchees

    @property
    def personnes_touchees_agreges(self):
        # Compte le nombre de personnes ayant des échantillons positifs pour cette épidémie
        synthesedistrict = SyntheseDistrict.objects.filter(maladie_id=self)
        total_cas_positif = synthesedistrict.aggregate(Sum('cas_positif'))['cas_positif__sum'] or 0

        return total_cas_positif

    @property
    def personnes_decedes_agreges(self):
        # Compte le nombre de personnes ayant des échantillons positifs pour cette épidémie
        synthesedistrict = SyntheseDistrict.objects.filter(maladie_id=self)
        total_decede = synthesedistrict.aggregate(Sum('decede'))['decede__sum'] or 0

        return total_decede

    @property
    def personnes_decedees(self):
        # Compte le nombre de personnes décédées ayant des échantillons positifs pour cette épidémie
        nombre_personnes_decedees = Patient.objects.filter(
            echantillons__maladie=self,
            echantillons__resultat=True,
            decede=True
        ).distinct().count()
        return nombre_personnes_decedees

    @property
    def nombre_patients_positifs_ce_mois(self):
        current_month = now().month
        current_year = now().year
        return self.echantillon_set.filter(
            resultat=True,
            date_collect__month=current_month,
            date_collect__year=current_year
        ).count()

    @property
    def dernier_cas_positif(self):
        dernier = self.echantillon_set.filter(
            resultat=True
        ).order_by('-created_at').first()

        return dernier.created_at.date() if dernier and dernier.created_at else None

    # def is_active(self):
    #     today = timezone.now().date()
    #     if not self.date_debut:  # Si pas de date de début, considérer comme inactive
    #         return False
    #     return (self.date_debut <= today) and (self.date_fin is None or self.date_fin >= today)

    def is_active(self):
        today = timezone.now().date()
        recent_threshold = today - datetime.timedelta(days=15)

        return self.echantillon_set.filter(
            resultat=True,
            created_at__date__gte=recent_threshold
        ).exists()

    @property
    def status_display(self):
        dernier_cas = self.dernier_cas_positif
        if not dernier_cas:
            return "Aucun cas détecté"

        jours_depuis = (now().date() - dernier_cas).days
        if jours_depuis > 15:
            return f"Aucun nouveau cas depuis {jours_depuis} jours"
        return "Active"

    @property
    def status_class(self):
        dernier_cas = self.dernier_cas_positif
        if not dernier_cas:
            return "secondary"
        return "danger" if self.is_active() else "light"

    def __str__(self):
        return self.nom


class PreleveMode(models.Model):
    nom = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nom


class Echantillon(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="echantillons", null=True, blank=True, )
    code_echantillon = models.CharField(null=True, blank=True, max_length=12, unique=True)
    maladie = models.ForeignKey('Epidemie', null=True, blank=True, on_delete=models.CASCADE)
    mode_preleve = models.ForeignKey('PreleveMode', null=True, blank=True, on_delete=models.CASCADE)
    date_collect = models.DateTimeField(null=True, blank=True)
    site_collect = models.CharField(null=True, blank=True, max_length=500)
    agent_collect = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.CASCADE)
    status_echantillons = models.CharField(null=True, blank=True, max_length=10)
    resultat = models.BooleanField(default=False)
    linked = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # Générer un code_patient unique uniquement avec des chiffres
        if not self.code_echantillon:
            # Utiliser uuid4 pour générer un identifiant unique et extraire les chiffres
            self.code_echantillon = ''.join(filter(str.isdigit, str(uuid.uuid4().int)))[
                                    :12]  # Limiter à 20 chiffres maximum
        super(Echantillon, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.code_echantillon}- {self.patient}-{self.maladie}"


class City(models.Model):
    name = models.CharField(max_length=200)
    region = models.ForeignKey(HealthRegion, on_delete=models.CASCADE)
    geom = models.MultiPolygonField()

    def __str__(self):
        return self.name


class EpidemicCase(models.Model):
    disease_name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    date_reported = models.DateField()
    num_cases = models.IntegerField()

    def __str__(self):
        return f"{self.disease_name} in {self.city.name} on {self.date_reported}"


class StructureProvenance(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    district = models.ForeignKey(DistrictSanitaire, on_delete=models.CASCADE, related_name='structures')

    def __str__(self):
        return self.nom


class CasSynthese(models.Model):
    district_sanitaire = models.ForeignKey(DistrictSanitaire, on_delete=models.CASCADE, related_name='cas')
    structure_provenance = models.ForeignKey(ServiceSanitaire, on_delete=models.CASCADE, related_name='cas', null=True,
                                             blank=True)
    nbre_cas_suspects = models.IntegerField(default=0, help_text="Nombre de cas suspects.")
    date_enregistrement = models.DateField(help_text="Date d'enregistrement des cas suspects.")

    # Informations sur le cas suspect
    nom_prenoms_cas = models.CharField(max_length=200, blank=True, null=True,
                                       help_text="Nom et prénoms du cas suspect.")
    age = models.IntegerField(blank=True, null=True, help_text="Âge du cas suspect.")
    sexe = models.CharField(max_length=10, choices=[('Homme', 'Homme'), ('Femme', 'Femme')], blank=True, null=True)
    cas_positif = models.BooleanField(default=False, help_text="Indique si le cas est positif.")
    cas_negatif = models.BooleanField(default=False, help_text="Indique si le cas est négatif.")
    evacue = models.BooleanField(default=False, help_text="Indique si le cas a été évacué.")

    # Dates et suivi médical
    date_prelevement = models.DateField(blank=True, null=True, help_text="Date du prélèvement.")
    decede = models.BooleanField(default=False, help_text="Indique si le cas est décédé.")
    gueri = models.BooleanField(default=False, help_text="Indique si le cas est guéri.")
    suivi_en_cours = models.BooleanField(default=True, help_text="Indique si le suivi est en cours.")

    # Suivi des contacts
    nbre_sujets_contacts = models.IntegerField(default=0, help_text="Nombre de sujets contacts.")
    contacts_en_cours_suivi = models.IntegerField(default=0, help_text="Nombre de contacts en cours de suivi.")
    contacts_sorti_suivi = models.IntegerField(default=0, help_text="Nombre de contacts sortis du suivi.")
    devenu_suspect = models.IntegerField(default=0, help_text="Nombre de contacts devenus suspects.")
    devenu_positif = models.IntegerField(default=0, help_text="Nombre de contacts devenus positifs.")

    observations = models.TextField(blank=True, null=True, help_text="Observations sur le cas et son suivi.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cas en provenance de {self.structure_provenance} enregistré le {self.date_enregistrement}"


class Alert(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class SyntheseDistrict(models.Model):
    maladie = models.ForeignKey(Epidemie, on_delete=models.CASCADE, related_name='maladiesdesynthese')
    district_sanitaire = models.ForeignKey(DistrictSanitaire, on_delete=models.CASCADE, related_name='syntheses')
    nbre_cas_suspects = models.IntegerField(default=0, help_text="Nombre de cas suspects.")
    cas_positif = models.IntegerField(default=0, help_text="Indique si le cas est positif.")
    cas_negatif = models.IntegerField(default=0, help_text="Indique si le cas est négatif.")
    evacue = models.IntegerField(default=0, help_text="Indique si le cas a été évacué.")
    decede = models.IntegerField(default=0, help_text="Indique si le cas est décédé.")
    gueri = models.IntegerField(default=0, help_text="Indique si le cas est guéri.")
    suivi_en_cours = models.IntegerField(default=0, help_text="Indique si le suivi est en cours.")
    nbre_sujets_contacts = models.IntegerField(default=0, help_text="Nombre de sujets contacts.")
    contacts_en_cours_suivi = models.IntegerField(default=0, help_text="Nombre de contacts en cours de suivi.")
    contacts_sorti_suivi = models.IntegerField(default=0, help_text="Nombre de contacts sortis du suivi.")
    devenu_suspect = models.IntegerField(default=0, help_text="Nombre de contacts devenus suspects.")
    devenu_positif = models.IntegerField(default=0, help_text="Nombre de contacts devenus positifs.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['maladie', 'district_sanitaire']),  # Pour les jointures
            models.Index(fields=['created_at']),  # Pour les analyses temporelles
        ]
        # unique_together = ('maladie', 'district_sanitaire')  # Évite les doublons

    @classmethod
    def increment_counter(cls, epidemie, district, field_name):
        """Incrémente un champ et initialise explicitement tous les autres si création"""
        with transaction.atomic():
            obj, created = cls.objects.select_for_update().get_or_create(
                maladie=epidemie,
                district_sanitaire=district,
                defaults={
                    # Initialise tous les champs à 0 sauf celui ciblé
                    'nbre_cas_suspects': 0,
                    'cas_positif': 1 if field_name == 'cas_positif' else 0,
                    'cas_negatif': 1 if field_name == 'cas_negatif' else 0,
                    'evacue': 1 if field_name == 'evacue' else 0,
                    'decede': 1 if field_name == 'decede' else 0,
                    'gueri': 1 if field_name == 'gueri' else 0,
                    'suivi_en_cours': 1 if field_name == 'suivi_en_cours' else 0,
                    'nbre_sujets_contacts': 1 if field_name == 'nbre_sujets_contacts' else 0,
                    'contacts_en_cours_suivi': 1 if field_name == 'contacts_en_cours_suivi' else 0,
                    'contacts_sorti_suivi': 1 if field_name == 'contacts_sorti_suivi' else 0,
                    'devenu_suspect': 1 if field_name == 'devenu_suspect' else 0,
                    'devenu_positif': 1 if field_name == 'devenu_positif' else 0,
                }
            )
            if not created:
                setattr(obj, field_name, models.F(field_name) + 1)
                obj.save()

    def __str__(self):
        return f"Cas en provenance de {self.district_sanitaire} enregistré "


def generate_api_key():
    while True:
        key = secrets.token_urlsafe(32)  # ou get_random_string(50)
        if not Platform.objects.filter(api_key=key).exists():
            return key


class Platform(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=128, default=generate_api_key, unique=True)
    last_connected = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SignalementJournal(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='journaux_signalement')
    maladie = models.ForeignKey('Epidemie', on_delete=models.SET_NULL, null=True, blank=True)
    date_analyse = models.DateField(null=True, blank=True)
    hopital = models.ForeignKey('ServiceSanitaire', on_delete=models.SET_NULL, null=True, blank=True)
    commune = models.ForeignKey('Commune', on_delete=models.SET_NULL, null=True, blank=True)

    donnees_brutes = models.JSONField(null=True, blank=True, help_text="Requête JSON complète reçue.")
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    user_api = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                 help_text="Utilisateur API ayant envoyé le signalement.")

    statut_reception = models.CharField(
        max_length=50,
        choices=[
            ("SUCCES", "Succès"),
            ("ERREUR", "Erreur"),
            ("IGNORÉ", "Ignoré"),
        ],
        default="SUCCES"
    )
    message = models.TextField(blank=True, null=True, help_text="Message ou erreur retournée.")
    created_at = models.DateTimeField(auto_now_add=True)
    source_application = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True, blank=True,
                                           help_text="Nom de l'application ayant envoyé le signalement."
                                           )

    def __str__(self):
        return f"{self.maladie} - {self.patient} - {self.statut_reception}"
