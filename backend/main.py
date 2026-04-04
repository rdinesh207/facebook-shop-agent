import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

app = FastAPI(title="Facebook Shop Agent API")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev; narrow down in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    image: Optional[str] = None # Optional base64 encoded image
    # access_token: str = None # Could be used to override environment token

# Context manager for MCP client
mcp_client = None
agent = None

@app.on_event("startup")
async def startup_event():
    global mcp_client, agent
    
    print("Starting up Facebook Shop Agent backend...")
    
    # Path to the server script relative to this file
    server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fastmcp", "server.py"))
    print(f"Connecting to MCP server at: {server_path}")
    
    import sys
    mcp_client = MultiServerMCPClient(
        {
            "facebook-shop": {
                "command": sys.executable,
                "args": [server_path],
                "transport": "stdio",
            }
        }
    )
    
    try:
        # CRITICAL FIX: As of 0.1.0, MultiServerMCPClient should NOT be used as a context manager.
        # Calling get_tools() will automatically handle the connection.
        tools = await mcp_client.get_tools()
        print(f"Successfully discovered {len(tools)} tools from MCP server.")
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("WARNING: OPENAI_API_KEY not found in environment.")
            
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        # System instructions to help the agent discover context
        system_prompt = (
            "You are a Facebook Shop assistant. "
            "If a user asks to 'Sync Inventory' or list products and you don't know the catalog_id, "
            "always call 'list_shops' first to find the correct shop/catalog ID. "
            "Once you find the catalog, use 'list_products' with 'sync_to_db=True' to sync data to InsForge. "
            "\n\nERROR HANDLING: If a tool call fails or returns an error, do not report the technical error string directly to the user. "
            "Instead, interpret the error and provide a helpful, user-friendly explanation or ask for the missing information. "
            "For example, if an 'image_url' is required but missing, say: 'I need an image_url to proceed, could you provide one?'"
        )
        
        agent = create_react_agent(llm, tools, prompt=system_prompt)
        print("Agent initialized and ready.")
    except Exception as e:
        print(f"FATAL ERROR during startup: {e}")
        import traceback
        traceback.print_exc()

@app.on_event("shutdown")
async def shutdown_event():
    # MultiServerMCPClient handles its own cleanup.
    pass

@app.post("/chat")
async def chat(request: ChatRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Construct message history
    messages = []
    for m in request.history:
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            messages.append(AIMessage(content=m["content"]))
            
    # Construct current message (handle text + optional image)
    if request.image:
        # LangChain multi-modal message format
        user_content = [
            {"type": "text", "text": request.message},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{request.image}"}
            }
        ]
        messages.append(HumanMessage(content=user_content))
    else:
        messages.append(HumanMessage(content=request.message))
    
    try:
        result = await agent.ainvoke({"messages": messages})
        # Extract the last message from the result
        response_msg = result["messages"][-1]
        return {"response": response_msg.content}
    except Exception as e:
        print(f"Error invoking agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
