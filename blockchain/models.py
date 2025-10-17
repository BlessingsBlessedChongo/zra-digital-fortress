from django.db import models
import uuid
from django.utils import timezone

def generate_transaction_hash():
    """Generate a unique transaction hash starting with '0xZRA'."""
    return f"0xZRA{uuid.uuid4().hex[:20].upper()}"

class BlockchainTransaction(models.Model):
    """
    Simulates blockchain transactions for tax filings and payments
    This provides the immutable audit trail for our demo
    """
    TRANSACTION_TYPES = [
        ('TAX_FILING', 'Tax Filing Submission'),
        ('PAYMENT', 'Tax Payment'),
        ('REGISTRATION', 'Taxpayer Registration'),
        ('AUDIT', 'Audit Record'),
        ('FRAUD_FLAG', 'Fraud Flag'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed'),
    ]
    
    # Blockchain transaction ID (simulated hash)
    transaction_hash = models.CharField(
        max_length=100, 
        unique=True, 
        default=generate_transaction_hash  # Use the named function
    )
    
    # Reference to the actual business transaction
    reference_id = models.CharField(max_length=50)  # Tax filing ID, payment ID, etc.
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # Transaction data (JSON field for flexibility)
    transaction_data = models.JSONField(default=dict)
    
    # Blockchain simulation fields
    previous_hash = models.CharField(max_length=100, blank=True, null=True)
    block_number = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONFIRMED')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blockchain_transactions'
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['reference_id', 'transaction_type']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_hash}"
    
    def get_short_hash(self):
        """Return shortened hash for display"""
        return f"{self.transaction_hash[:10]}...{self.transaction_hash[-6:]}"

class Block(models.Model):
    """
    Simulates blockchain blocks containing multiple transactions
    For demo purposes to show how blockchain works
    """
    block_hash = models.CharField(max_length=100, unique=True)
    previous_block_hash = models.CharField(max_length=100, blank=True, null=True)
    block_number = models.IntegerField(unique=True)
    merkle_root = models.CharField(max_length=100)
    nonce = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Relationships
    transactions = models.ManyToManyField(BlockchainTransaction, related_name='blocks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blockchain_blocks'
        ordering = ['-block_number']
    
    def __str__(self):
        return f"Block #{self.block_number} - {self.get_short_hash()}"
    
    def get_short_hash(self):
        return f"{self.block_hash[:8]}...{self.block_hash[-6:]}"

class SmartContract(models.Model):
    """
    Simulates smart contracts for automated tax compliance
    """
    CONTRACT_TYPES = [
        ('VAT_VALIDATION', 'VAT Return Validation'),
        ('AUTO_REFUND', 'Automatic Refund Processing'),
        ('PENALTY_CALCULATION', 'Penalty Calculation'),
        ('COMPLIANCE_CHECK', 'Compliance Certificate'),
    ]
    
    contract_address = models.CharField(max_length=100, unique=True)
    contract_type = models.CharField(max_length=30, choices=CONTRACT_TYPES)
    contract_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Contract logic (simplified for demo)
    conditions = models.JSONField(default=dict)  # Business rules
    actions = models.JSONField(default=dict)     # Automated actions
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'smart_contracts'
    
    def __str__(self):
        return f"{self.contract_name} ({self.contract_address})"