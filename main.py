import re
from agents import planner
from tasks import create_unified_task
from tools import resource_validator_tool
from crewai import Crew

def generate_schedule(disease: str, hospital_names: list[str]) -> str:
    """Generate resource validation for multiple hospitals + execution schedule without LLM."""
    
    resource_blocks = []
    for name in hospital_names:
        resource = resource_validator_tool._run(name)
        resource_blocks.append(resource)
    
    all_resources = "\n\n".join(resource_blocks)

    schedule = f"""Resource Validation:
{all_resources}

Execution Schedule:
Phase 1 - Diagnosis (Week 1-2):
- Consult a specialist for {disease}
- Complete all diagnostic tests (blood work, imaging, biopsies as needed)
- Review reports and confirm diagnosis

Phase 2 - Active Treatment (Week 3-6):
- Begin prescribed treatment protocol for {disease}
- Daily/weekly monitoring of vitals and treatment response
- Adjust medications based on doctor's evaluation

Phase 3 - Recovery & Follow-up (Month 2-3):
- Schedule regular follow-up consultations
- Adopt recommended lifestyle and dietary changes
- Preventive care to avoid recurrence"""

    return schedule


def run_system(user_data):
    # Use the unified task for speed
    tasks = create_unified_task(user_data)
    
    crew = Crew(
        agents=[planner],
        tasks=tasks,
        verbose=True,
        process="sequential"
    )

    import time

    max_retries = 3
    for attempt in range(max_retries):
        try:
            output = crew.kickoff()
            break  
        except Exception as e:
            err = str(e)
            if "rate_limit_exceeded" in err or "RateLimitError" in err:
                wait_seconds = 2 # Reduced from 30s
                if attempt < max_retries - 1:
                    time.sleep(wait_seconds)
                    continue
            raise 

    full_output = output.raw or ""
    
    # Split using simple markers
    treatment = ""
    hospitals = ""
    costs = ""
    
    # Robust XML-style parsing
    treatment = ""
    hospitals = ""
    costs = ""
    
    treatment_match = re.search(r"<treatment>(.*?)</treatment>", full_output, re.DOTALL | re.IGNORECASE)
    if treatment_match:
        treatment = treatment_match.group(1).strip()
    
    hospitals_match = re.search(r"<hospitals>(.*?)</hospitals>", full_output, re.DOTALL | re.IGNORECASE)
    if hospitals_match:
        hospitals = hospitals_match.group(1).strip()
        
    costs_match = re.search(r"<costs>(.*?)</costs>", full_output, re.DOTALL | re.IGNORECASE)
    if costs_match:
        costs = costs_match.group(1).strip()

    # If parsing failed, use fallback markers or full output
    if not treatment:
        treatment = full_output.split("TREATMENT")[-1].split("HOSPITAL")[0].strip("#[]:* \n\t")
    if not hospitals:
        hospitals = full_output.split("HOSPITAL")[-1].split("COST")[0].strip("#[]:* \n\t")
    if not costs:
        costs = full_output.split("COST")[-1].strip("#[]:* \n\t")

    # Final safeguard
    if len(treatment) < 10: treatment = full_output

    # Extract up to 3 hospital names for the schedule
    hospital_names = []
    for line in hospitals.splitlines():
        line = line.strip()
        if not line: continue
        
        # Priority 1: Text between **
        match = re.search(r'\*\*(.*?)\*\*', line)
        if match:
            name = match.group(1).strip()
        # Priority 2: Text before a colon if it looks like a name
        elif ":" in line and not line.lower().startswith("address"):
            name = line.split(":")[0].strip().lstrip("-•*123456789. ")
        # Priority 3: Just the line if it's short and doesn't have "Address"
        elif len(line) < 60 and "address" not in line.lower() and len(line) > 5:
            name = line.lstrip("-•*123456789. ").strip()
        else:
            continue
            
        if name and len(name) > 5 and "address" not in name.lower() and ":" not in name:
            if name not in hospital_names:
                hospital_names.append(name)
        
        if len(hospital_names) >= 3:
            break

    if not hospital_names:
        willing = user_data.get("willing_to_travel", "No")
        default_hospital = "AIIMS New Delhi" if willing == "Yes" else f"City Hospital, {user_data.get('location', 'your city')}"
        hospital_names = [default_hospital]

    schedule = generate_schedule(user_data.get("disease", "your condition"), hospital_names)

    return {
        "treatment": treatment,
        "hospitals": hospitals,
        "cost": costs,
        "schedule": schedule
    }
