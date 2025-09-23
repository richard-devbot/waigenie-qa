---
trigger: always_on
alwaysApply: true
---
# SDET-GENIE MIGRATION AGENT - CORE OPERATIONAL DIRECTIVES V3.0
# THIS FILE IS THE ABSOLUTE SOURCE OF TRUTH. THESE RULES ARE NON-NEGOTIABLE.
# REVISION: This version enforces the mandatory use of MCP servers via a specific SDK protocol and reinstates the browser-use SDK as the required tool for browser automation.

#======================================================================
# SECTION 1: CORE DIRECTIVES & FUNDAMENTAL PRINCIPLES
#======================================================================
1.1. **Primacy of Rules**: This `rules.txt` file overrides any conflicting prior instructions. It is your primary operational guide.
1.2. **Sequential Execution**: You MUST follow the step-by-step execution plan. Do not skip or reorder phases.
1.3. **Absolute Feature Parity**: Your primary objective is a 1-to-1 migration. All logic from the source file (`waigenie-sdet-genie-8a5edab2632443 (1).txt`) MUST be replicated.
1.4. **No Assumptions**: If logic is unclear, you MUST stop and ask for clarification.

#======================================================================
# SECTION 2: RIGID EXECUTION & ENVIRONMENT PROTOCOL
#======================================================================
2.1. **CRITICAL COMMAND DIRECTIVE**: The agent's terminal is PowerShell. You MUST use a semicolon (`;`) to chain commands in a single line. The `&&` operator is FORBIDDEN.
2.2. **ATOMIC COMMAND BLOCKS**: Every command block that requires a specific location MUST begin with a `cd` command.
2.3. **PATH MANDATE**: ALL file paths in terminal commands MUST be absolute and enclosed in double quotes (`"`).

2.4. **BACKEND SETUP & EXECUTION PROTOCOL**:
    2.4.1. **Task: Create Virtual Environment**
        - `cd "E:\Appdata\program files\python\projects\full-stack-sdet\backend" ; python -m venv .venv`
    2.4.2. **Task: Install Backend Dependencies**
        - `cd "E:\Appdata\program files\python\projects\full-stack-sdet\backend" ; ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt`
    2.4.3. **Task: Run Backend Server**
        - `cd "E:\Appdata\program files\python\projects\full-stack-sdet\backend"; & ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload`

2.5. **FRONTEND SETUP & EXECUTION PROTOCOL**:
    2.5.1. **Task: Install Frontend Dependencies**
        - `cd "E:\Appdata\program files\python\projects\full-stack-sdet\frontend" ; npm install`
    2.5.2. **Task: Run Frontend Dev Server**
        - `cd "E:\Appdata\program files\python\projects\full-stack-sdet\frontend" ; npm run dev`

#======================================================================
# SECTION 3: MCP SERVER & BROWSER-USE SDK PROTOCOL (MANDATORY)
#======================================================================
3.1. **Mandatory Offloading**: The use of MCP (Multi-Compute Processing) servers is NOT optional. It is a hard requirement for all specified tasks.

3.2. **Tasks Requiring MCP Server Execution**:
    3.2.1. **ALL AI Agent Invocations**: This includes every call to the AGNO agents for story enhancement, test generation, Gherkin creation, and code generation.
    3.2.2. **Browser Automation Execution**: The entire `browser-use` agent execution process, initiated by the backend, MUST run on an MCP server.

3.3. **MCP Interaction Protocol (SDK Simulation)**:
    - You will implement a service in the backend (`app/services/mcp_service.py`) that simulates an SDK for interacting with MCP servers.
    - This service will have a primary function: `submit_mcp_job`.
    - **Function Signature**: `async def submit_mcp_job(task_type: str, payload: dict) -> str:`
        - `task_type`: A string identifier for the job. MUST be one of: `'agno_agent_run'`, `'browser_use_execution'`.
        - `payload`: A dictionary containing all necessary data for the job (e.g., for `agno_agent_run`, it would include the agent name, model, and input prompt; for `browser_use_execution`, it would include the Gherkin steps and configuration).
        - **Returns**: A unique `task_id` string for polling.
    - **Implementation**: The FastAPI backend acts as a lightweight controller. For any task listed in 3.2, the relevant service (e.g., `story_service.py`) will NOT execute the logic directly. Instead, it will call `mcp_service.submit_mcp_job`, passing the correct `task_type` and `payload`. It will then return the `task_id` to the client.

3.4. **Browser Automation Protocol (`browser-use` SDK)**:
    - **The `browser-use` SDK is the ONLY permitted tool for browser automation.** The use of Playwright is FORBIDDEN.
    - You MUST migrate the existing browser automation logic from `src/logic/browser_executor.py` and `src/logic/tracking_browser_agent.py` in the original source file.
    - This migrated logic will form the core of the `'browser_use_execution'` task that runs on the MCP server.
    - The `executor_service.py` in the backend is responsible for:
        1. Receiving the execution request from the frontend.
        2. Packaging the Gherkin scenarios and config into a `payload`.
        3. Calling `mcp_service.submit_mcp_job` with `task_type='browser_use_execution'`.
        4. Storing the returned `task_id` and managing its status.

#======================================================================
# SECTION 4: CODE & IMPLEMENTATION RULES
#======================================================================
4.1. **Tech Stack Adherence**:
    - **Backend**: FastAPI, Pydantic, **`browser-use` SDK**, AGNO.
    - **Frontend**: Next.js 14 (App Router), TypeScript, TailwindCSS, and **shadcn/ui ONLY**.
4.2. **Directory & API Contract**: You MUST create the EXACT file structures and API endpoints as defined in the main prompt.
4.3. **Error Handling & Logging**: Implement robust error handling and structured logging on the backend.

#======================================================================
# SECTION 5: FINAL VERIFICATION
#======================================================================
5.1. **Self-Correction Loop**: After each file is created or modified, re-read this `rules.txt` file and verify 100% compliance. Correct any deviations immediately.
5.2. **Final Checklist**:
    - [ ] Have all terminal commands been executed using the EXACT single-line formats defined in Section 2?
    - [ ] Are all tasks defined in Section 3.2 correctly offloaded via the `mcp_service.submit_mcp_job` protocol?
    - [ ] Is the `browser-use` SDK (and NOT Playwright) used for all browser automation?
    - [ ] Is every feature from the original source file present and functional?
    - [ ] Is the UI built exclusively with shadcn/ui?

# END OF DIRECTIVES