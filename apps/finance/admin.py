from django.contrib import admin
from .models import CostCenter, CostCluster
admin.site.register([CostCenter, CostCluster])
