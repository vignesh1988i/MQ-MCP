import logging
import httpx
import json

from typing import Any, Optional
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("mqmcpserver")

# Change this to point to your FastAPI server
URL_BASE = "http://localhost:8080"

# Change these to your FastAPI credentials
USER_NAME = "admin"
PASSWORD = "Password123"

# JWT token expiry duration (15 minutes)
TOKEN_EXPIRY_MINUTES = 15

# Global variables to store JWT token and expiry time
_jwt_token: Optional[str] = None
_token_expiry: Optional[datetime] = None

async def get_jwt_token() -> str:
    """Authenticate and get JWT token from FastAPI server"""
    global _jwt_token, _token_expiry
    
    # Check if we have a valid cached token
    if _jwt_token and _token_expiry:  
        # Add a 1-minute buffer before actual expiry to be safe
        if datetime.now() < (_token_expiry - timedelta(minutes=1)):
            logger.debug(f"Using cached JWT token (expires at {_token_expiry.strftime('%H:%M:%S')})")
            return _jwt_token
        else:
            logger.info("JWT token expired or about to expire, refreshing...")
    
    login_url = f"{URL_BASE}/token"
    logger.info(f"Requesting new JWT token from:   {login_url}")
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            # Using form data for OAuth2 password flow (standard for /token endpoints)
            logger.debug(f"Authenticating with username: {USER_NAME}")
            response = await client.post(
                login_url,
                data={"username": USER_NAME, "password": PASSWORD},
                timeout=30.0
            )
            
            logger.debug(f"Token response status: {response.status_code}")
            
            response.raise_for_status()
            token_data = response.json()
            
            # Standard OAuth2 response uses "access_token"
            _jwt_token = token_data.get("access_token") or token_data.get("token")
            
            if not _jwt_token:
                raise Exception("No access token found in response")
            
            # Set token expiry time (15 minutes from now)
            _token_expiry = datetime.now() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
            
            logger.info(f"✅ Successfully obtained JWT token (valid until {_token_expiry.strftime('%H:%M:%S')})")
            return _jwt_token
        except httpx.ConnectError as err:
            logger.error(f"Connection error - cannot reach server at {login_url}")
            logger.error(f"Make sure your FastAPI server is running on {URL_BASE}")
            raise Exception(f"Cannot connect to FastAPI server at {URL_BASE}.  Is it running?") from err
        except httpx.HTTPStatusError as err:
            logger.error(f"HTTP error during authentication: {err}")
            logger.error(f"Response status: {err.response.status_code}")
            logger.error(f"Response body: {err.response.text}")
            raise
        except httpx.HTTPError as err:
            logger. error(f"HTTP error during authentication: {err}")
            raise
        except Exception as err: 
            logger.error(f"Authentication failed: {err}")
            raise

def invalidate_token():
    """Invalidate the cached token (useful when getting 401 responses)"""
    global _jwt_token, _token_expiry
    logger.warning("Invalidating cached JWT token")
    _jwt_token = None
    _token_expiry = None

