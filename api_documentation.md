# ZRA AI Service API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://ai-service.zra.gov.zm`

## Authentication
Currently uses API key authentication (to be implemented):
Header: X-API-Key: your-api-key


## Endpoints

### AI Service Endpoints

#### 1. Health Check
**GET** `/api/v1/ai/health`

Check service status and database connectivity.

**Response:**

{
  "status": "healthy",
  "timestamp": 1698765432.123,
  "database": "connected",
  "models_loaded": true,
  "analysis_records": 15,
  "conversation_records": 8
}
2. Fraud Detection
POST /api/v1/ai/analyze-fraud

Analyze tax filing for potential fraud patterns.

Request Body:


{
  "filing_data": {
    "filing_id": "FILING_001",
    "taxpayer_id": "123456789A",
    "income": 50000,
    "deductions": 35000,
    "business_sector": "retail",
    "tax_period": "2024-Q1"
  },
  "taxpayer_history": [
    {
      "income": 48000,
      "deductions": 30000,
      "tax_period": "2023-Q4"
    }
  ],
  "context_data": {
    "source": "online_portal"
  }
}
Response:


{
  "success": true,
  "risk_score": 0.65,
  "risk_level": "HIGH",
  "risk_factors": [
    "High deduction ratio (70%) compared to industry average (35%)",
    "Income significantly below industry average"
  ],
  "confidence": 0.82,
  "recommendation": "Manual review recommended - request supporting documents",
  "analysis_id": "1",
  "processing_time_ms": 245
}
3. AI Chatbot
POST /api/v1/ai/chatbot

Get AI-powered responses to tax-related questions.

Request Body:


{
  "query": "What is the tax filing deadline?",
  "conversation_id": "uuid-optional",
  "context": {
    "user_type": "individual",
    "user_id": "123456789A"
  },
  "language": "en"
}
Response:


{
  "success": true,
  "response": "The tax filing deadline for individuals is 30th June each year...",
  "suggested_questions": [
    "What documents do I need?",
    "How to file online?",
    "Late filing penalties?"
  ],
  "confidence": 0.85,
  "conversation_id": "uuid-generated",
  "processing_time_ms": 120
}
4. Risk Analysis History
GET /api/v1/ai/risk-history/{taxpayer_id}

Get historical risk analysis for a taxpayer.

Response:


{
  "success": true,
  "taxpayer_id": "123456789A",
  "analyses": [
    {
      "filing_id": "FILING_001",
      "risk_score": 0.65,
      "risk_level": "HIGH",
      "risk_factors": ["..."],
      "analysis_timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 5
}
Blockchain Service Endpoints
1. Record Transaction
POST /api/v1/blockchain/transactions

Record a transaction on the blockchain simulation.

Request Body:

{
  "reference_id": "FILING_001",
  "transaction_type": "TAX_FILING",
  "transaction_data": {
    "taxpayer_id": "123456789A",
    "income": 50000,
    "tax_due": 7500
  }
}
Response:


{
  "success": true,
  "transaction_hash": "0xZRAABC123DEF456GHI789",
  "transaction": {
    "transaction_hash": "0xZRAABC123DEF456GHI789",
    "reference_id": "FILING_001",
    "transaction_type": "TAX_FILING",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "message": "Transaction recorded on blockchain"
}
2. Verify Transaction
GET /api/v1/blockchain/verify?hash={transaction_hash}

Verify a blockchain transaction.

Response:

{
  "success": true,
  "exists": true,
  "valid": true,
  "transaction": {
    "transaction_hash": "0xZRAABC123DEF456GHI789",
    "reference_id": "FILING_001",
    "status": "CONFIRMED"
  },
  "verification_timestamp": "2024-01-15T10:35:00Z"
}
Integration Examples
Java Backend Integration (Silas)
java
// Fraud detection call
HttpResponse<String> response = HttpClient.newHttpClient().send(
    HttpRequest.newBuilder()
        .uri(URI.create("http://ai-service:8000/api/v1/ai/analyze-fraud"))
        .header("Content-Type", "application/json")
        .POST(HttpRequest.BodyPublishers.ofString(jsonRequest))
        .build(),
    HttpResponse.BodyHandlers.ofString()
);
React Frontend Integration (Eric)
typescript
// Chatbot integration
const response = await fetch('/api/v1/ai/chatbot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        query: userQuestion,
        context: { userType: 'individual' }
    })
});
const data = await response.json();
Error Handling
All endpoints return standardized error responses:

json
{
  "success": false,
  "error": "Error description",
  "details": "Additional error information"
}
Common HTTP Status Codes:

200: Success

400: Bad Request (invalid input)

404: Not Found

500: Internal Server Error

text

## Step 5: Integration Test Scripts

**File: `ai-service/run_integration_tests.py`**
```python
#!/usr/bin/env python
"""
Comprehensive integration test script for ZRA AI Service
"""
import os
import sys
import django
import json
import time
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')
django.setup()

from integration_tests.test_utils import IntegrationTestClient

def main():
    """Run comprehensive integration tests"""
    print("🚀 ZRA AI Service Integration Tests")
    print("=" * 50)
    
    # Initialize test client
    client = IntegrationTestClient("http://localhost:8000")
    
    # Test individual endpoints
    print("\n1. Testing Health Check...")
    health_result = client.test_ai_service_health()
    print_result(health_result)
    
    print("\n2. Testing Fraud Detection...")
    fraud_result = client.test_fraud_detection_integration()
    print_result(fraud_result)
    
    print("\n3. Testing Chatbot...")
    chatbot_result = client.test_chatbot_integration()
    print_result(chatbot_result)
    
    print("\n4. Testing Blockchain...")
    blockchain_result = client.test_blockchain_integration()
    print_result(blockchain_result)
    
    # Test full integration flow
    print("\n5. Testing Full Integration Flow...")
    full_results = client.test_full_integration_flow()
    
    # Generate report
    report = client.generate_integration_report(full_results)
    
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST REPORT")
    print("=" * 50)
    
    print(f"Overall Status: {report['overall_status']}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Service: {report['service']} v{report['version']}")
    
    print("\nDetailed Results:")
    for test_name, test_details in report['test_details'].items():
        status_icon = "✅" if test_details['status'] == 'PASS' else "❌"
        print(f"  {status_icon} {test_name.upper()}: {test_details['status']}")
        if test_details.get('error'):
            print(f"     Error: {test_details['error']}")
    
    # Save report to file
    report_filename = f"integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: {report_filename}")
    
    # Exit with appropriate code
    if report['overall_status'] == 'PASS':
        print("\n🎉 All integration tests PASSED!")
        sys.exit(0)
    else:
        print("\n💥 Some integration tests FAILED!")
        sys.exit(1)

def print_result(result):
    """Print individual test result"""
    status_icon = "✅" if result.get('success') else "❌"
    print(f"  {status_icon} {result.get('endpoint', 'Unknown')}")
    
    if result.get('success'):
        if 'risk_score' in result.get('data', {}):
            print(f"     Risk Score: {result['data']['risk_score']}")
        if 'response' in result.get('data', {}):
            response_preview = result['data']['response'][:80] + "..." if len(result['data']['response']) > 80 else result['data']['response']
            print(f"     Response: {response_preview}")
    else:
        print(f"     Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)