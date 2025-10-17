"""
Optimized API views with caching and performance monitoring
"""
import time
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .ml_models.advanced_fraud_detector import AdvancedFraudDetector
from .ml_models.advanced_chatbot import AdvancedChatbotEngine
from .optimization.cache_manager import cache_manager
from .optimization.performance_monitor import performance_monitor

# Initialize optimized AI engines
advanced_fraud_detector = AdvancedFraudDetector()
advanced_chatbot = AdvancedChatbotEngine()

class OptimizedFraudDetectionAPI(APIView):
    """
    Optimized fraud detection with caching and performance monitoring
    """
    
    def post(self, request):
        start_time = time.time()
        endpoint_name = 'fraud_detection'
        
        try:
            filing_data = request.data.get('filing_data', {})
            taxpayer_history = request.data.get('taxpayer_history', {})
            
            # Check cache first
            cache_key = cache_manager.generate_cache_key('fraud_analysis', filing_data)
            cached_result = cache_manager.get_cached_analysis(filing_data)
            
            if cached_result:
                performance_monitor.record_cache_hit()
                response_time = time.time() - start_time
                performance_monitor.track_response_time(endpoint_name, response_time)
                
                return Response({
                    'success': True,
                    'cached': True,
                    **cached_result,
                    'processing_time_ms': int(response_time * 1000)
                })
            
            performance_monitor.record_cache_miss()
            
            # Perform advanced analysis
            ml_result = advanced_fraud_detector.predict(filing_data, taxpayer_history)
            ensemble_result = advanced_fraud_detector.ensemble_predict(
                filing_data, taxpayer_history, ml_result['fraud_probability']
            )
            
            # Prepare response
            response_data = {
                'success': True,
                'cached': False,
                'risk_score': ensemble_result['ensemble_score'],
                'risk_level': self._get_risk_level(ensemble_result['ensemble_score']),
                'ml_confidence': ensemble_result['ml_confidence'],
                'feature_importance': ensemble_result['feature_importance'],
                'analysis_method': 'advanced_ensemble',
                'recommendation': self._get_recommendation(ensemble_result['ensemble_score'])
            }
            
            # Cache the result
            cache_manager.cache_analysis_result(filing_data, response_data)
            
            response_time = time.time() - start_time
            performance_monitor.track_response_time(endpoint_name, response_time)
            response_data['processing_time_ms'] = int(response_time * 1000)
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            response_time = time.time() - start_time
            performance_monitor.track_response_time(endpoint_name, response_time)
            
            return Response({
                'success': False,
                'error': 'Analysis failed',
                'details': str(e),
                'processing_time_ms': int(response_time * 1000)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_risk_level(self, score):
        if score >= 0.7:
            return 'HIGH'
        elif score >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_recommendation(self, score):
        if score >= 0.7:
            return 'Immediate manual review required - high fraud probability'
        elif score >= 0.4:
            return 'Enhanced verification recommended - moderate risk'
        else:
            return 'Standard processing - low risk detected'

class OptimizedChatbotAPI(APIView):
    """
    Optimized chatbot with context awareness and caching
    """
    
    def post(self, request):
        start_time = time.time()
        endpoint_name = 'chatbot'
        
        try:
            user_query = request.data.get('query', '')
            conversation_id = request.data.get('conversation_id')
            context = request.data.get('context', {})
            
            # Check cache for similar queries
            cache_key_data = {'query': user_query, 'context': context}
            cached_response = cache_manager.get_cached_chat_response(user_query, context)
            
            if cached_response:
                performance_monitor.record_cache_hit()
                response_time = time.time() - start_time
                performance_monitor.track_response_time(endpoint_name, response_time)
                
                cached_response['cached'] = True
                cached_response['processing_time_ms'] = int(response_time * 1000)
                return Response(cached_response)
            
            performance_monitor.record_cache_miss()
            
            # Get enhanced response
            response_data = advanced_chatbot.get_enhanced_response(
                user_query, context, conversation_id
            )
            
            response_data['cached'] = False
            
            # Cache the response (except for personalized responses)
            if not context.get('user_id'):  # Don't cache personalized responses
                cache_manager.cache_chat_response(user_query, context, response_data)
            
            response_time = time.time() - start_time
            performance_monitor.track_response_time(endpoint_name, response_time)
            response_data['processing_time_ms'] = int(response_time * 1000)
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            response_time = time.time() - start_time
            performance_monitor.track_response_time(endpoint_name, response_time)
            
            return Response({
                'success': False,
                'error': 'Chatbot service unavailable',
                'details': str(e),
                'processing_time_ms': int(response_time * 1000)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PerformanceMetricsAPI(APIView):
    """
    API to get performance metrics for monitoring
    """
    
    @method_decorator(cache_page(60))  # Cache for 1 minute
    def get(self, request):
        metrics = performance_monitor.get_performance_metrics()
        return Response({
            'success': True,
            'metrics': metrics
        })