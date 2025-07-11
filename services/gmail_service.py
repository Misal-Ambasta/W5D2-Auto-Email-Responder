import asyncio
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

class GmailService:
    def __init__(self):
        self.service = None
        self.creds = None
    
    async def initialize(self):
        """Initialize Gmail API service"""
        try:
            self.creds = await self._get_credentials()
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Gmail service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {str(e)}")
            raise
    
    async def _get_credentials(self):
        """Get Gmail API credentials"""
        creds = None
        
        # Load existing token
        try:
            creds = Credentials.from_authorized_user_file(
                settings.GMAIL_TOKEN_PATH, 
                settings.GMAIL_SCOPES
            )
        except FileNotFoundError:
            pass
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GMAIL_CREDENTIALS_PATH, 
                    settings.GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(settings.GMAIL_TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    async def send_email(self, to: str, subject: str, body: str) -> str:
        """Send an email via Gmail API"""
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            message.attach(MIMEText(body, 'plain'))
            
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode()
            
            send_message = self.service.users().messages().send(
                userId="me",
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent successfully: {send_message['id']}")
            return send_message['id']
            
        except HttpError as e:
            logger.error(f"Gmail API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
    
    async def get_inbox_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get emails from inbox"""
        try:
            results = self.service.users().messages().list(
                userId="me",
                labelIds=['INBOX'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId="me", 
                    id=message['id']
                ).execute()
                
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                
                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'snippet': msg.get('snippet', ''),
                    'timestamp': msg['internalDate']
                })
            
            return emails
            
        except HttpError as e:
            logger.error(f"Gmail API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving emails: {str(e)}")
            raise
    
    async def process_inbox_emails(self):
        """Process inbox emails and generate auto-responses"""
        try:
            emails = await self.get_inbox_emails()
            
            for email in emails:
                # Check if email needs auto-response
                if await self._should_auto_respond(email):
                    # Generate and send response
                    await self._generate_auto_response(email)
                    
                await asyncio.sleep(settings.PROCESSING_DELAY)
                
        except Exception as e:
            logger.error(f"Error processing inbox emails: {str(e)}")
            raise
    
    async def _should_auto_respond(self, email: Dict[str, Any]) -> bool:
        """Determine if email should get auto-response"""
        # Add logic to determine if email needs auto-response
        # For now, return True for demonstration
        return True
    
    async def _generate_auto_response(self, email: Dict[str, Any]):
        """Generate and send auto-response for email"""
        # This would integrate with the response generator
        # For now, just log the action
        logger.info(f"Auto-responding to email: {email['id']}")
