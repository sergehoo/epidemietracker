import datetime

from django.contrib.auth.models import User
from django.contrib.gis.db import models
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


class HealthRegion(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DistrictSanitaire(models.Model):
    nom = models.CharField(max_length=100, null=True, blank=True, )
    region = models.ForeignKey(HealthRegion, on_delete=models.CASCADE, null=True, blank=True, )


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
    created_at = models.DateTimeField(auto_now_add=now, )

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user.username}- {self.user.first_name} {self.user.last_name}"

    class Meta:
        permissions = (
            ("can_edit_employee", "Can edit employee"),
            ("can_create_employee", "Can create employee"),
            ("can_view_salary", "can view salary"),
        )


class Commune(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)
    population = models.CharField(null=True, blank=True)
    is_in = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    osm_id = models.BigIntegerField(null=True, blank=True)
    osm_type = models.CharField(max_length=50, null=True, blank=True)
    geom = models.PointField()

    def __str__(self):
        return f"{self.name} - {self.place} ({self.geom})"


class Patient(models.Model):
    code_patient = models.CharField(max_length=225, blank=True, unique=True)
    nom = models.CharField(max_length=225)
    prenoms = models.CharField(max_length=225)
    contact = models.CharField(max_length=225)
    situation_matrimoniale = models.CharField(max_length=225, choices=situation_matrimoniales_choices)
    lieu_naissance = models.CharField(max_length=200, blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    genre = models.CharField(max_length=10, choices=Sexe_choices)
    nationalite = models.CharField(max_length=200)
    profession = models.CharField(max_length=100, null=True, blank=True)
    nbr_enfants = models.PositiveIntegerField(default=0)
    groupe_sanguin = models.CharField(choices=Goupe_sanguin_choices, max_length=20, null=True)
    niveau_etude = models.CharField(max_length=100, null=True, blank=True)
    employeur = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=now)
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True, blank=True)
    quartier = models.CharField(max_length=100, null=True, blank=True)
    # ville = models.ForeignKey('City', on_delete=models.SET_NULL, null=True)
    status = models.CharField(choices=Patient_statut_choices, max_length=100, default='Aucun', null=True, blank=True)
    gueris = models.BooleanField(default=False)
    decede = models.BooleanField(default=False)
    history = HistoricalRecords()

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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.prenoms} {self.nom}'


class Symptom(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Typeepidemie(models.Model):
    pass


class Epidemie(models.Model):
    nom = models.CharField(max_length=100)
    type = models.ForeignKey('Typeepidemie', null=True, blank=True, on_delete=models.CASCADE)
    description = HTMLField(blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    thumbnails = models.ImageField(null=True, blank=True, upload_to='epidemie/thumbnails')
    symptomes = models.ManyToManyField(Symptom, related_name='épidémies', blank=True, null=True)

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
            echantillons__resultat='POSITIF'
        ).distinct().count()
        return nombre_personnes_touchees

    @property
    def personnes_decedees(self):
        # Compte le nombre de personnes décédées ayant des échantillons positifs pour cette épidémie
        nombre_personnes_decedees = Patient.objects.filter(
            echantillons__maladie=self,
            echantillons__resultat='POSITIF',
            decede=True
        ).distinct().count()
        return nombre_personnes_decedees

    @property
    def nombre_patients_positifs_ce_mois(self):
        current_month = now().month
        current_year = now().year
        return self.echantillon_set.filter(
            resultat='POSITIF',
            date_collect__month=current_month,
            date_collect__year=current_year
        ).count()

    def __str__(self):
        return self.nom

    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.date_debut <= today and (self.date_fin is None or self.date_fin >= today)


class PreleveMode(models.Model):
    nom = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nom


class Echantillon(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="echantillons", null=True, blank=True, )
    code_echantillon = models.CharField(null=True, blank=True, max_length=10, unique=True)
    maladie = models.ForeignKey('Epidemie', null=True, blank=True, on_delete=models.CASCADE)
    mode_preleve = models.ForeignKey('PreleveMode', null=True, blank=True, on_delete=models.CASCADE)
    date_collect = models.DateTimeField(null=True, blank=True)
    site_collect = models.CharField(null=True, blank=True, max_length=100)
    agent_collect = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.CASCADE)
    status_echantillons = models.CharField(null=True, blank=True, max_length=10)
    resultat = models.CharField(choices=Resultat_choices, max_length=100, null=True, blank=True)
    linked = models.BooleanField(default=False, null=True, blank=True)
    used = models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.code_echantillon}- {self.patient}"


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
