from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Platform


class APIKeyAuthentication(BaseAuthentication):
    """
    Classe d'authentification personnalisée pour valider les requêtes M2M
    via une clé d'API statique.
    """

    def authenticate(self, request):
        # Le nom de l'en-tête que le client doit envoyer. Ex: X-API-KEY
        api_key_header = "X-API-KEY"

        # Récupérer la clé depuis les en-têtes de la requête.
        key = request.headers.get(api_key_header)
        if not key:
            # Si l'en-tête n'est pas présent, on ne tente pas cette méthode d'authentification.
            return None

        try:
            # Chercher une plateforme active avec cette clé.
            # C'est ici que la sécurité opère : la plateforme doit être active.
            platform = Platform.objects.get(api_key=key, is_active=True)
        except Platform.DoesNotExist:
            # Si la clé est invalide ou la plateforme désactivée, on lève une erreur.
            raise AuthenticationFailed('Clé d\'API invalide ou plateforme inactive.')

        # Si la clé est valide, l'authentification réussit.
        # On retourne l'utilisateur associé à la plateforme et la plateforme elle-même.
        # request.user sera l'utilisateur.
        # request.auth sera l'objet platform.
        return (platform.user, platform)

    def authenticate_header(self, request):
        """
        Utilisé pour la réponse 401 Unauthorized, indiquant comment s'authentifier.
        """
        return 'X-API-KEY'