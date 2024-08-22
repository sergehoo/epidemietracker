from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from dingue.views import HomePageView, PatientListView, EchantillonListView
from mpox.views import MpoxHomeDash

urlpatterns = [

                  # path('dash/', dashboard_view, name='mpox-dashboard'),
                  path('', MpoxHomeDash.as_view(), name='mpox-dashboard'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
