"""This module defines the main entry point for the Company Research Apify Actor.

This actor gathers comprehensive information about a company based on its domain name,
including focus areas, products, markets, key personnel, and more.

The actor coordinates multiple data sources and Apify actors to collect:
- Company profiles from LinkedIn, Crunchbase, and PitchBook
- Recent news articles via Google Search
- Funding history and financial metrics
- Key personnel information
- Market presence and competitors

The collected data is processed and analyzed to generate a comprehensive company report
using Google's LLM.

Key Functions:
- validate_domain: Validates and cleans input domain name
- get_company_news: Retrieves recent news articles about the company
- get_professional_profiles: Finds company profiles on professional platforms
- scrape_linkedin_company: Extracts data from LinkedIn company profile
- scrape_crunchbase_org: Collects funding and company data from Crunchbase
- get_pitchbook_profile: Gathers company information from PitchBook
- generate_company_report: Creates comprehensive report using LLM
- get_funding_timeline: Structures funding data chronologically
- sanitize_data: Removes circular references from data structures
"""

from apify import Actor
import validators
import asyncio
import re
from typing import Dict, List
from datetime import datetime
import json
from tools.llm_api import create_llm_client
from dotenv import load_dotenv
import os
from src.company_research_crew import CompanyResearchCrew
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

async def get_pitchbook_profile(Actor, url: str) -> Dict:
    """Get basic PitchBook profile info if available.
    
    Args:
        Actor: Apify Actor instance
        url: PitchBook company profile URL
        
    Returns:
        Dict containing PitchBook profile data or empty dict if not found
    """
    if not url:
        return {"profile_url": ""}

    run_input = {
        "url": url,
    }
    
    actor_run = await Actor.call(actor_id="pratikdani/pitchbook-companies-scraper", run_input=run_input)
    if actor_run is None:
        raise RuntimeError('Actor task failed to start.')
    run_client = Actor.apify_client.run(actor_run.id)
    await run_client.wait_for_finish()
    dataset_client = run_client.dataset()
    items = await dataset_client.list_items()
    items = items.items
    # print(items)
    return {**items[0], "result_type": "pitchbook"} if items else {"result_type": "pitchbook"}

async def validate_domain(domain: str) -> str:
    """Validate and clean the input domain.
    
    Args:
        domain: Raw domain name input
        
    Returns:
        Cleaned and validated domain name
        
    Raises:
        ValueError: If domain is invalid or empty
    """
    if not domain:
        raise ValueError("Domain is required")
    
    # Remove protocol and www if present
    domain = re.sub(r'^(https?://)?(www\.)?', '', domain.lower())
    
    # Remove trailing path and query parameters
    domain = domain.split('/')[0]
    
    if not validators.domain(domain):
        raise ValueError(f"Invalid domain: {domain}")
    
    return domain

async def get_company_news(Actor, domain: str) -> List[Dict]:
    """Get recent news articles about the company using Google Search Scraper.
    
    Args:
        Actor: Apify Actor instance
        domain: Company domain name
        
    Returns:
        List of dicts containing news article details:
        - title: Article title
        - url: Article URL
        - description: Article snippet
        - emphasized_keywords: Highlighted terms
        - date: Publication date
    """
    company_name = domain.split('.')[0]
    search_query = f"{company_name} company news"
    
    run_input = {
        "queries": search_query,  # Must be a list of queries
        "maxPagesPerQuery": 2,
        "resultsPerPage": 5
    }
    actor_run = await Actor.call(actor_id="apify/google-search-scraper", run_input=run_input)
    if actor_run is None:
        raise RuntimeError('Actor task failed to start.')
    run_client = Actor.apify_client.run(actor_run.id)
    await run_client.wait_for_finish()
    dataset_client = run_client.dataset()
    items = await dataset_client.list_items()
    dataset_items = items.items
    results = dataset_items[1]['organicResults']
    news_articles = []
    for item in results:
        if item.get("title") and item.get("url"):
            news_articles.append({
                "title": item["title"],
                "url": item["url"],
                "description": item.get("description", ""),
                "emphasized_keywords": item.get("emphasizedKeywords", []),
                "date": item.get("date", "")
            })
    return news_articles[:]

