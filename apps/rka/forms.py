from django import forms
from django.forms import inlineformset_factory
from .models import TravelRequest, ExpenseItem


class TravelRequestForm(forms.ModelForm):
    destination_label = forms.CharField(label="Ziel (Bezeichnung)", required=False)
    destination_street = forms.CharField(label="Ziel (Stra?e / Nr.)", required=False,
                                         widget=forms.TextInput(attrs={"style": "width: 100%;"}))
    destination_city = forms.CharField(label="Ziel (Ort)", required=False,
                                       widget=forms.TextInput(attrs={"style": "width: 100%;"}))
    purpose = forms.CharField(label="Zweck der Reise", required=False,
                              widget=forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}))
    origin = forms.CharField(label="Fahrt von", required=False,
                             widget=forms.TextInput(attrs={"style": "width: 100%;"}))

    class Meta:
        model = TravelRequest
        fields = [
            "origin",
            "destination_label", "destination_street", "destination_city",
            "purpose",
            "start_date", "start_time", "end_date", "end_time",
            "cost_center", "approver_function"
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        # Vorbelegung "Fahrt von" aus Profil (Stra?e + Hausnummer + Ort)
        if self.request and self.request.user and hasattr(self.request.user, "profile"):
            prof = self.request.user.profile
            street = getattr(prof, "street", "") or ""
            nr     = getattr(prof, "house_number", "") or ""
            city   = getattr(prof, "city", "") or ""
            addr = (street + (" " + nr if nr else "")).strip()
            display = ", ".join([p for p in [addr, city] if p])
            if not self.initial.get("origin") and not (self.instance and self.instance.pk):
                self.initial["origin"] = display

        # Breitere Eingaben standardisieren
        for k in ["origin", "destination_label", "destination_street", "destination_city"]:
            if k in self.fields:
                self.fields[k].widget.attrs.setdefault("style", "width: 100%;")

        # Falls Instanz bereits Daten hat: Form-Felder damit bef?llen
        if self.instance and getattr(self.instance, "pk", None):
            if getattr(self.instance, "destination_label", None):
                self.initial["destination_label"] = self.instance.destination_label
            if getattr(self.instance, "destination_street", None):
                self.initial["destination_street"] = self.instance.destination_street
            if getattr(self.instance, "destination_city", None):
                self.initial["destination_city"] = self.instance.destination_city
            if getattr(self.instance, "purpose", None):
                self.initial["purpose"] = self.instance.purpose

    def clean(self):
        data = super().clean()
        # Ziel-Komponenten zu altem 'destination' zusammensetzen (Kompatibilit?t)
        parts = []
        if data.get("destination_label"):
            parts.append(data["destination_label"])
        # Stra?e + Ort h?bsch zusammensetzen
        street = data.get("destination_street", "").strip()
        city   = data.get("destination_city", "").strip()
        addr = ", ".join([p for p in [street, city] if p])
        if addr:
            parts.append(addr)
        destination_combined = " ? ".join(parts) if parts else ""
        # in instance schreiben, damit gespeichert wird
        self.instance.destination = destination_combined
        self.instance.destination_label  = data.get("destination_label", "")
        self.instance.destination_street = street
        self.instance.destination_city   = city
        # Zweck sicher in instance (auch wenn Meta-Feld vorhanden)
        self.instance.purpose = data.get("purpose", "")
        return data
class ExpenseItemForm(forms.ModelForm):
    class Meta:
        model = ExpenseItem
        fields = ["date", "description", "amount"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

ExpenseItemFormSet = inlineformset_factory(
    TravelRequest,
    ExpenseItem,
    form=ExpenseItemForm,
    extra=1,
    can_delete=True,
)
