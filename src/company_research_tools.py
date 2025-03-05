from crewai.tools import BaseTool
from pydantic import Field, ConfigDict
from typing import Dict, List, Optional
from apify import Actor
import re
import validators
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

class CompanyNewsSearchTool(BaseTool):
    """Tool for searching recent company news articles"""
    name: str = "Company News Search"
    description: str = """
    Searches for and retrieves recent news articles about a company using its domain name.
    Returns articles with titles, URLs, descriptions, and publication dates.
    """
    actor: Actor = Field(description="Apify Actor instance")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, domain: str) -> List[Dict]:
        """Execute synchronously by creating a new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_run(domain))
        finally:
            loop.close()

    async def _async_run(self, domain: str) -> List[Dict]:
        """Async implementation of the tool"""
        company_name = domain.split('.')[0]
        search_query = f"{company_name} company news"
        
        run_input = {
            "queries": search_query,
            "maxPagesPerQuery": 2,
            "resultsPerPage": 5
        }
        
        actor_run = await self.actor.call(actor_id="apify/google-search-scraper", run_input=run_input)
        if actor_run is None:
            raise RuntimeError('Actor task failed to start.')
            
        run_client = self.actor.apify_client.run(actor_run.id)
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

class GoogleSearchTool(BaseTool):
    """Tool for searching recent company news articles"""
    name: str = "Google Search"
    description: str = """
    Searches google for a given query and returns the results
    """
    actor: Actor = Field(description="Apify Actor instance")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, query: str) -> List[Dict]:
        """Execute synchronously by creating a new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_run(query))
        finally:
            loop.close()

    async def _async_run(self, query: str) -> List[Dict]:
        """Async implementation of the tool"""
        search_query = f"{query}"
        
        run_input = {
            "queries": search_query,
            "maxPagesPerQuery": 2,
            "resultsPerPage": 5
        }
        
        actor_run = await self.actor.call(actor_id="apify/google-search-scraper", run_input=run_input)
        if actor_run is None:
            raise RuntimeError('Actor task failed to start.')
            
        run_client = self.actor.apify_client.run(actor_run.id)
        await run_client.wait_for_finish()
        dataset_client = run_client.dataset()
        items = await dataset_client.list_items()
        dataset_items = items.items
        return dataset_items
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

class ProfessionalProfilesTool(BaseTool):
    """Tool for finding company profiles on professional platforms"""
    name: str = "Professional Profiles Search"
    description: str = """
    Finds company profiles on LinkedIn, Crunchbase, and PitchBook using domain name.
    Returns profile URLs and descriptions for each platform.
    """
    actor: Actor = Field(description="Apify Actor instance")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, domain: str) -> Dict:
        """Execute synchronously by creating a new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_run(domain))
        finally:
            loop.close()

    async def _async_run(self, domain: str) -> Dict:
        """Async implementation of the tool"""
        # print(f"Searching profiles for domain: {domain}")
        search_queries = [
            f"site:crunchbase.com company {domain}",
            f"site:linkedin.com company {domain}",
            f"site:pitchbook.com company {domain}"
        ]
        
        run_input = {
            "queries": "\n".join(search_queries),
            "maxPagesPerQuery": 1,
            "resultsPerPage": 1
        }
        
        actor_run = await self.actor.call(actor_id="apify/google-search-scraper", run_input=run_input)
        if actor_run is None:
            raise RuntimeError('Actor task failed to start.')
            
        run_client = self.actor.apify_client.run(actor_run.id)
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

class LinkedInScraperTool(BaseTool):
    """Tool for scraping LinkedIn company profiles"""
    name: str = "LinkedIn Company Profile Scraper"
    description: str = """
    Scrapes detailed company information from LinkedIn company profiles.
    Requires a valid LinkedIn company profile URL.
    """
    actor: Actor = Field(description="Apify Actor instance")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, url: str) -> Dict:
        """Execute synchronously by creating a new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_run(url))
        finally:
            loop.close()

    async def _async_run(self, url: str) -> Dict:
        """Async implementation of the tool"""
        if not url:
            return {}
            
        run_input = {"url": url}

        actor_run = await self.actor.call(actor_id="pratikdani/linkedin-company-profile-scraper", run_input=run_input)
        if actor_run is None:
            raise RuntimeError('Actor task failed to start.')
            
        run_client = self.actor.apify_client.run(actor_run.id)
        await run_client.wait_for_finish()
        dataset_client = run_client.dataset()
        items = await dataset_client.list_items()
        items = items.items

        return {**items[0], "result_type": "linkedin"} if items else {"result_type": "linkedin"}

class CrunchbaseScraperTool(BaseTool):
    """Tool for scraping Crunchbase organization profiles"""
    name: str = "Crunchbase Organization Scraper"
    description: str = """
    Scrapes detailed company information from Crunchbase organization profiles.
    Requires a valid Crunchbase organization URL.
    """
    actor: Actor = Field(description="Apify Actor instance")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, url: str) -> Dict:
        """Execute synchronously by creating a new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_run(url))
        finally:
            loop.close()

    async def _async_run(self, url: str) -> Dict:
        """Async implementation of the tool"""
        if not url:
            return {}
        
        run_input = {"url": url}

        actor_run = await self.actor.call(actor_id="pratikdani/crunchbase-companies-scraper", run_input=run_input)
        if actor_run is None:
            raise RuntimeError('Actor task failed to start.')
            
        run_client = self.actor.apify_client.run(actor_run.id)
        await run_client.wait_for_finish()
        dataset_client = run_client.dataset()
        items = await dataset_client.list_items()
        items = items.items
        
        return {**items[0], "result_type": "crunchbase"} if items else {"result_type": "crunchbase"}

class PitchBookScraperTool(BaseTool):
    """Tool for scraping PitchBook company profiles"""
    name: str = "PitchBook Company Profile Scraper"
    description: str = """
    Scrapes detailed company information from PitchBook company profiles.
    Requires a valid PitchBook company profile URL.
    """
    actor: Actor = Field(description="Apify Actor instance")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, url: str) -> Dict:
        """Execute synchronously by creating a new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_run(url))
        finally:
            loop.close()

    async def _async_run(self, url: str) -> Dict:
        """Async implementation of the tool"""
        if not url:
            return {"profile_url": ""}

        run_input = {"url": url}
        
        actor_run = await self.actor.call(actor_id="pratikdani/pitchbook-companies-scraper", run_input=run_input)
        if actor_run is None:
            raise RuntimeError('Actor task failed to start.')
            
        run_client = self.actor.apify_client.run(actor_run.id)
        await run_client.wait_for_finish()
        dataset_client = run_client.dataset()
        items = await dataset_client.list_items()
        items = items.items
        
        return {**items[0], "result_type": "pitchbook"} if items else {"result_type": "pitchbook"} 