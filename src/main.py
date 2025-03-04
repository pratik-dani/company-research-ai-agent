"""This module defines the main entry point for the Company Research Apify Actor.

This actor gathers comprehensive information about a company based on its domain name,
including focus areas, products, markets, key personnel, and more.
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
load_dotenv()

async def get_pitchbook_profile(Actor, url: str) -> Dict:
    """Get basic PitchBook profile info if available."""
    if not url:
        return {"profile_url": ""}

    run_input = {
        "url": url,
    }
    
    # run = client.actor("pratikdani/pitchbook-companies-scraper")
    # run = run.call(run_input=run_input)
    # items = client.dataset(run["defaultDatasetId"]).list_items().items

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
    """Validate and clean the input domain."""
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
    """Get recent news articles about the company using Google Search Scraper."""
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
    # Proper async execution chain
    # try:
    # actor_call = client.actor("apify/google-search-scraper")
    
    # run = actor_call.call(run_input=run_input)
    # dataset = client.dataset(run["defaultDatasetId"])
    # # print(dataset.list_items().items)
    # dataset_items = dataset.list_items().items

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
    # except Exception as e:
    #     Actor.log.error(f"News collection failed: {str(e)}")
    #     return []

async def get_professional_profiles(Actor, domain: str) -> Dict:  # Changed to async client
    """Find professional platform profiles using targeted Google searches."""
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
    
    # try:
    # Proper async execution chain
    # actor_call = client.actor("apify/google-search-scraper")
    # run = actor_call.call(run_input=run_input)
    # dataset = client.dataset(run["defaultDatasetId"])
    # dataset_items = dataset.list_items().items

    actor_run = await Actor.call(actor_id="apify/google-search-scraper", run_input=run_input)
    if actor_run is None:
        raise RuntimeError('Actor task failed to start.')
    run_client = Actor.apify_client.run(actor_run.id)
    await run_client.wait_for_finish()
    dataset_client = run_client.dataset()
    items = await dataset_client.list_items()
    dataset_items = items.items


    results = [j for j in [s.get('organicResults', [])[0] for s in dataset_items]]
    # print(results)

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
    
    # except Exception as e:
    #     Actor.log.error(f"Profile detection failed: {str(e)}")
    #     return {}

def get_funding_timeline(crunchbase_data: Dict) -> List[Dict]:
    """Structure funding data into timeline format"""
    timeline = []
    for round_info in crunchbase_data.get('funding_rounds_list', []):
        # print(round_info)
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
    """Scrape LinkedIn company profile with enhanced employee data."""
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

    
    # run = client.actor("pratikdani/linkedin-company-profile-scraper")
    # run = run.call(run_input=run_input)
    # items = client.dataset(run["defaultDatasetId"]).list_items().items
    # print(items)
    return {**items[0], "result_type": "linkedin"} if items else {"result_type": "linkedin"}

async def scrape_crunchbase_org(Actor, url: str) -> Dict:
    """Scrape Crunchbase with detailed funding analysis."""
    if not url:
        return {}
    
    run_input = {
        "url": url
        # "maxDepth": 1,
        # "proxyConfiguration": {"useApifyProxy": True}
    }

    actor_run = await Actor.call(actor_id="pratikdani/crunchbase-companies-scraper", run_input=run_input)
    if actor_run is None:
        raise RuntimeError('Actor task failed to start.')
    run_client = Actor.apify_client.run(actor_run.id)
    await run_client.wait_for_finish()
    dataset_client = run_client.dataset()
    items = await dataset_client.list_items()
    items = items.items
    
    # run = client.actor("pratikdani/crunchbase-companies-scraper")
    # run = run.call(run_input=run_input)
    # items = client.dataset(run["defaultDatasetId"]).list_items().items
    # print(items)
    return {**items[0], "result_type": "crunchbase"} if items else {"result_type": "crunchbase"}

    # results = items[1]['organicResults']

def generate_company_report(data: Dict) -> str:
    """Generate a comprehensive company report using Google's LLM."""
    # try:
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
    # model = "gemini-2.0-pro-exp-02-05"
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
        # max_tokens=2000
    )
    
    response = client.models.count_tokens(
        model=model,
        contents=report
    )
    output_tokens = response.total_tokens
    tokens_used = input_tokens + output_tokens
    return report, tokens_used
    # except Exception as e:
    #     Actor.log.error(f"Report generation failed: {str(e)}")
    #     return "Error generating report"

