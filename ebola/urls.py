from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from ebola.views import EbolaHomeDash

urlpatterns = [

                  # path('dash/', dashboard_view, name='mpox-dashboard'),
                  path('', EbolaHomeDash.as_view(), name='ebola-dashboard'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
