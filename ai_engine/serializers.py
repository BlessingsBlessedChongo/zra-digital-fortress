from rest_framework import serializers
from .models import TaxFilingAnalysis, ChatbotConversation, ChatMessage, FraudPattern

class TaxFilingAnalysisSerializer(serializers.ModelSerializer):
    risk_score_percentage = serializers.SerializerMethodField()
    analysis_age = serializers.SerializerMethodField()
    
    class Meta:
        model = TaxFilingAnalysis
        fields = [
            'filing_id', 'taxpayer_id', 'risk_score', 'risk_score_percentage',
            'risk_level', 'risk_factors', 'confidence_score', 'anomaly_detection',
            'pattern_analysis', 'recommendations', 'analysis_age', 'model_version',
            'processing_time_ms', 'created_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_risk_score_percentage(self, obj):
        return f"{obj.risk_score * 100:.1f}%"
    
    def get_analysis_age(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.analysis_timestamp
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600} hours ago"
        else:
            return f"{delta.seconds // 60} minutes ago"


class FraudPatternSerializer(serializers.ModelSerializer):
    detection_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = FraudPattern
        fields = [
            'pattern_name', 'pattern_type', 'description', 'detection_rules',
            'risk_weight', 'common_indicators', 'detection_count',
            'false_positive_count', 'detection_rate', 'last_detected',
            'is_active', 'created_at'
        ]
    
    def get_detection_rate(self, obj):
        total = obj.detection_count + obj.false_positive_count
        if total == 0:
            return "0%"
        accuracy = (obj.detection_count / total) * 100
        return f"{accuracy:.1f}%"


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'message_type', 'message_content', 'intent_detected',
            'confidence', 'suggested_actions', 'timestamp'
        ]


class ChatbotConversationSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatbotConversation
        fields = [
            'conversation_id', 'user_id', 'session_id', 'initial_query',
            'conversation_context', 'language', 'total_messages',
            'user_satisfaction_score', 'resolved', 'messages', 'duration',
            'started_at', 'ended_at'
        ]
    
    def get_duration(self, obj):
        if obj.ended_at:
            duration = obj.ended_at - obj.started_at
            return f"{duration.seconds // 60}m {duration.seconds % 60}s"
        return "Ongoing"


# Request/Response serializers for API endpoints
class FraudDetectionRequestSerializer(serializers.Serializer):
    filing_data = serializers.JSONField()
    taxpayer_history = serializers.JSONField(required=False, default=dict)
    context_data = serializers.JSONField(required=False, default=dict)


class FraudDetectionResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    risk_score = serializers.FloatField(min_value=0.0, max_value=1.0)
    risk_level = serializers.CharField()
    risk_factors = serializers.ListField(child=serializers.CharField())
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    recommendation = serializers.CharField()
    detailed_analysis = serializers.JSONField(required=False)


class ChatbotRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    conversation_id = serializers.UUIDField(required=False)
    context = serializers.JSONField(required=False, default=dict)
    language = serializers.CharField(default='en')


class ChatbotResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    response = serializers.CharField()
    suggested_questions = serializers.ListField(child=serializers.CharField())
    confidence = serializers.FloatField()
    conversation_id = serializers.UUIDField(required=False)