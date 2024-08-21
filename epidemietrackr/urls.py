from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from dingue.views import HomePageView
from epidemie.views import HealthRegionViewSet, CityViewSet, EpidemicCaseViewSet, LandinguePageView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api-auth/', include('rest_framework.urls')),
                  path('accounts/', include('allauth.urls')),
                  path('dingue/', include('dingue.urls')),
                  path('mpox/', include('mpox.urls')),
                  path('covid/', include('covid.urls')),
                  path('ebola/', include('ebola.urls')),
                  path('', LandinguePageView.as_view(), name='landing'),


              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
