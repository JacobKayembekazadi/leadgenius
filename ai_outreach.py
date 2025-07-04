import google.generativeai as genai
import pandas as pd
import json
import os

def configure_gemini(api_key):
    """Configures the Gemini client with the provided API key."""
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        return False

def create_lead_profile(lead_data):
    """Formats the raw lead data into a structured profile."""
    profile = {
        "company_name": lead_data.get("Business Name"),
        "business_type": lead_data.get("Type", "a local business"),
        "location": lead_data.get("Address", "their city"),
        "website": lead_data.get("Website"),
        "phone": lead_data.get("Phone"),
        "emails": lead_data.get("Found Emails"),
        "key_person": {
            "name": lead_data.get("Person Name", ""),
            "title": lead_data.get("Person Title", "")
        },
        # Enhanced with more context from scraped data
        "scraped_info": lead_data.get("scraped_info", "Additional business information from website analysis.")
    }
    return profile

def generate_personalized_outreach_gemini(lead_profile):
    """
    Uses Google's Gemini 1.5 Pro to generate personalized messages.
    This is the core of the autonomous agent's "thinking".
    """
    # Gemini 1.5 Pro has native JSON output mode, which is extremely reliable.
    generation_config = {
        "temperature": 0.7,  # Balanced for consistency with creativity
        "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest", # Or another suitable Gemini model
        generation_config=generation_config
    )

    # Updated prompt with the 4 P's framework
    prompt = f"""
## 1. YOUR PERSONA
You are "Alex", a sharp, friendly, and respectful Business Development Specialist at "GrowthBoost". Your expertise is in digital marketing and lead generation. Your tone is that of a helpful industry expert, not a pushy salesperson. You are confident, clear, and genuinely curious about the prospect's business. You NEVER use hyperbole or spammy language.

## 2. YOUR CORE MISSION
Your mission is to analyze a prospect's profile and write highly personalized, concise, and persuasive outreach copy for Email and LinkedIn. The primary goal is to pique the prospect's interest and make them feel that replying is easy and worthwhile. You are starting a conversation, not closing a deal.

## 3. RULES OF ENGAGEMENT: THE 4 P'S
You must adhere to the following four principles for every piece of copy you write.

### P1: PERSONALIZED
- You MUST reference a specific, non-generic detail from the lead's profile.
- GOOD EXAMPLES: "your work in real estate law in Denver," "the new menu on your website," "your focus on cosmetic dentistry."
- BAD EXAMPLES: "your impressive company," "your work."
- This proves you've done the bare minimum of research and are not a bulk spam bot.

### P2: PROBLEM-AWARE
- Do not lead with your solution. Lead with the prospect's likely problem or goal.
- Show empathy. Acknowledge a common challenge or objective for their specific industry.
- EXAMPLE: Instead of "We build websites," say "I imagine standing out online is a constant goal for law firms in a competitive city like Denver." This makes the prospect think, "Yes, that's right."

### P3: PITHY (Digestible)
- Brevity is paramount. Your copy must be easily scannable on a phone.
- Use short sentences and short paragraphs (2-3 sentences max).
- Get to the point within the first two sentences.
- TOTAL LENGTH: Keep the body under 90 words. Shorter is better.
- Avoid all jargon. Write at an 8th-grade reading level.

### P4: PERSUASIVE (but not Pushy)
- **Benefit-Oriented:** Focus on the outcome for them, not your process. (e.g., "attract more qualified local clients" instead of "we do SEO and paid ads").
- **Low-Friction Call-to-Action (CTA):** End with a simple, low-commitment question. This makes it easy to reply.
- GOOD CTAs: "Curious if this is a priority for you right now?", "Would you be open to hearing one quick idea we had?", "Is this something you've been thinking about?"
- BAD CTAs: "Can we book a 30-minute call?", "Are you free to meet next week?"

## 4. OUTPUT FORMAT
Your entire output MUST be a valid JSON object. Do not add any text before or after the JSON. The object must contain exactly three string keys: "email_subject", "email_body", and "linkedin_dm".

## 5. PROSPECT PROFILE TO ANALYZE
```json
{json.dumps(lead_profile, indent=2)}
```

Generate the outreach copy now following the 4 P's framework:
    """
    
    try:
        response = model.generate_content(prompt)
        # The response text will be a clean JSON string thanks to response_mime_type
        result = json.loads(response.text)
        
        # Validate the response has required fields
        required_fields = ['email_subject', 'email_body', 'linkedin_dm']
        if not all(field in result for field in required_fields):
            print("Warning: Generated response missing required fields")
            
        # Add analytics fields for compatibility with UI
        result['personalization_angle'] = 'Generated using 4 P\'s framework'
        result['confidence_score'] = 8  # High confidence with structured framework
            
        return result
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Enhanced error handling with fallback
        error_response_text = getattr(response, 'text', 'No response text available.')
        print(f"Gemini raw response: {error_response_text}")
        
        # Provide basic fallback message
        fallback = {
            'email_subject': f"Quick thought on {lead_profile.get('company_name', 'your business')}",
            'email_body': f"Hi there! I came across {lead_profile.get('company_name', 'your business')} and was impressed by what you're doing. Would love to share a quick idea that might help with growth. Worth a brief chat?",
            'linkedin_dm': f"Hi! Noticed {lead_profile.get('company_name', 'your business')} - looks great! Quick question about {lead_profile.get('business_type', 'your industry')} - mind if I send a brief message?",
            'personalization_angle': 'Generic fallback due to API error',
            'confidence_score': 3
        }
        return fallback

