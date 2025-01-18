import google.generativeai as genai
from typing import List, Dict
import json
import os
import asyncio

class IndustryResearchAgent:
    def __init__(self, model):
        self.model = model
    
    async def research_company(self, company_name: str) -> Dict:
        prompt = f"""
        Provide a comprehensive analysis of {company_name} including:
        1. Industry sector and main business areas
        2. Key products and services
        3. Strategic focus areas
        4. Current technological infrastructure
        5. Main operational challenges
        
        Return your response in this exact JSON format:
        {{
            "industry_sector": "description here",
            "products_and_services": "description here",
            "strategic_focus": "description here",
            "tech_infrastructure": "description here",
            "operational_challenges": "description here"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Find JSON content between curly braces
            response_text = response.text
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                # Fallback structure if JSON parsing fails
                return {
                    "industry_sector": response_text,
                    "products_and_services": "",
                    "strategic_focus": "",
                    "tech_infrastructure": "",
                    "operational_challenges": ""
                }
        except Exception as e:
            print(f"Error in research_company: {str(e)}")
            print(f"Raw response: {response.text}")
            # Return a structured fallback response
            return {
                "industry_sector": "Error processing response",
                "products_and_services": "",
                "strategic_focus": "",
                "tech_infrastructure": "",
                "operational_challenges": ""
            }

class UseCaseGenerationAgent:
    def __init__(self, model):
        self.model = model
    
    async def generate_use_cases(self, company_analysis: Dict) -> List[Dict]:
        prompt = f"""
        Based on this company analysis:
        {json.dumps(company_analysis, indent=2)}
        
        Generate 5 specific AI/ML use cases that could benefit this company.
        
        Return your response in this exact JSON format:
        [
            {{
                "title": "Use Case Title",
                "description": "Detailed description",
                "benefits": "Expected benefits",
                "complexity": "High/Medium/Low",
                "roi_impact": "Potential ROI impact",
                "technologies": "Required AI/ML technologies"
            }}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                # Fallback structure
                return [{
                    "title": "Error processing response",
                    "description": response_text,
                    "benefits": "",
                    "complexity": "",
                    "roi_impact": "",
                    "technologies": ""
                }]
        except Exception as e:
            print(f"Error in generate_use_cases: {str(e)}")
            print(f"Raw response: {response.text}")
            return [{
                "title": "Error processing response",
                "description": "Failed to generate use cases",
                "benefits": "",
                "complexity": "",
                "roi_impact": "",
                "technologies": ""
            }]

class ResourceAssetAgent:
    def __init__(self, model):
        self.model = model
        
    async def collect_resources(self, use_cases: List[Dict]) -> Dict:
        resources = {}
        for use_case in use_cases:
            prompt = f"""
            For this AI/ML use case:
            {json.dumps(use_case, indent=2)}
            
            Find relevant resources and return them in this exact JSON format:
            {{
                "github_repositories": ["repo1 with link", "repo2 with link"],
                "datasets": ["dataset1 with link", "dataset2 with link"],
                "research_papers": ["paper1 with link", "paper2 with link"]
            }}
            """
            
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = response_text[start:end]
                    resources[use_case['title']] = json.loads(json_str)
                else:
                    resources[use_case['title']] = {
                        "github_repositories": [],
                        "datasets": [],
                        "research_papers": []
                    }
            except Exception as e:
                print(f"Error collecting resources for {use_case['title']}: {str(e)}")
                print(f"Raw response: {response.text}")
                resources[use_case['title']] = {
                    "github_repositories": [],
                    "datasets": [],
                    "research_papers": []
                }
            
        return resources


class AIUseCaseGenerator:
    def __init__(self, google_api_key: str):
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        self.research_agent = IndustryResearchAgent(self.model)
        self.use_case_agent = UseCaseGenerationAgent(self.model)
        self.resource_agent = ResourceAssetAgent(self.model)
        
    async def generate_proposal(self, company_name: str) -> Dict:
        try:
            company_analysis = await self.research_agent.research_company(company_name)
            
            use_cases = await self.use_case_agent.generate_use_cases(company_analysis)
            
            resources = await self.resource_agent.collect_resources(use_cases)
            
            # Create final proposal
            proposal = {
                "company_analysis": company_analysis,
                "use_cases": use_cases,
                "resources": resources
            }
            
            # Save proposal
            self._save_proposal_markdown(proposal, company_name)
            self._save_proposal_json(proposal, company_name)
            
            return proposal
            
        except Exception as e:
            print(f"Error generating proposal: {str(e)}")
            raise
    
    def _save_proposal_markdown(self, proposal: Dict, company_name: str):
        markdown_content = f"""
        # AI Use Case Proposal for {company_name}

        ## Company Analysis
        {self._format_section(proposal['company_analysis'])}

        ## Recommended Use Cases
        {self._format_use_cases(proposal['use_cases'])}

        ## Resources & References
        {self._format_resources(proposal['resources'])}
        """
        
        with open(f"{company_name}_proposal.md", "w") as f:
            f.write(markdown_content)

    def _save_proposal_json(self, proposal: Dict, company_name: str):
        with open(f"{company_name}_proposal.json", "w") as f:
            json.dump(proposal, f, indent=2)

    def _format_section(self, section: Dict) -> str:
        markdown = ""
        for key, value in section.items():
            markdown += f"### {key.title()}\n{value}\n\n"
        return markdown

    def _format_use_cases(self, use_cases: List[Dict]) -> str:
        markdown = ""
        for use_case in use_cases:
            markdown += f"### {use_case['title']}\n"
            markdown += f"**Description:** {use_case['description']}\n\n"
            markdown += f"**Benefits:** {use_case['benefits']}\n\n"
            markdown += f"**Complexity:** {use_case['complexity']}\n\n"
            markdown += f"**ROI Impact:** {use_case['roi_impact']}\n\n"
            markdown += f"**Technologies:** {use_case['technologies']}\n\n"
            markdown += "---\n\n"
        return markdown

    def _format_resources(self, resources: Dict) -> str:
        markdown = ""
        for use_case_title, resource_data in resources.items():
            markdown += f"### Resources for {use_case_title}\n\n"
            for category, links in resource_data.items():
                markdown += f"#### {category}\n"
                if isinstance(links, list):
                    for link in links:
                        markdown += f"- {link}\n"
                else:
                    markdown += f"{links}\n"
            markdown += "\n"
        return markdown

async def main():
    try:
        google_api_key = os.getenv('google_api_key')
        generator = AIUseCaseGenerator(google_api_key)
        company_name = "Seagate"
        proposal = await generator.generate_proposal(company_name)
        print(f"Proposal generated for {company_name}!")
        print(f"Files saved: {company_name}_proposal.md and {company_name}_proposal.json")
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())