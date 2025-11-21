# Gemini-Triage-Engine
A proof-of-concept repository for building robust, multi-stage LLM applications. Features a triage agent acting as a central dispatcher for routing requests to specialized handlers or escalating to human intervention.

# 🤖 A2A-Support-Engine

## Agent-to-Agent (A2A) Customer Support Dispatcher

This project implements a robust, multi-agent conversational system using the **Google Gemini API** that demonstrates the **Agent-to-Agent (A2A) orchestration pattern** for enterprise customer support. The system uses a specialized **Triage Agent** to route requests and a **Knowledge Agent** to execute tools and deliver final, grounded answers.

The architecture ensures that complex or sensitive queries are immediately flagged for human escalation, while routine support requests are handled efficiently and autonomously.

---

## ✨ Architecture and Workflow

The system operates based on a clear, sequential A2A protocol:

1.  **Triage Agent (Dispatcher):** Analyzes the user query and the entire session history. Its sole output is a routing decision:
    * `ESCALATION_REQUIRED` (for sensitive issues like refunds/managers).
    * `Knowledge Agent` (for technical or general questions resolvable by tools).
2.  **Knowledge Agent (Executor):** Takes over if routed. It is configured with tools and system instructions to:
    * Use the **Custom Tool** (`get_product_info`) for internal knowledge retrieval.
    * Use the **Built-in Google Search Tool** for real-time external information.
    * Synthesize the tool outputs into a final, comprehensive, and friendly customer response.



[Image of A2A Multi-Agent System architecture diagram for support]


---

## ⚙️ Key Features

* **A2A Orchestration:** Decoupled Triage/Routing from Execution/Answering for modularity and control.
* **Intelligent Routing:** Directs sensitive queries to human agents immediately.
* **Tool-Grounding:** Utilizes both custom functions and real-time search for accurate answers.
* **Session Memory:** Maintains full conversational context across multi-turn interactions, allowing the agent to remember previously discussed products.
* **Observability:** Detailed terminal logging of A2A dispatch and tool calls for easy debugging and demonstration.
* **User Interface:** Provides both an automated simulation mode and a live interactive chat mode via a command-line menu.

---

## 🛠️ Setup and Installation

### Prerequisites

* Python 3.10+
* A **Gemini API Key** (obtainable from Google AI Studio).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourUsername/A2A-Support-Engine.git](https://github.com/YourUsername/A2A-Support-Engine.git)
    cd A2A-Support-Engine
    ```

2.  **Install dependencies:** The project requires the official Gemini SDK and its underlying libraries.
    ```bash
    pip install -r requirements.txt
    ```

### 🔐 Configuration: Setting the API Key (Crucial Step)

The project reads the API key securely from an environment variable named `GOOGLE_API_KEY`.

#### If using GitHub Codespaces (Recommended Secure Method):
1.  Go to your GitHub repository **Settings** $\to$ **Secrets and variables** $\to$ **Codespaces**.
2.  Add a new secret named `GOOGLE_API_KEY` and paste your key as the value.
3.  **Restart your Codespace** to load the new secret.

#### If running locally (e.g., in Windows/Linux Terminal):
Set the variable in your current shell session **before** running the script:

* **Linux/macOS:** `export GOOGLE_API_KEY='YOUR_KEY'`
* **Windows (CMD):** `set GOOGLE_API_KEY=YOUR_KEY`

---

## 🏃 Usage

Run the main Python script directly from your terminal:

`bash
python final_agent_system.py`

You will be presented with the main execution menu:

```
========================================
 Apex Tech Support Agent Demonstration
========================================
1) Run Simulated Cases (Automated Demo)
2) Start Interactive Chat (Enter your own prompts)
3) Exit
```

Note: Running the script directly from the terminal ensures the correct environment variables are inherited, avoiding issues encountered when running via Jupyter kernels.
