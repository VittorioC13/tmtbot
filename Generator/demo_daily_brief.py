#!/usr/bin/env python3
"""
Demo script to show what the daily TMT brief looks like
This simulates the output format without requiring API keys
"""

from datetime import datetime

def create_sample_daily_brief():
    """Create a sample daily brief to show the format"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    sample_brief = f"""
TMT SECTOR M&A & VALUATION BRIEF - {today}

Generated on {today}
CONFIDENTIAL - FOR INTERNAL USE ONLY

EXECUTIVE SUMMARY

Key highlights from the past 24 hours:
• Microsoft completed its $68.7 billion acquisition of Activision Blizzard, the largest gaming industry deal ever
• NVIDIA reported record Q4 revenue of $22.1 billion, driven by AI chip demand
• Meta Platforms announced a $50 billion share buyback program
• AWS launched new AI services expected to generate $10 billion in annual revenue by 2025
• Apple's Vision Pro exceeded sales expectations with 200,000 units sold in first month

Major deal announcements and their significance:
• The Microsoft-Activision deal creates a major player in the metaverse and cloud gaming space
• NVIDIA's strong performance reflects the AI boom and data center expansion
• Meta's buyback signals confidence in future growth despite regulatory challenges
• AWS's AI services expansion strengthens its cloud leadership position
• Apple's Vision Pro success validates the AR/VR market potential

Critical market movements and their implications:
• TMT sector continues to lead market growth with AI and cloud computing driving valuations
• Gaming industry consolidation accelerating as major tech companies seek content and IP
• AI infrastructure spending creating new revenue streams for semiconductor and cloud companies
• Regulatory scrutiny increasing for big tech M&A deals

Key takeaways for investors and stakeholders:
• AI and cloud computing remain primary growth drivers in TMT sector
• Content and IP acquisitions becoming strategic priorities for tech giants
• Regulatory environment increasingly challenging for large-scale M&A
• AR/VR market showing signs of mainstream adoption

1. RECENT TMT M&A ACTIVITY

Microsoft-Activision Blizzard Deal ($68.7 Billion)
• Deal Structure: All-cash transaction
• Transaction Value: $68.7 billion, representing 45% premium to undisturbed share price
• Strategic Rationale: Microsoft seeks to strengthen its gaming portfolio and metaverse positioning
• Expected Synergies: Cross-platform gaming integration, cloud gaming expansion
• Regulatory Considerations: Subject to antitrust review in multiple jurisdictions
• Integration Timeline: Expected to close in 2023

Potential Follow-on Deals:
• Other gaming companies may become acquisition targets
• Cloud gaming infrastructure investments likely to increase
• Content licensing and distribution deals expected to accelerate

2. MARKET DYNAMICS & SENTIMENT

Overall TMT Sector Sentiment: Bullish
• Strong earnings performance across major tech companies
• AI and cloud computing driving growth and valuations
• Gaming and entertainment sector showing strong momentum
• Semiconductor demand remains robust

Key Market Drivers:
• AI/ML adoption across industries
• Cloud computing migration and expansion
• Gaming industry growth and consolidation
• Digital transformation initiatives

Key Headwinds:
• Regulatory scrutiny of big tech companies
• Supply chain constraints in semiconductor industry
• Rising interest rates affecting valuations
• Geopolitical tensions impacting global markets

Subsector Performance Analysis:
• Cloud Computing: Strong growth with AWS, Azure, and GCP leading
• Gaming: Consolidation driving valuations and strategic M&A
• Semiconductors: AI demand creating new growth opportunities
• Social Media: Regulatory challenges but strong user engagement

Trading Multiples Trends:
• Software companies trading at 8-12x revenue multiples
• Gaming companies at 4-6x revenue multiples
• Cloud infrastructure at 6-10x revenue multiples
• Semiconductor companies at 3-5x revenue multiples

3. TECH/AI LANDSCAPE

Major Technological Announcements:
• AWS Bedrock: Managed service for building generative AI applications
• NVIDIA's AI chip dominance: 80% market share in AI training chips
• Apple Vision Pro: Spatial computing platform with strong early adoption
• Microsoft's AI integration: Copilot and AI features across product suite

AI/ML Developments and Market Impact:
• Generative AI creating new revenue streams for cloud providers
• AI chip demand driving semiconductor industry growth
• AI-powered productivity tools becoming mainstream
• AI infrastructure spending expected to reach $200 billion by 2025

Emerging Technology Trends:
• Spatial computing and AR/VR gaining traction
• Edge computing and 5G enabling new applications
• Quantum computing investments increasing
• Blockchain and Web3 development continuing

