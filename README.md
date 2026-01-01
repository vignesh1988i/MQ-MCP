# MQ-MCP Server

A Model Context Protocol (MCP) server for IBM MQ (Message Queue) management and interaction. This server enables Claude and other MCP clients to query and manage IBM MQ queue managers, queues, and channels by connecting to a FastAPI application that wraps the IBM MQ REST API.

## Author

**Vignesh SR**

## Purpose

The MQ-MCP Server acts as a bridge between MCP clients (like Claude Desktop) and a FastAPI application (fastapi-app). The FastAPI application wraps the IBM MQ REST API to provide access to IBM MQ infrastructure. MQ-MCP provides tools that connect to this FastAPI application to enable:

- List and monitor queue managers
- View queue manager status
- Manage queues and retrieve queue details
- Monitor channels
- Execute MQSC commands remotely
- Maintain secure JWT-based authentication for all operations

## Features

- **Queue Manager Management**: List, monitor, and get status of queue managers
- **Queue Operations**: List queues, get queue details, and retrieve queue attributes
- **Channel Management**: List and monitor message channels
- **MQSC Command Execution**: Run MQSC commands on queue managers
- **JWT Authentication**: Secure token-based authentication with auto-refresh
- **Token Caching**: Intelligent token caching with expiry management
- **Error Handling**: Comprehensive logging and error handling
- **Async Support**: Fully asynchronous operations for better performance

## Installation

### Prerequisites

- Python 3.8 or higher
- A running **fastapi-app** instance (which wraps the IBM MQ REST API)
- pip package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vignesh1988i/MQ-MCP.git
   cd mq-mcp-server
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements_mqmcpserver.txt
   ```

## Configuration

### Required Settings

Edit `mqmcpserver.py` and update the following configuration variables to connect to your fastapi-app instance:

```python
# FastAPI application endpoint (the app that wraps IBM MQ REST API)
URL_BASE = "http://localhost:8080"

# Credentials for fastapi-app authentication
USER_NAME = "admin"
PASSWORD = "Password123"

# JWT token expiry duration (in minutes)
TOKEN_EXPIRY_MINUTES = 15
```

### Optional Configuration

For Claude Desktop integration, update your `mcp_config.json`:

```json
{
  "mcpServers": {
    "mqmcpserver": {
      "command": "python",
      "args": ["path/to/mqmcpserver.py"]
    }
  }
}
```

## Architecture

```
Claude Desktop (or MCP Client)
    ↓
MQ-MCP Server (mqmcpserver.py)
    ↓
fastapi-app (wraps IBM MQ REST API)
    ↓
IBM MQ REST API
    ↓
IBM MQ Infrastructure
```

## Usage

### Starting the Server

```bash
python mqmcpserver.py
```

The server will start with stdio transport, ready to handle MCP client requests.

### Available Tools

#### 1. **dspmq**
List available queue managers and their status.

```
Example: dspmq
Returns: JSON list of queue managers with status
```

#### 2. **get_qmgr_status**
Get the status of a specific queue manager.

```
Parameters:
  - qmgr_name: The name of the queue manager
Example: get_qmgr_status("QM_PROD")
```

#### 3. **list_queues**
List all queues for a specific queue manager.

```
Parameters:
  - qmgr_name: The name of the queue manager
Example: list_queues("QM_PROD")
```

#### 4. **get_queue_details**
Get detailed information about a specific queue.

```
Parameters:
  - qmgr_name: The name of the queue manager
  - queue_name: The name of the queue
Example: get_queue_details("QM_PROD", "Q.ORDERS")
```

#### 5. **get_queue_attributes**
Get attributes of a specific queue.

```
Parameters:
  - qmgr_name: The name of the queue manager
  - queue_name: The name of the queue
Example: get_queue_attributes("QM_PROD", "Q.ORDERS")
```

#### 6. **list_channels**
List all channels for a specific queue manager.

```
Parameters:
  - qmgr_name: The name of the queue manager
