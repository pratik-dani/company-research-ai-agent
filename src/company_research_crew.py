from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
# from crewai_tools import SerperDevTool, WikipediaTools
from src.company_research_tools import (
    CompanyNewsSearchTool,
    ProfessionalProfilesTool,
    LinkedInScraperTool,
    CrunchbaseScraperTool,
    PitchBookScraperTool,
    GoogleSearchTool,
)
from pydantic import ConfigDict
import os
from dotenv import load_dotenv
import logging
# Suppress warnings and tool output
logging.getLogger('crewai').setLevel(logging.ERROR)
os.environ['CREWAI_LOGGING'] = 'ERROR'

load_dotenv()

@CrewBase
class CompanyResearchCrew:
    """Crew for comprehensive company research"""
    
    def __init__(self, actor):
        self.actor = actor
        # Initialize Gemini LLM
        self.llm = LLM(
            model="gemini/gemini-2.0-flash-lite",
            temperature=0.7,
            api_key=os.getenv("GOOGLE_API_KEY"),  # Make sure to set this in your .env file
            verbose=False  # Suppress LLM output
        )
        super().__init__()
    
    @agent
    def researcher(self) -> Agent:
        return Agent(
            role="Company Research Specialist",
            goal="Gather comprehensive information about companies from various sources. Use the tools provided to gather information.",
            backstory="""You are an expert business researcher with years of experience
            in gathering and analyzing company information. You excel at finding accurate
            and relevant details about organizations, their products, and market presence.""",
            tools=[
                # SerperDevTool(),
                # WikipediaTools(),
                CompanyNewsSearchTool(actor=self.actor),
                ProfessionalProfilesTool(actor=self.actor),
                LinkedInScraperTool(actor=self.actor),
                CrunchbaseScraperTool(actor=self.actor),
                PitchBookScraperTool(actor=self.actor),
                GoogleSearchTool(actor=self.actor)
            ],
            llm=self.llm,
            verbose=False  # Suppress agent output
        )
    
    @agent
    def data_analyst(self) -> Agent:
        return Agent(
            role="Business Data Analyst",
            goal="Analyze company data and extract meaningful insights",
            backstory="""You are a skilled data analyst specializing in business metrics
            and market analysis. You have a strong background in interpreting company 
            performance data and identifying market trends.""",
            llm=self.llm,
            verbose=False  # Suppress agent output
        )
    
    @agent
    def content_compiler(self) -> Agent:
        return Agent(
            role="Business Report Writer",
            goal="Compile research findings into comprehensive, well-structured reports",
            backstory="""You are an experienced business writer who excels at organizing
            complex information into clear, actionable reports. You have a keen eye for
            important details and can present information in a professional format.""",
            llm=self.llm,
            verbose=False  # Suppress agent output
        )

    @task
    def research_company(self) -> Task:
        return Task(
            description="""Research the company using their domain name: {domain}. Focus on key insights about the company's:
                1. Overview and core business
                2. Products and services
                3. Market presence and performance
                4. Key personnel and organization
                5. Financial metrics and funding
                6. Technology stack and digital presence
                7. Recent developments and news
                8. Major Competitors""",
            expected_output="Detailed research findings covering all requested aspects",
            agent=self.researcher()
        )

    @task
    def analyze_data(self) -> Task:
        return Task(
            description="""Analyze the research findings to extract key insights about:
            1. business focus,
            2. product lineup,
            3. market and demographic details,
            4. funding rounds,
            5. notable executives,
            6. social media profiles,
            7. a list of major competitors
            """,
            expected_output="Analysis report with key business insights",
            agent=self.data_analyst()
        )

    @task
    def compile_report(self) -> Task:
        return Task(
            description="""Create a comprehensive report combining all research and analysis.
            Structure the information clearly and highlight key findings.""",
            expected_output="Final structured report in JSON format",
            agent=self.content_compiler()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.researcher(),
                self.data_analyst(),
                # self.content_compiler()
            ],
            tasks=[
                self.research_company(),
                self.analyze_data(),
                # self.compile_report()
            ],
            process=Process.sequential,
            verbose=True,  # Suppress crew output
            max_rpm=100,  # No rate limiting
            show_tools_output=False  # Suppress tools output
        ) 