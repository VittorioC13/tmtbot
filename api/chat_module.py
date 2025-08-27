"""
TMT Bot Chat Module - Integrated LLM Chat Feature
This module integrates the chat feature directly into the dashboard for seamless UX.
"""

import os
import json
import openai
from datetime import datetime
from typing import List, Dict, Optional
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

# Create a Blueprint for the chat feature
chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# In-memory storage for chat messages (can be replaced with database later)
chat_messages = []

class ChatMessage:
    def __init__(self, user_id: int, message: str, response: str, sector: str = None):
        self.user_id = user_id
        self.message = message
        self.response = response
        self.timestamp = datetime.utcnow()
        self.sector = sector

class LLMService:
    def __init__(self):
        # Try to get API key from environment
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            # Fallback to a demo mode
            self.demo_mode = True
            print("⚠️  OPENAI_API_KEY not found. Running in demo mode.")
        else:
            self.demo_mode = False
            self.client = openai.OpenAI(api_key=api_key)
    
    def get_context_for_sector(self, sector: str) -> str:
        """Get relevant context for the user's selected sector"""
        if sector == 'TMT':
            return """You are an expert TMT (Technology, Media, and Telecommunications) analyst. 
            You have deep knowledge of tech trends, M&A activities, market analysis, and investment banking in the TMT sector.
            You can discuss deals, market trends, career advice for investment banking, and technical analysis.
            Be conversational, helpful, and provide specific insights about the TMT sector."""
        elif sector == 'Energy':
            return """You are an expert Energy sector analyst. 
            You have deep knowledge of energy markets, renewable energy trends, oil & gas, and investment banking in the energy sector.
            You can discuss deals, market trends, career advice for investment banking, and technical analysis.
            Be conversational, helpful, and provide specific insights about the Energy sector."""
        else:
            return """You are an expert investment banking analyst with broad market knowledge.
            You can discuss deals, market trends, career advice for investment banking, and technical analysis across various sectors.
            Be conversational, helpful, and provide specific insights."""
    
    def generate_demo_response(self, user_message: str, sector: str) -> str:
        """Generate demo responses when API key is not available"""
        demo_responses = {
            'TMT': [
                "Based on today's TMT sector analysis, I can see significant M&A activity in the software space. The recent deal between TechCorp and DataFlow shows a clear trend toward AI integration in enterprise solutions.",
                "The TMT sector is experiencing strong growth in cloud computing and cybersecurity. Companies are increasingly focusing on digital transformation initiatives.",
                "From an investment banking perspective, the TMT sector offers excellent opportunities in fintech and digital payments. The regulatory environment is becoming more favorable for tech companies.",
                "Looking at recent TMT deals, we're seeing a surge in AI and machine learning acquisitions. Companies are positioning themselves for the next wave of technological innovation.",
                "The TMT sector's valuation multiples remain attractive despite market volatility. This presents opportunities for strategic acquisitions and investments."
            ],
            'Energy': [
                "The energy sector is showing interesting developments in renewable energy investments. Solar and wind projects are attracting significant capital from institutional investors.",
                "Oil prices remain volatile, but the transition to clean energy is creating new opportunities in battery storage and hydrogen technologies.",
                "Energy M&A activity is picking up, particularly in the midstream sector. Infrastructure investments are becoming increasingly attractive to private equity firms.",
                "The energy transition is accelerating, with major oil companies diversifying into renewable energy. This creates unique investment opportunities.",
                "Energy storage solutions are becoming a key focus area for investors, with battery technology and grid infrastructure seeing increased deal flow."
            ],
            'default': [
                "I can provide insights on market trends, deal analysis, and investment banking topics. What specific area would you like to discuss?",
                "The current market environment presents interesting opportunities across various sectors. Would you like to discuss any particular deals or trends?",
                "From an investment banking perspective, I can help you understand deal structures, valuation methods, and market dynamics.",
                "Market analysis shows interesting patterns across different sectors. What specific insights are you looking for?",
                "I can help you understand the latest market trends and their implications for investment strategies."
            ]
        }
        
        import random
        responses = demo_responses.get(sector, demo_responses['default'])
        return random.choice(responses)
    
    def generate_response(self, user_message: str, user_sector: str = None, chat_history: List[Dict] = None) -> str:
        """Generate AI response based on user message and context"""
        
        if self.demo_mode:
            return self.generate_demo_response(user_message, user_sector or 'TMT')
        
        # Build system prompt
        system_prompt = self.get_context_for_sector(user_sector or 'TMT')
        system_prompt += """
        
        Instructions:
        - Be conversational and helpful
        - Provide specific, actionable insights
        - Reference current market trends when relevant
        - If asked about deals, provide detailed analysis
        - For career questions, give practical investment banking advice
        - Keep responses concise but informative (2-3 sentences)
        - If you don't know something, be honest about it
        - Focus on the user's selected sector when relevant
        """
        
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history if provided
        if chat_history:
            for msg in chat_history[-10:]:  # Last 10 messages for context
                messages.append({"role": "user", "content": msg['message']})
                messages.append({"role": "assistant", "content": msg['response']})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500,  # Shorter responses for dashboard integration
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again later."

# Initialize the service
llm_service = LLMService()

# Chat API routes
@chat_bp.route('/api/send', methods=['POST'])
@login_required
def send_message():
    """API endpoint for sending chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get user's chat history (last 10 messages)
        user_history = [msg for msg in chat_messages if msg.user_id == current_user.id][-10:]
        
        # Convert to format expected by LLM service
        history = []
        for msg in user_history:
            history.append({
                'message': msg.message,
                'response': msg.response
            })
        
        # Generate AI response
        ai_response = llm_service.generate_response(
            user_message=user_message,
            user_sector=getattr(current_user, 'selected_sector', None),
            chat_history=history
        )
        
        # Save to memory (in production, save to database)
        chat_message = ChatMessage(
            user_id=current_user.id,
            message=user_message,
            response=ai_response,
            sector=getattr(current_user, 'selected_sector', None)
        )
        chat_messages.append(chat_message)
        
        return jsonify({
            'response': ai_response,
            'timestamp': chat_message.timestamp.isoformat(),
            'demo_mode': llm_service.demo_mode
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/api/history')
@login_required
def get_history():
    """Get user's chat history"""
    try:
        user_messages = [msg for msg in chat_messages if msg.user_id == current_user.id]
        
        history = []
        for msg in user_messages:
            history.append({
                'id': id(msg),  # Use object id as unique identifier
                'message': msg.message,
                'response': msg.response,
                'timestamp': msg.timestamp.isoformat(),
                'sector': msg.sector
            })
        
        return jsonify({'history': history})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/api/status')
@login_required
def get_status():
    """Get chat service status"""
    return jsonify({
        'demo_mode': llm_service.demo_mode,
        'user_sector': getattr(current_user, 'selected_sector', None),
        'premium_status': getattr(current_user, 'premium_status', 'none'),
        'has_valid_premium': getattr(current_user, 'has_valid_premium', False)
    })

# Function to register the chat blueprint with the main app
def register_chat_module(app):
    """Register the chat module with the main Flask app"""
    app.register_blueprint(chat_bp)
    print("✅ Chat module registered successfully")
    
    # Check if OpenAI API key is available
    if not os.environ.get('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not found. Chat will run in demo mode.")
        print("   To enable full AI chat, set OPENAI_API_KEY environment variable.")
    else:
        print("✅ OpenAI API key found. Full AI chat enabled.")
