from mcp_sdk import MCPServer

from .resources import AudioKitResource


def create_mcp_server() -> MCPServer:
    """Create and configure MCP server instance"""
    server = MCPServer(
        name="AudioKit MCP",
        version="2.0.0",
        description="Audio processing and knowledge management MCP server",
        resources=[AudioKitResource],
    )

    return server
