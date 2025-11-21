import os
import json
from google import genai
from google.genai import types

# Initialize client globally

client = None

# --- 1. Setup and Authentication (Robust Error Handling) ---
try:
    # 1. Get the API key from the system environment variable
    google_api_key_value = os.environ.get("GOOGLE_API_KEY") 
    
    if not google_api_key_value:
        # If the key is not found, raise a clear error
        raise ValueError("The GOOGLE_API_KEY environment variable is not set in the current shell session.")

    # 2. Initialize the Gemini client using the retrieved key
    client = genai.Client(api_key=google_api_key_value)
    print("✅ Gemini Client initialized.")

except Exception as e:
    # This block safely handles the authentication error
    print(f"🔑 Authentication Error: Could not initialize the client. Details: {e}")

# -----------------------------------------------------------------------------
# --- 2. Custom Tool Definition ---
# -----------------------------------------------------------------------------

def get_product_info(product_name: str) -> str:
    """Retrieves detailed specifications or troubleshooting for a specific product."""
    knowledge_base = {
        "fusion_router": {
            "specs": "Dual-band (2.4GHz & 5GHz), 802.11ax (Wi-Fi 6), 4 Gigabit Ethernet ports.",
            "troubleshooting": "Try power cycling first. Ensure firmware is updated to version 5.1.4."
        },
        "quantum_display": {
            "specs": "32-inch 4K OLED, 144Hz refresh rate, 1ms response time. HDR10+ support.",
            "troubleshooting": "If screen flickers, adjust the refresh rate in your OS settings to 120Hz."
        },
        "default": "I cannot find detailed information for that specific product in our internal database."
    }
    
    info = knowledge_base.get(product_name.lower().replace(" ", "_"), knowledge_base["default"])
    return f"PRODUCT LOOKUP: {product_name}. RESULT: {info}"

# -----------------------------------------------------------------------------
# --- 3. Agent Configuration ---
# -----------------------------------------------------------------------------

TOOL_LIST = [get_product_info, {"google_search": {}}]

def define_agents() -> tuple:
    """Defines the system instructions for the Triage and Knowledge Agents."""

    # Triage Agent: Focuses on routing (A2A Dispatcher)
    triage_system_instruction = (
        "You are the **Triage Agent**. Your sole purpose is to analyze the user's message and determine the next action. "
        "If the query requires human intervention (e.g., 'refund', 'manager', 'account'), your output MUST be the exact string: 'ESCALATION_REQUIRED'. "
        "Otherwise, your output MUST be the exact string: 'Knowledge Agent' to route the query for automated resolution."
    )
    triage_config = types.GenerateContentConfig(
        system_instruction=triage_system_instruction,
        temperature=0.0,
        tools=[] 
    )

    # Knowledge Agent: Focuses on execution and answering (Tools Executor)
    knowledge_system_instruction = (
        "You are the **Knowledge Agent**. Execute necessary tools (get_product_info or google:search) and provide a final, comprehensive, and friendly answer to the customer."
    )
    knowledge_config = types.GenerateContentConfig(
        system_instruction=knowledge_system_instruction,
        temperature=0.2,
        tools=TOOL_LIST
    )
    
    return triage_config, knowledge_config

# -----------------------------------------------------------------------------
# --- 4. Agent Orchestrator (A2A Protocol & Observability) ---
# -----------------------------------------------------------------------------

