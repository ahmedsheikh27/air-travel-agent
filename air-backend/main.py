from __future__ import annotations as _annotations

import asyncio
import random
import uuid
import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# Import from external agents library with aliases to avoid conflicts
from agents import (
    HandoffOutputItem,
    ItemHelpers,
    MessageOutputItem,
    RunContextWrapper,
    Runner,
    ToolCallItem,
    ToolCallOutputItem,
    TResponseInputItem,
    Agent,
)
from openai import AsyncOpenAI
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Import from our local modular structure
from models.context import AirlineAgentContext
from airline_agents.triage_agent import triage_agent
from airline_agents.faq_agent import faq_agent
from airline_agents.seat_booking_agent import seat_booking_agent
from dotenv import load_dotenv

load_dotenv()

### CONTEXT
gemini_api_key = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")  # Paste your MongoDB Compass or Atlas URI here
mongo_client = AsyncIOMotorClient(MONGODB_URI)
db = mongo_client["airline_db"]  # Use your preferred DB name

# Helper to save conversation logs
def get_conversation_id(state_key):
    # You can customize this to use a real session/user id
    return state_key

# Save only booking data (AirlineAgentContext) to DB
async def save_booking(context: AirlineAgentContext):
    # Add pdf_url to context if not already present
    if not hasattr(context, 'pdf_url') or context.pdf_url is None:
        context.pdf_url = f"/tickets/{context.confirmation_number}.pdf"
    from tools.booking_tools import generate_ticket_pdf
    pdf_path = generate_ticket_pdf(context)
    print(f"PDF ticket generated: {pdf_path}")
    print("Final booking details being sent to DB:")
    print(context.dict())
    try:
        result = await db.bookings.insert_one(context.dict())
        print("Booking details successfully saved to DB.")
        print(f"MongoDB insert result: {result}")
    except Exception as e:
        print("Error saving booking to DB:", e)

### RUN

async def main():
    current_agent: Agent[AirlineAgentContext] = triage_agent
    input_items: list[TResponseInputItem] = []
    context = AirlineAgentContext()

    conversation_id = uuid.uuid4().hex[:16]

    while True:
        user_input = input("Enter your message: ")
        input_items.append({"content": user_input, "role": "user"})
        result = await Runner.run(current_agent, input_items, context=context)

        for new_item in result.new_items:
            agent_name = new_item.agent.name
            if isinstance(new_item, MessageOutputItem):
                print(f"{agent_name}: {ItemHelpers.text_message_output(new_item)}")
            elif isinstance(new_item, HandoffOutputItem):
                print(
                    f"Handed off from {new_item.source_agent.name} to {new_item.target_agent.name}"
                )
            elif isinstance(new_item, ToolCallItem):
                print(f"{agent_name}: Calling a tool")
            elif isinstance(new_item, ToolCallOutputItem):
                print(f"{agent_name}: Tool call output: {new_item.output}")
            else:
                print(f"{agent_name}: Skipping item: {new_item.__class__.__name__}")
        input_items = result.to_input_list()
        current_agent = result.last_agent


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Print when connected to MongoDB
@app.on_event("startup")
async def startup_db_client():
    try:
        # The ping command is cheap and does not require auth
        await db.command("ping")
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

# Shared runner logic for all agents
async def process_message(agent, input_items, context, user_input):
    input_items.append({"content": user_input, "role": "user"})
    result = await Runner.run(agent, input_items, context=context)
    responses = []
    for new_item in result.new_items:
        agent_name = new_item.agent.name
        if isinstance(new_item, MessageOutputItem):
            responses.append({"type": "message", "agent": agent_name, "content": ItemHelpers.text_message_output(new_item)})
        elif isinstance(new_item, HandoffOutputItem):
            responses.append({"type": "handoff", "from": new_item.source_agent.name, "to": new_item.target_agent.name})
        elif isinstance(new_item, ToolCallItem):
            responses.append({"type": "tool_call", "agent": agent_name})
        elif isinstance(new_item, ToolCallOutputItem):
            responses.append({"type": "tool_call_output", "agent": agent_name, "output": new_item.output})
        else:
            responses.append({"type": "skip", "agent": agent_name, "item": new_item.__class__.__name__})
    return responses, result.to_input_list(), result.last_agent

