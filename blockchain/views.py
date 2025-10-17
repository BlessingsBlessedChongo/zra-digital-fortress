from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import BlockchainTransaction, SmartContract
from .serializers import BlockchainTransactionSerializer, TransactionCreateSerializer

class BlockchainTransactionAPI(APIView):
    """
    API for recording transactions on the blockchain simulation
    """
    
    def post(self, request):
        try:
            serializer = TransactionCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid transaction data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create blockchain transaction
            transaction = serializer.save()
            
            # Serialize for response
            transaction_data = BlockchainTransactionSerializer(transaction).data
            
            return Response({
                'success': True,
                'transaction_hash': transaction.transaction_hash,
                'transaction': transaction_data,
                'message': 'Transaction recorded on blockchain'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to record transaction: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request, transaction_hash=None):
        try:
            if transaction_hash:
                # Get specific transaction
                transaction = BlockchainTransaction.objects.get(transaction_hash=transaction_hash)
                serializer = BlockchainTransactionSerializer(transaction)
                return Response({
                    'success': True,
                    'transaction': serializer.data
                })
            else:
                # List recent transactions
                transactions = BlockchainTransaction.objects.all().order_by('-timestamp')[:50]
                serializer = BlockchainTransactionSerializer(transactions, many=True)
                return Response({
                    'success': True,
                    'transactions': serializer.data,
                    'total_count': transactions.count()
                })
                
        except BlockchainTransaction.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Transaction not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyTransactionAPI(APIView):
    """
    API for verifying blockchain transactions
    """
    
    def get(self, request):
        transaction_hash = request.GET.get('hash')
        reference_id = request.GET.get('reference_id')
        
        try:
            if transaction_hash:
                transaction = BlockchainTransaction.objects.get(transaction_hash=transaction_hash)
            elif reference_id:
                transaction = BlockchainTransaction.objects.filter(reference_id=reference_id).first()
            else:
                return Response({
                    'success': False,
                    'error': 'Must provide either transaction_hash or reference_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not transaction:
                return Response({
                    'success': False,
                    'error': 'Transaction not found',
                    'exists': False
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verify transaction integrity (simplified for demo)
            is_valid = (
                transaction.transaction_hash.startswith('0xZRA') and
                len(transaction.transaction_hash) == 28 and
                transaction.status == 'CONFIRMED'
            )
            
            serializer = BlockchainTransactionSerializer(transaction)
            
            return Response({
                'success': True,
                'exists': True,
                'valid': is_valid,
                'transaction': serializer.data,
                'verification_timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
def record_transaction_legacy(request):
    """
    Legacy endpoint for recording transactions
    """
    try:
        data = json.loads(request.body)
        
        # Create transaction using the modern API logic
        view = BlockchainTransactionAPI()
        view.request = request._request
        response = view.post(request._request)
        
        return JsonResponse(response.data, status=response.status_code)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)