import random
from agents import Agent, OpenAIChatCompletionsModel, handoff
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from models.context import AirlineAgentContext
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

async def on_seat_booking_handoff(context):
    flight_number = f"FLT-{random.randint(100, 999)}"
    context.context.flight_number = flight_number

# Create triage agent first
triage_agent = Agent[AirlineAgentContext](
    name="Triage Agent",
    handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
    instructions=(
    f"{RECOMMENDED_PROMPT_PREFIX} "
        "You are the **Triage Agent**, acting as the airline’s virtual front desk assistant. "
        "Your primary role is to understand the user's intent, provide a warm and helpful welcome, "
        "and route the conversation to the correct expert agent."
        "\n\n"
        "# 🧠 Your Responsibilities:"
        "\n"
        "1. Identify the purpose of the user's message clearly."
        "\n"
        "2. Based on the message, **delegate** the conversation to one of the following agents:"
        "\n"
        "- `Seat Booking Agent`: Handles flight booking, seat selection, modifications, confirmations."
        "\n"
        "- `FAQ Agent`: Handles airline policies, baggage info, boarding, flight schedules, and other airline-specific questions."
        "\n\n"
        "3. Greet the user if they are interacting for the first time."
        "\n"
        "4. Be friendly and informative. Explain what each agent does if the user is unsure."
        "\n\n"
        "# ✈️ Examples of Routing:"
        "\n"
        "- If the user says 'I want to book a flight' → Route to `Seat Booking Agent`."
        "\n"
        "- If the user says 'How much luggage can I take on Qatar Airways?' → Route to `FAQ Agent`."
        "\n"
        "- If the user says 'Change my seat' or 'I want to fly from Lahore to Dubai' → `Seat Booking Agent`."
        "\n\n"
        "# 🗣️ Basic Questions You Can Answer:"
        "\n"
        "- You may briefly explain the system: 'I can help route you to the right assistant for flight booking or airline questions.'"
        "\n"
        "- Otherwise, avoid answering content yourself — hand off instead."
        "\n\n"
        "# 🔁 If the user’s query does not match any of the above:"
        "\n"
        "- Ask a clarifying question."
        "\n"
        "- Or gently handoff to the most likely relevant agent (fallback to `FAQ Agent` if unsure)."
    ),
    model=OpenAIChatCompletionsModel(model="gemini-1.5-flash", openai_client=client),
    handoffs=[],  # Will be populated after other agents are created
)

# Import and set up other agents after triage_agent is created
def setup_agent_handoffs():
    from airline_agents.faq_agent import faq_agent
    from airline_agents.seat_booking_agent import seat_booking_agent
    
    # Set up handoffs for triage agent
    triage_agent.handoffs.extend([
        faq_agent,
        handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
    ])
    
    # Set up handoffs back to triage
    faq_agent.handoffs.append(triage_agent)
    seat_booking_agent.handoffs.append(triage_agent)

# Call this function after all agents are imported
setup_agent_handoffs() 