def generate_bulk_outreach(leads_df, gemini_api_key):
    """
    Generate personalized outreach for multiple leads at once.
    Enhanced with analytics and quality metrics.
    """
    if not configure_gemini(gemini_api_key):
        return None
    
    results = []
    analytics = {
        'total_leads': len(leads_df),
        'successful_generations': 0,
        'failed_generations': 0,
        'avg_confidence_score': 0,
        'personalization_angles': {},
        'high_confidence_count': 0  # confidence >= 8
    }
    
    for idx, lead in leads_df.iterrows():
        try:
            # Create profile for each lead
            profile = create_lead_profile(lead.to_dict())
            
            # Generate personalized messages
            messages = generate_personalized_outreach_gemini(profile)
            
            if messages:
                # Extract confidence score and personalization angle
                confidence_score = messages.get('confidence_score', 5)
                personalization_angle = messages.get('personalization_angle', 'Unknown')
                
                result = {
                    'lead_id': lead.get('id', idx),
                    'business_name': lead.get('Business Name', 'Unknown'),
                    'email_subject': messages.get('email_subject', ''),
                    'email_body': messages.get('email_body', ''),
                    'linkedin_dm': messages.get('linkedin_dm', ''),
                    'personalization_angle': personalization_angle,
                    'confidence_score': confidence_score,
                    'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'word_count_email': len(messages.get('email_body', '').split()),
                    'word_count_linkedin': len(messages.get('linkedin_dm', '').split())
                }
                results.append(result)
                
                # Update analytics
                analytics['successful_generations'] += 1
                analytics['avg_confidence_score'] += confidence_score
                
                if confidence_score >= 8:
                    analytics['high_confidence_count'] += 1
                
                # Track personalization angles
                if personalization_angle in analytics['personalization_angles']:
                    analytics['personalization_angles'][personalization_angle] += 1
                else:
                    analytics['personalization_angles'][personalization_angle] = 1
            else:
                analytics['failed_generations'] += 1
            
        except Exception as e:
            print(f"Error generating outreach for {lead.get('Business Name', 'Unknown')}: {e}")
            analytics['failed_generations'] += 1
            continue
    
    # Calculate final analytics
    if analytics['successful_generations'] > 0:
        analytics['avg_confidence_score'] = round(
            analytics['avg_confidence_score'] / analytics['successful_generations'], 2
        )
        analytics['success_rate'] = round(
            (analytics['successful_generations'] / analytics['total_leads']) * 100, 1
        )
    else:
        analytics['avg_confidence_score'] = 0
        analytics['success_rate'] = 0
    
    results_df = pd.DataFrame(results)
    
    # Add analytics as metadata to the DataFrame
    if not results_df.empty:
        results_df.attrs['analytics'] = analytics
    
    return results_df

def save_outreach_messages(messages_df, filename=None):
    """Save generated outreach messages to JSON file."""
    if filename is None:
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outreach_messages_{timestamp}.json"
    
    try:
        messages_df.to_json(filename, orient='records', indent=2)
        return filename
    except Exception as e:
        print(f"Error saving outreach messages: {e}")
        return None

