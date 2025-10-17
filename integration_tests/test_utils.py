"""
Integration testing utilities for ZRA Digital Fortress
"""
import requests
import json
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class IntegrationTestClient:
    """
    Client for testing integration with other services
    """
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ZRA-Integration-Test/1.0'
        })
    
    def test_ai_service_health(self):
        """Test AI service health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/ai/health")
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json(),
                'endpoint': '/api/v1/ai/health'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'endpoint': '/api/v1/ai/health'
            }
    
    def test_fraud_detection_integration(self, test_data=None):
        """Test fraud detection with sample data"""
        if test_data is None:
            test_data = {
                "filing_data": {
                    "filing_id": "INTEGRATION_TEST_001",
                    "taxpayer_id": "987654321B",
                    "income": 45000,
                    "deductions": 35000,
                    "business_sector": "services",
                    "tax_period": "2024-Q1",
                    "tax_due": 6500
                },
                "taxpayer_history": [
                    {
                        "income": 42000,
                        "deductions": 28000,
                        "tax_period": "2023-Q4",
                        "tax_due": 5800
                    }
                ],
                "context_data": {
                    "source": "integration_test",
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/analyze-fraud",
                json=test_data
            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json(),
                'endpoint': '/api/v1/ai/analyze-fraud',
                'test_data': test_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'endpoint': '/api/v1/ai/analyze-fraud'
            }
    
    def test_chatbot_integration(self, query="How do I file taxes?"):
        """Test chatbot with common queries"""
        test_data = {
            "query": query,
            "context": {
                "user_type": "individual",
                "session_id": "integration_test_session",
                "source": "integration_test"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/chatbot",
                json=test_data
            )
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json(),
                'endpoint': '/api/v1/ai/chatbot',
                'query': query
            }
            
            # Additional validation for chatbot responses
            if result['success']:
                response_data = result['data']
                result['has_response'] = bool(response_data.get('response'))
                result['has_suggestions'] = bool(response_data.get('suggested_questions'))
                result['confidence'] = response_data.get('confidence', 0)
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'endpoint': '/api/v1/ai/chatbot'
            }
    
    def test_blockchain_integration(self):
        """Test blockchain transaction recording"""
        test_data = {
            "reference_id": f"BLOCKCHAIN_TEST_{int(time.time())}",
            "transaction_type": "TAX_FILING",
            "transaction_data": {
                "taxpayer_id": "987654321B",
                "filing_id": "INTEGRATION_TEST_001",
                "income": 45000,
                "tax_due": 6500,
                "filing_period": "2024-Q1",
                "submission_timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/blockchain/transactions",
                json=test_data
            )
            
            result = {
                'success': response.status_code == 201,
                'status_code': response.status_code,
                'data': response.json(),
                'endpoint': '/api/v1/blockchain/transactions'
            }
            
            # Verify transaction was created
            if result['success']:
                transaction_hash = result['data'].get('transaction_hash')
                if transaction_hash:
                    # Test verification endpoint
                    verify_response = self.session.get(
                        f"{self.base_url}/api/v1/blockchain/verify",
                        params={'hash': transaction_hash}
                    )
                    result['verification'] = {
                        'success': verify_response.status_code == 200,
                        'data': verify_response.json()
                    }
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'endpoint': '/api/v1/blockchain/transactions'
            }
    
    def test_full_integration_flow(self):
        """Test complete integration flow: Fraud detection → Blockchain → Chatbot"""
        results = {}
        
        logger.info("Starting full integration flow test...")
        
        # 1. Test fraud detection
        results['fraud_detection'] = self.test_fraud_detection_integration()
        
        # 2. Test blockchain recording
        results['blockchain'] = self.test_blockchain_integration()
        
        # 3. Test chatbot assistance
        results['chatbot'] = self.test_chatbot_integration()
        
        # 4. Test health endpoint
        results['health'] = self.test_ai_service_health()
        
        # Calculate overall success
        results['overall_success'] = all(
            result['success'] for result in results.values() 
            if isinstance(result, dict) and 'success' in result
        )
        
        logger.info(f"Integration flow test completed: {results['overall_success']}")
        return results
    
    def generate_integration_report(self, results):
        """Generate a detailed integration test report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'service': 'ZRA AI Service',
            'version': '1.0.0',
            'overall_status': 'PASS' if results.get('overall_success') else 'FAIL',
            'test_details': {}
        }
        
        for test_name, test_result in results.items():
            if test_name != 'overall_success':
                report['test_details'][test_name] = {
                    'status': 'PASS' if test_result.get('success') else 'FAIL',
                    'endpoint': test_result.get('endpoint', 'Unknown'),
                    'status_code': test_result.get('status_code'),
                    'response_time': test_result.get('response_time'),
                    'details': test_result.get('data', {}),
                    'error': test_result.get('error')
                }
        
        return report