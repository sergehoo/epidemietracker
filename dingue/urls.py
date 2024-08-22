from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from dingue.views import HomePageView, PatientListView, EchantillonListView, import_view, import_echantillons
from .views import dashboard_view, HealthRegionViewSet, CityViewSet, EpidemicCaseViewSet, PatientViewSet, \
    ServiceSanitaireViewSet, CommuneViewSet, CommuneAggregatedViewSet

router = DefaultRouter()
router.register(r'healthregions', HealthRegionViewSet)
router.register(r'cities', CityViewSet)
router.register(r'epidemiccases', EpidemicCaseViewSet)
router.register(r'patient', PatientViewSet)
# router.register(r'commune', CommuneViewSet)
router.register(r'communes_aggregated', CommuneAggregatedViewSet)
router.register(r'service_sanitaire', ServiceSanitaireViewSet)

urlpatterns = [
                  path('api/', include(router.urls)),
                  path('dash/', dashboard_view, name='tethome'),
                  path('import_data/', import_view, name='import_view'),

                  path('import-echantillons/', import_echantillons, name='import_echantillons'),

                  path('patients/liste/', PatientListView.as_view(), name='patientlist'),
                  path('enquete/liste/', EchantillonListView.as_view(), name='echantillons'),
                  path('', HomePageView.as_view(), name='dingue-home'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
