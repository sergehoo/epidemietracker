import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from faker import Faker
from epidemie.models import City, Employee, Commune, Patient


class Command(BaseCommand):
    help = 'Populate the database with fake data for testing'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Créer des données factices pour Commune
        city = City.objects.first()
        for _ in range(50):
            Commune.objects.create(
                ville=city,
                name=fake.city(),
                geom=Point(fake.longitude(), fake.latitude())
            )

        # Créer des données factices pour Patient
        communes = Commune.objects.all()
        employee = Employee.objects.first()

        for _ in range(100):
            patient = Patient.objects.create(
                code_patient=f'PAT{random.randint(1000, 9999)}',
                nom=fake.last_name(),
                prenoms=fake.first_name(),
                contact=fake.phone_number(),
                situation_matrimoniale=random.choice(['Célibataire', 'Marié', 'Divorcé', 'Veuf']),
                lieu_naissance=fake.city(),
                date_naissance=fake.date_of_birth(minimum_age=18, maximum_age=80),
                genre=random.choice(['M', 'F']),
                nationalite='Ivoirienne',
                profession=fake.job(),
                nbr_enfants=random.randint(0, 5),
                groupe_sanguin=random.choice(['O+', 'A+', 'B+', 'AB+', 'O-', 'A-', 'B-', 'AB-']),
                niveau_etude=random.choice(['Primary', 'High School', 'University', 'None']),
                employeur=fake.company(),
                created_by=employee,
                commune=random.choice(communes),
                quartier=fake.street_name(),
                ville=communes[0].ville,
                status=random.choice(['Actif', 'Inactif'])
            )

            # Créer des données factices pour Constante
            # constante = Constante.objects.create(
            #     patient=patient,
            #     poids=random.uniform(50, 100),
            #     taille=random.uniform(1.5, 2),
            #     temperature=random.uniform(36, 39)
            # )

            # Créer des données factices pour Consultation
            # Consultation.objects.create(
            #     patient=patient,
            #     constante=constante,
            #     diagnostic=fake.text(),
            #     traitement=fake.text()
            # )

        self.stdout.write(self.style.SUCCESS('Data successfully populated!'))