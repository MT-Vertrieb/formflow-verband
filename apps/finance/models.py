
from django.db import models

class CostCenter(models.Model):
    year = models.PositiveIntegerField()
    code = models.CharField(max_length=12)  # digits only by validation
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = ('year','code')

    def __str__(self):
        return f"{self.year} - {self.code} {self.name}"

class CostCluster(models.Model):
    year = models.PositiveIntegerField()
    code = models.CharField(max_length=12)  # continuous numbering across all cost centers
    name = models.CharField(max_length=200)
    cost_center = models.ForeignKey(CostCenter, on_delete=models.CASCADE, related_name='clusters')

    class Meta:
        unique_together = ('year','code')

    def __str__(self):
        return f"{self.year} - {self.code} {self.name}"
