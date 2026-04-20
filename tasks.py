from crewai import Task
from agents import planner, researcher, cost_agent, scheduler_agent
from tools import hospital_tool, cost_tool, resource_validator_tool

def create_unified_task(user_data):
    willing = user_data.get('willing_to_travel', 'No')
    if willing == "Yes":
        hospital_scope = f"Find the top 3 best hospitals in ALL OF INDIA renowned for treating {user_data['disease']}. These should be nationally recognized centers of excellence."
    else:
        hospital_scope = f"Find 3 real hospitals in {user_data['location']} that treat {user_data['disease']}."

    task = Task(
        description=f"""
        Act as a senior medical expert. Provide a comprehensive healthcare plan for {user_data['patient_name']} ({user_data['age']}y, {user_data['gender']}) suffering from {user_data['disease']}.
        
        1. TREATMENT SUMMARY:
        - Explain the condition clearly (100-150 words).
        - Provide 5-6 detailed care steps and lifestyle advice.
        - Ensure it feels professional and supportive.
        
        2. HOSPITALS:
        - {hospital_scope}
        - IMPORTANT: Provide 3 DIFFERENT, REAL hospitals.
        - Each hospital MUST have its own UNIQUE and SPECIFIC address (include locality or street if possible).
        - DO NOT repeat the same address for different hospitals.
        
        3. COSTS:
        - Provide average Low, Medium, and High treatment cost ranges in INR for {user_data['disease']}.
        - Then, provide a specific cost estimate for each of the 3 hospitals.
        
        FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
        
        <treatment>
        <Detailed explanation and steps here>
        </treatment>
        
        <hospitals>
        - **Hospital Name 1**
          Address: <Specific Unique Address>
        - **Hospital Name 2**
          Address: <Specific Unique Address>
        - **Hospital Name 3**
          Address: <Specific Unique Address>
        </hospitals>
          
        <costs>
        Average Low: ₹<val>
        Average Medium: ₹<val>
        Average High: ₹<val>
        
        **Hospital Name 1**
        - Low: ₹<val>
        - Medium: ₹<val>
        - High: ₹<val>
        ...
        </costs>
        """,
        expected_output="Detailed medical plan with unique hospital data and comprehensive treatment summary",
        agent=planner
    )
    return [task]

def create_tasks(user_data):

    if not user_data:
        raise ValueError("user_data is empty")
    task1 = Task(
        description=f"""
Explain {user_data['disease']} in simple words for a {user_data['age']} year old {user_data['gender']} patient named {user_data['patient_name']} (max 80 words).
Give only 4 key treatment steps.
""",
        expected_output="Short medical explanation",
        agent=planner
    )

    willing = user_data.get('willing_to_travel', 'No')
    if willing == "Yes":
        hospital_scope = f"Find the top 3 best hospitals in ALL OF INDIA renowned for treating {user_data['disease']}. These should be nationally recognized centers of excellence."
        hospital_address_note = "Return the hospital's city and state as address (e.g. AIIMS, Ansari Nagar, New Delhi)."
    else:
        hospital_scope = f"Find 3 real hospitals in {user_data['location']} that treat {user_data['disease']}."
        hospital_address_note = f"Return the local area/locality within {user_data['location']} as address (e.g. Vijay Nagar, Indore)."

    task2 = Task(
        description=f"""
{hospital_scope}
For each hospital return ONLY:
- Hospital Name
- Address: {hospital_address_note}

Do NOT include any website links, URLs, or phone numbers.
""",
        expected_output="List of 3 hospitals with name and address",
        agent=researcher
    )

    task3 = Task(
    description=f"""
Review the list of hospitals found by the researcher.
1. First, estimate the GENERAL AVERAGE treatment cost for {user_data['disease']} using the cost_tool.
2. Then, for EACH hospital, provide the cost estimate.

Return the output in this EXACT format:

Average Low: ₹<value>
Average Medium: ₹<value>
Average High: ₹<value>

**Hospital Name 1**
- Low: ₹<value>
- Medium: ₹<value>
- High: ₹<value>

**Hospital Name 2**
- Low: ₹<value>
- Medium: ₹<value>
- High: ₹<value>

Do NOT say anything like "requirements are met"
Do NOT add explanation
""",
    expected_output="Average costs and list of hospitals with their respective 3 line INR cost",
    agent=cost_agent,
    tools=[cost_tool]
)
    return [task1, task2, task3]