def sanitize_data(obj, seen=None):
    """
    Remove circular references from the data structure
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

async def main() -> None:
    """Main entry point for the Company Research Actor."""
    async with Actor:
        # Get input and validate
        actor_input = await Actor.get_input() or {}
        domain = actor_input.get('domain', '')

        # Validate domain
        try:
            domain = await validate_domain(domain)
            Actor.log.info(f'Starting company research for domain: {domain}')
        except ValueError as e:
            Actor.log.error(f"Domain validation failed: {str(e)}")
            await Actor.push_data({
                "status": "error",
                "message": str(e)
            })
        
        # Gather company information from multiple sources
        try:
            # Get recent news
            # Create tasks for parallel execution
            news_task = asyncio.create_task(get_company_news(Actor, domain))
            profiles_task = asyncio.create_task(get_professional_profiles(Actor, domain))

            # Wait for both tasks to complete
            news_articles, professional_profiles = await asyncio.gather(news_task, profiles_task)

            Actor.log.info(f'Collected {len(news_articles)} news articles')
            Actor.log.info(f'Found total social profiles: {len(professional_profiles)}')

            # Compile final results
            result = {
                "domain": domain,
                "recent_news": news_articles,
            }


            # Prepare tasks for parallel execution
            tasks = []
            if professional_profiles.get('linkedin'):
                tasks.append(scrape_linkedin_company(Actor, professional_profiles['linkedin']))
            if professional_profiles.get('crunchbase'):
                tasks.append(scrape_crunchbase_org(Actor, professional_profiles['crunchbase']))
            if professional_profiles.get('pitchbook'):
                tasks.append(get_pitchbook_profile(Actor, professional_profiles['pitchbook']))

            # Run tasks in parallel
            results = await asyncio.gather(*tasks)

            # Process results
            linkedin_data, crunchbase_data, pitchbook_data = {}, {}, {}
            for result in results:
                if isinstance(result, dict):
                    result_type = result.get('result_type', None)
                    if result_type == "linkedin":
                        linkedin_data = result
                        Actor.log.info('LinkedIn data collection complete')
                    elif result_type == "crunchbase":
                        crunchbase_data = result
                        crunchbase_data['funding_timeline'] = get_funding_timeline(crunchbase_data)
                        Actor.log.info(f'Crunchbase data collected with {len(crunchbase_data.get("funding_timeline", []))} funding rounds')
                    elif result_type == "pitchbook":
                        pitchbook_data = result
                        Actor.log.info('Pitchbook data collection complete')
            # print(pitchbook_data)
            # Log if any data wasn't collected
            if not linkedin_data:
                Actor.log.info('No LinkedIn profile found or data collection failed')
            if not crunchbase_data:
                Actor.log.info('No Crunchbase profile found or data collection failed')
            if not pitchbook_data:
                Actor.log.info('No Pitchbook profile found or data collection failed')

            # Compile final results with new data
            result.update({
                "linkedin_url": professional_profiles.get('linkedin', ''),
                "pitchbook_url": professional_profiles.get('pitchbook', ''),
                "crunchbase_url": professional_profiles.get('crunchbase', ''),
                "linkedin_data": linkedin_data,
                "pitchbook_data": pitchbook_data,
                "crunchbase_data": crunchbase_data,
                "funding_analysis": {
                    "total_raised": sum(round['amount'] for round in crunchbase_data.get('funding_timeline', [])),
                    "rounds": crunchbase_data.get('funding_timeline', []),
                    "valuation": crunchbase_data.get('key_metrics', {}).get('valuation')
                }
            })

            # Generate company report
            Actor.log.info('Generating comprehensive company report...')
            report, tokens_used = generate_company_report(result)
            result['generated_report'] = report
            Actor.log.info('Report generation complete')
            await Actor.charge(event_name="generate_report")

            # await Actor.push_data(result)
            report = {
                "domain": domain,
                "generated_report": report
            }
            await Actor.push_data(report)
            Actor.log.info('Company research completed successfully')
        
        except Exception as e:
            Actor.log.error(f'Error during company research: {str(e)}')
            import traceback
            Actor.log.error(f'Traceback: {traceback.format_exc()}')
            await Actor.push_data({
                "status": "error",
                "message": str(e)
            })

