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
        "temperature": 0.7,
        "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest", # Or another suitable Gemini model
        generation_config=generation_config
    )

    # Combine system instructions and user data into a single, clear prompt.
    prompt = f"""
    You are "Alex", a friendly and professional business development assistant for a marketing agency called "GrowthBoost". 
    Your goal is to write short, compelling, and highly personalized outreach messages to potential clients based on the profile provided.
    
    YOUR GUIDELINES:
    1.  **Human Tone**: Do not sound like a generic bot. Be warm, approachable, and professional.
    2.  **Concise**: Keep all messages under 100 words. Shorter is better.
    3.  **Personalize**: You MUST reference one specific detail from the lead's profile (e.g., their business type, a service they offer, or their location).
    4.  **Soft CTA**: The call-to-action should be low-pressure. Ask if they're open to exploring ideas, not to book a call immediately.
    5.  **Output Format**: Your entire output must be a valid JSON object with exactly two keys: "email_body" and "linkedin_dm".

    Here is the profile for the lead to contact:
    
    ```json
    {json.dumps(lead_profile, indent=2)}
    ```

    Now, generate the JSON output based on the profile and your guidelines.
    """
    
    try:
        response = model.generate_content(prompt)
        # The response text will be a clean JSON string thanks to response_mime_type
        return json.loads(response.text)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Handle cases where the model might fail or return malformed content
        error_response_text = getattr(response, 'text', 'No response text available.')
        print(f"Gemini raw response: {error_response_text}")
        return None

def generate_bulk_outreach(leads_df, gemini_api_key):
    """
    Generate personalized outreach for multiple leads at once.
    """
    if not configure_gemini(gemini_api_key):
        return None
    
    results = []
    
    for idx, lead in leads_df.iterrows():
        try:
            # Create profile for each lead
            profile = create_lead_profile(lead.to_dict())
            
            # Generate personalized messages
            messages = generate_personalized_outreach_gemini(profile)
            
            if messages:
                result = {
                    'lead_id': lead.get('id', idx),
                    'business_name': lead.get('Business Name', 'Unknown'),
                    'email_body': messages.get('email_body', ''),
                    'linkedin_dm': messages.get('linkedin_dm', ''),
                    'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(result)
            
        except Exception as e:
            print(f"Error generating outreach for {lead.get('Business Name', 'Unknown')}: {e}")
            continue
    
    return pd.DataFrame(results)

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
            
            # 4. Generate personalized messages with the Gemini "Brain"
            print("🧠 Agent (powered by Gemini) is thinking...")
            generated_messages = generate_personalized_outreach_gemini(profile)
            
            if generated_messages:
                print("\n✅ Agent generated the following outreach drafts:")
                print("-" * 40)
                print("📧 DRAFT EMAIL BODY:")
                print(generated_messages.get('email_body', 'Error: Not generated'))
                print("-" * 40)
                print("🔗 DRAFT LINKEDIN DM:")
                print(generated_messages.get('linkedin_dm', 'Error: Not generated'))
                print("-" * 40) 