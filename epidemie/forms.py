from django import forms
from django.utils.safestring import mark_safe
from tinymce.widgets import TinyMCE

from epidemie.models import Patient, Commune, Information

SEXE_CHOICES = [
    ('Homme', 'Homme'),
    ('Femme', 'Femme')
]
NATIONALITE_CHOICES = [
    ('Côte d\'Ivoire', 'Côte d\'Ivoire'),
    ('Afghanistan', 'Afghanistan'),
    ('Afrique du Sud', 'Afrique du Sud'),
    ('Albanie', 'Albanie'),
    ('Algérie', 'Algérie'),
    ('Allemagne', 'Allemagne'),
    ('Angola', 'Angola'),
    ('Antigua-et-Barbuda', 'Antigua-et-Barbuda'),
    ('Arabie saoudite', 'Arabie saoudite'),
    ('Argentine', 'Argentine'),
    ('Arménie', 'Arménie'),
    ('Australie', 'Australie'),
    ('Autriche', 'Autriche'),
    ('Azerbaïdjan', 'Azerbaïdjan'),
    ('Bahamas', 'Bahamas'),
    ('Bahreïn', 'Bahreïn'),
    ('Bangladesh', 'Bangladesh'),
    ('Barbade', 'Barbade'),
    ('Belau', 'Belau'),
    ('Belgique', 'Belgique'),
    ('Belize', 'Belize'),
    ('Bénin', 'Bénin'),
    ('Bhoutan', 'Bhoutan'),
    ('Biélorussie', 'Biélorussie'),
    ('Birmanie', 'Birmanie'),
    ('Bolivie', 'Bolivie'),
    ('Bosnie-Herzégovine', 'Bosnie-Herzégovine'),
    ('Botswana', 'Botswana'),
    ('Brésil', 'Brésil'),
    ('Brunei', 'Brunei'),
    ('Bulgarie', 'Bulgarie'),
    ('Burkina', 'Burkina'),
    ('Burundi', 'Burundi'),
    ('Cambodge', 'Cambodge'),
    ('Cameroun', 'Cameroun'),
    ('Canada', 'Canada'),
    ('Cap-Vert', 'Cap-Vert'),
    ('Chili', 'Chili'),
    ('Chine', 'Chine'),
    ('Chypre', 'Chypre'),
    ('Colombie', 'Colombie'),
    ('Comores', 'Comores'),
    ('Congo', 'Congo'),
    ('Cook', 'Cook'),
    ('Corée du Nord', 'Corée du Nord'),
    ('Corée du Sud', 'Corée du Sud'),
    ('Costa Rica', 'Costa Rica'),
    ('Croatie', 'Croatie'),
    ('Cuba', 'Cuba'),
    ('Danemark', 'Danemark'),
    ('Djibouti', 'Djibouti'),
    ('Dominique', 'Dominique'),
    ('Écosse', 'Écosse'),
    ('Égypte', 'Égypte'),
    ('Émirats arabes unis', 'Émirats arabes unis'),
    ('Équateur', 'Équateur'),
    ('Érythrée', 'Érythrée'),
    ('Espagne', 'Espagne'),
    ('Estonie', 'Estonie'),
    ('États-Unis', 'États-Unis'),
    ('Éthiopie', 'Éthiopie'),
    ('Fidji', 'Fidji'),
    ('Finlande', 'Finlande'),
    ('France', 'France'),
    ('Gabon', 'Gabon'),
    ('Gambie', 'Gambie'),
    ('Géorgie', 'Géorgie'),
    ('Ghana', 'Ghana'),
    ('Grèce', 'Grèce'),
    ('Grenade', 'Grenade'),
    ('Guatemala', 'Guatemala'),
    ('Guinée', 'Guinée'),
    ('Guinée-Bissao', 'Guinée-Bissao'),
    ('Guinée équatoriale', 'Guinée équatoriale'),
    ('Guyana', 'Guyana'),
    ('Haïti', 'Haïti'),
    ('Honduras', 'Honduras'),
    ('Hongrie', 'Hongrie'),
    ('Inde', 'Inde'),
    ('Indonésie', 'Indonésie'),
    ('Iran', 'Iran'),
    ('Irak', 'Irak'),
    ('Irlande', 'Irlande'),
    ('Islande', 'Islande'),
    ('Israël', 'Israël'),
    ('Italie', 'Italie'),
    ('Jamaïque', 'Jamaïque'),
    ('Japon', 'Japon'),
    ('Jordanie', 'Jordanie'),
    ('Kazakhstan', 'Kazakhstan'),
    ('Kenya', 'Kenya'),
    ('Kirghizistan', 'Kirghizistan'),
    ('Kiribati', 'Kiribati'),
    ('Koweït', 'Koweït'),
    ('Laos', 'Laos'),
    ('Lesotho', 'Lesotho'),
    ('Lettonie', 'Lettonie'),
    ('Liban', 'Liban'),
    ('Liberia', 'Liberia'),
    ('Libye', 'Libye'),
    ('Liechtenstein', 'Liechtenstein'),
    ('Lituanie', 'Lituanie'),
    ('Luxembourg', 'Luxembourg'),
    ('Macédoine', 'Macédoine'),
    ('Madagascar', 'Madagascar'),
    ('Malaisie', 'Malaisie'),
    ('Malawi', 'Malawi'),
    ('Maldives', 'Maldives'),
    ('Mali', 'Mali'),
    ('Malte', 'Malte'),
    ('Maroc', 'Maroc'),
    ('Marshall', 'Marshall'),
    ('Maurice', 'Maurice'),
    ('Mauritanie', 'Mauritanie'),
    ('Mexique', 'Mexique'),
    ('Micronésie', 'Micronésie'),
    ('Moldavie', 'Moldavie'),
    ('Monaco', 'Monaco'),
    ('Mongolie', 'Mongolie'),
    ('Mozambique', 'Mozambique'),
    ('Namibie', 'Namibie'),
    ('Nauru', 'Nauru'),
    ('Népal', 'Népal'),
    ('Nicaragua', 'Nicaragua'),
    ('Niger', 'Niger'),
    ('Nigeria', 'Nigeria'),
    ('Niue', 'Niue'),
    ('Norvège', 'Norvège'),
    ('Nouvelle-Zélande', 'Nouvelle-Zélande'),
    ('Oman', 'Oman'),
    ('Ouganda', 'Ouganda'),
    ('Ouzbékistan', 'Ouzbékistan'),
    ('Pakistan', 'Pakistan'),
    ('Palestine', 'Palestine'),
    ('Panama', 'Panama'),
    ('Papouasie - Nouvelle Guinée', 'Papouasie - Nouvelle Guinée'),
    ('Paraguay', 'Paraguay'),
    ('Pays-Bas', 'Pays-Bas'),
    ('Pérou', 'Pérou'),
    ('Philippines', 'Philippines'),
    ('Pologne', 'Pologne'),
    ('Portugal', 'Portugal'),
    ('Qatar', 'Qatar'),
    ('République centrafricaine', 'République centrafricaine'),
    ('République démocratique du Con', 'République démocratique du Con'),
    ('République dominicaine', 'République dominicaine'),
    ('République tchèque', 'République tchèque'),
    ('Roumanie', 'Roumanie'),
    ('Royaume-Uni', 'Royaume-Uni'),
    ('Russie', 'Russie'),
    ('Rwanda', 'Rwanda'),
    ('Saint-Christophe-et-Niévès', 'Saint-Christophe-et-Niévès'),
    ('Sainte-Lucie', 'Sainte-Lucie'),
    ('Saint-Marin', 'Saint-Marin'),
    ('Saint-Siège', 'Saint-Siège'),
    ('Saint-Vincent-et-les-Grenadine', 'Saint-Vincent-et-les-Grenadine'),
    ('Salomon', 'Salomon'),
    ('Salvador', 'Salvador'),
    ('Samoa occidentales', 'Samoa occidentales'),
    ('Sao Tomé-et-Principe', 'Sao Tomé-et-Principe'),
    ('Sénégal', 'Sénégal'),
    ('Seychelles', 'Seychelles'),
    ('Sierra Leone', 'Sierra Leone'),
    ('Singapour', 'Singapour'),
    ('Slovaquie', 'Slovaquie'),
    ('Slovénie', 'Slovénie'),
    ('Somalie', 'Somalie'),
    ('Soudan', 'Soudan'),
    ('Sri Lanka', 'Sri Lanka'),
    ('Suède', 'Suède'),
    ('Suisse', 'Suisse'),
    ('Suriname', 'Suriname'),
    ('Swaziland', 'Swaziland'),
    ('Syrie', 'Syrie'),
    ('Tadjikistan', 'Tadjikistan'),
    ('Tanzanie', 'Tanzanie'),
    ('Tchad', 'Tchad'),
    ('Thaïlande', 'Thaïlande'),
    ('Togo', 'Togo'),
    ('Tonga', 'Tonga'),
    ('Trinité-et-Tobago', 'Trinité-et-Tobago'),
    ('Tunisie', 'Tunisie'),
    ('Turkménistan', 'Turkménistan'),
    ('Turquie', 'Turquie'),
    ('Tuvalu', 'Tuvalu'),
    ('Ukraine', 'Ukraine'),
    ('Uruguay', 'Uruguay'),
    ('Vanuatu', 'Vanuatu'),
    ('Venezuela', 'Venezuela'),
    ('Viêt Nam', 'Viêt Nam'),
    ('Yémen', 'Yémen'),
    ('Yougoslavie', 'Yougoslavie'),
    ('Zambie', 'Zambie'),
    ('Zimbabwe', 'Zimbabwe')

]
villes_choices = [
    ('Abidjan', 'Abidjan'),
    ('Yamoussoukro', 'Yamoussoukro'),
    ('Bouaké', 'Bouaké'),
    ('Daloa', 'Daloa'),
    ('Korhogo', 'Korhogo'),
    ('Man', 'Man'),
    ('San Pedro', 'San Pedro'),
    ('Divo', 'Divo'),
    ('Gagnoa', 'Gagnoa'),
    ('Abengourou', 'Abengourou'),
    ('Agboville', 'Agboville'),
    ('Grand-Bassam', 'Grand-Bassam'),
    ('Soubré', 'Soubré'),
    ('Ferkessédougou', 'Ferkessédougou'),
    ('Odienné', 'Odienné'),
    ('Séguéla', 'Séguéla'),
    ('Bingerville', 'Bingerville'),
    ('Bondoukou', 'Bondoukou'),
    ('Daoukro', 'Daoukro'),
    ('Issia', 'Issia'),
    ('Sassandra', 'Sassandra'),
    ('Tengrela', 'Tengrela'),
    ('Agnibilékrou', 'Agnibilékrou'),
    ('Anyama', 'Anyama'),
    ('Arrah', 'Arrah'),
    ('Béoumi', 'Béoumi'),
    ('Biankouma', 'Biankouma'),
    ('Bouna', 'Bouna'),
    ('Boundiali', 'Boundiali'),
    ('Dabou', 'Dabou'),
    ('Danané', 'Danané'),
    ('Duékoué', 'Duékoué'),
    ('Grand-Lahou', 'Grand-Lahou'),
    ('Guiglo', 'Guiglo'),
    ('Katiola', 'Katiola'),
    ('Lakota', 'Lakota'),
    ('Méagui', 'Méagui'),
    ('Mankono', 'Mankono'),
    ('Oumé', 'Oumé'),
    ('Sinfra', 'Sinfra'),
    ('Tiassalé', 'Tiassalé'),
    ('Touba', 'Touba'),
    ('Toumodi', 'Toumodi'),
    ('Vavoua', 'Vavoua'),
    ('Yopougon', 'Yopougon'),
    ('Zuenoula', 'Zuenoula'),
    ('Autre', 'Autre'),
]
professions_choices = [
    ('Médecin', 'Médecin'),
    ('Infirmier/Infirmière', 'Infirmier/Infirmière'),
    ('Dentiste', 'Dentiste'),
    ('Pharmacien/Pharmacienne', 'Pharmacien/Pharmacienne'),
    ('Vétérinaire', 'Vétérinaire'),
    ('Ingénieur', 'Ingénieur'),
    ('Architecte', 'Architecte'),
    ('Professeur/Professeure', 'Professeur/Professeure'),
    ('Enseignant/Enseignante', 'Enseignant/Enseignante'),
    ('Chercheur/Chercheuse', 'Chercheur/Chercheuse'),
    ('Scientifique', 'Scientifique'),
    ('Technicien/Technicienne', 'Technicien/Technicienne'),
    ('Informaticien/Informaticienne', 'Informaticien/Informaticienne'),
    ('Programmeur/Programmeuse', 'Programmeur/Programmeuse'),
    ('Développeur/Développeuse', 'Développeur/Développeuse'),
    ('Analyste', 'Analyste'),
    ('Consultant/Consultante', 'Consultant/Consultante'),
    ('Électricien/Électricienne', 'Électricien/Électricienne'),
    ('Plombier/Plombière', 'Plombier/Plombière'),
    ('Mécanicien/Mécanicienne', 'Mécanicien/Mécanicienne'),
    ('Charpentier/Charpentière', 'Charpentier/Charpentière'),
    ('Maçon/Maçonne', 'Maçon/Maçonne'),
    ('Couvreur/Couvreuse', 'Couvreur/Couvreuse'),
    ('Menuisier/Menuisière', 'Menuisier/Menuisière'),
    ('Forgeron/Forgeronne', 'Forgeron/Forgeronne'),
    ('Serrurier/Serrurière', 'Serrurier/Serrurière'),
    ('Couturier/Couturière', 'Couturier/Couturière'),
    ('Coiffeur/Coiffeuse', 'Coiffeur/Coiffeuse'),
    ('Esthéticien/Esthéticienne', 'Esthéticien/Esthéticienne'),
    ('Chef cuisinier/Chef cuisinière', 'Chef cuisinier/Chef cuisinière'),
    ('Serveur/Serveuse', 'Serveur/Serveuse'),
    ('Barman/Barmaid', 'Barman/Barmaid'),
    ('Agriculteur/Agricultrice', 'Agriculteur/Agricultrice'),
    ('Éleveur/Éleveuse', 'Éleveur/Éleveuse'),
    ('Pêcheur/Pêcheuse', 'Pêcheur/Pêcheuse'),
    ('Jardinier/Jardinière', 'Jardinier/Jardinière'),
    ('Conducteur/Conductrice', 'Conducteur/Conductrice'),
    ('Chauffeur/Chauffeuse', 'Chauffeur/Chauffeuse'),
    ('Pilote', 'Pilote'),
    ('Steward/Hôtesse de l\'air', 'Steward/Hôtesse de l\'air'),
    ('Agent de bord', 'Agent de bord'),
    ('Policier/Policière', 'Policier/Policière'),
    ('Gendarme', 'Gendarme'),
    ('Pompier', 'Pompier'),
    ('Soldat', 'Soldat'),
    ('Officier', 'Officier'),
    ('Avocat/Avocate', 'Avocat/Avocate'),
    ('Juge', 'Juge'),
    ('Notaire', 'Notaire'),
    ('Écrivain/Écrivaine', 'Écrivain/Écrivaine'),
    ('Journaliste', 'Journaliste'),
    ('Photographe', 'Photographe'),
    ('Réalisateur/Réalisatrice', 'Réalisateur/Réalisatrice'),
    ('Acteur/Actrice', 'Acteur/Actrice'),
    ('Musicien/Musicienne', 'Musicien/Musicienne'),
    ('Chanteur/Chanteuse', 'Chanteur/Chanteuse'),
    ('Danseur/Danseuse', 'Danseur/Danseuse'),
    ('Artiste peintre', 'Artiste peintre'),
    ('Sculpteur/Sculptrice', 'Sculpteur/Sculptrice'),
    ('Designer', 'Designer'),
    ('Graphiste', 'Graphiste'),
    ('Webdesigner', 'Webdesigner'),
    ('Publicitaire', 'Publicitaire'),
    ('Marketeur/Marketeuse', 'Marketeur/Marketeuse'),
    ('Comptable', 'Comptable'),
    ('Banquier/Banquière', 'Banquier/Banquière'),
    ('Assureur/Assureuse', 'Assureur/Assureuse'),
    ('Courtier/Courtière', 'Courtier/Courtière'),
    ('Gestionnaire', 'Gestionnaire'),
    ('Directeur/Directrice', 'Directeur/Directrice'),
    ('Cadre', 'Cadre'),
    ('Assistant/Assistante', 'Assistant/Assistante'),
    ('Secrétaire', 'Secrétaire'),
    ('Réceptionniste', 'Réceptionniste'),
    ('Agent d\'entretien', 'Agent d\'entretien'),
    ('Facteur/Factrice', 'Facteur/Factrice'),
    ('Livreur/Livreuse', 'Livreur/Livreuse'),
    ('Éboueur/Éboueuse', 'Éboueur/Éboueuse'),
    ('Gardien/Gardienne', 'Gardien/Gardienne'),
    ('Concierge', 'Concierge'),
    ('Bibliothécaire', 'Bibliothécaire'),
    ('Archiviste', 'Archiviste'),
    ('Documentaliste', 'Documentaliste'),
    ('Traducteur/Traductrice', 'Traducteur/Traductrice'),
    ('Interprète', 'Interprète'),
    ('Autre', 'Autre')
]
Goupe_sanguin_choices = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
]

