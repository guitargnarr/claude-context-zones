#!/usr/bin/env python3
"""
Claude Zones MCP Server

Model Context Protocol server that provides zone detection and switching
capabilities to Claude Code mid-session.

Usage:
    python -m claude_context_zones.mcp_server

Add to claude_desktop_config.json:
{
  "mcpServers": {
    "claude-zones": {
      "command": "python",
      "args": ["-m", "claude_context_zones.mcp_server"]
    }
  }
}
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

# MCP protocol implementation
# This is a minimal MCP server using stdio transport

from .detector import (
    detect_zone,
    load_zone_config,
    load_inherited_config,
    get_zone_metrics,
    log_zone_usage,
    load_user_zones,
    merge_zones,
    DEFAULT_ZONES,
)


class MCPServer:
    """Minimal MCP server for zone management."""

    def __init__(self):
        self.current_zone_override: Optional[str] = None
        self.tools = {
            "detect_zone": self.tool_detect_zone,
            "get_zone_config": self.tool_get_zone_config,
            "switch_zone": self.tool_switch_zone,
            "list_zones": self.tool_list_zones,
            "get_metrics": self.tool_get_metrics,
            "clear_override": self.tool_clear_override,
        }

    async def tool_detect_zone(self, arguments: dict) -> dict:
        """Detect the current zone based on working directory."""
        path = arguments.get("path", os.getcwd())

        # Check for manual override first
        if self.current_zone_override:
            user_zones = load_user_zones()
            zones = merge_zones(DEFAULT_ZONES, user_zones)
            if self.current_zone_override in zones:
                return {
                    "zone": self.current_zone_override,
                    "source": "manual_override",
                    "path": path,
                    "message": f"Currently in manually overridden zone: {self.current_zone_override}"
                }

        result = detect_zone(path, log=True)
        return {
            "zone": result["zone"],
            "source": "detected",
            "matched_pattern": result.get("matched_pattern"),
            "inheritance": result.get("inheritance", []),
            "path": result["path"]
        }

    async def tool_get_zone_config(self, arguments: dict) -> dict:
        """Get the behavioral configuration for a zone."""
        zone_name = arguments.get("zone")
        include_inheritance = arguments.get("include_inheritance", True)

        if not zone_name:
            # Detect current zone
            if self.current_zone_override:
                zone_name = self.current_zone_override
            else:
                result = detect_zone()
                zone_name = result["zone"]

        if include_inheritance:
            config = load_inherited_config(zone_name)
        else:
            user_zones = load_user_zones()
            zones = merge_zones(DEFAULT_ZONES, user_zones)
            zone_config = zones.get(zone_name, {})
            config_path = zone_config.get("config", f"zones/{zone_name}.md")
            config = load_zone_config(config_path)

        return {
            "zone": zone_name,
            "config": config
        }

    async def tool_switch_zone(self, arguments: dict) -> dict:
        """Manually switch to a different zone for this session."""
        zone_name = arguments.get("zone")

        if not zone_name:
            return {"error": "zone parameter required"}

        user_zones = load_user_zones()
        zones = merge_zones(DEFAULT_ZONES, user_zones)

        if zone_name not in zones:
            return {
                "error": f"Unknown zone: {zone_name}",
                "available_zones": list(zones.keys())
            }

        self.current_zone_override = zone_name
        log_zone_usage(zone_name, f"manual_switch:{os.getcwd()}")

        config = load_inherited_config(zone_name)

        return {
            "success": True,
            "zone": zone_name,
            "message": f"Switched to {zone_name} zone. Behavioral instructions updated.",
            "config": config
        }

    async def tool_list_zones(self, arguments: dict) -> dict:
        """List all available zones."""
        user_zones = load_user_zones()
        zones = merge_zones(DEFAULT_ZONES, user_zones)

        zone_list = []
        for name, config in zones.items():
            zone_list.append({
                "name": name,
                "paths": config.get("paths", []),
                "inherits": config.get("inherits", []),
                "config": config.get("config", f"zones/{name}.md")
            })

        return {
            "zones": zone_list,
            "current_override": self.current_zone_override
        }

    async def tool_get_metrics(self, arguments: dict) -> dict:
        """Get zone usage metrics."""
        return get_zone_metrics()

    async def tool_clear_override(self, arguments: dict) -> dict:
        """Clear manual zone override, return to auto-detection."""
        previous = self.current_zone_override
        self.current_zone_override = None

        result = detect_zone(log=True)

        return {
            "success": True,
            "previous_override": previous,
            "current_zone": result["zone"],
            "message": f"Override cleared. Now in auto-detected zone: {result['zone']}"
        }

    def get_tool_definitions(self) -> list:
        """Return MCP tool definitions."""
        return [
            {
                "name": "detect_zone",
                "description": "Detect the current Claude Code zone based on working directory. Returns zone name, inheritance chain, and matched pattern.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to check. Defaults to current working directory."
                        }
                    }
                }
            },
            {
                "name": "get_zone_config",
                "description": "Get the behavioral configuration/instructions for a zone. Use this to understand how to behave in the current context.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "zone": {
                            "type": "string",
                            "description": "Zone name. If not provided, uses current zone."
                        },
                        "include_inheritance": {
                            "type": "boolean",
                            "description": "Include inherited zone configs. Defaults to true.",
                            "default": True
                        }
                    }
                }
            },
            {
                "name": "switch_zone",
                "description": "Manually switch to a different zone for this session. Use when the user explicitly requests different behavioral context.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "zone": {
                            "type": "string",
                            "description": "Zone name to switch to (e.g., 'finance', 'career', 'development')"
                        }
                    },
                    "required": ["zone"]
                }
            },
            {
                "name": "list_zones",
                "description": "List all available zones with their path patterns and inheritance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_metrics",
                "description": "Get zone usage metrics - which zones are used most, recent history.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "clear_override",
                "description": "Clear any manual zone override and return to auto-detection based on working directory.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    async def handle_request(self, request: dict) -> dict:
        """Handle an MCP request."""
        method = request.get("method", "")
        request_id = request.get("id")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "claude-zones",
                        "version": "1.1.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": self.get_tool_definitions()
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name not in self.tools:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }

            try:
                result = await self.tools[tool_name](arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }

        elif method == "notifications/initialized":
            # No response needed for notifications
            return None

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }


async def run_server():
    """Run the MCP server using stdio transport."""
    server = MCPServer()

    # Read from stdin, write to stdout
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, asyncio.get_event_loop())

    buffer = ""

    while True:
        try:
            # Read a line
            line = await reader.readline()
            if not line:
                break

            line = line.decode('utf-8').strip()
            if not line:
                continue

            # Parse JSON-RPC request
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Handle request
            response = await server.handle_request(request)

            # Send response (if not a notification)
            if response is not None:
                response_str = json.dumps(response) + "\n"
                writer.write(response_str.encode('utf-8'))
                await writer.drain()

        except Exception as e:
            # Log error but keep running
            sys.stderr.write(f"Error: {e}\n")
            continue


def main():
    """Entry point for MCP server."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
