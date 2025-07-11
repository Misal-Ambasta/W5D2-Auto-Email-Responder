from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
import logging
from contextlib import asynccontextmanager

from services.gmail_service import GmailService
from services.policy_service import PolicyService
from services.response_generator import ResponseGenerator
from services.cache_service import CacheService
from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    await gmail_service.initialize()
    await policy_service.load_policies()
    await cache_service.initialize()
    logger.info("Auto Email Responder started successfully")
    
    yield
    
    # Shutdown event (if needed)
    # Add any cleanup code here

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
gmail_service = GmailService()
policy_service = PolicyService()
response_generator = ResponseGenerator()
cache_service = CacheService()

# Pydantic models
class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    priority: Optional[str] = "normal"

class EmailResponse(BaseModel):
    id: str
    status: str
    generated_response: str
    policies_used: List[str]
    timestamp: datetime

class PolicyRequest(BaseModel):
    title: str
    content: str
    category: str
    keywords: List[str]

class BatchEmailRequest(BaseModel):
    emails: List[EmailRequest]
    use_cache: bool = True

# @app.on_event("startup")
# async def startup_event():
#     """Initialize services on startup"""
#     await gmail_service.initialize()
#     await policy_service.load_policies()
#     await cache_service.initialize()
#     logger.info("Auto Email Responder started successfully")

@app.get("/")
async def root():
    return {"message": "Auto Email Responder API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/emails/send", response_model=EmailResponse)
async def send_email(email_request: EmailRequest):
    """Send a single email with AI-generated response"""
    try:
        # Generate intelligent response
        response_data = await response_generator.generate_response(
            subject=email_request.subject,
            body=email_request.body,
            priority=email_request.priority
        )
        
        # Send email via Gmail
        email_id = await gmail_service.send_email(
            to=email_request.to,
            subject=email_request.subject,
            body=response_data["response"]
        )
        
        return EmailResponse(
            id=email_id,
            status="sent",
            generated_response=response_data["response"],
            policies_used=response_data["policies_used"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emails/batch", response_model=List[EmailResponse])
async def send_batch_emails(batch_request: BatchEmailRequest):
    """Send multiple emails with batch processing"""
    try:
        responses = []
        
        # Process emails in batches
        for email_request in batch_request.emails:
            response_data = await response_generator.generate_response(
                subject=email_request.subject,
                body=email_request.body,
                priority=email_request.priority,
                use_cache=batch_request.use_cache
            )
            
            email_id = await gmail_service.send_email(
                to=email_request.to,
                subject=email_request.subject,
                body=response_data["response"]
            )
            
            responses.append(EmailResponse(
                id=email_id,
                status="sent",
                generated_response=response_data["response"],
                policies_used=response_data["policies_used"],
                timestamp=datetime.now()
            ))
        
        return responses
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails/inbox")
async def get_inbox_emails():
    """Retrieve inbox emails"""
    try:
        emails = await gmail_service.get_inbox_emails()
        return {"emails": emails, "count": len(emails)}
    except Exception as e:
        logger.error(f"Error retrieving emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emails/process-inbox")
async def process_inbox_emails(background_tasks: BackgroundTasks):
    """Process inbox emails with auto-responses"""
    try:
        background_tasks.add_task(gmail_service.process_inbox_emails)
        return {"message": "Inbox processing started", "status": "processing"}
    except Exception as e:
        logger.error(f"Error processing inbox: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/policies/add")
async def add_policy(policy_request: PolicyRequest):
    """Add a new company policy"""
    try:
        policy_id = await policy_service.add_policy(
            title=policy_request.title,
            content=policy_request.content,
            category=policy_request.category,
            keywords=policy_request.keywords
        )
        return {"policy_id": policy_id, "status": "added"}
    except Exception as e:
        logger.error(f"Error adding policy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/policies/search")
async def search_policies(query: str):
    """Search for relevant policies"""
    try:
        policies = await policy_service.search_policies(query)
        return {"policies": policies, "count": len(policies)}
    except Exception as e:
        logger.error(f"Error searching policies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/policies/all")
async def get_all_policies():
    """Get all company policies"""
    try:
        policies = await policy_service.get_all_policies()
        return {"policies": policies, "count": len(policies)}
    except Exception as e:
        logger.error(f"Error retrieving policies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        stats = await cache_service.get_stats()
        return {"cache_stats": stats}
    except Exception as e:
        logger.error(f"Error retrieving cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache/clear")
async def clear_cache():
    """Clear all cached data"""
    try:
        await cache_service.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# config/settings.py