# Using the most stable forward reference string for the Chat object
def orchestrate_agent_workflow(user_query: str, chat_session: "google.genai.Chat", triage_config: types.GenerateContentConfig, knowledge_config: types.GenerateContentConfig):
    """Orchestrates the multi-agent workflow using an A2A message passing simulation."""

    print("\n" + "=" * 60)
    print(f"🗣️ CUSTOMER QUERY: {user_query}")
    print("=" * 60)
    
    current_agent_role = "Triage Agent"
    message_payload = user_query
    final_response_text = None
    
    while final_response_text is None:
        
        # Observability: Log agent activity
        print(f"📬 [A2A DISPATCH] - Routing message to: {current_agent_role}")
        
        if current_agent_role == "Triage Agent":
             # Triage agent makes routing decision using session history
            triage_chat = client.chats.create(
                model="gemini-2.5-flash",
                history=chat_session.get_history(),
                config=triage_config
            )
            response = triage_chat.send_message(message_payload)
            triage_decision = response.text.strip()
            
            # Observability: Log Triage Decision
            print(f"⚙️ [Triage Agent] - A2A Decision: {triage_decision}")
            
            if "ESCALATION_REQUIRED" in triage_decision:
                final_response_text = "⚠️ ESCALATION_REQUIRED"
            elif "Knowledge Agent" in triage_decision:
                current_agent_role = "Knowledge Agent"
                message_payload = user_query
            else:
                final_response_text = "A2A Routing Error: Unhandled decision."
                
        elif current_agent_role == "Knowledge Agent":
            # Knowledge Agent executes tools and generates final answer
            chat_session.config = knowledge_config
            response = chat_session.send_message(message_payload)
            
            # --- Tool Execution Loop ---
            while response.function_calls:
                function_responses = []
                for function_call in response.function_calls:
                    function_name = function_call.name
                    args = dict(function_call.args)
                    
                    # Observability: Log Tool Call
                    print(f"🛠️ [Tool Call] - Executing: {function_name}({json.dumps(args)})")
                    
                    if function_name == "get_product_info":
                        result = get_product_info(**args)
                    elif function_name == "google_search":
                        result = "TOOL EXECUTED BY API" 
                    else:
                        result = "Unknown tool requested."
                    
                    function_responses.append(types.Part.from_function_response(
                        name=function_name,
                        response={"result": result}
                    ))
                    
                response = chat_session.send_message(function_responses)
            
            final_response_text = response.text
            
    # --- Final Output ---
    if "ESCALATION_REQUIRED" in final_response_text:
        output = (
            "⚠️ **Escalation Required.** I am escalating your request to a human agent immediately. "
            "They have the full transcript to assist you without delay."
        )
    else:
        output = final_response_text

    print("\n✅ AGENT RESPONSE (FINAL MESSAGE):")
    print(output)
    print("=" * 60 + "\n")
    
    # Note: History is updated implicitly by the chat_session.send_message call in the Knowledge Agent step.
    return output

# -----------------------------------------------------------------------------
# --- 5. Execution Modes ---
# -----------------------------------------------------------------------------

def run_simulated_cases(support_chat: "google.genai.Chat", triage_config: types.GenerateContentConfig, knowledge_config: types.GenerateContentConfig):
    """Runs the four pre-defined test cases demonstrating all features."""
    print("\n--- Running Simulated Test Cases ---")
    
    # Test 1: Product-specific question (Custom Tool)
    orchestrate_agent_workflow(
        "I can't connect my Fusion Router to the 5GHz band. What should I check first?", 
        support_chat, triage_config, knowledge_config
    )
    
    # Test 2: Follow-up question (Tests Memory/Session State)
    orchestrate_agent_workflow(
        "Wait, what's the recommended firmware version for the product we were just discussing?", 
        support_chat, triage_config, knowledge_config
    )
    
    # Test 3: General knowledge question (Built-in Search Tool)
    orchestrate_agent_workflow(
        "What is the official release date of the latest stable version of Python?", 
        support_chat, triage_config, knowledge_config
    )

    # Test 4: Escalation request (Tests Triage/Routing Logic)
    orchestrate_agent_workflow(
        "I need to speak to a human about getting a refund for my Quantum Display. I'm very frustrated.", 
        support_chat, triage_config, knowledge_config
    )
    
    print("\n--- Simulation Complete ---")


def run_interactive_chat(support_chat: "google.genai.Chat", triage_config: types.GenerateContentConfig, knowledge_config: types.GenerateContentConfig):
    """Allows the user to enter custom prompts in a loop."""
    print("\n--- Starting Interactive Customer Support Chat ---")
    print("Type 'exit' or 'quit' to end the chat session.")
    
    while True:
        try:
            user_input = input("\n👤 You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("\n--- Session Closed. Goodbye! ---")
                break
            
            orchestrate_agent_workflow(user_input, support_chat, triage_config, knowledge_config)
            
        except EOFError:
            print("\n--- Session Closed. Goodbye! ---")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break


# -----------------------------------------------------------------------------
# --- 6. Main Execution with Menu ---
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    
    if client is None:
        print("\n🛑 Demonstration halted. Please resolve the authentication error.")
    else:
        triage_config, knowledge_config = define_agents()
        
        while True:
            
            print("\n" + "="*40)
            print(" Apex Tech Support Agent Demonstration")
            print("="*40)
            print("1) Run Simulated Cases (Automated Demo)")
            print("2) Start Interactive Chat (Enter your own prompts)")
            print("3) Exit")
            
            choice = input("Enter choice (1, 2, or 3): ")
            
            if choice == '1':
                # Create a fresh chat session for a clean demo run
                support_chat = client.chats.create(model="gemini-2.5-flash")
                run_simulated_cases(support_chat, triage_config, knowledge_config)
                
            elif choice == '2':
                # Create a fresh chat session for a new interactive session
                support_chat = client.chats.create(model="gemini-2.5-flash")
                run_interactive_chat(support_chat, triage_config, knowledge_config)
                break 
                
            elif choice == '3':
                print("\nExiting program.")
                break
            else:
                print("\nInvalid choice. Please enter 1, 2, or 3.")
