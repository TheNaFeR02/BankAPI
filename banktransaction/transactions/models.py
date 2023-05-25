from django.db import models
from django.core.exceptions import ValidationError
import uuid

# Create your models here.
class Account(models.Model):
    owner = models.OneToOneField('auth.User', related_name='accounts', on_delete=models.CASCADE)
    identification_id = models.CharField(max_length=255)
    opening_date = models.DateTimeField(auto_now_add=True)
    
    CURRENCY_CHOICES = (
        ('COP', 'Pesos Colombianos'),
        # Add other currencies as needed
    )
    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Suspended', 'Suspended'),
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open') 

    def __str__(self):
        return self.owner.__str__()
    
class Transaction(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]

    SEDE = [
        ('BARRANQUILLA', 'Barranquilla'),
        ('CARTAGENA', 'Cartagena'),
        ('SANTA MARTA', 'Santa Marta'),
        ('SINCELEJO', 'Sincelejo'),
        ('MONTERIA', 'Monteria'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card_number = models.CharField(max_length=16, null=True)
    cvv = models.IntegerField(null=True)
    expiration_date = models.DateField(null=True)
    sede = models.CharField(max_length=20, choices=SEDE, default='Barranquilla')
    description = models.CharField(max_length=200, null=True)
    datetime = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class Card(models.Model):
    CARD_TYPE_CHOICES = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]

    CARD_BRAND_CHOICES = [
        ('VISA', 'Visa'),
        ('MAST', 'MasterCard'),
        ('AMEX', 'American Express'),
        # add more card types as needed
    ]

    account = models.ForeignKey('Account', related_name='cards',on_delete=models.CASCADE, null=True)
    card_number = models.CharField(max_length=16, primary_key=True, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    expiration_date = models.DateField()
    cvv = models.IntegerField()
    card_type = models.CharField(max_length=200, choices=CARD_TYPE_CHOICES)
    card_brand = models.CharField(max_length=200, choices=CARD_BRAND_CHOICES)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
    
    def clean(self):
        if self.card_type == 'DEBIT' and (self.credit_limit or self.interest_rate):
            raise ValidationError("Debit cards should not have a credit limit or interest rate.")
        elif self.card_type == 'CREDIT' and (self.credit_limit is None or self.interest_rate is None):
            raise ValidationError("Credit cards should have a credit limit and interest rate.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.card_number