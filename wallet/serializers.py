from asgiref.sync import sync_to_async

from django.utils.datetime_safe import datetime
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from wallet.models import Customer, Wallet, Transaction
from wallet.tasks import update_balance_after_deposit, update_balance_after_withdrawal


def disable_field_validator(is_disabled: str):
    if is_disabled != 'true':
        raise serializers.ValidationError("is_disabled value is not valid")
    return is_disabled


def enabled_validator(wallet):
    if not wallet.is_enable:
        raise serializers.ValidationError('Disabled')
    return True


class CustomerSerializer(serializers.ModelSerializer):
    customer_xid = serializers.UUIDField(allow_null=False, write_only=True)
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_xid', 'token']

    def create(self, validated_data):
        customer, created = Customer.objects.get_or_create(customer_xid=validated_data.get('customer_xid'))
        if created:
            Wallet.objects.get_or_create(customer=customer)
        return customer

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)


class EnableWalletSerializer(serializers.ModelSerializer):

    owned_by = serializers.PrimaryKeyRelatedField(read_only=True, source='customer')
    status = serializers.SerializerMethodField(read_only=True)
    enabled_at = serializers.DateTimeField(source='status_updated_at', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'owned_by', 'status', 'balance', 'enabled_at']

    def update(self, instance, validated_data):
        if not instance.is_enable:
            instance.is_enable = True
            instance.status_updated_at = datetime.now()
            instance.save()
        else:
            raise serializers.ValidationError("Already disabled")

        return instance

    def get_status(self, obj):
        if obj.is_enable:
            return 'enabled'


class DisableWalletSerializer(serializers.ModelSerializer):

    owned_by = serializers.PrimaryKeyRelatedField(read_only=True, source='customer')
    status = serializers.SerializerMethodField(read_only=True)
    is_disabled = serializers.CharField(max_length=20, validators=[disable_field_validator], write_only=True)
    disabled_at = serializers.DateTimeField(source='status_updated_at', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'owned_by', 'status', 'balance', 'disabled_at', 'is_disabled']

    def update(self, instance, validated_data):
        if instance.is_enable:
            instance.is_enable = False
            instance.status_updated_at = datetime.now()
            instance.save()
        else:
            raise serializers.ValidationError("Already disabled")

        return instance

    def get_status(self, obj):
        if not obj.is_enable:
            return 'disabled'


class DepositSerializer(serializers.ModelSerializer):
    deposited_by = serializers.PrimaryKeyRelatedField(source='wallet', read_only=True)
    deposited_at = serializers.DateTimeField(read_only=True, source='created_at')
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'deposited_by', 'deposited_at', 'reference_id', 'amount', 'status']

    def get_status(self, obj):
        if obj:
            return 'success'
        else:
            return 'fail'

    def create(self, validated_data):
        customer_xid = validated_data.pop('customer_xid')
        wallet = Wallet.objects.get(customer_id=customer_xid)
        validated_data['wallet'] = wallet
        validated_data['created_by_id'] = customer_xid
        transaction = Transaction.objects.create(**validated_data)
        update_balance_after_deposit(wallet, transaction)
        return transaction


class DepositSerializer(serializers.ModelSerializer):
    deposited_by = serializers.PrimaryKeyRelatedField(source='created_by', read_only=True)
    deposited_at = serializers.DateTimeField(read_only=True, source='created_at')
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'deposited_by', 'deposited_at', 'reference_id', 'amount', 'status']

    def get_status(self, obj):
        if obj:
            return 'success'
        else:
            return 'fail'

    def create(self, validated_data):
        customer_xid = validated_data.pop('customer_xid')
        wallet = Wallet.objects.get(customer_id=customer_xid)
        enabled_validator(wallet)
        validated_data['wallet'] = wallet
        validated_data['created_by_id'] = customer_xid
        transaction = Transaction.objects.create(**validated_data)
        update_balance_after_deposit(wallet.id, validated_data.get('amount'))
        # sync_to_async(update_balance_after_deposit, thread_sensitive=True)(wallet.id, validated_data.get('amount'))
        return transaction


class WithdrawalSerializer(serializers.ModelSerializer):
    withdrawn_by = serializers.PrimaryKeyRelatedField(source='created_by', read_only=True)
    withdrawn_at = serializers.DateTimeField(read_only=True, source='created_at')
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'withdrawn_by', 'withdrawn_at', 'reference_id', 'amount', 'status']

    def get_status(self, obj):
        if obj:
            return 'success'
        else:
            return 'fail'

    def create(self, validated_data):
        customer_xid = validated_data.pop('customer_xid')
        wallet = Wallet.objects.get(customer_id=customer_xid)
        enabled_validator(wallet)
        if wallet.balance < validated_data.get('amount'):
            raise serializers.ValidationError("The wallet balance are lower than amount")

        validated_data['wallet'] = wallet
        validated_data['created_by_id'] = customer_xid
        validated_data['type'] = 'WID'
        transaction = Transaction.objects.create(**validated_data)
        update_balance_after_withdrawal(wallet, transaction)
        return transaction
