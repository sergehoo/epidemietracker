from celery import shared_task

from epidemie.models import HealthRegion, City, Commune, EpidemicCase


@shared_task
def sync_health_regions():
    # Code pour synchroniser les régions de santé
    regions = HealthRegion.objects.all()
    # Logique de synchronisation ou autre traitement
    return f"Synchronisation de {regions.count()} régions de santé réussie."


@shared_task
def process_city_data(city_id):
    # Code pour traiter les données d'une ville
    try:
        city = City.objects.get(id=city_id)
        # Traitement spécifique sur la ville
        return f"Traitement des données de la ville {city.name} réussi."
    except City.DoesNotExist:
        return "Ville non trouvée."


@shared_task
def generate_commune_report():
    # Code pour générer un rapport sur les communes
    communes = Commune.objects.all()
    # Générer un rapport (par exemple, un fichier PDF ou CSV)
    return f"Rapport généré pour {communes.count()} communes."


@shared_task
def alert_for_epidemic_cases():
    # Code pour alerter en cas d'épidémie
    cases = EpidemicCase.objects.filter(status="confirmed")
    # Logique d'alerte, par exemple, envoyer des notifications
    return f"Alertes envoyées pour {cases.count()} cas confirmés."
