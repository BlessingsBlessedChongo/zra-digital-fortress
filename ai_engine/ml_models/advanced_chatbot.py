import re
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

class AdvancedChatbotEngine:
    """
    Enhanced chatbot with context awareness and external knowledge integration
    """
    
    def __init__(self, knowledge_base_path=None):
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.conversation_memory = {}
        self.external_apis = {
            'tax_calculator': 'http://localhost:8080/api/v1/tax/calculate',
            'taxpayer_info': 'http://localhost:8080/api/v1/taxpayers/'
        }
        
    def _load_knowledge_base(self, path):
        """Load enhanced knowledge base from file or use default"""
        default_kb = {
            'filing': {
                'patterns': [r'file.*tax', r'submit.*return', r'filing.*process'],
                'response': 'You can file taxes online through the ZRA portal. The process involves: 1) Login with TPIN, 2) Select tax type, 3) Enter income and deductions, 4) Review and submit. Would you like me to guide you through any specific step?',
                'actions': ['start_filing', 'show_deadlines'],
                'priority': 1
            },
            'payment': {
                'patterns': [r'how.*pay', r'payment.*methods', r'mobile.*money', r'bank.*transfer'],
                'response': 'ZRA accepts payments through: MTN Mobile Money, Airtel Money, Bank Transfer, and Credit/Debit Cards. You can pay online or at any ZRA office. All online payments receive instant confirmation.',
                'actions': ['show_payment_options', 'calculate_tax'],
                'priority': 1
            },
            'deadlines': {
                'patterns': [r'deadline', r'due date', r'when.*file', r'last date'],
                'response': 'Tax filing deadlines: Individual Income Tax - 30th June, Corporate Tax - 6 months after financial year end, VAT - 21st of following month. Late filing incurs 10% penalty.',
                'actions': ['show_calendar', 'set_reminder'],
                'priority': 2
            },
            'deductions': {
                'patterns': [r'deductions', r'what.*claim', r'allowable.*expenses', r'napsa'],
                'response': 'Allowable deductions include: NAPSA contributions (up to 10% of income), medical expenses, education costs, insurance premiums. You need supporting documents for all claims.',
                'actions': ['calculate_deductions', 'show_limits'],
                'priority': 2
            },
            'registration': {
                'patterns': [r'register', r'tpin', r'new.*taxpayer', r'how.*start'],
                'response': 'To register for a TPIN: Visit any ZRA office with your NRC, proof of address, and business registration (if applicable). Online registration is also available through the ZRA portal.',
                'actions': ['start_registration', 'check_status'],
                'priority': 1
            }
        }
        
        try:
            if path:
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load knowledge base from {path}: {e}")
        
        return default_kb
    
    def get_enhanced_response(self, user_query: str, context: Dict, conversation_id: str = None) -> Dict:
        """
        Get enhanced response with context awareness and external data integration
        """
        try:
            # Update conversation memory
            if conversation_id:
                self._update_conversation_memory(conversation_id, user_query, context)
            
            # Analyze query intent
            intent_analysis = self._analyze_intent(user_query, context)
            
            # Check if we need external data
            enhanced_context = self._enhance_with_external_data(context, intent_analysis)
            
            # Get base response
            base_response = self._get_base_response(user_query, enhanced_context)
            
            # Personalize response
            personalized_response = self._personalize_response(base_response, enhanced_context, intent_analysis)
            
            # Generate follow-up actions
            actions = self._generate_actions(intent_analysis, enhanced_context)
            
            return {
                'answer': personalized_response,
                'suggested_questions': self._generate_suggestions(intent_analysis),
                'actions': actions,
                'confidence': intent_analysis.get('confidence', 0.8),
                'intent': intent_analysis.get('primary_intent'),
                'conversation_id': conversation_id,
                'context_used': enhanced_context.get('context_used', [])
            }
            
        except Exception as e:
            logger.error(f"Enhanced chatbot error: {e}")
            return self._get_fallback_response(user_query)
    
    def _analyze_intent(self, query: str, context: Dict) -> Dict:
        """Advanced intent analysis with multiple intent detection"""
        query_lower = query.lower()
        
        intents = []
        confidence_scores = []
        
        # Check knowledge base for matches
        for topic, data in self.knowledge_base.items():
            for pattern in data['patterns']:
                if re.search(pattern, query_lower):
                    score = len(pattern) / (1 + query_lower.count(' '))  # Simple scoring
                    intents.append({
                        'topic': topic,
                        'type': 'knowledge',
                        'score': score,
                        'priority': data.get('priority', 1),
                        'actions': data.get('actions', [])
                    })
                    confidence_scores.append(score)
        
        # Check for urgency indicators
        urgency_indicators = [r'urgent', r'emergency', r'asap', r'now', r'immediately']
        if any(re.search(indicator, query_lower) for indicator in urgency_indicators):
            intents.append({
                'topic': 'urgent',
                'type': 'urgency',
                'score': 0.9,
                'priority': 0,  # Highest priority
                'actions': ['escalate_to_agent']
            })
        
        # Sort by priority and score
        intents.sort(key=lambda x: (x['priority'], x['score']))
        
        primary_intent = intents[0] if intents else {'topic': 'general', 'type': 'fallback', 'score': 0.1}
        
        return {
            'primary_intent': primary_intent,
            'all_intents': intents,
            'confidence': max(confidence_scores) if confidence_scores else 0.1
        }
    
    def _enhance_with_external_data(self, context: Dict, intent_analysis: Dict) -> Dict:
        """Enhance context with external API data"""
        enhanced_context = context.copy()
        context_used = []
        
        try:
            # If user is authenticated, fetch their data
            user_id = context.get('user_id')
            if user_id and intent_analysis['primary_intent']['topic'] in ['filing', 'payment']:
                # In real implementation, call Silas' backend
                # taxpayer_data = requests.get(f"{self.external_apis['taxpayer_info']}{user_id}").json()
                # enhanced_context['taxpayer_data'] = taxpayer_data
                context_used.append('user_profile')
            
            # If query involves calculations, prepare tax calculation
            if 'calculate' in intent_analysis['primary_intent'].get('actions', []):
                enhanced_context['can_calculate'] = True
                context_used.append('tax_calculation')
                
        except Exception as e:
            logger.warning(f"External data enhancement failed: {e}")
        
        enhanced_context['context_used'] = context_used
        return enhanced_context
    
    def _get_base_response(self, query: str, context: Dict) -> str:
        """Get base response from knowledge base"""
        query_lower = query.lower()
        
        for topic, data in self.knowledge_base.items():
            for pattern in data['patterns']:
                if re.search(pattern, query_lower):
                    return data['response']
        
        # Fallback response
        return "I understand you're asking about taxes. I can help with filing, payments, deadlines, deductions, and registration. Could you please specify what you need help with?"
    
    def _personalize_response(self, base_response: str, context: Dict, intent_analysis: Dict) -> str:
        """Personalize the response based on context"""
        response = base_response
        
        # Add user-specific information if available
        user_type = context.get('user_type')
        if user_type == 'individual':
            response += " As an individual taxpayer, remember to keep your NRC and employment details handy."
        elif user_type == 'business':
            response += " For business taxpayers, ensure you have your business registration documents available."
        
        # Add urgency note if detected
        if intent_analysis['primary_intent']['topic'] == 'urgent':
            response = "🚨 URGENT: " + response + " I've flagged this as urgent for faster processing."
        
        return response
    
    def _generate_actions(self, intent_analysis: Dict, context: Dict) -> List[Dict]:
        """Generate actionable items based on intent"""
        actions = []
        primary_intent = intent_analysis['primary_intent']
        
        base_actions = {
            'start_filing': {'type': 'navigation', 'label': 'Start Tax Filing', 'url': '/file-taxes'},
            'show_payment_options': {'type': 'info', 'label': 'View Payment Methods', 'url': '/payments'},
            'calculate_tax': {'type': 'tool', 'label': 'Use Tax Calculator', 'url': '/calculator'},
            'escalate_to_agent': {'type': 'support', 'label': 'Talk to Human Agent', 'url': '/support'}
        }
        
        for action_key in primary_intent.get('actions', []):
            if action_key in base_actions:
                actions.append(base_actions[action_key])
        
        return actions
    
    def _generate_suggestions(self, intent_analysis: Dict) -> List[str]:
        """Generate context-aware suggested questions"""
        topic = intent_analysis['primary_intent']['topic']
        
        suggestion_map = {
            'filing': ['What documents do I need?', 'How to file online?', 'Filing deadlines?'],
            'payment': ['Payment methods?', 'Mobile money payments?', 'Payment deadlines?'],
            'deadlines': ['Individual deadlines?', 'Business deadlines?', 'Late filing penalties?'],
            'deductions': ['NAPSA contributions?', 'Medical expense claims?', 'Education deductions?'],
            'registration': ['TPIN registration?', 'Business registration?', 'Required documents?'],
            'general': ['Filing process', 'Payment options', 'Registration help', 'Deduction information']
        }
        
        return suggestion_map.get(topic, suggestion_map['general'])
    
    def _update_conversation_memory(self, conversation_id: str, query: str, context: Dict):
        """Update conversation memory for context awareness"""
        if conversation_id not in self.conversation_memory:
            self.conversation_memory[conversation_id] = {
                'start_time': datetime.now(),
                'message_count': 0,
                'topics_discussed': [],
                'user_preferences': {}
            }
        
        memory = self.conversation_memory[conversation_id]
        memory['message_count'] += 1
        memory['last_activity'] = datetime.now()
        
        # Simple topic tracking (in real implementation, use proper NLP)
        if 'file' in query.lower() and 'filing' not in memory['topics_discussed']:
            memory['topics_discussed'].append('filing')
        if 'pay' in query.lower() and 'payment' not in memory['topics_discussed']:
            memory['topics_discussed'].append('payment')
    
    def _get_fallback_response(self, query: str) -> Dict:
        """Get fallback response when errors occur"""
        return {
            'answer': "I'm experiencing some technical difficulties. Please try again in a moment or contact ZRA support for immediate assistance.",
            'suggested_questions': ['Try again', 'Contact support', 'Browse help topics'],
            'actions': [{'type': 'support', 'label': 'Contact Support', 'url': '/support'}],
            'confidence': 0.1,
            'intent': 'error'
        }