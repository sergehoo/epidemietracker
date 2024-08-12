import random
from datetime import datetime
from django.contrib.gis.geos import Point
from django.core.management import BaseCommand
from faker import Faker
from epidemie.models import City, Employee, Commune, Patient, Epidemie, Echantillon, PreleveMode

def patient_code():
    WordStack = ['MD', 'AC', 'NG', 'SO', 'SD', 'IP', 'CI', 'BC']
    random_str = random.choice(WordStack)
    current_date = datetime.now().strftime("%Y%m%d")
    traking = (random_str + str(random.randrange(0, 999999, 1)) + current_date + int(datetime.now().microsecond))
    return traking

class Command(BaseCommand):
    help = 'Populate the database with fake data for testing in Côte d\'Ivoire'

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')

        # Récupérer les communes existantes dans la base de données
        communes = Commune.objects.all()

        if not communes.exists():
            self.stdout.write(self.style.ERROR("Aucune commune n'a été trouvée. Veuillez d'abord charger les données des communes."))
            return

        employee = Employee.objects.first()

        for _ in range(1000):
            commune = random.choice(communes)
            patient = Patient.objects.create(
                code_patient=f'HU{random.randrange(0, 99999999, 2) + int(datetime.now().microsecond)}',
                nom=fake.last_name(),
                prenoms=fake.first_name(),
                contact=fake.phone_number(),
                situation_matrimoniale=random.choice(['Célibataire', 'Marié', 'Divorcé', 'Veuf']),
                lieu_naissance=commune.name,
                date_naissance=fake.date_of_birth(minimum_age=18, maximum_age=80),
                genre=random.choice(['M', 'F']),
                nationalite='Ivoirienne',
                profession=fake.job(),
                nbr_enfants=random.randint(0, 5),
                groupe_sanguin=random.choice(['O+', 'A+', 'B+', 'AB+', 'O-', 'A-', 'B-', 'AB-']),
                niveau_etude=random.choice(['Primary', 'High School', 'University', 'None']),
                employeur=fake.company(),
                created_by=employee,
                commune=commune,
                quartier=fake.street_name(),
                status=random.choice(['Actif', 'Inactif']),
                gueris=random.choice([True, False]),
                decede=random.choice([True, False]),
            )

            # Créer des données factices pour Echantillon
            dengue = Epidemie.objects.get(nom="DENGUE")
            mode_preleve = PreleveMode.objects.first()

            Echantillon.objects.create(
                patient=patient,
                code_echantillon=f'ECH{random.randint(1000, 9999)}',
                maladie=dengue,
                mode_preleve=mode_preleve,
                date_collect=fake.date_time_this_year(),
                site_collect=commune.name,
                agent_collect=employee,
                resultat=random.choice(['POSITIF', 'NEGATIF']),
                linked=random.choice([True, False]),
                used=random.choice([True, False])
            )

        self.stdout.write(self.style.SUCCESS('Data successfully populated!'))