Example: list_channels("QM_PROD")
```

#### 7. **get_channel_details**
Get details of a specific channel.

```
Parameters:
  - qmgr_name: The name of the queue manager
  - channel_name: The name of the channel
Example: get_channel_details("QM_PROD", "CHANNEL.001")
```

#### 8. **runmqsc**
Execute an MQSC command on a queue manager.

```
Parameters:
  - qmgr_name: The name of the queue manager
  - mqsc_command: The MQSC command to execute
Example: runmqsc("QM_PROD", "DISPLAY QMGR")
```

## Authentication

The server uses JWT (JSON Web Tokens) for secure authentication:

- **Automatic Token Management**: Tokens are automatically requested and cached
- **Token Refresh**: Tokens are refreshed 1 minute before expiry to prevent interruptions
- **401 Handling**: If a 401 Unauthorized response is received, the token is invalidated and refreshed automatically
- **Secure Communication**: Uses Bearer token authentication in HTTP headers

## Testing

A test client is provided in `test_mqmcp_client.py` for development and debugging:

```bash
python test_mqmcp_client.py
```

## Logging

The server provides comprehensive logging output. Log messages include:

- Authentication status
- API requests and responses
- Token management events
- Error details and troubleshooting information

Configure logging level by modifying the `logging.basicConfig()` in `mqmcpserver.py`.

## Requirements

See `requirements_mqmcpserver.txt` for all dependencies:

- mcp (Model Context Protocol)
- httpx (Async HTTP client)
- fastmcp (FastMCP framework)
- python-dotenv (Environment variable management)
- ollama-mcp-bridge (Ollama MCP integration)

## Error Handling

The server includes robust error handling for:

- **Connection Errors**: Clear messages when the FastAPI server is unreachable
- **Authentication Errors**: Detailed logging of authentication failures
- **HTTP Errors**: Comprehensive HTTP status error handling
- **Token Expiry**: Automatic token refresh handling

## Troubleshooting

### Connection Error: "Cannot connect to FastAPI server"

1. Verify the **fastapi-app** instance is running on `URL_BASE`
2. Check network connectivity to the fastapi-app endpoint
3. Verify firewall settings allow connections to fastapi-app

### Authentication Error: "No access token found in response"

1. Verify username and password are correct for fastapi-app
2. Check that the `/token` endpoint is accessible on fastapi-app
3. Review fastapi-app server logs for authentication issues

### 401 Unauthorized Errors

1. Token may have expired - server will auto-refresh
2. If persistent, verify credentials and token endpoint
3. Check server logs for authentication details

## File Structure

```
mq-mcp-server/
├── mqmcpserver.py              # Main MCP server implementation
├── requirements_mqmcpserver.txt # Python dependencies
├── mcp_config.json             # MCP configuration (sample)
├── test_mqmcp_client.py         # Test client for development
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Notes

- Ensure your **fastapi-app** instance is running before starting the MQ-MCP Server
- The fastapi-app should be properly configured to connect to your IBM MQ infrastructure
- Keep credentials secure - consider using environment variables for production
- Token expiry is configurable; adjust based on your security requirements
- MQSC command support depends on your fastapi-app implementation

### About ollama-mcp-bridge

**ollama-mcp-bridge** is integrated into this project to enable AI-powered interactions with your IBM MQ infrastructure. It bridges the gap between MCP servers (like MQ-MCP) and Ollama language models, allowing you to:

- Use local Ollama LLMs to analyze and interpret MQ data
- Generate intelligent insights from queue manager status and queue metrics
- Automate complex MQ operations based on LLM recommendations
- Leverage natural language processing for better MQ management

This integration enables a more intuitive and intelligent interface to your IBM MQ systems through conversational AI.

## License

This project is provided as-is for IBM MQ management purposes.

## Support

For issues or questions, please refer to the project repository or contact the author.

---

**Last Updated**: January 2026
**Author**: Vignesh SR
