from rest_framework import serializers
import uuid
import random
import string

from epidemie.models import Patient, Epidemie, ServiceSanitaire, Echantillon, Employee, Sexe_choices


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


class EpidemieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Epidemie
        fields = '__all__'


class ServiceSanitaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSanitaire
        fields = '__all__'


class EchantillonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Echantillon
        fields = '__all__'

    def create(self, validated_data):
        # Générer un code unique pour l'échantillon
        validated_data['code_echantillon'] = ''.join(filter(str.isdigit, str(uuid.uuid4().int)))[:12]
        return super().create(validated_data)


class NouveauCasSerializer(serializers.Serializer):
    patient = PatientSerializer()
    epidemie = serializers.PrimaryKeyRelatedField(queryset=Epidemie.objects.all())
    service_sanitaire = serializers.PrimaryKeyRelatedField(queryset=ServiceSanitaire.objects.all())
    agent_collect = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False)
    mode_preleve = serializers.PrimaryKeyRelatedField(queryset=ServiceSanitaire.objects.all(), required=False)
    site_collect = serializers.CharField(required=False, allow_blank=True)
    date_collect = serializers.DateTimeField()
    resultat = serializers.BooleanField()

    def create(self, validated_data):
        patient_data = validated_data.pop('patient')

        # Vérifier si le patient existe déjà
        patient, created = Patient.objects.get_or_create(
            nom=patient_data['nom'],
            prenoms=patient_data['prenoms'],
            contact=patient_data.get('contact', ''),
            defaults=patient_data
        )

        # Créer l'échantillon
        echantillon = Echantillon.objects.create(
            patient=patient,
            maladie=validated_data['epidemie'],
            mode_preleve=validated_data.get('mode_preleve'),
            date_collect=validated_data['date_collect'],
            site_collect=validated_data.get('site_collect', ''),
            agent_collect=validated_data.get('agent_collect'),
            status_echantillons='En attente',
            resultat=validated_data['resultat']
        )

        return echantillon


# serializers.py
class SignalementExterneSerializer(serializers.Serializer):
    code_patient = serializers.CharField()
    nom = serializers.CharField()
    prenoms = serializers.CharField()
    genre = serializers.ChoiceField(choices=Sexe_choices)
    date_naissance = serializers.DateField()
    contact = serializers.CharField()
    maladie_detectee = serializers.CharField()
    code_icd = serializers.CharField(required=False, allow_blank=True)
    date_analyse = serializers.DateField()
    hopital = serializers.CharField()
    commune = serializers.CharField()
    code_echantillon = serializers.CharField(required=False, allow_blank=True)
    source_application = serializers.CharField(required=False, allow_blank=True)
