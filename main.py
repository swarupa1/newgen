
from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Global variable to store jobs
jobs_data = []
last_updated = None

def scrape_jobs():
    """Scrape jobs from multiple sources"""
    global jobs_data, last_updated
    
    jobs = []
    
    # Indeed UK - jobs with visa sponsorship
    try:
        indeed_url = "https://uk.indeed.com/jobs?q=visa+sponsorship&l=United+Kingdom"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(indeed_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        for card in job_cards[:10]:  # Limit to first 10 jobs
            try:
                title_elem = card.find('h2', class_='jobTitle')
                title = title_elem.get_text().strip() if title_elem else "N/A"
                
                company_elem = card.find('span', class_='companyName')
                company = company_elem.get_text().strip() if company_elem else "N/A"
                
                location_elem = card.find('div', class_='companyLocation')
                location = location_elem.get_text().strip() if location_elem else "N/A"
                
                summary_elem = card.find('div', class_='summary')
                summary = summary_elem.get_text().strip() if summary_elem else "N/A"
                
                link_elem = title_elem.find('a') if title_elem else None
                link = f"https://uk.indeed.com{link_elem['href']}" if link_elem and link_elem.get('href') else "#"
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'summary': summary[:200] + "..." if len(summary) > 200 else summary,
                    'source': 'Indeed UK',
                    'link': link,
                    'visa_sponsorship': True
                })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error scraping Indeed: {e}")
    
    # Add some sample jobs for demonstration
    sample_jobs = [
        {
            'title': 'Software Engineer - Visa Sponsorship Available',
            'company': 'Tech Solutions UK',
            'location': 'London, England',
            'summary': 'We are looking for talented software engineers. Visa sponsorship available for qualified candidates.',
            'source': 'Sample Data',
            'link': '#',
            'visa_sponsorship': True
        },
        {
            'title': 'Data Scientist with Sponsorship',
            'company': 'AI Innovations Ltd',
            'location': 'Manchester, England',
            'summary': 'Join our data science team. We provide visa sponsorship for international candidates.',
            'source': 'Sample Data',
            'link': '#',
            'visa_sponsorship': True
        },
        {
            'title': 'Marketing Manager - Tier 2 Visa',
            'company': 'Global Marketing Co',
            'location': 'Birmingham, England',
            'summary': 'Marketing manager position with Tier 2 visa sponsorship for the right candidate.',
            'source': 'Sample Data',
            'link': '#',
            'visa_sponsorship': True
        }
    ]
    
    jobs.extend(sample_jobs)
    jobs_data = jobs
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def background_scraper():
    """Background thread to scrape jobs periodically"""
    while True:
        try:
            scrape_jobs()
            print(f"Jobs updated at {last_updated}")
            time.sleep(3600)  # Update every hour
        except Exception as e:
            print(f"Error in background scraper: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

@app.route('/')
def home():
    return render_template('index.html', jobs=jobs_data, last_updated=last_updated)

@app.route('/api/jobs')
def api_jobs():
    return jsonify({
        'jobs': jobs_data,
        'last_updated': last_updated,
        'total_jobs': len(jobs_data)
    })

@app.route('/refresh')
def refresh_jobs():
    scrape_jobs()
    return jsonify({
        'message': 'Jobs refreshed successfully',
        'total_jobs': len(jobs_data),
        'last_updated': last_updated
    })

if __name__ == '__main__':
    # Initial scrape
    scrape_jobs()
    
    # Start background scraping thread
    scraper_thread = threading.Thread(target=background_scraper, daemon=True)
    scraper_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