async def get_professional_profiles(Actor, domain: str) -> Dict:  # Changed to async client
    """Find professional platform profiles using targeted Google searches.
    
    Args:
        Actor: Apify Actor instance
        domain: Company domain name
        
    Returns:
        Dict containing:
        - linkedin: LinkedIn company profile URL
        - crunchbase: Crunchbase profile URL
        - pitchbook: PitchBook profile URL
        - *_description: Profile descriptions for each platform
    """
    search_queries = [
        f"site:crunchbase.com company {domain}",
        f"site:linkedin.com company {domain}",
        f"site:pitchbook.com company {domain}"
    ]
    
    run_input = {
        "queries": "\n".join(search_queries),  # Should be a list, not joined string
        "maxPagesPerQuery": 1,
        "resultsPerPage": 1
    }
    
    actor_run = await Actor.call(actor_id="apify/google-search-scraper", run_input=run_input)
    if actor_run is None:
        raise RuntimeError('Actor task failed to start.')
    run_client = Actor.apify_client.run(actor_run.id)
    await run_client.wait_for_finish()
    dataset_client = run_client.dataset()
    items = await dataset_client.list_items()
    dataset_items = items.items


    results = [j for j in [s.get('organicResults', [])[0] for s in dataset_items]]

    profiles = {
        "linkedin": "",
        "crunchbase": "",
        "pitchbook": ""
    }
    
    platform_patterns = {
        "linkedin": r"linkedin\.com/company/[^/]+",
        "crunchbase": r"crunchbase\.com/organization/[^/]+",
        "pitchbook": r"pitchbook\.com/profiles/company/[^/]+"
    }
    
    for item in results:
        url = item.get('url', '').lower()
        for platform, pattern in platform_patterns.items():
            if re.search(pattern, url) and not profiles[platform]:
                profiles[platform] = url
                profiles[f'{platform}_description'] = item.get('description', '')
                break
    
    return profiles

def get_funding_timeline(crunchbase_data: Dict) -> List[Dict]:
    """Structure funding data into timeline format.
    
    Args:
        crunchbase_data: Raw Crunchbase company data
        
    Returns:
        List of funding rounds sorted by date:
        - date: ISO format date
        - amount: Funding amount in USD
        - investors: List of lead investors
    """
    timeline = []
    for round_info in crunchbase_data.get('funding_rounds_list', []):
        try:
            timeline.append({
                "date": datetime.strptime(round_info['announced_on'], '%Y-%m-%d').isoformat(),
                "amount": float(round_info.get('money_raised', {}).get('value_usd', 0)),
                "investors": [i.get('names', None) for i in round_info.get('lead_investors', [])]
            })
        except (KeyError, ValueError):
            continue
    return sorted(timeline, key=lambda x: x['date'])

async def scrape_linkedin_company(Actor, url: str) -> Dict:
    """Scrape LinkedIn company profile with enhanced employee data.
    
    Args:
        Actor: Apify Actor instance
        url: LinkedIn company profile URL
        
    Returns:
        Dict containing LinkedIn profile data or empty dict if not found
    """
    if not url:
        return {}
        
    run_input = {
        "url": url
    }

    actor_run = await Actor.call(actor_id="pratikdani/linkedin-company-profile-scraper", run_input=run_input)
    if actor_run is None:
        raise RuntimeError('Actor task failed to start.')
    run_client = Actor.apify_client.run(actor_run.id)
    await run_client.wait_for_finish()
    dataset_client = run_client.dataset()
    items = await dataset_client.list_items()
    items = items.items

    return {**items[0], "result_type": "linkedin"} if items else {"result_type": "linkedin"}

async def scrape_crunchbase_org(Actor, url: str) -> Dict:
    """Scrape Crunchbase with detailed funding analysis.
    
    Args:
        Actor: Apify Actor instance
        url: Crunchbase organization URL
        
    Returns:
        Dict containing Crunchbase profile data or empty dict if not found
    """
    if not url:
        return {}
    
    run_input = {
        "url": url
    }

    actor_run = await Actor.call(actor_id="pratikdani/crunchbase-companies-scraper", run_input=run_input)
    if actor_run is None:
        raise RuntimeError('Actor task failed to start.')
    run_client = Actor.apify_client.run(actor_run.id)
    await run_client.wait_for_finish()
    dataset_client = run_client.dataset()
    items = await dataset_client.list_items()
    items = items.items
    
    return {**items[0], "result_type": "crunchbase"} if items else {"result_type": "crunchbase"}

