from __future__ import annotations

import pytest

from ai_api import AIResponseError, MISSION_TYPES, validate_ai_design


def design_for(mission_type):
    return {
        "mission_type": mission_type,
        "recommended_orbit": "leo",
        "altitude_km": 550,
        "payload": "Mission payload",
        "power_watts": 500,
        "mass_class": "Small Satellite",
        "lifetime_years": 4,
        "adcs_type": "Three-axis stabilized",
        "justification": "A realistic conceptual architecture for this mission.",
    }


@pytest.mark.parametrize("mission_type", MISSION_TYPES)
def test_all_eight_mission_types_are_supported(mission_type):
    result = validate_ai_design(design_for(mission_type.lower()))
    assert result["mission_type"] == mission_type
    assert result["recommended_orbit"] == "LEO"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.pop("payload"),
        lambda value: value.update({"unexpected": "field"}),
        lambda value: value.update({"mission_type": "Tourism"}),
        lambda value: value.update({"recommended_orbit": "Mars"}),
        lambda value: value.update({"power_watts": -1}),
        lambda value: value.update({"justification": ""}),
    ],
)
def test_invalid_ai_payloads_are_rejected(mutation):
    value = design_for("Earth Observation")
    mutation(value)
    with pytest.raises(AIResponseError):
        validate_ai_design(value)

