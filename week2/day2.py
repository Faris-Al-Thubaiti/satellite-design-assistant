import json
# satellites = [
#     {
#         "name": "AgriVision-1",
#         "mission_type": "Earth Observation",
#         "orbit": "SSO",
#         "altitude_km": 600,
#         "payload": "Multispectral Camera",
#         "mass_kg": 450,
#         "is_active": True
#     },
#     {
#         "name": "DesertCom-1",
#         "mission_type": "Communication",
#         "orbit": "GEO",
#         "altitude_km": 35786,
#         "payload": "Communication Transponder",
#         "mass_kg": 3200,
#         "is_active": True
#     },
#     {
#         "name": "NavArabia-1",
#         "mission_type": "Navigation",
#         "orbit": "MEO",
#         "altitude_km": 20200,
#         "payload": "Atomic Clock and Navigation Signal Transmitter",
#         "mass_kg": 1800,
#         "is_active": False
#     }
# ]
# with open("week2/satellites.json", "w") as file:
#     json.dump(satellites, file, indent=4)
# with open("week2/satellites.json", "r") as file:
#     loaded_satellites = json.load(file)
# print("Before modifications")
# print(json.dumps(loaded_satellites, indent=4))
# weather_exists = False

# for satellite in loaded_satellites:
#     if satellite["name"] == "WeatherSat-1":
#         weather_exists = True

# if not weather_exists:
#     loaded_satellites.append(
#         {
#             "name": "WeatherSat-1",
#             "mission_type": "Weather Monitoring",
#             "orbit": "GEO",
#             "altitude_km": 35786,
#             "payload": "Multispectral Weather Imager",
#             "mass_kg": 4500,
#             "is_active": False
#         }
#     )

# for satellite in loaded_satellites:
#     if satellite["name"] == "NavArabia-1":
#         satellite["is_active"] = True

# for satellite in loaded_satellites:
#     if satellite["name"] == "AgriVision-1":
#         satellite.pop("mass_kg", None)
# with open("week2/satellites.json", "w") as file:
#     json.dump(loaded_satellites, file, indent=4)
# print("\nAfter modifications:")
# print(json.dumps(loaded_satellites, indent=4))
# with open("week2/knowledge_base.json", "r") as file:
#     knowledge_base = json.load(file)

# user_mission = input("Enter the mission type: ")

# recommendation = knowledge_base.get(user_mission)

# if recommendation is not None:
#     for key, value in recommendation.items():
#         print(key, ":", value)
# else:
#     print("The mission was not found")
with open("week2/ai_response.json", "r") as file:
    ai_design_simulation = json.load(file)
report = f"""
Satellite Design Report
-----------------------
Mission: {ai_design_simulation["mission"]}
Objective: {ai_design_simulation["objective"]}
Orbit: {ai_design_simulation["orbit"]}
Altitude: {ai_design_simulation["altitude_km"]} km
Payload: {ai_design_simulation["payload"]}
Power Budget: {ai_design_simulation["power_budget_w"]} W
Mass: {ai_design_simulation["mass_kg"]} kg
Confidence: {ai_design_simulation["confidence"] * 100}%
"""
print(report)