situation_matrimoniales_choices = [
    ('Celibataire', 'Celibataire'),
    ('Concubinage', 'Concubinage'),
    ('Marie', 'Marié'),
    ('Divorce', 'Divorcé'),
    ('Veuf', 'Veuf'),
    ('Autre', 'Autre'),
]


class PatientForm(forms.ModelForm):
    numeros_cmu = forms.CharField(required=False, label="N° CMU ",
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control', 'placeholder': '0002515155515'}))
    nom = forms.CharField(label="Nom",
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex:Ogah'}))
    prenoms = forms.CharField(label="Prenom",
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex:Serge'}))

    contact = forms.CharField(label="Contact",
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex:0701020304'}))

    lieu_naissance = forms.CharField(label="Lieu de naissance", widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_naissance = forms.DateField(label="Date de naissance",
                                     widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'Date'}))
    genre = forms.ChoiceField(choices=SEXE_CHOICES, label="Sexe", widget=forms.Select(attrs={'class': 'form-control'}))
    situation_matrimoniale = forms.ChoiceField(label="Situation Matrimoniale", choices=situation_matrimoniales_choices,
                                               widget=forms.Select(attrs={'class': 'form-control select2 form-select ',
                                                                          'data-search': 'on'}))
    nationalite = forms.ChoiceField(choices=NATIONALITE_CHOICES, label="Nationalité", widget=forms.Select(
        attrs={'class': 'form-control select2 form-select ', 'data-search': 'on'}))
    profession = forms.CharField(label="Profession",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex:Medecin'}))

    nbr_enfants = forms.IntegerField(label="Nombre d'Enfant", widget=forms.NumberInput(attrs={'class': 'form-control'}))

    groupe_sanguin = forms.ChoiceField(choices=Goupe_sanguin_choices, label="Groupe Sanguin", widget=forms.Select(
        attrs={'class': 'form-control select2 form-select ', 'data-search': 'on'}))

    niveau_etude = forms.CharField(label="Niveau d'etude", widget=forms.TextInput(attrs={'class': 'form-control'}))

    employeur = forms.CharField(label="Employeur",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex:Ministere'}))

    commune = forms.ModelChoiceField(queryset=Commune.objects.all(), label='Ville/Commune', widget=forms.Select(
        attrs={'class': 'form-control select2 form-select ', 'data-search': 'on'}))

    class Meta:
        model = Patient
        fields = '__all__'
        exclude = (
            'created_by',
            'created_at',
            'status',
            'gueris',
            'quartier',
            'decede',
            'profession')

    # def clean_data(self):
    #     medical_history = self.cleaned_data['medical_history']
    #     current_medications = self.cleaned_data['current_medications']
    #     allergies = self.cleaned_data['allergies']
    #     try:
    #         json_data = json.loads(medical_history)
    #         json_data1 = json.loads(current_medications)
    #         json_data2 = json.loads(allergies)
    #     except ValueError as e:
    #         raise forms.ValidationError("Invalid JSON data")
    #     return json_data, json_data1, json_data2
    #
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Vérifiez si le champ est requis
            if field.required:
                # Ajoutez le signe '*' à l'étiquette du champ
                field.label = mark_safe(f"{field.label} <span style='color: red;'>*</span>")


class InfoscreateForm(forms.ModelForm):
    titre = forms.CharField(label="Titre",
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex:Titre de l\'information '}))
    message = forms.CharField(required=True, label="Contenu",
                                       widget=TinyMCE(attrs={'class': 'form-control', 'cols': 80, 'rows': 5}))

    class Meta:
        model = Information
        fields = '__all__'
        exclude = ('auteur','date_added')
