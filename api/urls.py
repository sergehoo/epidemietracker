from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import HealthRegionViewSet, CityViewSet, EpidemicCaseViewSet, PatientViewSet, CommuneAggregatedViewSet, \
    ServiceSanitaireViewSet, dashboard_view, CasSyntheseViewSet, SyntheseDistrictViewSet, get_infected_cases_data
from epidemie.views import import_view, import_echantillons, PatientListView, EchantillonListView, HomePageView, \
    import_excel

router = DefaultRouter()
router.register(r'healthregions', HealthRegionViewSet)
router.register(r'cities', CityViewSet)
router.register(r'epidemiccases', EpidemicCaseViewSet)
router.register(r'patient', PatientViewSet)
# router.register(r'commune', CommuneViewSet)
router.register(r'communes_aggregated', CommuneAggregatedViewSet)
router.register(r'service_sanitaire', ServiceSanitaireViewSet)
router.register(r'cas-synthese', CasSyntheseViewSet)
router.register(r'synthese-district', SyntheseDistrictViewSet)

urlpatterns = [
                  path('api/', include(router.urls)),

                  path('dash/', dashboard_view, name='tethome'),
                  path('import_data/', import_view, name='import_view'),

                  path('import-echantillons/', import_echantillons, name='import_echantillons'),
                  path('import-excel/', import_excel, name='import_excel'),

                  path('patients/liste/', PatientListView.as_view(), name='patientlist'),
                  path('enquete/liste/', EchantillonListView.as_view(), name='echantillons'),
                  path('api/epidemie/<int:epidemie_id>/cases/', get_infected_cases_data,
                       name='infected_cases_data'),

                  path('', HomePageView.as_view(), name='dingue-home'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
