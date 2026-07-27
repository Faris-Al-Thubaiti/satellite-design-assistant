import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import json
from datetime import datetime
from pathlib import Path
# Load environment variables
load_dotenv()


# Get API key
api_key = os.getenv("OPENAI_API_KEY")
# Check for API key
if not api_key:
    raise ValueError("API key not found")


# Create OpenAI client
client = OpenAI(
    api_key=api_key
)

print("OpenAI client created successfully")


def analyze_mission(mission_description):

    instructions = """
You are a satellite systems engineer.

Your task is to analyze the provided mission description
and create a conceptual satellite design.

Return ONLY a valid JSON object.
Do not include:
- Markdown
- Explanations outside JSON
- Comments
- Additional text

The JSON must contain exactly these fields:

{
    "mission_type": "",
    "recommended_orbit": "",
    "altitude_km": 0,
    "payload": "",
    "power_watts": 0,
    "mass_class": "",
    "lifetime_years": 0,
    "adcs_type": "",
    "justification": ""
}

Rules:
- altitude_km must be a number.
- power_watts must be a number.
- lifetime_years must be a number.
- recommended_orbit must be one of:
  LEO, MEO, GEO, SSO, HEO.
- Put all engineering reasoning inside the justification field only.
"""

    try:

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=instructions,
            input=mission_description
        )

        if not response.output_text:
            return "Error: Empty AI response"

        design = json.loads(response.output_text)
        return design

    except json.JSONDecodeError:
        print("AI response was not valid JSON")
        return None
    
    except OpenAIError as e:
        print("Design generation failed")
        return None

    except Exception as e:
        return f"Unexpected error: {e}"

# Test mission

mission = "I need a satellite for taking pictures of taif city every few days"

design = analyze_mission(mission)

def print_recommendation(rec):

    print("\n===== Satellite Design Recommendation =====")

    print("Mission Type:", rec["mission_type"])
    print("Orbit:", rec["recommended_orbit"])
    print("Altitude:", rec["altitude_km"], "km")
    print("Payload:", rec["payload"])
    print("Power:", rec["power_watts"], "Watts")
    print("Mass Class:", rec["mass_class"])
    print("Lifetime:", rec["lifetime_years"], "years")
    print("ADCS:", rec["adcs_type"])

    print("\nJustification:")
    print(rec["justification"])

def save_result(mission, recommendation):

    new_result = {
        "date": datetime.now().isoformat(),
        "mission": mission,
        "recommendation": recommendation
    }

    # Always locate results.json beside day5.py
    filename = Path(__file__).resolve().parent / "results.json"

    try:
        with open(filename, "r", encoding="utf-8") as file:
            results = json.load(file)

        # Protect against the old dictionary format
        if not isinstance(results, list):
            print("Old results format detected. Resetting the file.")
            results = []

    except (FileNotFoundError, json.JSONDecodeError):
        results = []

    results.append(new_result)

    # Rewrite the complete updated list
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    print("Result saved successfully")
    print("File location:", filename)

if design:

    print_recommendation(design)

    save_result(mission, design)

else:
    print("Failed to generate satellite design")