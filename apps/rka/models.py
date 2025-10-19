from django.db import models
from django.conf import settings
from apps.iam.models import Function
from apps.settingsmgr.models import ModuleApprovalConfig


class TravelRequest(models.Model):
    STATUS = [
        ("DRAFT", "Entwurf"),
        ("IN_REVIEW", "Im Genehmigungsprozess"),
        ("RETURNED", "Zur Korrektur zurückgegeben"),
        ("APPROVED", "Final genehmigt"),
        ("REJECTED", "Abgelehnt"),
    ]

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    step1_function = models.ForeignKey(
        Function,
        on_delete=models.PROTECT,
        help_text="Entscheider Nr. 1 (vom Antragsteller gewählt)",
    )
    status = models.CharField(max_length=16, choices=STATUS, default="IN_REVIEW")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"RKA #{self.pk} von {self.applicant}"

    # --- Sequenz-Logik (Schritt 1 + feste Steps 2–5 aus Settings) ---
    def approval_sequence(self):
        cfg = ModuleApprovalConfig.objects.filter(module="RKA", is_active=True).first()
        if not cfg:
            return [self.step1_function]
        return cfg.step_functions(self.step1_function)

    def current_step_number(self) -> int:
        """Nächster zu bearbeitender Schritt: Anzahl bereits protokollierter 'APPROVE'-Schritte + 1."""
        # Wir zählen nur tatsächlich genehmigte Schritte als erledigt.
        done = self.events.filter(decision="APPROVE").count()
        return done + 1

    def current_function(self):
        """Welche Funktion ist jetzt am Zug? None, wenn fertig oder nicht im Prozess."""
        if self.status not in ("IN_REVIEW", "RETURNED"):
            return None
        seq = self.approval_sequence()
        idx = self.current_step_number() - 1  # 0-basiert
        return seq[idx] if 0 <= idx < len(seq) else None

    def is_final_approval_after_next(self) -> bool:
        """True, wenn der nächste APPROVE die Kette abschließt."""
        seq = self.approval_sequence()
        return self.current_step_number() >= len(seq)

    def finalize_if_complete(self):
        """Aufrufen nach einem APPROVE: wenn alles durch, Status setzen."""
        if self.is_final_approval_after_next():
            self.status = "APPROVED"
            self.save()


class ApprovalEvent(models.Model):
    DECISION = [
        ("APPROVE", "Genehmigt"),
        ("RETURN", "Zur Korrektur zurückgegeben"),
        ("REJECT", "Abgelehnt"),
    ]

    request = models.ForeignKey(TravelRequest, related_name="events", on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField(help_text="1..n entsprechend der Reihenfolge")
    function = models.ForeignKey(Function, on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    decision = models.CharField(max_length=10, choices=DECISION)
    comment = models.TextField(blank=True, default="")
    ip_address = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"RKA #{self.request_id} – Step {self.step_number}: {self.get_decision_display()}"
