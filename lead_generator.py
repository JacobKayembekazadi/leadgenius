import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import googlemaps
import requests
from bs4 import BeautifulSoup
import re
import time

class LeadGenerator:
    """
    Advanced Lead Generation System
    Generates high-quality leads based on specified criteria
    """
    
    def __init__(self):
        self.company_prefixes = [
            "Innovative", "Global", "Advanced", "Smart", "Digital", "Future", 
            "Elite", "Prime", "Quantum", "Dynamic", "Strategic", "NextGen",
            "Optimal", "Synergy", "Pinnacle", "Vertex", "Apex", "Summit"
        ]
        
        self.company_suffixes = [
            "Solutions", "Systems", "Technologies", "Corp", "Inc", "LLC",
            "Group", "Enterprises", "Partners", "Ventures", "Labs", "Works",
            "Dynamics", "Innovations", "Services", "Consulting", "Studio"
        ]
        
        self.first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
            "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
            "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
            "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
            "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle",
            "Kenneth", "Laura", "Kevin", "Sarah", "Brian", "Kimberly", "George", "Deborah"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
            "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
            "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
            "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
        ]
        
        self.job_titles = {
            "Technology": [
                "CTO", "VP Engineering", "Director of Technology", "IT Director", 
                "Software Development Manager", "DevOps Manager", "Security Manager"
            ],
            "Healthcare": [
                "Medical Director", "Hospital Administrator", "Clinical Manager",
                "Health Information Manager", "Nursing Director", "Practice Manager"
            ],
            "Finance": [
                "CFO", "Finance Director", "Investment Manager", "Risk Manager",
                "Compliance Officer", "Treasury Manager", "Controller", "Audit Manager"
            ],
            "Education": [
                "Dean", "Academic Director", "Curriculum Manager", "Education Technology Director",
                "Student Services Director", "Research Director", "Department Head"
            ],
            "Real Estate": [
                "Property Manager", "Real Estate Director", "Development Manager",
                "Asset Manager", "Facilities Manager", "Commercial Real Estate Manager"
            ],
            "Manufacturing": [
                "Operations Director", "Plant Manager", "Production Manager",
                "Quality Control Manager", "Supply Chain Manager", "Manufacturing Engineer"
            ],
            "Retail": [
                "Store Manager", "Regional Manager", "Merchandising Manager",
                "Customer Experience Manager", "Inventory Manager", "Sales Director"
            ],
            "Consulting": [
                "Managing Partner", "Principal Consultant", "Practice Lead",
                "Business Development Manager", "Client Relationship Manager"
            ],
            "Marketing": [
                "CMO", "Marketing Director", "Digital Marketing Manager",
                "Brand Manager", "Content Marketing Manager", "Growth Manager"
            ],
            "E-commerce": [
                "E-commerce Director", "Digital Commerce Manager", "Online Sales Manager",
                "Marketplace Manager", "Customer Success Manager", "Product Manager"
            ]
        }
        
        self.domain_extensions = [".com", ".io", ".co", ".net", ".org", ".biz"]
        
    def generate_company_name(self, industry: str) -> str:
        """Generate a realistic company name"""
        prefix = random.choice(self.company_prefixes)
        suffix = random.choice(self.company_suffixes)
        return f"{prefix} {suffix}"
    
    def generate_contact_name(self) -> tuple:
        """Generate a realistic contact name"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        return first_name, last_name
    
    def generate_email(self, first_name: str, last_name: str, company_name: str) -> str:
        """Generate a realistic email address"""
        domain = company_name.lower().replace(" ", "").replace("&", "and")
        domain = ''.join(c for c in domain if c.isalnum())[:15]
        
        email_formats = [
            f"{first_name.lower()}.{last_name.lower()}",
            f"{first_name.lower()}{last_name.lower()}",
            f"{first_name[0].lower()}.{last_name.lower()}",
            f"{first_name[0].lower()}{last_name.lower()}"
        ]
        
        email_prefix = random.choice(email_formats)
        extension = random.choice(self.domain_extensions)
        
        return f"{email_prefix}@{domain}{extension}"
    
    def generate_phone_number(self) -> str:
        """Generate a realistic phone number"""
        area_codes = ["415", "650", "510", "408", "925", "707", "831", "209"]
        area_code = random.choice(area_codes)
        exchange = f"{random.randint(200, 999)}"
        number = f"{random.randint(1000, 9999)}"
        return f"({area_code}) {exchange}-{number}"
    
    def generate_website(self, company_name: str) -> str:
        """Generate a realistic website URL"""
        domain = company_name.lower().replace(" ", "").replace("&", "and")
        domain = ''.join(c for c in domain if c.isalnum())[:20]
        extension = random.choice(self.domain_extensions)
        return f"https://www.{domain}{extension}"
    
    def calculate_lead_score(self, params: Dict[str, Any], company_data: Dict[str, Any]) -> float:
        """Calculate lead score based on various factors"""
        base_score = 5.0
        
        # Industry alignment boost
        if company_data['industry'] == params['industry']:
            base_score += 2.0
        
        # Company size preference
        if params['quality_preference'] == "High Quality (Fewer leads)":
            if company_data['company_size'] in ["Large (201-1000)", "Enterprise (1000+)"]:
                base_score += 2.0
        
        # Location proximity
        if params['location'] and params['location'].lower() in company_data['location'].lower():
            base_score += 1.0
        
        # Add randomness
        random_factor = np.random.normal(0, 0.5)
        final_score = max(0.1, min(10.0, base_score + random_factor))
        
        return round(final_score, 1)
    
    def generate_leads(self, params: Dict[str, Any]) -> pd.DataFrame:
        """Generate leads based on specified parameters"""
        leads_data = []
        
        locations = [
            "San Francisco, CA", "New York, NY", "Los Angeles, CA", "Chicago, IL",
            "Boston, MA", "Seattle, WA", "Austin, TX", "Denver, CO", "Atlanta, GA",
            "Miami, FL", "Dallas, TX", "Phoenix, AZ", "Philadelphia, PA", "Houston, TX"
        ]
        
        company_sizes = ["Startup (1-10)", "Small (11-50)", "Medium (51-200)", 
                        "Large (201-1000)", "Enterprise (1000+)"]
        
        for i in range(params['num_leads']):
            # Generate company information
            industry = params['industry'] if random.random() < 0.7 else random.choice(list(self.job_titles.keys()))
            company_name = self.generate_company_name(industry)
            company_size = random.choice(company_sizes)
            location = params['location'] if params['location'] and random.random() < 0.4 else random.choice(locations)
            
            # Generate contact information
            first_name, last_name = self.generate_contact_name()
            job_title = random.choice(self.job_titles[industry])
            email = self.generate_email(first_name, last_name, company_name)
            phone = self.generate_phone_number()
            website = self.generate_website(company_name)
            
            # Create company data for scoring
            company_data = {
                'industry': industry,
                'company_size': company_size,
                'location': location
            }
            
            # Calculate lead score
            lead_score = self.calculate_lead_score(params, company_data)
            
            # Generate additional metadata
            lead_id = str(uuid.uuid4())[:8]
            created_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Add to leads data
            lead = {
                'lead_id': lead_id,
                'company_name': company_name,
                'industry': industry,
                'company_size': company_size,
                'location': location,
                'contact_name': f"{first_name} {last_name}",
                'first_name': first_name,
                'last_name': last_name,
                'job_title': job_title,
                'email': email,
                'phone': phone,
                'website': website,
                'lead_score': lead_score,
                'created_date': created_date.strftime('%Y-%m-%d'),
                'status': 'New'
            }
            
            leads_data.append(lead)
        
        # Create DataFrame and sort by lead score
        df = pd.DataFrame(leads_data)
        df = df.sort_values('lead_score', ascending=False).reset_index(drop=True)
        
        return df


# --- Functions to find contact information on a website ---

def find_emails(text):
    """Finds all email addresses in a given string of text."""
    # A simple regex for finding email addresses
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

def scrape_website_for_contacts(url):
    """
    Scrapes a website to find email addresses.
    It checks the homepage and a potential 'contact' page.
    """
    emails = set()
    try:
        # Add http if missing, required for requests
        if not url.startswith('http'):
            url = 'https://' + url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 1. Scrape the homepage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raises an error for bad status codes
        
        soup = BeautifulSoup(response.text, 'html.parser')
        homepage_emails = find_emails(soup.get_text())
        for email in homepage_emails:
            emails.add(email)

        # 2. Look for a "contact" page and scrape it
        contact_links = soup.find_all('a', href=re.compile(r'contact', re.IGNORECASE))
        if contact_links:
            contact_url = contact_links[0].get('href')
            if not contact_url.startswith('http'):
                from urllib.parse import urljoin
                contact_url = urljoin(url, contact_url)
            
            contact_response = requests.get(contact_url, headers=headers, timeout=10)
            contact_response.raise_for_status()
            contact_soup = BeautifulSoup(contact_response.text, 'html.parser')
            contact_page_emails = find_emails(contact_soup.get_text())
            for email in contact_page_emails:
                emails.add(email)
                
    except requests.RequestException as e:
        print(f"Could not scrape {url}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while scraping {url}: {e}")
        return []
        
    return list(emails)


# --- Main function to generate leads ---

def generate_leads(api_key, query, max_results=20):
    """
    Generates leads by searching Google Maps and then scraping websites.
    """
    gmaps = googlemaps.Client(key=api_key)
    leads = []
    
    try:
        # Use text_search to find places based on the query
        places_result = gmaps.places(query=query)
        
        results_count = 0
        for place in places_result.get('results', []):
            if results_count >= max_results:
                break

            place_id = place['place_id']
            # Get detailed information for each place
            place_details = gmaps.place(place_id=place_id, fields=[
                'name', 'formatted_address', 'website', 'formatted_phone_number'
            ])
            
            p = place_details.get('result', {})
            website = p.get('website')
            emails = []
            
            if website:
                # Be a responsible scraper
                time.sleep(1) 
                emails = scrape_website_for_contacts(website)

            lead_data = {
                'Business Name': p.get('name', 'N/A'),
                'Address': p.get('formatted_address', 'N/A'),
                'Phone': p.get('formatted_phone_number', 'N/A'),
                'Website': website if website else 'N/A',
                'Found Emails': ', '.join(emails) if emails else 'None Found'
            }
            leads.append(lead_data)
            results_count += 1
            
            # This allows the Streamlit app to update in real-time
            yield f"Found {results_count}/{len(places_result.get('results', []))}: {p.get('name')}", leads

    except googlemaps.exceptions.ApiError as e:
        raise Exception(f"Google Maps API Error: {e.message}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}") 