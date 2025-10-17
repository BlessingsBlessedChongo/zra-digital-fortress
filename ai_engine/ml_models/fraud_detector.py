import numpy as np
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FraudDetector:
    """
    Simplified fraud detection engine for tax data
    Uses rule-based system with some ML concepts for demo
    """
    
    def __init__(self):
        self.industry_averages = {
            'retail': {'income_ratio': 1.0, 'deduction_ratio': 0.35},
            'manufacturing': {'income_ratio': 1.0, 'deduction_ratio': 0.28},
            'services': {'income_ratio': 1.0, 'deduction_ratio': 0.42},
            'construction': {'income_ratio': 1.0, 'deduction_ratio': 0.38},
            'agriculture': {'income_ratio': 1.0, 'deduction_ratio': 0.32}
        }
        
        self.risk_weights = {
            'income_deviation': 0.3,
            'deduction_ratio': 0.25,
            'historical_inconsistency': 0.2,
            'round_numbers': 0.15,
            'unusual_timing': 0.1
        }
    
    def analyze(self, filing_data, taxpayer_history=None):
        """
        Analyze tax filing for potential fraud patterns
        
        Args:
            filing_data: Dictionary containing tax filing information
            taxpayer_history: Previous filings for this taxpayer (optional)
        
        Returns:
            Dictionary with risk analysis results
        """
        try:
            logger.info(f"Analyzing filing: {filing_data.get('filing_id', 'Unknown')}")
            
            # Extract key data with defaults
            income = filing_data.get('income', 0)
            deductions = filing_data.get('deductions', 0)
            business_sector = filing_data.get('business_sector', 'services').lower()
            tax_period = filing_data.get('tax_period', '')
            
            # Calculate basic metrics
            deduction_ratio = deductions / income if income > 0 else 0
            taxable_income = income - deductions
            
            # Risk factor analysis
            risk_factors = []
            risk_score = 0.0
            
            # 1. Income deviation from industry average
            industry_risk = self._check_industry_deviation(income, business_sector, taxpayer_history)
            if industry_risk['risk'] > 0:
                risk_factors.append(industry_risk['reason'])
                risk_score += industry_risk['risk'] * self.risk_weights['income_deviation']
            
            # 2. Deduction ratio analysis
            deduction_risk = self._check_deduction_ratio(deduction_ratio, business_sector)
            if deduction_risk['risk'] > 0:
                risk_factors.append(deduction_risk['reason'])
                risk_score += deduction_risk['risk'] * self.risk_weights['deduction_ratio']
            
            # 3. Historical consistency
            if taxpayer_history:
                history_risk = self._check_historical_consistency(filing_data, taxpayer_history)
                if history_risk['risk'] > 0:
                    risk_factors.append(history_risk['reason'])
                    risk_score += history_risk['risk'] * self.risk_weights['historical_inconsistency']
            
            # 4. Round number analysis
            round_risk = self._check_round_numbers(income, deductions, taxable_income)
            if round_risk['risk'] > 0:
                risk_factors.append(round_risk['reason'])
                risk_score += round_risk['risk'] * self.risk_weights['round_numbers']
            
            # 5. Timing analysis
            timing_risk = self._check_filing_timing(tax_period)
            if timing_risk['risk'] > 0:
                risk_factors.append(timing_risk['reason'])
                risk_score += timing_risk['risk'] * self.risk_weights['unusual_timing']
            
            # Cap risk score at 1.0
            risk_score = min(risk_score, 1.0)
            
            # Determine risk level
            risk_level = self._get_risk_level(risk_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_level, risk_factors)
            
            # Calculate confidence (simplified)
            confidence = max(0.7, 1.0 - (len(risk_factors) * 0.05))
            
            return {
                'score': risk_score,
                'level': risk_level,
                'factors': risk_factors,
                'recommendation': recommendations,
                'confidence': confidence,
                'detailed_analysis': {
                    'deduction_ratio': deduction_ratio,
                    'taxable_income': taxable_income,
                    'industry_comparison': industry_risk,
                    'factors_breakdown': {
                        'income_deviation': industry_risk['risk'],
                        'deduction_ratio': deduction_risk['risk'],
                        'historical_inconsistency': history_risk.get('risk', 0) if taxpayer_history else 0,
                        'round_numbers': round_risk['risk'],
                        'unusual_timing': timing_risk['risk']
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error in fraud analysis: {str(e)}")
            return {
                'score': 0.0,
                'level': 'LOW',
                'factors': ['Analysis error'],
                'recommendation': 'Manual review required due to analysis error',
                'confidence': 0.0,
                'detailed_analysis': {'error': str(e)}
            }
    
    def _check_industry_deviation(self, income, business_sector, history):
        """Check if income significantly deviates from industry average"""
        sector_data = self.industry_averages.get(business_sector, self.industry_averages['services'])
        
        # Simple heuristic: very low income relative to typical business
        if income < 10000:  # Unrealistically low for most businesses
            return {
                'risk': 0.8,
                'reason': f"Income (ZMW {income:,.0f}) significantly below typical {business_sector} business levels"
            }
        elif income < 25000:
            return {
                'risk': 0.4,
                'reason': f"Income below average for {business_sector} sector"
            }
        
        return {'risk': 0.0, 'reason': ''}
    
    def _check_deduction_ratio(self, deduction_ratio, business_sector):
        """Check if deduction ratio is suspiciously high"""
        sector_data = self.industry_averages.get(business_sector, self.industry_averages['services'])
        typical_ratio = sector_data['deduction_ratio']
        
        if deduction_ratio > 0.7:
            return {
                'risk': 0.9,
                'reason': f"Deductions represent {deduction_ratio:.1%} of income (typical: {typical_ratio:.1%})"
            }
        elif deduction_ratio > 0.5:
            return {
                'risk': 0.6,
                'reason': f"High deduction ratio ({deduction_ratio:.1%}) compared to industry average ({typical_ratio:.1%})"
            }
        elif deduction_ratio > typical_ratio + 0.1:
            return {
                'risk': 0.3,
                'reason': f"Above average deduction ratio for {business_sector} sector"
            }
        
        return {'risk': 0.0, 'reason': ''}
    
    def _check_historical_consistency(self, current_filing, history):
        """Check for inconsistencies with historical filing patterns"""
        if not history or len(history) == 0:
            return {'risk': 0.0, 'reason': ''}
        
        current_income = current_filing.get('income', 0)
        historical_incomes = [f.get('income', 0) for f in history if f.get('income', 0) > 0]
        
        if not historical_incomes:
            return {'risk': 0.0, 'reason': ''}
        
        avg_historical = np.mean(historical_incomes)
        
        if avg_historical > 0:
            deviation = abs(current_income - avg_historical) / avg_historical
            
            if deviation > 0.5:  # 50% deviation
                return {
                    'risk': 0.7,
                    'reason': f"Income deviates {deviation:.1%} from historical average"
                }
            elif deviation > 0.3:
                return {
                    'risk': 0.4,
                    'reason': f"Significant income change from historical pattern"
                }
        
        return {'risk': 0.0, 'reason': ''}
    
    def _check_round_numbers(self, income, deductions, taxable_income):
        """Check for suspicious round numbers that might indicate estimation"""
        def is_round_number(num):
            return num % 1000 == 0 or num % 5000 == 0
        
        round_count = sum([
            is_round_number(income),
            is_round_number(deductions),
            is_round_number(taxable_income)
        ])
        
        if round_count >= 2:
            return {
                'risk': 0.5,
                'reason': "Multiple round numbers suggest estimated figures"
            }
        elif round_count == 1:
            return {
                'risk': 0.2,
                'reason': "Some figures appear rounded"
            }
        
        return {'risk': 0.0, 'reason': ''}
    
    def _check_filing_timing(self, tax_period):
        """Check if filing timing is unusual"""
        # For demo, consider very early or very late filings as slightly suspicious
        try:
            if tax_period:
                # Simple check - if it's extremely early (first week) or late (last day)
                if "early" in tax_period.lower() or "delay" in tax_period.lower():
                    return {
                        'risk': 0.3,
                        'reason': "Unusual filing timing pattern"
                    }
        except:
            pass
        
        return {'risk': 0.0, 'reason': ''}
    
    def _get_risk_level(self, risk_score):
        """Convert numerical risk score to categorical level"""
        if risk_score >= 0.7:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendations(self, risk_level, risk_factors):
        """Generate appropriate recommendations based on risk level"""
        base_recommendations = {
            'LOW': 'Standard processing - no additional review required',
            'MEDIUM': 'Consider automated verification checks',
            'HIGH': 'Manual review recommended - request supporting documents'
        }
        
        recommendation = base_recommendations.get(risk_level, 'Review required')
        
        # Add specific actions based on risk factors
        if any('deduction' in factor.lower() for factor in risk_factors):
            recommendation += ' | Verify deduction documentation'
        if any('income' in factor.lower() for factor in risk_factors):
            recommendation += ' | Cross-reference with third-party data'
        
        return recommendation