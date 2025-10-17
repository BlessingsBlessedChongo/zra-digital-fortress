from django.db import models
from django.utils import timezone
import uuid

class TaxFilingAnalysis(models.Model):
    """
    Stores AI analysis results for tax filings
    """
    RISK_LEVELS = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Risk'),
    ]
    
    # Reference to the tax filing from Silas' backend
    filing_id = models.CharField(max_length=50, unique=True)
    taxpayer_id = models.CharField(max_length=20)  # TPIN
    
    # AI Analysis Results
    risk_score = models.FloatField(default=0.0)  # 0.0 - 1.0
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='LOW')
    risk_factors = models.JSONField(default=list)  # List of identified risk factors
    confidence_score = models.FloatField(default=0.0)  # AI confidence in analysis
    
    # Detailed analysis
    anomaly_detection = models.JSONField(default=dict)  # Specific anomalies found
    pattern_analysis = models.JSONField(default=dict)   # Behavioral patterns
    recommendations = models.JSONField(default=list)    # AI recommendations
    
    # Metadata
    analysis_timestamp = models.DateTimeField(default=timezone.now)
    processing_time_ms = models.IntegerField(default=0)
    model_version = models.CharField(max_length=50, default='v1.0-demo')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tax_filing_analysis'
        indexes = [
            models.Index(fields=['filing_id']),
            models.Index(fields=['taxpayer_id', 'analysis_timestamp']),
            models.Index(fields=['risk_level', 'analysis_timestamp']),
        ]
        ordering = ['-analysis_timestamp']
    
    def __str__(self):
        return f"Analysis for {self.filing_id} - Risk: {self.risk_score:.2f}"


class ChatbotConversation(models.Model):
    """
    Stores chatbot interactions for learning and analytics
    """
    conversation_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user_id = models.CharField(max_length=20, blank=True)  # TPIN if logged in
    session_id = models.CharField(max_length=100)  # Browser session
    
    # Conversation context
    initial_query = models.TextField()
    conversation_context = models.JSONField(default=dict)
    language = models.CharField(max_length=10, default='en')
    
    # Analytics
    total_messages = models.IntegerField(default=0)
    user_satisfaction_score = models.FloatField(null=True, blank=True)  # 1-5 scale
    resolved = models.BooleanField(default=False)
    
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chatbot_conversations'
        indexes = [
            models.Index(fields=['user_id', 'started_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Chat {self.conversation_id} - User: {self.user_id}"


class ChatMessage(models.Model):
    """
    Individual messages within a chatbot conversation
    """
    MESSAGE_TYPES = [
        ('USER', 'User Message'),
        ('BOT', 'Bot Response'),
        ('SYSTEM', 'System Message'),
    ]
    
    conversation = models.ForeignKey(
        ChatbotConversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    message_content = models.TextField()
    
    # AI-specific fields for bot responses
    intent_detected = models.CharField(max_length=100, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    suggested_actions = models.JSONField(default=list)
    
    timestamp = models.DateTimeField(default=timezone.now)
    processing_time_ms = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.message_content[:50]}..."


class FraudPattern(models.Model):
    """
    Known fraud patterns for AI training and detection
    """
    PATTERN_TYPES = [
        ('UNDER_REPORTING', 'Income Under-reporting'),
        ('OVER_DEDUCTION', 'Excessive Deductions'),
        ('FALSE_EXPENSES', 'Fictitious Expenses'),
        ('SHELL_COMPANIES', 'Shell Company Fraud'),
        ('VAT_FRAUD', 'VAT Carousel Fraud'),
        ('PAYROLL_FRAUD', 'Payroll Tax Evasion'),
    ]
    
    pattern_name = models.CharField(max_length=100)
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPES)
    description = models.TextField()
    
    # Detection rules (simplified for demo)
    detection_rules = models.JSONField(default=dict)
    risk_weight = models.FloatField(default=1.0)  # How serious this pattern is
    common_indicators = models.JSONField(default=list)
    
    # Effectiveness tracking
    detection_count = models.IntegerField(default=0)
    false_positive_count = models.IntegerField(default=0)
    last_detected = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fraud_patterns'
    
    def __str__(self):
        return f"{self.pattern_name} ({self.pattern_type})"