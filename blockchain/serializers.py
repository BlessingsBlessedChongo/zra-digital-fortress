from rest_framework import serializers
from .models import BlockchainTransaction, Block, SmartContract

class BlockchainTransactionSerializer(serializers.ModelSerializer):
    short_hash = serializers.SerializerMethodField()
    transaction_age = serializers.SerializerMethodField()
    
    class Meta:
        model = BlockchainTransaction
        fields = [
            'transaction_hash', 'short_hash', 'reference_id', 'transaction_type',
            'transaction_data', 'previous_hash', 'block_number', 'timestamp',
            'status', 'transaction_age', 'created_at'
        ]
        read_only_fields = ['transaction_hash', 'created_at']
    
    def get_short_hash(self, obj):
        return obj.get_short_hash()
    
    def get_transaction_age(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.timestamp
        return f"{delta.days}d {delta.seconds//3600}h ago"


class BlockSerializer(serializers.ModelSerializer):
    short_hash = serializers.SerializerMethodField()
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Block
        fields = [
            'block_hash', 'short_hash', 'previous_block_hash', 'block_number',
            'merkle_root', 'nonce', 'timestamp', 'transaction_count', 'created_at'
        ]
    
    def get_short_hash(self, obj):
        return obj.get_short_hash()
    
    def get_transaction_count(self, obj):
        return obj.transactions.count()


class SmartContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartContract
        fields = [
            'contract_address', 'contract_type', 'contract_name', 'description',
            'conditions', 'actions', 'is_active', 'created_at'
        ]


class TransactionCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new blockchain transactions
    """
    reference_id = serializers.CharField(max_length=50)
    transaction_type = serializers.ChoiceField(choices=BlockchainTransaction.TRANSACTION_TYPES)
    transaction_data = serializers.JSONField()
    
    def create(self, validated_data):
        return BlockchainTransaction.objects.create(**validated_data)