# In-memory conversation state (for demo; in production use a database or session)
conversation_states = {
    "triage": {"input_items": [], "context": AirlineAgentContext(), "agent": triage_agent},
    "faq": {"input_items": [], "context": AirlineAgentContext(), "agent": faq_agent},
    "seat_booking": {"input_items": [], "context": AirlineAgentContext(), "agent": seat_booking_agent},
}

@app.post("/triage/send")
async def triage_send(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    state = conversation_states["triage"]
    responses, input_items, agent = await process_message(state["agent"], state["input_items"], state["context"], user_input)
    state["input_items"] = input_items
    state["agent"] = agent

    pdf_url = None
    # Check if a booking was confirmed in agent responses
    for resp in responses:
        if resp["type"] == "message" and "Booking confirmed!" in resp["content"]:
            print("Context before save_booking:", state["context"].dict())
            await save_booking(state["context"])
            from tools.booking_tools import generate_ticket_pdf
            pdf_path = generate_ticket_pdf(state["context"])
            pdf_url = f"/tickets/{state['context'].confirmation_number}.pdf"
            break

    # Return only the responses (no chat storage in DB)
    handoff_item = next((item for item in responses if item["type"] == "handoff"), None)
    if handoff_item:
        target = handoff_item["to"].lower()
        if "faq" in target:
            agent_key = "faq"
        elif "seat" in target:
            agent_key = "seat_booking"
        else:
            agent_key = "triage"
        agent_state = conversation_states[agent_key]
        agent_responses, agent_input_items, agent_obj = await process_message(
            agent_state["agent"], agent_state["input_items"], agent_state["context"], user_input
        )
        agent_state["input_items"] = agent_input_items
        agent_state["agent"] = agent_obj
        return JSONResponse({"user_message": user_input, "responses": agent_responses, "pdf_url": pdf_url})
    else:
        return JSONResponse({"user_message": user_input, "responses": responses, "pdf_url": pdf_url})

@app.get("/triage/response")
async def triage_response():
    state = conversation_states["triage"]
    input_items = state["input_items"]
    # Return the last message(s) from the input_items
    return JSONResponse({"responses": input_items if input_items else []})

@app.get("/faq/response")
async def faq_response():
    state = conversation_states["faq"]
    input_items = state["input_items"]
    return JSONResponse({"responses": input_items if input_items else []})

@app.get("/seat_booking/response")
async def seat_booking_response():
    state = conversation_states["seat_booking"]
    input_items = state["input_items"]
    return JSONResponse({"responses": input_items if input_items else []})

@app.post("/triage/end")
async def triage_end():
    conversation_id = get_conversation_id("triage")
    end_time = datetime.datetime.now(datetime.timezone.utc)
    result = await db.conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"end_timestamp": end_time}}
    )
    if result.matched_count == 0:
        return JSONResponse({"error": "Conversation not found."}, status_code=404)
    return JSONResponse({"message": "Conversation ended.", "end_timestamp": end_time.isoformat()})

@app.get("/tickets/{confirmation_number}.pdf")
async def get_ticket_pdf(confirmation_number: str):
    # Fetch the booking context from the database
    booking = await db.bookings.find_one({"confirmation_number": confirmation_number})
    if not booking:
        return JSONResponse({"error": "Ticket not found."}, status_code=404)
    from models.context import AirlineAgentContext
    from tools.booking_tools import generate_ticket_pdf
    context = AirlineAgentContext(**booking)
    pdf_bytes = generate_ticket_pdf(context)
    from fastapi.responses import Response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={confirmation_number}.pdf"}
    )

# Optionally, add GET endpoints to fetch conversation state if needed

if __name__ == "__main__":
    asyncio.run(main())