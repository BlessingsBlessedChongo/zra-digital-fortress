from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import time
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import TaxFilingAnalysis, ChatbotConversation, ChatMessage, FraudPattern
from .serializers import (
    FraudDetectionRequestSerializer, FraudDetectionResponseSerializer,
    ChatbotRequestSerializer, ChatbotResponseSerializer,
    TaxFilingAnalysisSerializer
)
from .ml_models.fraud_detector import FraudDetector
from .ml_models.chatbot_engine import ChatbotEngine

logger = logging.getLogger(__name__)

# Initialize AI engines
fraud_detector = FraudDetector()
chatbot_engine = ChatbotEngine()

class FraudDetectionAPI(APIView):
    """
    API endpoint for AI-powered fraud detection
    Called by Silas' Java backend when tax filings are submitted
    """
    
    def post(self, request):
        start_time = time.time()
        
        try:
            # Validate input data
            serializer = FraudDetectionRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid request data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            filing_data = serializer.validated_data['filing_data']
            taxpayer_history = serializer.validated_data.get('taxpayer_history', {})
            context_data = serializer.validated_data.get('context_data', {})
            
            logger.info(f"Processing fraud detection for filing: {filing_data.get('filing_id', 'Unknown')}")
            
            # Perform AI analysis
            analysis_result = fraud_detector.analyze(filing_data, taxpayer_history)
            
            # Store analysis in database
            analysis_record = TaxFilingAnalysis.objects.create(
                filing_id=filing_data.get('filing_id', 'unknown'),
                taxpayer_id=filing_data.get('taxpayer_id', 'unknown'),
                risk_score=analysis_result['score'],
                risk_level=analysis_result['level'],
                risk_factors=analysis_result['factors'],
                confidence_score=analysis_result['confidence'],
                anomaly_detection=analysis_result['detailed_analysis'],
                pattern_analysis={
                    'matched_patterns': [],
                    'confidence_scores': []
                },
                recommendations=[analysis_result['recommendation']],
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
            
            # Prepare response
            response_data = {
                'success': True,
                'risk_score': analysis_result['score'],
                'risk_level': analysis_result['level'],
                'risk_factors': analysis_result['factors'],
                'confidence': analysis_result['confidence'],
                'recommendation': analysis_result['recommendation'],
                'analysis_id': str(analysis_record.id),
                'detailed_analysis': analysis_result['detailed_analysis'],
                'processing_time_ms': analysis_record.processing_time_ms
            }
            
            logger.info(f"Fraud analysis completed: {analysis_result['level']} risk for {analysis_record.filing_id}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in fraud detection API: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error during fraud analysis',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotAPI(APIView):
    """
    API endpoint for AI chatbot assistance
    Called by Eric's React frontend for taxpayer support
    """
    
    def post(self, request):
        start_time = time.time()
        
        try:
            # Validate input data
            serializer = ChatbotRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid request data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user_query = serializer.validated_data['query']
            conversation_id = serializer.validated_data.get('conversation_id')
            context = serializer.validated_data.get('context', {})
            language = serializer.validated_data.get('language', 'en')
            
            logger.info(f"Processing chatbot query: {user_query[:50]}...")
            
            # Get or create conversation
            if conversation_id:
                try:
                    conversation = ChatbotConversation.objects.get(conversation_id=conversation_id)
                except ChatbotConversation.DoesNotExist:
                    conversation = None
            else:
                conversation = None
            
            if not conversation:
                conversation = ChatbotConversation.objects.create(
                    user_id=context.get('user_id', ''),
                    session_id=context.get('session_id', 'default'),
                    initial_query=user_query,
                    conversation_context=context,
                    language=language
                )
            
            # Save user message
            user_message = ChatMessage.objects.create(
                conversation=conversation,
                message_type='USER',
                message_content=user_query
            )
            
            # Get AI response
            chatbot_response = chatbot_engine.get_response(user_query, context)
            
            # Save bot response
            bot_message = ChatMessage.objects.create(
                conversation=conversation,
                message_type='BOT',
                message_content=chatbot_response['answer'],
                intent_detected=chatbot_response['matched_topic'],
                confidence=chatbot_response['confidence'],
                suggested_actions=chatbot_response['suggestions'],
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
            
            # Update conversation
            conversation.total_messages = ChatMessage.objects.filter(conversation=conversation).count()
            conversation.save()
            
            # Prepare response
            response_data = {
                'success': True,
                'response': chatbot_response['answer'],
                'suggested_questions': chatbot_response['suggestions'],
                'confidence': chatbot_response['confidence'],
                'conversation_id': conversation.conversation_id,
                'processing_time_ms': bot_message.processing_time_ms
            }
            
            logger.info(f"Chatbot response generated with {chatbot_response['confidence']:.2f} confidence")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in chatbot API: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error in chatbot',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RiskAnalysisHistoryAPI(APIView):
    """
    API to retrieve historical risk analysis for a taxpayer
    Called by both frontend and backend for audit purposes
    """
    
    def get(self, request, taxpayer_id):
        try:
            analyses = TaxFilingAnalysis.objects.filter(
                taxpayer_id=taxpayer_id
            ).order_by('-analysis_timestamp')[:10]  # Last 10 analyses
            
            serializer = TaxFilingAnalysisSerializer(analyses, many=True)
            
            return Response({
                'success': True,
                'taxpayer_id': taxpayer_id,
                'analyses': serializer.data,
                'total_count': analyses.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving risk history: {str(e)}")
            return Response({
                'success': False,
                'error': 'Error retrieving risk analysis history'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckAPI(APIView):
    """
    Health check endpoint for integration testing
    Called by Emmanuel's DevOps scripts
    """
    
    def get(self, request):
        try:
            # Test database connection
            analysis_count = TaxFilingAnalysis.objects.count()
            conversation_count = ChatbotConversation.objects.count()
            
            health_status = {
                'status': 'healthy',
                'timestamp': time.time(),
                'database': 'connected',
                'models_loaded': True,
                'analysis_records': analysis_count,
                'conversation_records': conversation_count,
                'service': 'zra-ai-service'
            }
            
            return Response(health_status, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return Response({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# Legacy function-based views for compatibility
@csrf_exempt
@require_http_methods(["POST"])
def analyze_fraud_risk_legacy(request):
    """
    Legacy endpoint for backward compatibility
    """
    try:
        data = json.loads(request.body)
        
        # Convert to new format
        request_data = {
            'filing_data': data.get('filingData', {}),
            'taxpayer_history': data.get('taxpayerHistory', {}),
            'context_data': data.get('contextData', {})
        }
        
        # Use the class-based view logic
        view = FraudDetectionAPI()
        view.request = request._request  # Hack to make it work
        response = view.post(request._request)
        
        return JsonResponse(response.data, status=response.status_code)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_legacy(request):
    """
    Legacy endpoint for backward compatibility
    """
    try:
        data = json.loads(request.body)
        
        # Convert to new format
        request_data = {
            'query': data.get('query', ''),
            'conversation_id': data.get('conversationId'),
            'context': data.get('context', {}),
            'language': data.get('language', 'en')
        }
        
        # Use the class-based view logic
        view = ChatbotAPI()
        view.request = request._request
        response = view.post(request._request)
        
        return JsonResponse(response.data, status=response.status_code)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)