async def make_authenticated_request(method: str, endpoint: str, **kwargs) -> httpx.Response:
    """Make an authenticated request to the FastAPI server"""
    token = await get_jwt_token()
    
    headers = kwargs. get("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    kwargs["headers"] = headers
    
    url = f"{URL_BASE}{endpoint}"
    logger.info(f"Making {method} request to: {url}")
    
    async with httpx.AsyncClient(verify=False) as client:
        try:  
            response = await client.request(method, url, timeout=30.0, **kwargs)
            logger.debug(f"Response status: {response.status_code}")
            
            # If we get a 401, token might be expired or invalid, refresh and retry once
            if response.status_code == 401:
                logger.warning("Got 401 Unauthorized, invalidating token and retrying...")
                invalidate_token()
                token = await get_jwt_token()
                headers["Authorization"] = f"Bearer {token}"
                response = await client. request(method, url, timeout=30.0, **kwargs)
                logger.debug(f"Retry response status: {response.status_code}")
            
            response.raise_for_status()
            return response
        except httpx.ConnectError as err:
            logger.error(f"Connection error - cannot reach server at {url}")
            logger.error(f"Make sure your FastAPI server is running on {URL_BASE}")
            raise Exception(f"Cannot connect to FastAPI server at {URL_BASE}. Is it running?") from err
        except httpx.HTTPStatusError as err:
            logger.error(f"HTTP status error: {err}")
            logger.error(f"URL: {url}")
            logger.error(f"Response status: {err.response.status_code}")
            logger.error(f"Response body: {err.response.text}")
            raise
        except httpx.HTTPError as err:
            logger.error(f"HTTP error: {err}")
            logger.error(f"URL: {url}")
            raise
        except Exception as err:  
            logger.error(f"Request failed: {err}")
            raise

@mcp.tool()
async def dspmq() -> str:
    """List available queue managers and their status
    """
    try:  
        logger.info("Executing dspmq tool")
        response = await make_authenticated_request("GET", "/qmgr")
        return response.text
    except Exception as err:  
        logger.error(f"dspmq failed: {err}")
        return f"Error listing queue managers:  {err}"

@mcp. tool()
async def get_qmgr_status(qmgr_name: str) -> str:
    """Get the status of a specific queue manager

    Args:
        qmgr_name: The name of the queue manager
    """
    try:  
        logger.info(f"Getting status for queue manager: {qmgr_name}")
        response = await make_authenticated_request("GET", f"/qmgr/{qmgr_name}/status")
        return response.text
    except Exception as err:  
        logger.error(f"get_qmgr_status failed: {err}")
        return f"Error getting queue manager status:   {err}"

@mcp.tool()
async def list_queues(qmgr_name: str) -> str:
    """List all queues for a specific queue manager

    Args:   
        qmgr_name: The name of the queue manager
    """
    try:  
        logger.info(f"Listing queues for queue manager:  {qmgr_name}")
        response = await make_authenticated_request("GET", f"/qmgr/{qmgr_name}/queues")
        return response.text
    except Exception as err: 
        logger.error(f"list_queues failed: {err}")
        return f"Error listing queues: {err}"

@mcp.tool()
async def get_queue_details(qmgr_name: str, queue_name: str) -> str:
    """Get details of a specific queue

    Args:  
        qmgr_name: The name of the queue manager
        queue_name: The name of the queue
    """
    try:
        logger.info(f"Getting details for queue {queue_name} in {qmgr_name}")
        response = await make_authenticated_request("GET", f"/qmgr/{qmgr_name}/queues/{queue_name}")
        return response.text
    except Exception as err:  
        logger.error(f"get_queue_details failed:   {err}")
        return f"Error getting queue details: {err}"

@mcp.tool()
async def get_queue_attributes(qmgr_name:  str, queue_name: str) -> str:
    """Get attributes of a specific queue

    Args:  
        qmgr_name: The name of the queue manager
        queue_name: The name of the queue
    """
    try:
        logger.info(f"Getting attributes for queue {queue_name} in {qmgr_name}")
        response = await make_authenticated_request("GET", f"/qmgr/{qmgr_name}/queues/{queue_name}/attributes")
        return response.text
    except Exception as err:  
        logger.error(f"get_queue_attributes failed:  {err}")
        return f"Error getting queue attributes: {err}"

@mcp.tool()
async def list_channels(qmgr_name:   str) -> str:
    """List all channels for a specific queue manager

    Args:  
        qmgr_name: The name of the queue manager
    """
    try: 
        logger.info(f"Listing channels for queue manager:  {qmgr_name}")
        response = await make_authenticated_request("GET", f"/qmgr/{qmgr_name}/channels")
        return response.text
    except Exception as err:  
        logger.error(f"list_channels failed: {err}")
        return f"Error listing channels:   {err}"

@mcp.tool()
async def get_channel_details(qmgr_name:   str, channel_name: str) -> str:
    """Get details of a specific channel

    Args:   
        qmgr_name: The name of the queue manager
        channel_name: The name of the channel
    """
    try:
        logger.info(f"Getting details for channel {channel_name} in {qmgr_name}")
        response = await make_authenticated_request("GET", f"/qmgr/{qmgr_name}/channels/{channel_name}")
        return response.text
    except Exception as err:  
        logger.error(f"get_channel_details failed:  {err}")
        return f"Error getting channel details:  {err}"

@mcp. tool()
async def runmqsc(qmgr_name:  str, mqsc_command: str) -> str:
    """Run an MQSC command against a specific queue manager
    Note: This endpoint might not be available in your FastAPI implementation

    Args:  
        qmgr_name: A queue manager name   
        mqsc_command: An MQSC command to run on the queue manager   
    """
    try:  
        logger.info(f"Running MQSC command on {qmgr_name}: {mqsc_command}")
        response = await make_authenticated_request(
            "POST",
            f"/qmgr/{qmgr_name}/mqsc",
            json={"command": mqsc_command}
        )
        return response.text
    except Exception as err:  
        logger.error(f"runmqsc failed: {err}")
        return f"Error running MQSC command: {err}"

if __name__ == "__main__":   
    logger.info("Starting MCP server with stdio transport...")
    logger.info(f"JWT token expiry set to {TOKEN_EXPIRY_MINUTES} minutes")
    # Use stdio transport for testing and Claude Desktop integration
    mcp.run(transport='stdio')