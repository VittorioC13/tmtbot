#!/usr/bin/env python3
"""
Test script for the TMT Interview Generator
This script demonstrates the interview question generation functionality
"""

import sys
import os
from interview_generator import IBInterviewGenerator

def test_interview_generator():
    """Test the interview generator with sample news data"""
    
    print("🧪 Testing TMT Interview Generator")
    print("=" * 50)
    
    # Sample news data for testing
    sample_news = """
    Title: Microsoft Acquires Activision Blizzard for $68.7 Billion
    Description: Microsoft has completed its acquisition of Activision Blizzard in the largest gaming industry deal ever, creating a major player in the metaverse and cloud gaming space.
    Content: The deal values Activision at $68.7 billion, representing a premium of approximately 45% to Activision's undisturbed share price. The transaction is expected to close in 2023, subject to regulatory approvals.
    
    Title: NVIDIA Reports Record Q4 Revenue of $22.1 Billion
    Description: NVIDIA's fourth-quarter revenue surged 22% year-over-year to $22.1 billion, driven by strong demand for AI chips and data center solutions.
    Content: The company's data center segment grew 27% to $18.4 billion, while gaming revenue increased 15% to $2.9 billion. NVIDIA's market capitalization now exceeds $2 trillion.
    
    Title: Meta Platforms Announces $50 Billion Share Buyback Program
    Description: Meta Platforms has authorized a $50 billion share repurchase program and increased its quarterly dividend by 50% to $0.50 per share.
    Content: The buyback represents approximately 5% of Meta's current market cap. The company also reported strong Q4 results with revenue growth of 25% year-over-year to $40.1 billion.
    
    Title: Amazon Web Services Launches New AI Services
    Description: AWS has introduced new artificial intelligence services including Bedrock, a managed service for building generative AI applications.
    Content: The new services are expected to generate $10 billion in annual revenue by 2025. AWS currently leads the cloud infrastructure market with 32% market share.
    
    Title: Apple's Vision Pro Sales Exceed Expectations
    Description: Apple's Vision Pro mixed reality headset has sold over 200,000 units in its first month, exceeding initial projections and driving renewed interest in the AR/VR market.
    Content: The $3,499 device represents Apple's entry into the spatial computing market. Analysts estimate the AR/VR market could reach $100 billion by 2030.
    """
    
    try:
        # Initialize the interview generator
        generator = IBInterviewGenerator()
        
        print("📊 Generating Technical Questions...")
        technical_questions = generator.generate_technical_questions(sample_news)
        print("✅ Technical questions generated successfully!")
        print("\n" + "="*30 + " TECHNICAL QUESTIONS " + "="*30)
        print(technical_questions[:1000] + "..." if len(technical_questions) > 1000 else technical_questions)
        
        print("\n" + "="*30 + " BEHAVIORAL QUESTIONS " + "="*30)
        behavioral_questions = generator.generate_behavioral_questions(sample_news)
        print("✅ Behavioral questions generated successfully!")
        print(behavioral_questions[:1000] + "..." if len(behavioral_questions) > 1000 else behavioral_questions)
        
        print("\n" + "="*30 + " MARKET SIZING QUESTIONS " + "="*30)
        market_sizing_questions = generator.generate_market_sizing_questions(sample_news)
        print("✅ Market sizing questions generated successfully!")
        print(market_sizing_questions[:1000] + "..." if len(market_sizing_questions) > 1000 else market_sizing_questions)
        
        print("\n" + "="*30 + " CASE STUDY " + "="*30)
        case_study = generator.generate_case_study(sample_news)
        print("✅ Case study generated successfully!")
        print(case_study[:1500] + "..." if len(case_study) > 1500 else case_study)
        
        print("\n" + "="*30 + " COMPREHENSIVE PACKAGE " + "="*30)
        comprehensive_package = generator.generate_comprehensive_interview_package(sample_news)
        print("✅ Comprehensive interview package generated successfully!")
        
        # Save the package
        filename = generator.save_interview_package(comprehensive_package)
        if filename:
            print(f"📁 Interview package saved to: {filename}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("   • Technical valuation and deal structure questions")
        print("   • Behavioral interview scenarios")
        print("   • Market sizing problems")
        print("   • Comprehensive case studies")
        print("   • Interview tips and best practices")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_interview_generator() 