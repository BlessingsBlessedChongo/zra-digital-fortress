import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import logging
import os
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class AdvancedFraudDetector:
    """
    Advanced fraud detection using machine learning ensemble
    Combines rule-based and ML approaches for better accuracy
    """
    
    def __init__(self, model_path=None):
        self.model_path = model_path or 'ai_engine/ml_models/saved_models/'
        self.rule_based_detector = None  # Would be our previous detector
        self.ml_model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'income', 'deductions', 'deduction_ratio', 'income_industry_deviation',
            'historical_income_change', 'round_number_count', 'filing_timing_score'
        ]
        
        # Load or initialize model
        self._load_or_initialize_model()
    
    def _load_or_initialize_model(self):
        """Load saved model or initialize new one"""
        model_file = os.path.join(self.model_path, 'fraud_classifier.joblib')
        scaler_file = os.path.join(self.model_path, 'scaler.joblib')
        
        try:
            if os.path.exists(model_file) and os.path.exists(scaler_file):
                self.ml_model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                logger.info("Loaded pre-trained fraud detection model")
            else:
                self._initialize_new_model()
                logger.info("Initialized new fraud detection model")
        except Exception as e:
            logger.warning(f"Failed to load model, initializing new: {e}")
            self._initialize_new_model()
    
    def _initialize_new_model(self):
        """Initialize a new ML model with demo data"""
        # Create a simple Random Forest classifier
        self.ml_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        # Train with demo data (in real scenario, this would be historical data)
        demo_features, demo_labels = self._generate_demo_training_data()
        self.ml_model.fit(demo_features, demo_labels)
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.ml_model, os.path.join(self.model_path, 'fraud_classifier.joblib'))
        joblib.dump(self.scaler, os.path.join(self.model_path, 'scaler.joblib'))
    
    def _generate_demo_training_data(self):
        """Generate demo training data for the model"""
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [income, deductions, deduction_ratio, income_industry_deviation, 
        #           historical_income_change, round_number_count, filing_timing_score]
        features = []
        labels = []
        
        for i in range(n_samples):
            # Generate realistic features
            income = np.random.lognormal(10.5, 0.8)  # Log-normal distribution
            deductions = income * np.random.beta(2, 5)  # Most have low deductions
            
            # Create some fraudulent patterns
            is_fraud = np.random.random() < 0.1  # 10% fraud rate in demo data
            
            if is_fraud:
                # Fraud patterns: high deductions, low income, round numbers
                deductions = income * np.random.beta(5, 2)  # High deduction ratio
                if np.random.random() < 0.3:
                    income = np.round(income / 1000) * 1000  # Round numbers
                
                income_industry_deviation = np.random.normal(-0.5, 0.2)  # Low income
                historical_change = np.random.normal(-0.3, 0.3)  # Significant drops
                round_count = np.random.randint(2, 4)
                timing_score = np.random.uniform(0.7, 1.0)  # Unusual timing
            else:
                # Normal patterns
                income_industry_deviation = np.random.normal(0, 0.1)
                historical_change = np.random.normal(0, 0.1)
                round_count = np.random.randint(0, 2)
                timing_score = np.random.uniform(0, 0.3)
            
            deduction_ratio = deductions / income if income > 0 else 0
            
            feature_vector = [
                np.log1p(income),  # Log transform for normality
                np.log1p(deductions),
                deduction_ratio,
                income_industry_deviation,
                historical_change,
                round_count,
                timing_score
            ]
            
            features.append(feature_vector)
            labels.append(1 if is_fraud else 0)
        
        features = np.array(features)
        labels = np.array(labels)
        
        # Scale features
        features = self.scaler.fit_transform(features)
        
        return features, labels
    
    def extract_features(self, filing_data, taxpayer_history=None):
        """Extract features for ML model from filing data"""
        income = filing_data.get('income', 0)
        deductions = filing_data.get('deductions', 0)
        business_sector = filing_data.get('business_sector', 'services')
        
        # Calculate features
        deduction_ratio = deductions / income if income > 0 else 0
        
        # Industry deviation (simplified)
        industry_averages = {'retail': 50000, 'services': 60000, 'manufacturing': 70000}
        industry_avg = industry_averages.get(business_sector, 50000)
        income_industry_deviation = (income - industry_avg) / industry_avg if industry_avg > 0 else 0
        
        # Historical consistency
        historical_income_change = 0
        if taxpayer_history and len(taxpayer_history) > 0:
            prev_incomes = [f.get('income', 0) for f in taxpayer_history if f.get('income', 0) > 0]
            if prev_incomes:
                avg_historical = np.mean(prev_incomes)
                historical_income_change = (income - avg_historical) / avg_historical if avg_historical > 0 else 0
        
        # Round number analysis
        def is_round_number(num):
            return num % 1000 == 0 or num % 5000 == 0
        
        round_number_count = sum([
            is_round_number(income),
            is_round_number(deductions),
            is_round_number(income - deductions)
        ])
        
        # Filing timing (simplified)
        filing_timing_score = 0.1  # Default normal timing
        
        features = [
            np.log1p(income),
            np.log1p(deductions),
            deduction_ratio,
            income_industry_deviation,
            historical_income_change,
            round_number_count,
            filing_timing_score
        ]
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, filing_data, taxpayer_history=None):
        """Predict fraud probability using ML model"""
        try:
            # Extract features
            features = self.extract_features(filing_data, taxpayer_history)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get prediction probabilities
            fraud_probability = self.ml_model.predict_proba(features_scaled)[0][1]
            
            # Get feature importance for explanation
            feature_importance = dict(zip(
                self.feature_names,
                self.ml_model.feature_importances_
            ))
            
            return {
                'fraud_probability': float(fraud_probability),
                'prediction': fraud_probability > 0.5,
                'feature_importance': feature_importance,
                'model_confidence': float(np.max(self.ml_model.predict_proba(features_scaled)[0]))
            }
            
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return {
                'fraud_probability': 0.0,
                'prediction': False,
                'feature_importance': {},
                'model_confidence': 0.0,
                'error': str(e)
            }
    
    def ensemble_predict(self, filing_data, taxpayer_history=None, rule_based_score=0.0):
        """
        Combine ML and rule-based predictions for better accuracy
        """
        ml_result = self.predict(filing_data, taxpayer_history)
        
        # Ensemble weighting: 70% ML, 30% rule-based
        ml_weight = 0.7
        rule_weight = 0.3
        
        ensemble_score = (
            ml_result['fraud_probability'] * ml_weight +
            rule_based_score * rule_weight
        )
        
        return {
            'ensemble_score': ensemble_score,
            'ml_score': ml_result['fraud_probability'],
            'rule_based_score': rule_based_score,
            'final_prediction': ensemble_score > 0.6,  # Higher threshold for ensemble
            'ml_confidence': ml_result['model_confidence'],
            'feature_importance': ml_result['feature_importance']
        }