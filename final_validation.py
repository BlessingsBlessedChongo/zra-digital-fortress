#!/usr/bin/env python
"""
Final validation script for ZRA AI Service
Tests all features, performance, and integration points
"""
import os
import sys
import django
import requests
import json
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')
django.setup()

from integration_tests.test_utils import IntegrationTestClient

class FinalValidator:
    """
    Comprehensive validation for production readiness
    """
    
    def __init__(self):
        self.client = IntegrationTestClient()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'service': 'ZRA AI Service',
            'version': '1.0.0',
            'tests': {}
        }
    
    def run_comprehensive_validation(self):
        """Run all validation tests"""
        print("🔍 ZRA AI Service - Final Production Validation")
        print("=" * 60)
        
        self._test_core_functionality()
        self._test_performance()
        self._test_error_handling()
        self._test_integration_points()
        self._test_security()
        self._test_monitoring()
        
        self._generate_validation_report()
    
    def _test_core_functionality(self):
        """Test all core AI functionality"""
        print("\n1. Testing Core Functionality...")
        
        # Test fraud detection with various scenarios
        test_scenarios = [
            {
                'name': 'Low Risk Filing',
                'data': {'income': 50000, 'deductions': 15000, 'business_sector': 'services'},
                'expected_risk': 'LOW'
            },
            {
                'name': 'High Risk Filing', 
                'data': {'income': 10000, 'deductions': 8000, 'business_sector': 'retail'},
                'expected_risk': 'HIGH'
            },
            {
                'name': 'Medium Risk Filing',
                'data': {'income': 30000, 'deductions': 18000, 'business_sector': 'manufacturing'},
                'expected_risk': 'MEDIUM'
            }
        ]
        
        for scenario in test_scenarios:
            result = self.client.test_fraud_detection_integration({
                "filing_data": {
                    "filing_id": f"VALIDATION_{scenario['name'].upper()}",
                    "taxpayer_id": "123456789V",
                    **scenario['data']
                }
            })
            
            actual_risk = result.get('data', {}).get('risk_level', 'UNKNOWN')
            success = actual_risk == scenario['expected_risk']
            
            self.results['tests'][f"fraud_detection_{scenario['name']}"] = {
                'success': success,
                'expected': scenario['expected_risk'],
                'actual': actual_risk,
                'response_time': result.get('data', {}).get('processing_time_ms', 0)
            }
            
            status_icon = "✅" if success else "❌"
            print(f"   {status_icon} {scenario['name']}: {actual_risk} (expected: {scenario['expected_risk']})")
    
    def _test_performance(self):
        """Test performance under load"""
        print("\n2. Testing Performance...")
        
        # Test response times
        endpoints_to_test = [
            ('/api/v1/ai/health', 'GET'),
            ('/api/v1/ai/analyze-fraud', 'POST'),
            ('/api/v1/ai/chatbot', 'POST')
        ]
        
        performance_threshold = 2000  # 2 seconds
        
        for endpoint, method in endpoints_to_test:
            start_time = time.time()
            
            try:
                if method == 'GET':
                    response = self.client.session.get(f"{self.client.base_url}{endpoint}")
                else:
                    # Use simple test data for POST requests
                    test_data = {
                        'filing_data': {'income': 50000, 'deductions': 15000}
                    } if 'analyze-fraud' in endpoint else {
                        'query': 'What is the tax deadline?'
                    }
                    
                    response = self.client.session.post(
                        f"{self.client.base_url}{endpoint}",
                        json=test_data
                    )
                
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                success = response_time < performance_threshold and response.status_code == 200
                
                self.results['tests'][f"performance_{endpoint.split('/')[-1]}"] = {
                    'success': success,
                    'response_time_ms': response_time,
                    'threshold_ms': performance_threshold,
                    'status_code': response.status_code
                }
                
                status_icon = "✅" if success else "⚠️"
                print(f"   {status_icon} {endpoint}: {response_time:.0f}ms (threshold: {performance_threshold}ms)")
                
            except Exception as e:
                self.results['tests'][f"performance_{endpoint.split('/')[-1]}"] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"   ❌ {endpoint}: Failed - {e}")
    
    def _test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n3. Testing Error Handling...")
        
        error_test_cases = [
            {
                'name': 'Invalid JSON',
                'endpoint': '/api/v1/ai/analyze-fraud',
                'data': 'invalid json string',
                'expected_status': 400
            },
            {
                'name': 'Missing Required Fields',
                'endpoint': '/api/v1/ai/analyze-fraud', 
                'data': {},
                'expected_status': 400
            },
            {
                'name': 'Empty Query',
                'endpoint': '/api/v1/ai/chatbot',
                'data': {'query': ''},
                'expected_status': 400
            }
        ]
        
        for test_case in error_test_cases:
            try:
                response = self.client.session.post(
                    f"{self.client.base_url}{test_case['endpoint']}",
                    json=test_case['data'] if isinstance(test_case['data'], dict) else test_case['data'],
                    headers={'Content-Type': 'application/json'}
                )
                
                success = response.status_code == test_case['expected_status']
                
                self.results['tests'][f"error_handling_{test_case['name']}"] = {
                    'success': success,
                    'expected_status': test_case['expected_status'],
                    'actual_status': response.status_code
                }
                
                status_icon = "✅" if success else "❌"
                print(f"   {status_icon} {test_case['name']}: Status {response.status_code} (expected: {test_case['expected_status']})")
                
            except Exception as e:
                self.results['tests'][f"error_handling_{test_case['name']}"] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"   ❌ {test_case['name']}: Failed - {e}")
    
    def _test_integration_points(self):
        """Test integration with other services"""
        print("\n4. Testing Integration Points...")
        
        integration_tests = [
            ('Health Check', '/api/v1/ai/health', 'GET'),
            ('Blockchain Integration', '/api/v1/blockchain/transactions', 'POST'),
            ('Performance Metrics', '/api/v1/ai/performance', 'GET')
        ]
        
        for test_name, endpoint, method in integration_tests:
            try:
                if method == 'GET':
                    response = self.client.session.get(f"{self.client.base_url}{endpoint}")
                else:
                    response = self.client.session.post(
                        f"{self.client.base_url}{endpoint}",
                        json={'test': 'data'}
                    )
                
                success = response.status_code in [200, 201]
                
                self.results['tests'][f"integration_{test_name.lower().replace(' ', '_')}"] = {
                    'success': success,
                    'status_code': response.status_code,
                    'response': response.json() if success else None
                }
                
                status_icon = "✅" if success else "❌"
                print(f"   {status_icon} {test_name}: Status {response.status_code}")
                
            except Exception as e:
                self.results['tests'][f"integration_{test_name.lower().replace(' ', '_')}"] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"   ❌ {test_name}: Failed - {e}")
    
    def _test_security(self):
        """Test security measures"""
        print("\n5. Testing Security...")
        
        security_tests = [
            {
                'name': 'CORS Headers',
                'test': self._test_cors_headers
            },
            {
                'name': 'SQL Injection Protection',
                'test': self._test_sql_injection
            }
        ]
        
        for test in security_tests:
            try:
                result = test['test']()
                self.results['tests'][f"security_{test['name'].lower().replace(' ', '_')}"] = result
                
                status_icon = "✅" if result['success'] else "❌"
                print(f"   {status_icon} {test['name']}: {result.get('message', 'Completed')}")
                
            except Exception as e:
                self.results['tests'][f"security_{test['name'].lower().replace(' ', '_')}"] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"   ❌ {test['name']}: Failed - {e}")
    
    def _test_monitoring(self):
        """Test monitoring and observability"""
        print("\n6. Testing Monitoring...")
        
        try:
            # Test performance metrics endpoint
            response = self.client.session.get(f"{self.client.base_url}/api/v1/ai/performance")
            
            if response.status_code == 200:
                metrics = response.json()
                has_required_metrics = all(
                    key in metrics.get('metrics', {}) 
                    for key in ['system', 'application', 'endpoints']
                )
                
                self.results['tests']['monitoring_performance_metrics'] = {
                    'success': has_required_metrics,
                    'metrics_available': list(metrics.get('metrics', {}).keys())
                }
                
                status_icon = "✅" if has_required_metrics else "⚠️"
                print(f"   {status_icon} Performance Metrics: Available")
            else:
                self.results['tests']['monitoring_performance_metrics'] = {
                    'success': False,
                    'status_code': response.status_code
                }
                print(f"   ❌ Performance Metrics: Status {response.status_code}")
                
        except Exception as e:
            self.results['tests']['monitoring_performance_metrics'] = {
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ Monitoring Tests: Failed - {e}")
    
    def _test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = self.client.session.options(f"{self.client.base_url}/api/v1/ai/health")
        
        has_cors_headers = all(
            header in response.headers
            for header in ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods']
        )
        
        return {
            'success': has_cors_headers,
            'message': 'CORS headers properly configured' if has_cors_headers else 'Missing CORS headers'
        }
    
    def _test_sql_injection(self):
        """Test SQL injection protection"""
        # Test with potential SQL injection in query
        test_data = {
            'query': "'; DROP TABLE users; --"
        }
        
        response = self.client.session.post(
            f"{self.client.base_url}/api/v1/ai/chatbot",
            json=test_data
        )
        
        # Should handle gracefully without database errors
        success = response.status_code in [200, 400]  # Either proper response or bad request
        
        return {
            'success': success,
            'message': 'SQL injection handled properly' if success else 'Potential SQL injection vulnerability'
        }
    
    def _generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "=" * 60)
        print("📊 FINAL VALIDATION REPORT")
        print("=" * 60)
        
        total_tests = len(self.results['tests'])
        passed_tests = sum(1 for test in self.results['tests'].values() if test.get('success'))
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print(f"Validation Timestamp: {self.results['timestamp']}")
        print(f"Service Version: {self.results['version']}")
        
        # Test category summary
        categories = {}
        for test_name, test_result in self.results['tests'].items():
            category = test_name.split('_')[0]
            if category not in categories:
                categories[category] = {'passed': 0, 'total': 0}
            categories[category]['total'] += 1
            if test_result.get('success'):
                categories[category]['passed'] += 1
        
        print("\nCategory Breakdown:")
        for category, stats in categories.items():
            category_rate = (stats['passed'] / stats['total']) * 100
            print(f"  {category.title():<15} {category_rate:>6.1f}% ({stats['passed']}/{stats['total']})")
        
        # Save detailed report
        report_filename = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")
        
        # Final recommendation
        if success_rate >= 90:
            print("\n🎉 PRODUCTION READY: Service passed validation with excellent results!")
            print("   Ready for deployment and integration with other ZRA services.")
        elif success_rate >= 80:
            print("\n⚠️  ACCEPTABLE: Service passed with acceptable results.")
            print("   Some improvements needed before production deployment.")
        else:
            print("\n❌ NOT READY: Service requires significant improvements.")
            print("   Do not deploy to production until issues are resolved.")

def main():
    """Run final validation"""
    validator = FinalValidator()
    validator.run_comprehensive_validation()

if __name__ == "__main__":
    main()