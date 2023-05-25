from django.shortcuts import render
from django.db import transaction as db_transaction
from django.contrib.auth.models import User
from transactions.models import Card, Account, Transaction
from transactions.serializers import UserSerializer, CardSerializer, AccountSerializer, TransactionSerializer
from rest_framework import permissions
from rest_framework import viewsets
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        elif user.is_authenticated:
            return User.objects.filter(id=user.id)
        return User.objects.none()
    
class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAdminUser]

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAdminUser]

class TransactionViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAdminUser]


    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        card_number = validated_data.get('card_number')
        cvv = validated_data.get('cvv')
        expiration_date = validated_data.get('expiration_date')
        pay_amount = validated_data['total']

        try:
            # Get the card instance
            card = Card.objects.get(card_number=card_number)

            # Validate the card details
            if card.cvv != cvv:
                raise serializers.ValidationError("Invalid CVV.")
            if card.expiration_date != expiration_date:
                raise serializers.ValidationError("Invalid expiration date.")
            if card.expiration_date < timezone.now().date():
                raise serializers.ValidationError("The card is expired.")
            if card.balance < pay_amount:
                raise serializers.ValidationError("Insufficient balance.")

            # Create transaction and update card balance within a database transaction
            with db_transaction.atomic():
                # subtract the transaction amount from the card balance
                card.balance -= pay_amount
                card.save()

                # save transaction after deducting from card balance
                serializer.save()

        except Card.DoesNotExist:
            raise serializers.ValidationError("The card does not exist.")

