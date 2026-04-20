from crewai.tools import BaseTool
import requests
import random

# =========================
# 🏥 HOSPITAL TOOL
# =========================
class HospitalTool(BaseTool):
    name: str = "hospital_tool"
    description: str = "Find hospitals using OpenStreetMap Overpass API in India"

    def _run(self, query: str) -> str:
        try:
            overpass_url = "https://overpass-api.de/api/interpreter"

            osm_query = """
            [out:json];
            (
              node["amenity"="hospital"](6.0,68.0,37.0,97.0);
              way["amenity"="hospital"](6.0,68.0,37.0,97.0);
              relation["amenity"="hospital"](6.0,68.0,37.0,97.0);
            );
            out center 10;
            """

            response = requests.get(
                overpass_url,
                params={"data": osm_query},
                timeout=30
            )

            data = response.json()

            results = []

            for el in data.get("elements", [])[:5]:
                tags = el.get("tags", {})
                name = tags.get("name", "Unknown Hospital")

                lat = el.get("lat") or el.get("center", {}).get("lat")
                lon = el.get("lon") or el.get("center", {}).get("lon")
            return "\n".join(results)

        except Exception as e:
            return f"Hospital tool error: {str(e)}"
    def run(self, query: str) -> str:
        return self._run(query)

    


# =========================
# 💰 COST TOOL
# =========================
class CostTool(BaseTool):
    name: str = "cost_tool"
    description: str = "Estimate treatment cost in INR for diseases"

    #def _run(self, disease: str) -> str:
       # low = random.randint(50000, 150000)
       # mid = random.randint(150000, 400000)
       # high = random.randint(400000, 900000)

       # return f"""
#Disease: {disease}
#Low Cost: ₹{low:,}
#Medium Cost: ₹{mid:,}
#High Cost: ₹{high:,}
#""".strip()
    def _run(self, disease: str) -> str:
        low = random.randint(50000, 150000)
        mid = random.randint(150000, 400000)
        high = random.randint(400000, 900000)

        return f"Low: ₹{low}\nMedium: ₹{mid}\nHigh: ₹{high}"    
    def run(self, disease: str) -> str:
        return self._run(disease)
# =========================
# ✅ IMPORTANT: CREATE OBJECTS
# =========================
hospital_tool = HospitalTool()
cost_tool = CostTool()


# =========================
# 🩺 RESOURCE VALIDATOR TOOL (MOCK)
# =========================
class ResourceValidatorTool(BaseTool):
    name: str = "resource_validator_tool"
    description: str = "Validates mock resource availability at a hospital: doctors, beds, and estimated wait time."

    def _run(self, hospital_name: str) -> str:
        import random
        doctors_available = random.randint(2, 12)
        beds_available = random.randint(5, 80)
        wait_days = random.randint(1, 10)
        specialist = random.choice(["Oncologist", "Nephrologist", "Cardiologist", "Neurologist", "Orthopedic Surgeon"])

        return (
            f"Hospital: {hospital_name}\n"
            f"Specialist Available: {specialist} ({doctors_available} doctors)\n"
            f"Beds Available: {beds_available}\n"
            f"Estimated Wait Time: {wait_days} days"
        )

    def run(self, hospital_name: str) -> str:
        return self._run(hospital_name)

resource_validator_tool = ResourceValidatorTool()