Impact on Deal Valuations:
• AI capabilities becoming key valuation drivers
• Data and IP assets commanding premium valuations
• AI talent and expertise highly valued in acquisitions
• AI infrastructure companies seeing elevated multiples

4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

Microsoft-Activision Deal Impact:
• Shareholders: Activision shareholders receive 45% premium, Microsoft shareholders benefit from gaming expansion
• Employees: Potential synergies and restructuring, gaming talent retention critical
• Competitors: Sony and other gaming companies face increased competition
• Customers: Enhanced gaming ecosystem and cross-platform integration

NVIDIA Performance Impact:
• Shareholders: Strong returns driven by AI demand
• Employees: Continued growth and expansion opportunities
• Competitors: AMD and Intel facing increased pressure in AI segment
• Customers: Data centers and AI companies benefit from improved performance

Market Reaction and Analyst Commentary:
• Positive analyst coverage for Microsoft's strategic positioning
• NVIDIA receiving upgrades based on AI growth prospects
• Meta's buyback viewed as confidence signal
• Apple's Vision Pro success exceeding expectations

Expected Market Reaction:
• Gaming sector valuations likely to increase following Microsoft deal
• AI-related companies expected to maintain premium valuations
• Cloud computing growth expected to continue strong momentum
• Regulatory scrutiny may impact future large-scale M&A

Potential Counter-bids or Competing Offers:
• Other tech companies may seek gaming acquisitions
• Private equity interest in gaming and content companies
• Strategic buyers looking for AI and cloud capabilities
• Cross-border deals may face increased regulatory hurdles

Similar Deals Likely to Follow:
• Additional gaming industry consolidation
• AI infrastructure and software acquisitions
• Cloud computing platform expansions
• Content and IP acquisitions by tech companies

Sector Consolidation Predictions:
• Gaming industry consolidation accelerating
• AI and cloud computing market concentration increasing
• Semiconductor industry consolidation continuing
• Content and media industry transformation

Key Risks and Mitigants:
• Regulatory Risk: Antitrust scrutiny may delay or block deals
• Integration Risk: Cultural and operational challenges in large acquisitions
• Market Risk: Economic downturn could impact valuations
• Technology Risk: Rapid technological change may affect deal rationale

Page 1
    """
    
    return sample_brief

def create_sample_interview_package():
    """Create a sample interview package to show the format"""
    
    sample_package = """
# TMT SECTOR INVESTMENT BANKING INTERVIEW PREPARATION PACKAGE
Generated on: 2024-06-22 21:30:00
Based on recent TMT sector news and developments

## TABLE OF CONTENTS
1. Technical Questions (10 questions)
2. Behavioral Questions (8 questions)
3. Market Sizing Questions (5 questions)

---

## 1. TECHNICAL QUESTIONS

CATEGORY: Valuation Questions
DIFFICULTY: Medium
QUESTION: Microsoft is acquiring Activision Blizzard for $68.7 billion. If Activision has $8.1 billion in revenue and $4.5 billion in EBITDA, what are the implied EV/Revenue and EV/EBITDA multiples? How do these compare to recent gaming industry transactions?
CONTEXT: Microsoft's acquisition of Activision represents the largest gaming industry deal ever
EXPECTED FRAMEWORK: Calculate multiples, compare to industry averages, discuss strategic rationale

CATEGORY: Deal Structure Questions
DIFFICULTY: Hard
QUESTION: Microsoft is paying all-cash for Activision. What are the advantages and disadvantages of this structure versus a stock-for-stock deal? How would this impact Microsoft's balance sheet and credit metrics?
CONTEXT: All-cash $68.7 billion acquisition
EXPECTED FRAMEWORK: Cash vs. stock analysis, balance sheet impact, credit rating considerations

CATEGORY: Market & Sector Questions
DIFFICULTY: Easy
QUESTION: What are the key drivers of growth in the TMT sector today? How do you see these trends evolving over the next 3-5 years?
CONTEXT: TMT sector leading market growth
EXPECTED FRAMEWORK: Identify key trends, discuss drivers, provide forward-looking analysis

CATEGORY: Modeling Questions
DIFFICULTY: Hard
QUESTION: Build a simple merger model for Microsoft-Activision. What are the key assumptions you would make for revenue synergies and cost synergies? How would you model the accretion/dilution analysis?
CONTEXT: $68.7 billion gaming industry acquisition
EXPECTED FRAMEWORK: Revenue synergies, cost synergies, accretion/dilution analysis, key assumptions

