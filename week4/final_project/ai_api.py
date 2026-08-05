"""OpenAI integration and strict recommendation validation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


BASE_DIR = Path(__file__).resolve().parent
REPOSITORY_DIR = BASE_DIR.parents[1]
load_dotenv(REPOSITORY_DIR / ".env")
load_dotenv(BASE_DIR / ".env", override=False)

MISSION_TYPES = (
    "Earth Observation",
    "Communication",
    "Navigation",
    "Weather Monitoring",
    "Remote Sensing",
    "Scientific Research",
    "Technology Demonstration",
    "Disaster Management",
)

ALLOWED_ORBITS = {"LEO", "MEO", "GEO", "SSO", "HEO"}

AI_FIELDS = {
    "mission_type",
    "recommended_orbit",
    "altitude_km",
    "payload",
    "power_watts",
    "mass_class",
    "lifetime_years",
    "adcs_type",
    "justification",
}


class AIServiceError(RuntimeError):
    """The upstream AI request failed."""


class AIServiceUnavailable(AIServiceError):
    """The AI service is not configured."""


class AIResponseError(AIServiceError):
    """The AI returned an unsafe or incomplete payload."""


def _canonical_mission_type(value: object) -> str | None:
    normalized = str(value).strip().casefold()
    return next(
        (item for item in MISSION_TYPES if item.casefold() == normalized),
        None,
    )


def validate_ai_design(design: Any) -> dict[str, Any]:
    """Return a normalized design or raise a clear validation error."""

    if not isinstance(design, dict):
        raise AIResponseError("The AI response was not a JSON object.")

    received_fields = set(design)
    if received_fields != AI_FIELDS:
        missing = ", ".join(sorted(AI_FIELDS - received_fields))
        extra = ", ".join(sorted(received_fields - AI_FIELDS))
        details = []
        if missing:
            details.append(f"missing: {missing}")
        if extra:
            details.append(f"unexpected: {extra}")
        raise AIResponseError("The AI response fields were invalid (" + "; ".join(details) + ").")

    mission_type = _canonical_mission_type(design["mission_type"])
    if mission_type is None:
        raise AIResponseError("The AI returned an unsupported mission type.")

    orbit = str(design["recommended_orbit"]).strip().upper()
    if orbit not in ALLOWED_ORBITS:
        raise AIResponseError("The AI returned an unsupported orbit.")

    for field in ("altitude_km", "power_watts", "lifetime_years"):
        value = design[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise AIResponseError(f"The AI field '{field}' must be a positive number.")

    for field in ("payload", "mass_class", "adcs_type", "justification"):
        value = design[field]
        if not isinstance(value, str) or not value.strip():
            raise AIResponseError(f"The AI field '{field}' must contain text.")

    normalized_design = dict(design)
    normalized_design["mission_type"] = mission_type
    normalized_design["recommended_orbit"] = orbit

    for field in ("payload", "mass_class", "adcs_type", "justification"):
        normalized_design[field] = normalized_design[field].strip()

    return normalized_design


def analyze_mission(mission_description: str) -> dict[str, Any]:
    """Generate and validate one conceptual satellite recommendation."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIServiceUnavailable(
            "OPENAI_API_KEY is not configured. Add it to the repository .env file."
        )

    model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = OpenAI(api_key=api_key)

    allowed_types = ", ".join(MISSION_TYPES)
    instructions = f"""
You are a satellite systems engineer producing a conceptual design recommendation.

Return only one valid JSON object with exactly these fields:
{{
  "mission_type": "",
  "recommended_orbit": "",
  "altitude_km": 0,
  "payload": "",
  "power_watts": 0,
  "mass_class": "",
  "lifetime_years": 0,
  "adcs_type": "",
  "justification": ""
}}

mission_type must be exactly one of: {allowed_types}.
recommended_orbit must be exactly one of: LEO, MEO, GEO, SSO, HEO.
altitude_km, power_watts, and lifetime_years must be positive numbers.
Choose realistic conceptual values and put all engineering reasoning in justification.
Do not include Markdown, comments, code fences, or any text outside the JSON object.
""".strip()

    try:
        response = client.responses.create(
            model=model_name,
            instructions=instructions,
            input=mission_description,
        )
        response_text = (response.output_text or "").strip()
        if not response_text:
            raise AIResponseError("The AI returned an empty response.")
        return validate_ai_design(json.loads(response_text))
    except json.JSONDecodeError as error:
        raise AIResponseError("The AI response was not valid JSON.") from error
    except AIServiceError:
        raise
    except OpenAIError as error:
        raise AIServiceError("The AI service could not complete the analysis. Try again.") from error

