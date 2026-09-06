import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import (
    ClientSession,
    StdioServerParameters
)

from mcp.client.stdio import stdio_client


# =========================================================
# FIND MCP SERVER FILE
# =========================================================

# Find the folder containing this file
BASE_DIR = Path(
    __file__
).resolve().parent


# Build absolute path to MCP server
SERVER_FILE = (
    BASE_DIR / "mcp_server.py"
)


# =========================================================
# CREATE MCP CLIENT FUNCTION
# =========================================================

async def call_mcp_tool(
    tool_name: str,
    arguments: dict
) -> str:
    """
    Connect to our MCP server and execute
    one MCP tool.

    Parameters
    ----------
    tool_name:
        Name of the MCP tool.

    arguments:
        Arguments required by the tool.

    Returns
    -------
    str:
        Result returned by the MCP server.
    """

    # -----------------------------------------------------
    # DEFINE HOW MCP SHOULD START THE SERVER
    # -----------------------------------------------------

    server_params = StdioServerParameters(

        # Use the SAME Python environment
        # that is running this application.
        command=sys.executable,

        # Tell Python to execute our MCP server.
        args=[
            str(SERVER_FILE)
        ],

        # Pass current environment variables
        # to the MCP server.
        env=os.environ.copy()
    )


    try:

        # -------------------------------------------------
        # CONNECT TO MCP SERVER
        # -------------------------------------------------

        async with stdio_client(
            server_params
        ) as (
            read_stream,
            write_stream
        ):

            # Create MCP client session
            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                # Initialize MCP connection
                await session.initialize()


                # -------------------------------------------------
                # CHECK AVAILABLE TOOLS
                # -------------------------------------------------

                tools_response = (
                    await session.list_tools()
                )


                # Check that requested tool exists
                available_tools = [
                    tool.name
                    for tool
                    in tools_response.tools
                ]


                if tool_name not in available_tools:

                    return json.dumps({
                        "error": (
                            f"Tool '{tool_name}' "
                            "was not found.",
                            "Available tools:",
                            available_tools
                        )
                    })


                # -------------------------------------------------
                # CALL MCP TOOL
                # -------------------------------------------------

                result = await session.call_tool(
                    tool_name,
                    arguments
                )


                # -------------------------------------------------
                # EXTRACT TEXT RESULT
                # -------------------------------------------------

                output = []

                for content in result.content:

                    # MCP text content contains
                    # the actual tool response.
                    if hasattr(
                        content,
                        "text"
                    ):

                        output.append(
                            content.text
                        )


                # Join all returned text
                return "\n".join(
                    output
                )


    except Exception as e:

        # Return readable error instead
        # of crashing the application.
        return json.dumps({
            "error": f"MCP client error: {str(e)}"
        })


# =========================================================
# SYNCHRONOUS WRAPPER
# =========================================================

def call_mcp_tool_sync(
    tool_name: str,
    arguments: dict
) -> str:
    """
    Synchronous wrapper around the
    asynchronous MCP client.

    Streamlit and our LangGraph nodes
    can call this normal Python function.
    """

    return asyncio.run(
        call_mcp_tool(
            tool_name,
            arguments
        )
    )