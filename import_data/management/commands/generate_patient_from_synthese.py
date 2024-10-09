import random
import string
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from epidemie.models import SyntheseDistrict, Employee, Patient, Echantillon

class Command(BaseCommand):
    help = 'Génère automatiquement des patients et leurs échantillons en fonction des cas positifs dans chaque SyntheseDistrict'

    def handle(self, *args, **kwargs):
        # Récupérer toutes les synthèses des districts
        synthese_districts = SyntheseDistrict.objects.all()

        for synthese in synthese_districts:
            # Récupérer le nombre de cas positifs pour ce district
            cas_positifs = synthese.cas_positif

            # Récupérer l'épidémie liée à la synthèse
            epidemie = synthese.maladie

            # Récupérer l'employé par défaut (vous pouvez adapter cela)
            agent_collect = Employee.objects.filter(role='Agent de collecte').first()

            # Récupérer le nombre de patients existants pour ce district et cette maladie
            patients_existants = Patient.objects.filter(
                commune__district=synthese.district_sanitaire,
                echantillons__maladie=epidemie,
                status='Positif'
            ).distinct().count()

            # Vérifier si le nombre de patients correspond aux cas positifs
            if patients_existants < cas_positifs:
                patients_a_creer = cas_positifs - patients_existants

                self.stdout.write(self.style.WARNING(f'{patients_existants} patients existent déjà pour {synthese.district_sanitaire.nom}, création de {patients_a_creer} nouveaux patients.'))

                # Générer les patients restants pour atteindre le nombre de cas positifs
                for _ in range(patients_a_creer):
                    # Créer un patient aléatoire
                    patient = self.create_random_patient(synthese.district_sanitaire)

                    # Créer un échantillon pour ce patient
                    self.create_echantillon(patient, epidemie, agent_collect)

                self.stdout.write(self.style.SUCCESS(f'{patients_a_creer} nouveaux patients générés pour {synthese.district_sanitaire.nom}.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Le nombre de patients pour {synthese.district_sanitaire.nom} est déjà suffisant ({patients_existants} / {cas_positifs}).'))

    def create_random_patient(self, district):
        nom = self.random_string(6)
        prenoms = self.random_string(8)
        contact = self.random_contact()
        genre = random.choice(['M', 'F'])
        commune = district.commune_set.first()  # Associer un patient à une commune dans le district

        patient = Patient.objects.create(
            nom=nom,
            prenoms=prenoms,
            contact=contact,
            genre=genre,
            commune=commune,
            date_naissance=timezone.now() - timedelta(days=random.randint(6570, 29200)),  # âge entre 18 et 80 ans
            hopital=None,  # À définir selon votre structure
            quartier='Quartier Test',
            status='Positif',
            created_by=None,  # À définir si nécessaire
        )
        self.stdout.write(self.style.SUCCESS(f'Patient {nom} {prenoms} créé.'))
        return patient

    def create_echantillon(self, patient, epidemie, agent_collect):
        echantillon = Echantillon.objects.create(
            patient=patient,
            maladie=epidemie,
            mode_preleve=None,  # À définir selon votre structure
            date_collect=timezone.now(),
            site_collect='Site Collecte Test',
            agent_collect=agent_collect,
            status_echantillons='En cours',
            resultat=True,  # On suppose que le cas est positif
        )
        self.stdout.write(self.style.SUCCESS(f'Échantillon {echantillon.code_echantillon} créé pour {patient.nom}.'))

    def random_string(self, length):
        return ''.join(random.choices(string.ascii_uppercase, k=length))

    def random_contact(self):
        return '07' + ''.join(random.choices(string.digits, k=8))

# class Command(BaseCommand):
#     help = 'Génère automatiquement des patients et leurs échantillons pour le nombre de cas positifs dans chaque SyntheseDistrict'
#
#     def handle(self, *args, **kwargs):
#         # Récupérer toutes les synthèses des districts
#         synthese_districts = SyntheseDistrict.objects.all()
#
#         for synthese in synthese_districts:
#             cas_positifs = synthese.cas_positif
#
#             # Récupérer l'épidémie liée
#             epidemie = synthese.maladie
#
#             # Récupérer l'employé par défaut (vous pouvez adapter cela)
#             agent_collect = Employee.objects.filter(role='Agent de collecte').first()
#
#             # Générer des patients et leurs échantillons pour le nombre de cas positifs
#             for _ in range(cas_positifs):
#                 # Créer un patient aléatoire
#                 patient = self.create_random_patient(synthese.district_sanitaire)
#
#                 # Créer un échantillon pour ce patient
#                 self.create_echantillon(patient, epidemie, agent_collect)
#
#             self.stdout.write(self.style.SUCCESS(f'{cas_positifs} patients générés pour {synthese.district_sanitaire.nom}'))
#
#     def create_random_patient(self, district):
#         nom = self.random_string(6)
#         prenoms = self.random_string(8)
#         contact = self.random_contact()
#         genre = random.choice(['M', 'F'])
#         commune = district.commune_set.first()  # Associer un patient à une commune dans le district
#
#         patient = Patient.objects.create(
#             nom=nom,
#             prenoms=prenoms,
#             contact=contact,
#             genre=genre,
#             commune=commune,
#             date_naissance=timezone.now() - timedelta(days=random.randint(6570, 29200)),  # âge entre 18 et 80 ans
#             hopital=None,  # À définir selon votre structure
#             quartier='Quartier Test',
#             status='Positif',
#             created_by=None,  # À définir si nécessaire
#         )
#         self.stdout.write(self.style.SUCCESS(f'Patient {nom} {prenoms} créé.'))
#         return patient
#
#     def create_echantillon(self, patient, epidemie, agent_collect):
#         echantillon = Echantillon.objects.create(
#             patient=patient,
#             maladie=epidemie,
#             mode_preleve=None,  # À définir selon votre structure
#             date_collect=timezone.now(),
#             site_collect='Site Collecte Test',
#             agent_collect=agent_collect,
#             status_echantillons='En cours',
#             resultat=True,  # On suppose que le cas est positif
#         )
#         self.stdout.write(self.style.SUCCESS(f'Échantillon {echantillon.code_echantillon} créé pour {patient.nom}.'))
#
#     def random_string(self, length):
#         return ''.join(random.choices(string.ascii_uppercase, k=length))
#
#     def random_contact(self):
#         return '07' + ''.join(random.choices(string.digits, k=8))