import openai
import os
from datetime import datetime, timedelta
from config import OPENAI_API_KEY

class IBInterviewGenerator:
    def __init__(self):
        self.openai_client = openai.Client(api_key=OPENAI_API_KEY)
        
    def generate_technical_questions(self, news_items, deal_data=None):
        """Generate technical IB interview questions based on recent news"""
        
        technical_prompt = """
        As a senior Investment Banking interviewer, generate 10 technical interview questions based on recent TMT sector news and deals.
        
        Create questions in these categories:
        
        1. VALUATION QUESTIONS (3 questions)
        - DCF analysis scenarios
        - Comparable company analysis
        - Precedent transaction analysis
        - Multiples analysis
        
        2. DEAL STRUCTURE QUESTIONS (3 questions)
        - Cash vs. stock consideration
        - Synergy analysis
        - Financing structure
        - Regulatory considerations
        
        3. MARKET & SECTOR QUESTIONS (2 questions)
        - Market sizing
        - Competitive analysis
        - Industry trends
        - Risk assessment
        
        4. MODELING QUESTIONS (2 questions)
        - Merger model scenarios
        - LBO analysis
        - Sensitivity analysis
        - Returns analysis
        
        For each question:
        - Make it specific to recent TMT deals/news
        - Include relevant numbers and metrics
        - Provide expected answer framework
        - Include difficulty level (Easy/Medium/Hard)
        
        Base questions on this recent news:
        {news_items}
        
        Format each question as:
        CATEGORY: [Category Name]
        DIFFICULTY: [Easy/Medium/Hard]
        QUESTION: [The actual question]
        CONTEXT: [Brief context from recent news]
        EXPECTED FRAMEWORK: [Key points to cover in answer]
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior Investment Banking MD who has conducted hundreds of technical interviews. You excel at creating challenging, relevant questions that test candidates' understanding of valuation, deal structure, and market dynamics."},
                    {"role": "user", "content": technical_prompt.format(news_items=news_items)}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating technical questions: {str(e)}"
    
    def generate_behavioral_questions(self, news_items):
        """Generate behavioral interview questions based on recent deals"""
        
        behavioral_prompt = """
        As a senior Investment Banking interviewer, generate 8 behavioral interview questions based on recent TMT sector developments.
        
        Create questions in these categories:
        
        1. DEAL EXPERIENCE & MOTIVATION (2 questions)
        - Interest in specific deals
        - Motivation for IB career
        - Deal preferences and rationale
        
        2. TEAMWORK & LEADERSHIP (2 questions)
        - Team dynamics in deal execution
        - Leadership in high-pressure situations
        - Conflict resolution
        
        3. PROBLEM-SOLVING & ANALYSIS (2 questions)
        - Complex deal challenges
        - Analytical thinking
        - Creative solutions
        
        4. CLIENT RELATIONSHIP & COMMUNICATION (2 questions)
        - Client interaction scenarios
        - Communication skills
        - Relationship management
        
        For each question:
        - Reference specific recent deals or market events
        - Include STAR method framework expectations
        - Provide context from recent news
        - Include difficulty level
        
        Base questions on this recent news:
        {news_items}
        
        Format each question as:
        CATEGORY: [Category Name]
        DIFFICULTY: [Easy/Medium/Hard]
        QUESTION: [The actual question]
        CONTEXT: [Brief context from recent news]
        STAR FRAMEWORK: [Situation, Task, Action, Result expectations]
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior Investment Banking MD who has conducted hundreds of behavioral interviews. You excel at creating questions that reveal candidates' true motivations, teamwork abilities, and problem-solving skills."},
                    {"role": "user", "content": behavioral_prompt.format(news_items=news_items)}
                ],
                max_tokens=3000,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating behavioral questions: {str(e)}"
    
    def generate_case_study(self, news_items):
        """Generate a comprehensive case study based on recent deals"""
        
        case_study_prompt = """
        As a senior Investment Banking MD, create a comprehensive case study based on recent TMT sector developments.
        
        Structure the case study as follows:
        
        CASE STUDY: [Title based on recent deal/trend]
        
        EXECUTIVE SUMMARY
        - Brief overview of the scenario
        - Key players and stakeholders
        - Main challenges and opportunities
        
        BACKGROUND
        - Company profiles and market positions
        - Industry context and trends
        - Recent developments that led to this scenario
        
        THE CHALLENGE
        - Specific problem or opportunity to analyze
        - Key constraints and considerations
        - Stakeholder objectives and conflicts
        
        REQUIRED ANALYSIS
        1. Valuation Analysis
           - What valuation methods would you use?
           - What key assumptions would you make?
           - What are the main value drivers?
        
        2. Deal Structure Analysis
           - What are the optimal deal terms?
           - How would you structure the consideration?
           - What financing options are available?
        
        3. Strategic Analysis
           - What are the strategic rationales?
           - What synergies can be achieved?
           - What are the integration challenges?
        
        4. Risk Assessment
           - What are the key risks?
           - How would you mitigate them?
           - What are the regulatory considerations?
        
        DELIVERABLES
        - Specific outputs expected from the candidate
        - Format and presentation requirements
        - Time constraints and assumptions
        
        EVALUATION CRITERIA
        - What aspects will be evaluated
        - Key points to demonstrate
        - Common mistakes to avoid
        
        Base this case study on recent news:
        {news_items}
        
        Make it realistic, challenging, and relevant to current market conditions.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior Investment Banking MD who has designed and evaluated hundreds of case studies. You excel at creating realistic, challenging scenarios that test candidates' analytical and strategic thinking."},
                    {"role": "user", "content": case_study_prompt.format(news_items=news_items)}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating case study: {str(e)}"
    
    def generate_market_sizing_questions(self, news_items):
        """Generate market sizing questions for TMT subsectors"""
        
        market_sizing_prompt = """
        As a senior Investment Banking interviewer, generate 5 market sizing questions based on recent TMT sector developments.
        
        Create questions that test:
        1. Top-down market sizing approach
        2. Bottom-up market sizing approach
        3. Market penetration analysis
        4. Growth rate assumptions
        5. Competitive landscape analysis
        
        For each question:
        - Reference specific TMT subsectors from recent news
        - Include relevant market data points
        - Provide expected calculation framework
        - Include difficulty level
        
        Base questions on recent news:
        {news_items}
        
        Format each question as:
        CATEGORY: Market Sizing
        DIFFICULTY: [Easy/Medium/Hard]
        QUESTION: [The market sizing question]
        CONTEXT: [Brief context from recent news]
        EXPECTED FRAMEWORK: [Step-by-step approach to solve]
        KEY ASSUMPTIONS: [Important assumptions to consider]
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior Investment Banking MD who has conducted hundreds of market sizing interviews. You excel at creating questions that test candidates' logical thinking, market knowledge, and quantitative skills."},
                    {"role": "user", "content": market_sizing_prompt.format(news_items=news_items)}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating market sizing questions: {str(e)}"
    
    def generate_comprehensive_interview_package(self, news_items):
        """Generate a complete interview preparation package"""
        
        print("Generating comprehensive interview package...")
        
        # Generate all question types
        technical_questions = self.generate_technical_questions(news_items)
        behavioral_questions = self.generate_behavioral_questions(news_items)
        market_sizing_questions = self.generate_market_sizing_questions(news_items)
        
        # Combine into comprehensive package
        comprehensive_package = f"""
# TMT SECTOR INVESTMENT BANKING INTERVIEW PREPARATION PACKAGE
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Based on recent TMT sector news and developments

## TABLE OF CONTENTS
1. Technical Questions (10 questions)
2. Behavioral Questions (8 questions)
3. Market Sizing Questions (5 questions)

---

## 1. TECHNICAL QUESTIONS
{technical_questions}

---

## 2. BEHAVIORAL QUESTIONS
{behavioral_questions}

---

## 3. MARKET SIZING QUESTIONS
{market_sizing_questions}

---
*This package is generated based on recent TMT sector developments and is designed to help candidates prepare for Investment Banking interviews.*
        """
        
        return comprehensive_package
    
    def save_interview_package(self, package_content):
        """Save the interview package to a file"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            filename = f'interview_package_{today}.txt'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(package_content)
            
            return filename
        except Exception as e:
            print(f"Error saving interview package: {str(e)}")
            return None 