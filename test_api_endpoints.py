#!/usr/bin/env python
"""
Test script to verify all AI service API endpoints
"""
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')
django.setup()

BASE_URL = "http://localhost:8000/api/v1"

def test_health_check():
    """Test health check endpoint"""
    print("Testing Health Check...")
    response = requests.get(f"{BASE_URL}/ai/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✓ Health check completed\n")

def test_fraud_detection():
    """Test fraud detection endpoint"""
    print("Testing Fraud Detection...")
    
    test_data = {
        "filing_data": {
            "filing_id": "TEST_001",
            "taxpayer_id": "123456789A",
            "income": 25000,
            "deductions": 18000,
            "business_sector": "retail",
            "tax_period": "2024-Q1"
        },
        "taxpayer_history": [
            {"income": 28000, "deductions": 12000, "tax_period": "2023-Q4"},
            {"income": 26000, "deductions": 11000, "tax_period": "2023-Q3"}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/ai/analyze-fraud",
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Risk Score: {result.get('risk_score')}")
    print(f"Risk Level: {result.get('risk_level')}")
    print(f"Factors: {result.get('risk_factors')}")
    print("✓ Fraud detection test completed\n")

def test_chatbot():
    """Test chatbot endpoint"""
    print("Testing Chatbot...")
    
    test_data = {
        "query": "What is the tax filing deadline?",
        "context": {
            "user_type": "individual",
            "user_id": "123456789A"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/ai/chatbot",
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result.get('response')[:100]}...")
    print(f"Confidence: {result.get('confidence')}")
    print(f"Suggested Questions: {result.get('suggested_questions')}")
    print("✓ Chatbot test completed\n")

def test_blockchain():
    """Test blockchain transaction recording"""
    print("Testing Blockchain...")
    
    test_data = {
        "reference_id": "TEST_FILING_001",
        "transaction_type": "TAX_FILING",
        "transaction_data": {
            "taxpayer_id": "123456789A",
            "income": 25000,
            "tax_due": 3750,
            "filing_period": "2024-Q1"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/blockchain/transactions",
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Transaction Hash: {result.get('transaction_hash')}")
    print(f"Message: {result.get('message')}")
    print("✓ Blockchain test completed\n")

if __name__ == "__main__":
    print("🧪 Testing ZRA AI Service API Endpoints\n")
    
    # Make sure the server is running on localhost:8000
    try:
        test_health_check()
        test_fraud_detection()
        test_chatbot()
        test_blockchain()
        
        print("🎉 All API endpoint tests completed successfully!")
        print("\n📋 Service Endpoints Summary:")
        print("• GET  /api/v1/ai/health - Health check")
        print("• POST /api/v1/ai/analyze-fraud - Fraud detection")
        print("• POST /api/v1/ai/chatbot - AI chatbot")
        print("• GET  /api/v1/ai/risk-history/<taxpayer_id> - Risk history")
        print("• POST /api/v1/blockchain/transactions - Record transactions")
        print("• GET  /api/v1/blockchain/transactions - List transactions")
        print("• GET  /api/v1/blockchain/verify - Verify transactions")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Django server not running. Please run: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error during testing: {e}")