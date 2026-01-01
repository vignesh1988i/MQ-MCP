import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp():
    """Test MCP server by connecting to it"""
    
    # Configure connection to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["mqmcpserver.py"],
    )
    
    print("=" * 60)
    print("🚀 Starting MCP Server Test")
    print("=" * 60)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            print("\n📡 Initializing MCP session...")
            await session.initialize()
            print("✅ Session initialized")
            
            # List available tools
            print("\n📋 Listing available tools...")
            tools = await session.list_tools()
            print(f"\n✅ Found {len(tools. tools)} tools:")
            for tool in tools.tools:
                print(f"  • {tool.name}")
                print(f"    └─ {tool.description}")
            
            # Test 1: Get queue manager status
            print("\n" + "=" * 60)
            print("TEST 1: get_qmgr_status")
            print("=" * 60)
            try:
                result = await session.call_tool(
                    "get_qmgr_status",
                    arguments={"qmgr_name": "SRVIG"}  # ⚠️ Change to your actual queue manager name
                )
                print(f"✅ Result: {result. content}")
            except Exception as e: 
                print(f"❌ Error: {e}")
            
            # Test 2: List queues
            print("\n" + "=" * 60)
            print("TEST 2: list_queues")
            print("=" * 60)
            try:
                result = await session. call_tool(
                    "list_queues",
                    arguments={"qmgr_name": "SRVIG"}  # ⚠️ Change to your actual queue manager name
                )
                print(f"✅ Result: {result.content}")
            except Exception as e: 
                print(f"❌ Error: {e}")
            
            # Test 3: List channels
            print("\n" + "=" * 60)
            print("TEST 3: list_channels")
            print("=" * 60)
            try:
                result = await session.call_tool(
                    "list_channels",
                    arguments={"qmgr_name": "SRVIG"}  # ⚠️ Change to your actual queue manager name
                )
                print(f"✅ Result: {result.content}")
            except Exception as e:
                print(f"❌ Error:  {e}")
            
            # Test 4: Get queue details
            print("\n" + "=" * 60)
            print("TEST 4: get_queue_details")
            print("=" * 60)
            try:
                result = await session. call_tool(
                    "get_queue_details",
                    arguments={
                        "qmgr_name": "SRVIG",  # ⚠️ Change to your actual queue manager name
                        "queue_name": "SYSTEM.ADMIN.COMMAND.QUEUE"  # ⚠️ Change to an actual queue name
                    }
                )
                print(f"✅ Result: {result. content}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Test 5: Get queue attributes
            print("\n" + "=" * 60)
            print("TEST 5: get_queue_attributes")
            print("=" * 60)
            try:
                result = await session. call_tool(
                    "get_queue_attributes",
                    arguments={
                        "qmgr_name": "SRVIG",  # ⚠️ Change to your actual queue manager name
                        "queue_name": "SYSTEM.ADMIN.COMMAND.QUEUE"  # ⚠️ Change to an actual queue name
                    }
                )
                print(f"✅ Result: {result. content}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n" + "=" * 60)
            print("✅ All tests completed!")
            print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_mcp())