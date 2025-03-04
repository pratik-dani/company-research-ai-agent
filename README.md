# Company Research & Analysis Actor

## Overview
This actor performs comprehensive company research and analysis by aggregating data from multiple authoritative sources including LinkedIn, PitchBook, and Crunchbase. It collects detailed information about company profiles, financials, key personnel, market presence, investments, competitors, and recent developments. The consolidated data provides valuable insights for business intelligence, market research, competitive analysis, and investment decision making.

## Key Features
- Comprehensive company profiles with detailed information about operations, products, and services
- Real-time financial metrics including stock data, revenue, and funding history
- Competitive intelligence with identified competitors, market positioning, and industry analysis
- Social media presence and engagement metrics across major platforms
- Recent news and developments affecting the company
- Generated summary report with key insights and analysis

## Usage Scenarios
- Due diligence research for mergers, acquisitions, and investments
- Competitive analysis and market intelligence gathering
- Lead generation and business development prospecting
- Investment research and analysis for financial institutions
- Industry and market trend analysis
- Recruitment and talent acquisition research

## Output Fields

| Field Name | Type | Description |
|------------|------|-------------|
| domain | string | Domain name of the company being researched |
| recent_news | array | Latest news articles about the company with title, URL, description and key highlights |
| linkedin_data | object | Comprehensive LinkedIn profile data including employee count, followers, locations, job openings, and company description |
| pitchbook_data | object | Detailed investment data including funding rounds, investors, acquisitions, and competitor analysis |
| funding_analysis | object | Analysis of total funds raised, funding rounds timeline, and investment trends |
| generated_report | string | Markdown formatted comprehensive report summarizing key findings and insights |
| data_collection_date | string | Timestamp indicating when the data was collected |
| linkedin_url | string | URL to company's LinkedIn profile |
| pitchbook_url | string | URL to company's PitchBook profile |
| crunchbase_url | string | URL to company's Crunchbase profile |

## Input Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|-----------|
| domain | string | Domain name of the company to research (e.g., apple.com) | Yes |
| google_gemini_api_key | string | API key for accessing the Google Gemini API | Yes |


Uses these actors on Apify:
- https://apify.com/apify/google-search-scraper
- https://apify.com/pratikdani/linkedin-company-profile-scraper
- https://apify.com/pratikdani/crunchbase-companies-scraper
- https://apify.com/pratikdani/pitchbook-companies-scraper


## Sample Output



## Apify Company Report - March 4, 2025

This report provides an overview of Apify, a web scraping and automation platform, based on available data as of March 4, 2025.

**1. Overview and Core Business**

*   **Description:** Apify is a full-stack web scraping and browser automation platform that enables users to extract data from websites and automate workflows.  It allows users to turn any website into an API.
*   **Mission:** To make the web more open and programmable.
*   **Founded:** 2015
*   **Headquarters:** Prague, Czech Republic
*   **Industry:** Internet Software, Software Development
*   **Core Business:** Providing a platform and tools for web scraping, data extraction, and workflow automation.

**2. Products and Services**

*   **Apify Platform:** A cloud-based platform for developing, running, and managing web scraping solutions.
*   **Apify Actors:** Serverless microapps that can be developed, run, shared, and integrated.
*   **Crawlee:** A library for building reliable web scrapers in Node.js, supporting both JavaScript and Python.
*   **Apify Proxy:** Offers a pool of datacenter and residential proxies with smart IP address rotation.
*   **Apify Storage:** Enables storing and sharing structured data or binary files, with support for various export formats.
*   **Pre-built Actors (Scrapers):** Offerings such as Amazon Product Scraper and YouTube crawler and video scraper.

**3. Market Presence and Performance**

*   **Target Audience:** Businesses and developers needing web data extraction and automation capabilities.
*   **Monthly Website Visits:** 1,438,340 (as of the last update)
*   **Website Traffic Growth:** Monthly visits have increased by 12.97%
*   **Global Traffic Rank:** 44,654
*   **Key Regions for Website Traffic:** United States, India, Bolivia, Kenya, Philippines
*   **Competitors:** Octoparse, PhantomBuster, Mozenda, Diffbot, ScrapingBee

**4. Key Personnel and Organization**

*   **Company Type:** Privately Held, Venture Capital-Backed
*   **Employees:** Between 101-250 employees (LinkedIn data shows 126, Pitchbook data shows 113).
*   **Key Personnel:**
    *   **Jan Čurn:** Founder and CEO
    *   **Jakub Balada:** Founder
    *   **Marek Trunkat:** CTO
    *   **Dusan Antos:** CFO
    *    **Adam Kliment:** VP of Developer Experience

**5. Financial Metrics and Funding**

*   **Financing Status:** Venture Capital-Backed
*   **Total Funding Raised:** $3,486,941
*   **Funding Rounds:** 5 rounds
*   **Last Round:** Series Unknown - €2.8M (approximately $3M USD) - April 15, 2024, led by J&T Ventures with participation from Reflex Capital.
*   **Investors:** J&T Ventures, Reflex Capital, INCOMMING Ventures, Y Combinator
*   **No patent granted. But 2 trademark registered**

**6. Technology Stack and Digital Presence**

*   **Technology Stack:** Utilizes a modern technology stack (75 technologies identified by BuiltWith).
*   **Key Technologies:** IPhone / Mobile Compatible, Viewport Meta, Common Crawl, Google Tag Manager, Apple Mobile Web Clips Icon, HSTS, DNSSEC, Content Delivery Network, LetsEncrypt.
*   **Social Media:** Active on LinkedIn, Twitter, and Facebook.
*   **LinkedIn Followers:** 10,129+
*   **Blog:** Active blog presence on Apify website with regular updates on platform features, AI agents, and related topics.
*  **Observability Migration**: Transitioned from NewRelic to a self-hosted Grafana setup for cost savings and flexibility.
* Apify integrates with Amazon Bedrock Agents for web data accessibility.

**7. Recent Developments and News**

*   **Funding:** Secured approximately $3 million in funding in April 2024 from J&T Ventures and Reflex Capital.
*   **Product Launch:** Launched Crawlee for Python in July 2024.
*   **G2 Recognition:** Named a Top 50 Best IT Management Software Product by G2 in 2025 based on user feedback.
*   **AI Integration:** Focusing on integration with AI agents and large language models (LLMs).
*   **Community Engagement:** Active participation in developer communities, such as PyCon Namibia.
*   **New Social Media Presence:** Landed on Bluesky to increase community engagement.
*   **Recent Blog Posts:** Focus on AI agents and Web Data Accessibility for AI agents

**Summary and Key Insights**

Apify is a growing company in the web scraping and automation space. It has a strong technology platform, a growing user base, and is focused on integrating with emerging technologies like AI agents.  Recent funding and product launches suggest a period of expansion and innovation.  The company's focus on developer experience and community engagement is a positive indicator for future growth.
