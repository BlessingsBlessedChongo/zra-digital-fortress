from django.urls import path
from . import views

urlpatterns = [
    # Modern API endpoints (recommended)
    path('analyze-fraud', views.FraudDetectionAPI.as_view(), name='analyze_fraud'),
    path('chatbot', views.ChatbotAPI.as_view(), name='chatbot'),
    path('risk-history/<str:taxpayer_id>', views.RiskAnalysisHistoryAPI.as_view(), name='risk_history'),
    path('health', views.HealthCheckAPI.as_view(), name='health_check'),
    
    # Legacy endpoints for compatibility
    path('analyze-risk', views.analyze_fraud_risk_legacy, name='analyze_risk_legacy'),
    path('chatbot-legacy', views.chatbot_legacy, name='chatbot_legacy'),
]