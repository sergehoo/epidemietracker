from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from dingue.views import HomePageView, PatientListView, EchantillonListView
from mpox.views import MpoxHomeDash, HealthRegionViewSet, CityViewSet, EpidemicCaseViewSet, \
    CommuneAggregatedViewSet, ServiceSanitaireViewSet, PatientViewSet

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
                  # path('dash/', dashboard_view, name='mpox-dashboard'),
                  path('', MpoxHomeDash.as_view(), name='mpox-dashboard'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
