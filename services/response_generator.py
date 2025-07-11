import asyncio
from typing import Dict, List, Any
import logging

# Updated imports for LangChain v0.3
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from services.policy_service import PolicyService
from services.cache_service import CacheService
from config.settings import settings

logger = logging.getLogger(__name__)

class ResponseGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )
        self.policy_service = PolicyService()
        self.cache_service = CacheService()
        
        self.system_prompt = """
        You are an intelligent email response assistant for a company. 
        Your job is to generate helpful, professional, and accurate email responses 
        based on company policies and the customer's inquiry.
        
        Guidelines:
        1. Always be professional and courteous
        2. Use relevant company policies to provide accurate information
        3. If you don't have specific information, acknowledge it and offer to help
        4. Keep responses concise but complete
        5. Include next steps when appropriate
        """
    
    async def generate_response(
        self, 
        subject: str, 
        body: str, 
        priority: str = "normal",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Generate intelligent email response"""
        try:
            # Check cache first
            cache_key = f"response_{hash(subject + body)}"
            if use_cache:
                cached_response = await self.cache_service.get(cache_key)
                if cached_response:
                    return cached_response
            
            # Search for relevant policies
            query = f"{subject} {body}"
            relevant_policies = await self.policy_service.search_policies(query)
            
            # Generate response using LLM
            response = await self._generate_llm_response(
                subject, body, relevant_policies, priority
            )
            
            result = {
                'response': response,
                'policies_used': [p['title'] for p in relevant_policies],
                'priority': priority
            }
            
            # Cache the response
            if use_cache:
                await self.cache_service.set(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def _generate_llm_response(
        self, 
        subject: str, 
        body: str, 
        policies: List[Dict[str, Any]], 
        priority: str
    ) -> str:
        """Generate response using language model"""
        try:
            # Prepare context from policies
            policy_context = ""
            if policies:
                policy_context = "\n\nRelevant Company Policies:\n"
                for policy in policies:
                    policy_context += f"- {policy['title']}: {policy['content']}\n"
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
                Email Subject: {subject}
                Email Body: {body}
                Priority: {priority}
                {policy_context}
                
                Please generate a professional email response based on the above information.
                """)
            ])
            
            # Generate response
            chain = prompt | self.llm
            response = await chain.ainvoke({})
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error in LLM response generation: {str(e)}")
            raise
