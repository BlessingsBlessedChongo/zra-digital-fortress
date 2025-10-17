import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatbotEngine:
    """
    Rule-based chatbot engine for tax assistance
    Uses pattern matching for common tax questions
    """
    
    def __init__(self):
        self.knowledge_base = self._initialize_knowledge_base()
        self.greeting_patterns = [
            r'hello', r'hi', r'hey', r'good morning', r'good afternoon'
        ]
        self.farewell_patterns = [
            r'bye', r'goodbye', r'thank you', r'thanks', r'see you'
        ]
    
    def _initialize_knowledge_base(self):
        """Initialize the tax knowledge base with common questions"""
        return {
            'filing_deadline': {
                'patterns': [r'deadline', r'when.*file', r'due date', r'last date'],
                'response': 'The tax filing deadline for individuals is 30th June each year. For businesses, it depends on your financial year end.',
                'suggestions': ['What documents do I need?', 'How to file online?', 'Late filing penalties?']
            },
            'documents_required': {
                'patterns': [r'documents', r'what.*need', r'papers', r'requirements'],
                'response': 'For individual tax filing, you typically need: NRC, employment certificate, proof of deductions (NAPSA, medical, education), and bank statements.',
                'suggestions': ['Income tax rates?', 'Deduction limits?', 'How to claim expenses?']
            },
            'income_tax_rates': {
                'patterns': [r'tax rates', r'how much tax', r'income tax', r'tax brackets'],
                'response': 'Individual income tax rates in Zambia: 0% up to ZMW 4,800, 25% from ZMW 4,801-7,200, and 30% above ZMW 7,200.',
                'suggestions': ['Tax calculator', 'Deduction information', 'Filing process']
            },
            'deductions': {
                'patterns': [r'deductions', r'what.*claim', r'expenses', r'allowable'],
                'response': 'You can claim deductions for: NAPSA contributions (up to 10% of income), medical expenses, education costs, and insurance premiums. Keep receipts for verification.',
                'suggestions': ['NAPSA contribution limits', 'Medical expense claims', 'Education deductions']
            },
            'vat_information': {
                'patterns': [r'vat', r'value added tax', r'vat rate', r'vat registration'],
                'response': 'VAT rate in Zambia is 16%. Registration is required if your annual turnover exceeds ZMW 800,000. VAT returns are filed monthly or quarterly.',
                'suggestions': ['VAT filing process', 'VAT exemptions', 'Input VAT claims']
            },
            'payment_methods': {
                'patterns': [r'how.*pay', r'payment methods', r'mobile money', r'bank transfer'],
                'response': 'You can pay taxes through: MTN Mobile Money, Airtel Money, bank transfers, or at any ZRA office. Online payments are instant and secure.',
                'suggestions': ['Payment deadlines', 'Payment receipts', 'Failed payments']
            },
            'registration': {
                'patterns': [r'how.*register', r'get tpin', r'taxpayer number', r'new taxpayer'],
                'response': 'You can register for a TPIN online through the ZRA portal. You will need your NRC, contact details, and business information if applicable.',
                'suggestions': ['TPIN lookup', 'Business registration', 'Individual registration']
            },
            'penalties': {
                'patterns': [r'penalties', r'late filing', r'late payment', r'fines'],
                'response': 'Late filing penalty is 10% of tax due. Late payment interest is 5% per month. It is better to file on time even if you cannot pay immediately.',
                'suggestions': ['Penalty appeal process', 'Payment plans', 'Compliance certificates']
            }
        }
    
    def get_response(self, user_query, context=None):
        """
        Generate response to user query
        
        Args:
            user_query: User's question
            context: Conversation context (user type, history, etc.)
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            user_query = user_query.lower().strip()
            
            # Check for greetings
            if any(re.search(pattern, user_query) for pattern in self.greeting_patterns):
                return self._generate_greeting_response(context)
            
            # Check for farewells
            if any(re.search(pattern, user_query) for pattern in self.farewell_patterns):
                return self._generate_farewell_response()
            
            # Search knowledge base for matching topics
            matched_topic = self._find_matching_topic(user_query)
            
            if matched_topic:
                confidence = 0.85
                response = matched_topic['response']
                suggestions = matched_topic['suggestions']
            else:
                confidence = 0.3
                response = "I'm here to help with tax-related questions. You can ask me about filing deadlines, tax rates, deductions, VAT, payments, or registration. Could you please rephrase your question?"
                suggestions = ['Filing deadlines', 'Tax rates', 'Deduction information', 'Payment methods']
            
            # Personalize response based on context
            if context and context.get('user_type'):
                user_type = context['user_type']
                if user_type == 'individual':
                    response = self._personalize_for_individual(response)
                elif user_type == 'business':
                    response = self._personalize_for_business(response)
            
            return {
                'answer': response,
                'suggestions': suggestions,
                'confidence': confidence,
                'matched_topic': matched_topic['topic'] if matched_topic else 'general'
            }
            
        except Exception as e:
            logger.error(f"Error in chatbot response: {str(e)}")
            return {
                'answer': "I'm experiencing technical difficulties. Please try again or contact ZRA support for immediate assistance.",
                'suggestions': ['Try again', 'Contact support', 'Browse help topics'],
                'confidence': 0.0,
                'matched_topic': 'error'
            }
    
    def _find_matching_topic(self, user_query):
        """Find the best matching topic in knowledge base"""
        best_match = None
        highest_score = 0
        
        for topic, data in self.knowledge_base.items():
            for pattern in data['patterns']:
                if re.search(pattern, user_query):
                    # Simple scoring: use the first match for now
                    score = len(pattern)  # Longer patterns might be more specific
                    if score > highest_score:
                        highest_score = score
                        best_match = {
                            'topic': topic,
                            'response': data['response'],
                            'suggestions': data['suggestions']
                        }
                    break
        
        return best_match
    
    def _generate_greeting_response(self, context):
        """Generate greeting response based on time of day"""
        current_hour = datetime.now().hour
        
        if current_hour < 12:
            greeting = "Good morning! I'm your ZRA assistant."
        elif current_hour < 18:
            greeting = "Good afternoon! I'm here to help with your tax questions."
        else:
            greeting = "Good evening! I'm your ZRA assistant."
        
        response = f"{greeting} How can I help you with taxes today? You can ask me about filing, payments, deductions, or deadlines."
        
        return {
            'answer': response,
            'suggestions': ['Filing deadlines', 'Tax rates', 'Payment methods', 'Registration'],
            'confidence': 0.95,
            'matched_topic': 'greeting'
        }
    
    def _generate_farewell_response(self):
        """Generate farewell response"""
        response = "You're welcome! Remember to file your taxes by the 30th of June. Feel free to ask if you have more questions. Have a great day!"
        
        return {
            'answer': response,
            'suggestions': [],
            'confidence': 0.9,
            'matched_topic': 'farewell'
        }
    
    def _personalize_for_individual(self, response):
        """Personalize response for individual taxpayers"""
        # Add individual-specific context if needed
        if 'individual' not in response.lower():
            response += " As an individual taxpayer, make sure you have your NRC and employment details ready."
        return response
    
    def _personalize_for_business(self, response):
        """Personalize response for business taxpayers"""
        # Add business-specific context if needed
        if 'business' not in response.lower():
            response += " For businesses, remember to maintain proper records and consider VAT registration if your turnover exceeds ZMW 800,000."
        return response