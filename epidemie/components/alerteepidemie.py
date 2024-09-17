#alerteepidemie.py

from datetime import datetime, timedelta

from django.db.models import Count
from django_unicorn.components import UnicornView

from epidemie.models import Echantillon, Alert, Epidemie


class AlerteepidemieView(UnicornView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alerts = []

    def fetch_alerts(self):
        today = datetime.now()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=31)).replace(day=1)

        # Obtenez les épidémies avec le nombre de patients positifs ce mois-ci
        epidemies = Epidemie.objects.all()
        self.alerts = [
            {
                'message': f"{epidemie.nombre_patients_positifs_ce_mois} nouveaux cas de {epidemie.nom} ce mois-ci",
                'url': '#'  # Mettez à jour cette URL si nécessaire
            }
            for epidemie in epidemies
            if epidemie.nombre_patients_positifs_ce_mois > 0
        ]

        # Créez des alertes dans la base de données
        for alert in self.alerts:
            Alert.objects.create(message=alert['message'])
            # Debugging: Print to confirm alert creation
            print("Alert created:", alert['message'])
# class AlerteepidemieView(UnicornView):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.alerts = []
#
#     def fetch_alerts(self):
#         today = datetime.now()
#         start_of_week = today - timedelta(days=today.weekday())
#
#         new_cases = Echantillon.objects.filter(
#             date_collect__gte=start_of_week
#         ).values('maladie__nom', 'patient__commune__district__nom').annotate(count=Count('id'))
#
#         self.alerts = [
#             {
#                 'message': f"{entry['count']} nouveaux cas de {entry['maladie__nom']} détectés dans le district de {entry['patient__commune__district__nom']} cette semaine",
#                 'url': '#'  # Mettez à jour cette URL si nécessaire
#             }
#             for entry in new_cases
#         ]
#
#         # Créez des alertes dans la base de données
#         for alert in self.alerts:
#             Alert.objects.create(message=alert['message'])
#     # alerts = []
#     #
#     # def mount(self):
#     #     self.fetch_alerts()
#     #
#     # def fetch_alerts(self):
#     #     # Calculate the start of the week
#     #     today = datetime.now()
#     #     start_of_week = today - timedelta(days=today.weekday())
#     #
#     #     # Query to find the new cases in the last week
#     #     new_cases = Echantillon.objects.filter(
#     #         maladie__nom='DENGUE',
#     #         date_collect__gte=start_of_week
#     #     ).values('patient__commune__district__nom').annotate(count=Count('id'))
#     #
#     #     # Generate alert messages
#     #     self.alerts = [
#     #         f"{entry['count']} nouveaux cas de DENGUE detecter dans le district de {entry['patient__commune__district__nom']} cette semaine"
#     #         for entry in new_cases
#     #     ]
#     #
#     #     # Save alerts in the database
#     #     for message in self.alerts:
#     #         Alert.objects.create(message=message)
