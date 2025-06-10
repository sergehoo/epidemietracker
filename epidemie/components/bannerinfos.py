

from django_unicorn.components import UnicornView

from epidemie.models import Information


class BannerinfosView(UnicornView):
    messages = []

    def mount(self):
        # Chargez les messages à afficher dans la bande d'information
        self.messages = Information.objects.all().order_by('-date_added')[:5]