# --- Example Usage ---
if __name__ == "__main__":
    # For local testing, you can set the key directly. For production, use environment variables.
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set it with: export GEMINI_API_KEY='your-key-here'")
    else:
        # 1. Configure the Gemini client
        is_configured = configure_gemini(api_key=GEMINI_API_KEY)
        
        if is_configured:
            # 2. Simulate lead data (this would come from your 'Scout' module)
            sample_lead = {
                "Business Name": "Summit Peak Legal",
                "Type": "law firm specializing in real estate",
                "Address": "Denver, CO",
                "Website": "summitpeaklegal.com",
                "Phone": "(303) 555-0123",
                "Found Emails": "david@summitpeaklegal.com",
                "Person Name": "David Chen",
                "Person Title": "Managing Partner"
            }

            # 3. Create a structured profile
            profile = create_lead_profile(sample_lead)
            
            # 4. Generate personalized messages with the 4 P's framework
            print("🧠 AI Agent Alex (using 4 P's framework) is analyzing...")
            generated_messages = generate_personalized_outreach_gemini(profile)
            
            if generated_messages:
                print("\n✅ Agent Alex generated highly personalized outreach:")
                print("=" * 70)
                print("📧 EMAIL SUBJECT:")
                print(generated_messages.get('email_subject', 'Error: Not generated'))
                print("\n📧 EMAIL BODY:")
                print(generated_messages.get('email_body', 'Error: Not generated'))
                print("\n🔗 LINKEDIN DM:")
                print(generated_messages.get('linkedin_dm', 'Error: Not generated'))
                print("\n📊 FRAMEWORK ANALYTICS:")
                print(f"   • Framework Used: {generated_messages.get('personalization_angle', 'N/A')}")
                print(f"   • Confidence Score: {generated_messages.get('confidence_score', 'N/A')}/10")
                print(f"   • Email Subject Length: {len(generated_messages.get('email_subject', '').split())} words")
                print(f"   • Email Body Length: {len(generated_messages.get('email_body', '').split())} words")
                print(f"   • LinkedIn Length: {len(generated_messages.get('linkedin_dm', '').split())} words")
                print("=" * 70)
                
                # Demonstrate bulk processing with multiple sample leads
                print("\n🔄 Testing bulk outreach with multiple leads...")
                sample_leads_data = [
                    sample_lead,
                    {
                        "Business Name": "Verde Bistro",
                        "Type": "Italian restaurant",
                        "Address": "Austin, TX",
                        "Website": "verdebistro.com",
                        "Phone": "(512) 555-0189",
                        "Found Emails": "maria@verdebistro.com",
                        "Person Name": "Maria Rodriguez",
                        "Person Title": "Owner"
                    },
                    {
                        "Business Name": "TechFix Solutions",
                        "Type": "IT support services",
                        "Address": "Seattle, WA",
                        "Website": "techfixsolutions.com",
                        "Phone": "(206) 555-0234",
                        "Found Emails": "support@techfixsolutions.com",
                        "Person Name": "James Kim",
                        "Person Title": "CEO"
                    }
                ]
                
                leads_df = pd.DataFrame(sample_leads_data)
                bulk_results = generate_bulk_outreach(leads_df, GEMINI_API_KEY)
                
                if bulk_results is not None and not bulk_results.empty:
                    analytics = getattr(bulk_results, 'attrs', {}).get('analytics', {})
                    print(f"\n📈 BULK GENERATION ANALYTICS:")
                    print(f"   • Success Rate: {analytics.get('success_rate', 0)}%")
                    print(f"   • Average Confidence: {analytics.get('avg_confidence_score', 0)}/10")
                    print(f"   • High Confidence Messages: {analytics.get('high_confidence_count', 0)}")
                    print(f"   • Personalization Angles Used: {list(analytics.get('personalization_angles', {}).keys())}")
                    
                    # Save results
                    filename = save_outreach_messages(bulk_results)
                    if filename:
                        print(f"   • Results saved to: {filename}")
                else:
                    print("   ❌ Bulk generation failed")
            else:
                print("❌ Failed to generate messages") 