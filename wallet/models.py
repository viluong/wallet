import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


TRANSACTION_CHOICES = (
    ("DEP", "Deposit"),
    ("WID", "Withdrawal"),
)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Customer(AbstractUser):
    username = None
    USERNAME_FIELD = 'customer_xid'
    REQUIRED_FIELDS = []
    customer_xid = models.UUIDField(primary_key=True, blank=False, null=False, default=uuid.uuid4)

    def __str__(self):
        return self.customer_xid


class Wallet(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='wallet')
    balance = models.FloatField(default=0)
    is_enable = models.BooleanField(default=False)
    status_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.customer.customer_xid


class Transaction(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='wallet_transactions')
    reference_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    type = models.CharField(choices=TRANSACTION_CHOICES, default='DEP', max_length=20)
    amount = models.FloatField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   null=True, blank=True,
                                   on_delete=models.CASCADE, related_name='user_transactions')

    class Meta:
        unique_together = ('reference_id', 'type',)
