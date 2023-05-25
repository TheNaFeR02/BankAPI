from rest_framework import serializers
from django.contrib.auth.models import User
from transactions.models import Card, Transaction, Account

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email']
    
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['account','card_number', 'balance', 'expiration_date', 'cvv', 'card_type', 'card_brand', 'credit_limit', 'interest_rate']

    def validate(self, data):
        card_type = data.get('card_type')
        credit_limit = data.get('credit_limit')
        interest_rate = data.get('interest_rate')

        if card_type == 'DEBIT' and (credit_limit or interest_rate):
            raise serializers.ValidationError("Debit cards should not have a credit limit or interest rate.")
        elif card_type == 'CREDIT' and (credit_limit is None or interest_rate is None):
            raise serializers.ValidationError("Credit cards should have a credit limit and interest rate.")

        return data
    

class AccountSerializer(serializers.ModelSerializer):
    # debit_card = CardSerializer()
    # credit_card = CardSerializer()
    cards = CardSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ['owner', 'identification_id', 'opening_date', 'cards' , 'currency', 'status']


class TransactionSerializer(serializers.ModelSerializer):
    card_number = serializers.CharField(required=True)
    cvv = serializers.IntegerField(required=True)
    expiration_date = serializers.DateField(required=True)

    class Meta:
        model = Transaction
        fields = ['id','card_number', 'cvv', 'expiration_date','sede','description','datetime','cuotas','total']