def generate_company_report(data: Dict) -> str:
    """Generate a comprehensive company report using Google's LLM.
    
    Args:
        data: Collected company data from all sources
        
    Returns:
        Tuple containing:
        - Generated markdown report
        - Number of tokens used
    """
    from tools.llm_api import query_llm
    google_gemini_api_key = os.getenv('GOOGLE_API_KEY')
    sanitized_data = sanitize_data(data)

    prompt = f"""You are a business analyst. Generate a comprehensive company report based on the following data. 
    Focus on key insights about the company's:
    1. Overview and core business
    2. Products and services
    3. Market presence and performance
    4. Key personnel and organization
    5. Financial metrics and funding
    6. Technology stack and digital presence
    7. Recent developments and news
    
    Make it professional but easy to read. Use bullet points where appropriate. Give the report in a markdown format. Only give the report, no other text.
    
    Data: {json.dumps(sanitized_data, indent=2)}
    """
    model = "gemini-2.0-flash"
    client = create_llm_client(provider="gemini", google_gemini_api_key=google_gemini_api_key)
    response = client.models.count_tokens(
        model=model,
        contents=prompt
    )
    input_tokens = response.total_tokens
    report = query_llm(
        prompt=prompt,
        provider="gemini",
        model=model,
        google_gemini_api_key=google_gemini_api_key,
    )
    
    response = client.models.count_tokens(
        model=model,
        contents=report
    )
    output_tokens = response.total_tokens
    tokens_used = input_tokens + output_tokens
    return report, tokens_used

def sanitize_data(obj, seen=None):
    """Remove circular references from the data structure.
    
    Args:
        obj: Input data structure to sanitize
        seen: Set of object IDs already processed (for recursion)
        
    Returns:
        Sanitized data structure with circular references removed
    """
    if seen is None:
        seen = set()
        
    if isinstance(obj, dict):
        # Create new dict with sanitized items
        return {
            key: sanitize_data(value, seen | {id(obj)})
            for key, value in obj.items()
            if id(value) not in seen
        }
    elif isinstance(obj, (list, tuple, set)):
        # Create new list/tuple/set with sanitized items
        return type(obj)(
            sanitize_data(item, seen | {id(obj)})
            for item in obj
            if id(item) not in seen
        )
    else:
        # Return non-container objects as-is
        return obj

import re
def extract_dict_from_json(json_str: str) -> Dict:
    """Extract a dictionary from a JSON string.
    
    Args:
        json_str: JSON string to extract dictionary from
    
    Returns:
        Dictionary containing the extracted data
    """
    try:
        json_string = re.search(r'```json(.*)```', json_str, re.DOTALL).group(1)
        return json.loads(json_string)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON string")

async def main() -> None:
    """Main entry point for the Company Research Actor.
    
    Coordinates the collection and processing of company data from multiple sources:
    1. Validates input domain
    2. Collects news articles and professional profiles
    3. Scrapes detailed data from LinkedIn, Crunchbase and PitchBook
    4. Generates comprehensive company report
    5. Handles errors and pushes results to output
    """
    async with Actor as actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        domain = actor_input.get('domain')
        # print(domain)
        
        if not domain:
            raise ValueError("Domain name is required")

        domain = await validate_domain(domain)

        # Initialize and run the CrewAI crew with the actor instance
        research_crew = CompanyResearchCrew(actor=actor)
        result = research_crew.crew().kickoff(inputs={'domain': domain})
        response = {
            "domain": domain,
            "report": result,
        }
        dataset = await Actor.open_dataset(name='agent-data')
        await dataset.push_data(response)
        await dataset.export_to(
            key="company-report.csv",
            format="csv",
            include_content=True,
            to_key_value_store_name='agent-data'
        )

        # result = extract_dict_from_json(result)
        # Save the results
        await Actor.push_data(response)
        
        # Log completion
        Actor.log.info("Company research completed successfully")