CATEGORY: Valuation Questions
DIFFICULTY: Medium
QUESTION: NVIDIA is trading at 45x P/E and 18x EV/Revenue. What factors justify these elevated multiples? How would you value NVIDIA using a DCF model?
CONTEXT: NVIDIA's strong AI-driven performance
EXPECTED FRAMEWORK: Growth prospects, competitive moat, DCF assumptions, terminal value

---

## 2. BEHAVIORAL QUESTIONS

CATEGORY: Deal Experience & Motivation
DIFFICULTY: Medium
QUESTION: The Microsoft-Activision deal is the largest gaming acquisition ever. What interests you most about this transaction, and how does it relate to your interest in investment banking?
CONTEXT: Record-breaking gaming industry deal
STAR FRAMEWORK: Situation (deal context), Task (understanding), Action (analysis), Result (insights)

CATEGORY: Teamwork & Leadership
DIFFICULTY: Hard
QUESTION: Imagine you're working on a complex M&A deal like Microsoft-Activision. How would you handle conflicting opinions within your team about deal valuation or structure?
CONTEXT: Complex M&A transaction with multiple stakeholders
STAR FRAMEWORK: Situation (conflict), Task (resolution), Action (approach), Result (outcome)

CATEGORY: Problem-Solving & Analysis
DIFFICULTY: Medium
QUESTION: If you were advising Microsoft on the Activision acquisition, what would be your top 3 concerns and how would you address them?
CONTEXT: Strategic gaming industry acquisition
STAR FRAMEWORK: Situation (acquisition context), Task (identify concerns), Action (solutions), Result (outcome)

CATEGORY: Client Relationship & Communication
DIFFICULTY: Easy
QUESTION: How would you explain the strategic rationale behind Microsoft's Activision acquisition to a client who is not familiar with the gaming industry?
CONTEXT: Complex strategic acquisition
STAR FRAMEWORK: Situation (client education), Task (explain rationale), Action (communication approach), Result (understanding)

---

## 3. MARKET SIZING QUESTIONS

CATEGORY: Market Sizing
DIFFICULTY: Medium
QUESTION: Estimate the total addressable market for cloud gaming services globally. Consider factors like internet penetration, gaming adoption, and willingness to pay.
CONTEXT: Microsoft's gaming expansion and cloud gaming focus
EXPECTED FRAMEWORK: Top-down approach, key assumptions, market segmentation
KEY ASSUMPTIONS: Global population, gaming penetration, cloud adoption rates

CATEGORY: Market Sizing
DIFFICULTY: Hard
QUESTION: What is the market size for AI infrastructure and data center services? Consider both hardware and software components.
CONTEXT: NVIDIA's AI chip dominance and AWS AI services
EXPECTED FRAMEWORK: Bottom-up approach, hardware vs. software, growth drivers
KEY ASSUMPTIONS: Data center growth, AI adoption rates, pricing trends

CATEGORY: Market Sizing
DIFFICULTY: Easy
QUESTION: Estimate the global market for AR/VR headsets and related software. How do you see this market evolving?
CONTEXT: Apple Vision Pro success and AR/VR market growth
EXPECTED FRAMEWORK: Market segmentation, adoption curve, pricing analysis
KEY ASSUMPTIONS: Consumer adoption, enterprise use cases, price elasticity

CATEGORY: Market Sizing
DIFFICULTY: Medium
QUESTION: What is the addressable market for generative AI services in enterprise applications?
CONTEXT: AWS Bedrock and enterprise AI adoption
EXPECTED FRAMEWORK: Enterprise segmentation, use case analysis, pricing models
KEY ASSUMPTIONS: Enterprise adoption rates, average contract values, market penetration

CATEGORY: Market Sizing
DIFFICULTY: Hard
QUESTION: Estimate the global market for gaming content and intellectual property. Include both traditional and mobile gaming.
CONTEXT: Gaming industry consolidation and content acquisition
EXPECTED FRAMEWORK: Content types, monetization models, geographic breakdown
KEY ASSUMPTIONS: Gaming revenue, content licensing, IP valuation

---
*This package is generated based on recent TMT sector developments and is designed to help candidates prepare for Investment Banking interviews.*
    """
    
    return sample_package

if __name__ == "__main__":
    print("📊 SAMPLE DAILY TMT BRIEF")
    print("=" * 60)
    print(create_sample_daily_brief())
    
    print("\n" + "=" * 60)
    print("🎓 SAMPLE INTERVIEW PACKAGE")
    print("=" * 60)
    print(create_sample_interview_package()) 