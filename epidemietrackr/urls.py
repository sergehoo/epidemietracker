from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

from epidemie.views import LandingPageView, EpidemieDetailView, PatientCreateView, PatientUpdateView, \
    PatientDeleteView, EchantillonCreateView, EchantillonUpdateView, EchantillonDeleteView, InformationDetailView, \
    InformationCreateView, import_data, import_synthese_view

urlpatterns = [
                  path("healthz", lambda r: HttpResponse("ok")),
                  path('admin/', admin.site.urls),
                  path('api-auth/', include('rest_framework.urls')),
                  # path('api/', include(router.urls)),

                  path('tinymce/', include('tinymce.urls')),
                  path("unicorn/", include("django_unicorn.urls")),
                  path('import-data/', import_data, name='import_data'),


                  path('accounts/', include('allauth.urls')),
                  path('epidemie/', include('api.urls')),
                  path('mpox/', include('mpox.urls')),
                  path('covid/', include('covid.urls')),
                  path('ebola/', include('ebola.urls')),
                  path('', LandingPageView.as_view(), name='landing'),
                  path('epidemie/<int:pk>/', EpidemieDetailView.as_view(), name='epidemie-detail'),

                  path('information/create/', InformationCreateView.as_view(), name='infos-create'),
                  path('information/<int:pk>/', InformationDetailView.as_view(), name='infos-detail'),

                  path('patient/create/', PatientCreateView.as_view(), name='patient-create'),
                  path('patient/<int:pk>/update/', PatientUpdateView.as_view(), name='patient-update'),
                  path('patient/<int:pk>/delete/', PatientDeleteView.as_view(), name='patient-delete'),

                  path('synthese/import/', import_synthese_view, name='import_synthese'),



                  # URLs pour les vues de Echantillon
                  path('echantillon/create/', EchantillonCreateView.as_view(), name='echantillon-create'),
                  path('echantillon/<int:pk>/update/', EchantillonUpdateView.as_view(), name='echantillon-update'),
                  path('echantillon/<int:pk>/delete/', EchantillonDeleteView.as_view(), name='echantillon-delete'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
