from django.db import models
from django_multitenant.mixins import TenantModelMixin
from django_multitenant.models import TenantManager

class Company(TenantModelMixin, models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    tenant_id = 'id'

    class Meta:
        db_table = 'tenant_company'

    def __str__(self):
        return self.name

class Product(TenantModelMixin, models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.ForeignKey('tenant.Company', on_delete=models.CASCADE)
    tenant_id = 'company_id'

    objects = TenantManager()

    class Meta:
        db_table = 'tenant_product'

    def __str__(self):
        return self.name
