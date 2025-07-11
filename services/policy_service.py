import asyncio
import json
from typing import List, Dict, Any, Optional
import logging

# Updated imports for LangChain v0.3
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config.settings import settings

logger = logging.getLogger(__name__)

class PolicyService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.vector_store = None
        self.policies = []
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    async def load_policies(self):
        """Load company policies from storage"""
        try:
            # Load default policies
            await self._load_default_policies()
            
            # Initialize vector store
            if self.policies:
                documents = []
                for policy in self.policies:
                    chunks = self.text_splitter.split_text(policy['content'])
                    for chunk in chunks:
                        documents.append(Document(
                            page_content=chunk,
                            metadata={
                                'title': policy['title'],
                                'category': policy['category'],
                                'keywords': policy['keywords']
                            }
                        ))
                
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                logger.info(f"Loaded {len(self.policies)} policies")
            
        except Exception as e:
            logger.error(f"Error loading policies: {str(e)}")
            raise
    
    async def _load_default_policies(self):
        """Load default company policies"""
        default_policies = [
            {
                'id': 'refund_policy',
                'title': 'Refund Policy',
                'content': '''
                Our refund policy allows customers to request refunds within 30 days of purchase.
                Refunds are processed within 5-7 business days. Digital products are non-refundable
                unless there is a technical issue. For subscription services, refunds are prorated
                based on usage.
                ''',
                'category': 'billing',
                'keywords': ['refund', 'money back', 'return', 'billing']
            },
            {
                'id': 'support_hours',
                'title': 'Support Hours',
                'content': '''
                Our customer support team is available Monday through Friday, 9 AM to 6 PM EST.
                For urgent technical issues, we provide 24/7 support through our emergency hotline.
                Response times are typically within 2 hours during business hours and 24 hours
                outside business hours.
                ''',
                'category': 'support',
                'keywords': ['support', 'hours', 'contact', 'help']
            },
            {
                'id': 'shipping_policy',
                'title': 'Shipping Policy',
                'content': '''
                We offer free shipping on orders over $50. Standard shipping takes 3-5 business days.
                Express shipping is available for an additional fee and takes 1-2 business days.
                International shipping is available to most countries with delivery times of 7-14 days.
                ''',
                'category': 'shipping',
                'keywords': ['shipping', 'delivery', 'tracking', 'orders']
            }
        ]
        
        self.policies = default_policies
    
    async def add_policy(self, title: str, content: str, category: str, keywords: List[str]) -> str:
        """Add a new policy"""
        try:
            policy_id = f"policy_{len(self.policies) + 1}"
            new_policy = {
                'id': policy_id,
                'title': title,
                'content': content,
                'category': category,
                'keywords': keywords
            }
            
            self.policies.append(new_policy)
            
            # Update vector store
            await self._update_vector_store()
            
            logger.info(f"Added new policy: {title}")
            return policy_id
            
        except Exception as e:
            logger.error(f"Error adding policy: {str(e)}")
            raise
    
    async def search_policies(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant policies using semantic search"""
        try:
            if not self.vector_store:
                return []
            
            # Perform semantic search
            docs = self.vector_store.similarity_search(query, k=k)
            
            # Extract relevant policies
            relevant_policies = []
            for doc in docs:
                policy_info = {
                    'title': doc.metadata['title'],
                    'category': doc.metadata['category'],
                    'content': doc.page_content,
                    'keywords': doc.metadata['keywords']
                }
                relevant_policies.append(policy_info)
            
            return relevant_policies
            
        except Exception as e:
            logger.error(f"Error searching policies: {str(e)}")
            raise
    
    async def get_all_policies(self) -> List[Dict[str, Any]]:
        """Get all company policies"""
        return self.policies
    
    async def _update_vector_store(self):
        """Update vector store with new policies"""
        try:
            documents = []
            for policy in self.policies:
                chunks = self.text_splitter.split_text(policy['content'])
                for chunk in chunks:
                    documents.append(Document(
                        page_content=chunk,
                        metadata={
                            'title': policy['title'],
                            'category': policy['category'],
                            'keywords': policy['keywords']
                        }
                    ))
            
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            
        except Exception as e:
            logger.error(f"Error updating vector store: {str(e)}")
            raise
