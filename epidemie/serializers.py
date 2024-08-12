from rest_framework import serializers
from .models import HealthRegion, City, EpidemicCase, Commune, Patient, ServiceSanitaire


class HealthRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRegion
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class EpidemicCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpidemicCase
        fields = '__all__'


class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    commune = CommuneSerializer()

    class Meta:
        model = Patient
        fields = '__all__'



class ServiceSanitaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSanitaire
        fields = '__all__'
#
# class ServiceSanitaireSerializer(GeoFeatureModelSerializer):
#     class Meta:
#         model = ServiceSanitaire
#         geo_field = "geom"
#         fields = ('id', 'nom', 'type', 'district', 'upstream', 'date_modified', 'source_url', 'completeness', 'uuid', 'source', 'what3words', 'version')