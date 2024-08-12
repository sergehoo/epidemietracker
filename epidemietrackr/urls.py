
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from dingue.views import HomePageView
from epidemie.views import HealthRegionViewSet, CityViewSet, EpidemicCaseViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('dingue/', include('dingue.urls')),
    path('', HomePageView.as_view(), name='dingue-home'),



]