"""
MCP Server para GoHighLevel (GHL)
Permite a Claude conectarse a GHL para analizar contactos, conversaciones, llamadas y oportunidades.
"""

import asyncio
import os
import json
from typing import Any
import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

GHL_API_KEY = os.getenv("GHL_API_KEY")
GHL_BASE_URL = "https://services.leadconnectorhq.com"

app = Server("ghl-cleardent")


def headers():
    return {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Content-Type": "application/json",
        "Version": "2021-07-28",
    }


async def ghl_get(path: str, params: dict = None) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{GHL_BASE_URL}{path}", headers=headers(), params=params)
        resp.raise_for_status()
        return resp.json()


async def ghl_post(path: str, body: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{GHL_BASE_URL}{path}", headers=headers(), json=body)
        resp.raise_for_status()
        return resp.json()


# ─────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_locations",
            description="Obtiene las locations/subcuentas disponibles para este token de GHL",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_contacts",
            description="Obtiene los contactos de una location de GHL",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {"type": "string", "description": "ID de la location"},
                    "limit": {"type": "integer", "description": "Número de contactos (máx 100)", "default": 25},
                    "query": {"type": "string", "description": "Búsqueda por nombre, email o teléfono"},
                },
                "required": ["location_id"],
            },
        ),
        types.Tool(
            name="get_contact_detail",
            description="Obtiene el detalle completo de un contacto por su ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_id": {"type": "string", "description": "ID del contacto"},
                },
                "required": ["contact_id"],
            },
        ),
        types.Tool(
            name="get_conversations",
            description="Obtiene las conversaciones recientes de una location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {"type": "string", "description": "ID de la location"},
                    "limit": {"type": "integer", "description": "Número de conversaciones", "default": 20},
                    "contact_id": {"type": "string", "description": "Filtrar por contacto (opcional)"},
                },
                "required": ["location_id"],
            },
        ),
        types.Tool(
            name="get_conversation_messages",
            description="Obtiene los mensajes de una conversación específica",
            inputSchema={
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string", "description": "ID de la conversación"},
                },
                "required": ["conversation_id"],
            },
        ),
        types.Tool(
            name="get_pipelines",
            description="Obtiene los pipelines (embudos de ventas) de una location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {"type": "string", "description": "ID de la location"},
                },
                "required": ["location_id"],
            },
        ),
        types.Tool(
            name="get_opportunities",
            description="Obtiene las oportunidades/leads de un pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {"type": "string", "description": "ID de la location"},
                    "pipeline_id": {"type": "string", "description": "ID del pipeline (opcional)"},
                    "status": {"type": "string", "description": "Estado: open, won, lost, abandoned", "default": "open"},
                    "limit": {"type": "integer", "description": "Número de oportunidades", "default": 25},
                },
                "required": ["location_id"],
            },
        ),
        types.Tool(
            name="get_calls",
            description="Obtiene el registro de llamadas de una location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {"type": "string", "description": "ID de la location"},
                    "limit": {"type": "integer", "description": "Número de llamadas", "default": 20},
                    "contact_id": {"type": "string", "description": "Filtrar por contacto (opcional)"},
                },
                "required": ["location_id"],
            },
        ),
        types.Tool(
            name="get_campaigns",
            description="Obtiene las campañas activas de una location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {"type": "string", "description": "ID de la location"},
                },
                "required": ["location_id"],
            },
        ),
        types.Tool(
            name="get_custom_fields",
            description="Obtiene los campos personalizados definidos en la location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {"type": "string", "description": "ID de la location"},
                },
                "required": ["location_id"],
            },
        ),
    ]


# ─────────────────────────────────────────────
# TOOL HANDLERS
# ─────────────────────────────────────────────

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        result = await _dispatch(name, arguments)
        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    except httpx.HTTPStatusError as e:
        error = {"error": f"HTTP {e.response.status_code}", "detail": e.response.text}
        return [types.TextContent(type="text", text=json.dumps(error, ensure_ascii=False, indent=2))]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


async def _dispatch(name: str, args: dict) -> Any:
    loc = args.get("location_id")

    if name == "get_locations":
        return await ghl_get("/locations/search", {"limit": 20})

    elif name == "get_contacts":
        params = {"locationId": loc, "limit": args.get("limit", 25)}
        if args.get("query"):
            params["query"] = args["query"]
        return await ghl_get("/contacts/", params)

    elif name == "get_contact_detail":
        return await ghl_get(f"/contacts/{args['contact_id']}")

    elif name == "get_conversations":
        params = {"locationId": loc, "limit": args.get("limit", 20)}
        if args.get("contact_id"):
            params["contactId"] = args["contact_id"]
        return await ghl_get("/conversations/search", params)

    elif name == "get_conversation_messages":
        return await ghl_get(f"/conversations/{args['conversation_id']}/messages")

    elif name == "get_pipelines":
        return await ghl_get("/opportunities/pipelines", {"locationId": loc})

    elif name == "get_opportunities":
        params = {
            "location_id": loc,
            "status": args.get("status", "open"),
            "limit": args.get("limit", 25),
        }
        if args.get("pipeline_id"):
            params["pipeline_id"] = args["pipeline_id"]
        return await ghl_get("/opportunities/search", params)

    elif name == "get_calls":
        params = {"locationId": loc, "limit": args.get("limit", 20), "type": "call"}
        if args.get("contact_id"):
            params["contactId"] = args["contact_id"]
        return await ghl_get("/conversations/search", params)

    elif name == "get_campaigns":
        return await ghl_get("/campaigns/", {"locationId": loc})

    elif name == "get_custom_fields":
        return await ghl_get("/locations/customFields", {"locationId": loc})

    else:
        return {"error": f"Tool desconocida: {name}"}


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
