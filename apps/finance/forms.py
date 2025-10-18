from django import forms

class CSVUploadForm(forms.Form):
    year = forms.IntegerField(min_value=2000, max_value=2100, label="Haushaltsjahr")
    file = forms.FileField(label="CSV-Datei (Semikolon-getrennt)")
    dry_run = forms.BooleanField(
        required=False,
        initial=True,
        label="Testlauf (nur prüfen, nichts übernehmen)"
    )
    kind = forms.ChoiceField(
        choices=[
            ('costcenters','Kostenstellen (KS) – z. B. 100;Präsidium'),
            ('clusters','Kostencluster (Cluster) – z. B. 101;Präsente;100')
        ],
        label="Import-Typ"
    )
