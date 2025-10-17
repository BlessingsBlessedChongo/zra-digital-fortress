from django.urls import path
from . import views

urlpatterns = [
    # Modern API endpoints
    path('transactions', views.BlockchainTransactionAPI.as_view(), name='transactions'),
    path('transactions/<str:transaction_hash>', views.BlockchainTransactionAPI.as_view(), name='transaction_detail'),
    path('verify', views.VerifyTransactionAPI.as_view(), name='verify_transaction'),
    
    # Legacy endpoints
    path('record', views.record_transaction_legacy, name='record_transaction_legacy'),
]