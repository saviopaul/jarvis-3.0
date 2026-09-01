"""
mcp_hub.py - Universal Model Context Protocol (MCP) & Autonomous Tool Hub

Provides Claude-MCP style tool execution, allowing Jarvis to invoke:
1. Live Code Execution (Replit / Emergent sandbox)
2. Live Website Builder & Hosting
3. Playable MP4 Video Generator
4. GitHub & Cloud Deploy Actions
5. Document & Vision Intelligence
"""

import os
import json
import logging
from code_sandbox import execute_python_code
from website_engine import build_and_host_website
from video_engine import create_educational_video
from tools import create_github_repo, push_file_to_github, trigger_render_deploy

logger = logging.getLogger(__name__)

# Registry of MCP Tools
MCP_TOOLS = {
    "execute_python": {
        "name": "execute_python",
        "description": "Executes Python code in a live sandbox (Replit style) and returns terminal output.",
        "handler": execute_python_code
    },
    "build_website": {
        "name": "build_website",
        "description": "Generates a full responsive HTML/Tailwind website and hosts it live at a public URL.",
        "handler": build_and_host_website
    },
    "create_video": {
        "name": "create_video",
        "description": "Generates an animated cartoon MP4 video with slides and spoken voice narration.",
        "handler": create_educational_video
    },
    "github_push": {
        "name": "github_push",
        "description": "Creates or updates a file in a GitHub repository.",
        "handler": push_file_to_github
    }
}


def list_available_mcps() -> list:
    """Returns the list of registered MCP tools and descriptions."""
    return [
        {"name": k, "description": v["description"]}
        for k, v in MCP_TOOLS.items()
    ]
