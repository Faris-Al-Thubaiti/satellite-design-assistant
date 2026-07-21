#Exercise 1
# satellite = {
#     "name": "FarisSat",
#     "country": "Saudi Arabia",
#     "mission_type": "Earth Observation",
#     "orbit": "LEO",
#     "altitude_km": 600,
#     "mass_kg": 300,
#     "launch_year": 2030,
#     "is_active": False
# }

# print("Satellite Name:", satellite.get("name"))
# print("Country:", satellite.get("country"))
# print("Mission Type:", satellite.get("mission_type"))
# print("Orbit:", satellite.get("orbit"))
# print("Altitude in km:", satellite.get("altitude_km"))
# print("Mass in kg:", satellite.get("mass_kg"))
# print("Launch Year:", satellite.get("launch_year"))
# print("Is Active:", satellite.get("is_active"))
#---------------------------------------------------------------------
#Exercise 2
# satellite_mission_orbit = {
#     "earth observation": "LEO / SSO",
#     "communication": "GEO",
#     "navigation": "MEO",
#     "remote sensing": "SSO",
#     "scientific research": "Depends on objective",
#     "technology demonstration": "LEO",
#     "disaster management": "LEO / GEO",
#     "weather monitoring": "GEO / LEO"
# }

# user_input = input(
#     "Enter the mission type to recommend an orbit: "
# ).strip().lower() # Used the 2 functions to remove addition spaces and convert every character to small

# recommended_orbit = satellite_mission_orbit.get(
#     user_input,
#     "Mission type is undefined"
# )

# print("Recommended orbit:", recommended_orbit)
#--------------------------------------------------------------------------------
#Exercise 3
# mission_recommendations = [
#     {
#         "mission": {
#             "type": "Earth Observation",
#             "objective": "Monitor urban expansion and coastline changes in Saudi Arabia"
#         },
#         "orbit": {
#             "type": "SSO",
#             "altitude_km": 600
#         },
#         "payload": {
#             "type": "High-resolution optical camera",
#             "purpose": "Capture detailed images of cities and coastal regions"
#         },
#         "subsystems": {
#             "power": "Solar panels and rechargeable battery",
#             "communication": "X-band downlink",
#             "adcs": "Three-axis stabilization",
#             "thermal": "Passive thermal control",
#             "computer": "On-board computer"
#         }
#     },

#     {
#         "mission": {
#             "type": "Communication",
#             "objective": "Provide continuous television and communication services across the Middle East"
#         },
#         "orbit": {
#             "type": "GEO",
#             "altitude_km": 35786
#         },
#         "payload": {
#             "type": "Communication transponder",
#             "purpose": "Receive, amplify, and retransmit communication signals"
#         },
#         "subsystems": {
#             "power": "Large solar panels and rechargeable batteries",
#             "communication": "Radio-frequency communication system",
#             "adcs": "Precise Earth-pointing three-axis stabilization",
#             "thermal": "Active and passive thermal control",
#             "computer": "On-board communication processor"
#         }
#     },

#     {
#         "mission": {
#             "type": "Navigation",
#             "objective": "Provide regional positioning services for aircraft, ships, and vehicles"
#         },
#         "orbit": {
#             "type": "MEO",
#             "altitude_km": 20200
#         },
#         "payload": {
#             "type": "Atomic clock and navigation signal transmitter",
#             "purpose": "Broadcast accurate timing and positioning signals"
#         },
#         "subsystems": {
#             "power": "Solar panels and rechargeable battery",
#             "communication": "Navigation signal transmission system",
#             "adcs": "Three-axis stabilization",
#             "thermal": "Active thermal control",
#             "computer": "Navigation on-board computer"
#         }
#     },

#     {
#         "mission": {
#             "type": "Remote Sensing",
#             "objective": "Monitor vegetation health, soil conditions, and water stress"
#         },
#         "orbit": {
#             "type": "SSO",
#             "altitude_km": 700
#         },
#         "payload": {
#             "type": "Multispectral camera",
#             "purpose": "Capture visible and infrared data for environmental analysis"
#         },
#         "subsystems": {
#             "power": "Solar panels and rechargeable battery",
#             "communication": "X-band data downlink",
#             "adcs": "High-precision three-axis stabilization",
#             "thermal": "Passive thermal control",
#             "computer": "Image-processing on-board computer"
#         }
#     },

#     {
#         "mission": {
#             "type": "Scientific Research",
#             "objective": "Measure radiation and charged particles in near-Earth space"
#         },
#         "orbit": {
#             "type": "LEO",
#             "altitude_km": 800
#         },
#         "payload": {
#             "type": "Radiation detector and particle sensor",
#             "purpose": "Measure radiation levels and particle activity"
#         },
#         "subsystems": {
#             "power": "Solar panels and rechargeable battery",
#             "communication": "S-band telemetry system",
#             "adcs": "Basic three-axis stabilization",
#             "thermal": "Passive thermal control",
#             "computer": "Scientific data-handling computer"
#         }
#     },

#     {
#         "mission": {
#             "type": "Technology Demonstration",
#             "objective": "Test a new compact satellite computer in space"
#         },
#         "orbit": {
#             "type": "LEO",
#             "altitude_km": 500
#         },
#         "payload": {
#             "type": "Experimental on-board computer",
#             "purpose": "Test radiation tolerance, temperature resistance, and processing performance"
#         },
#         "subsystems": {
#             "power": "Small solar panels and rechargeable battery",
#             "communication": "S-band telemetry system",
#             "adcs": "Basic three-axis stabilization",
#             "thermal": "Passive thermal control",
#             "computer": "Experimental flight computer"
#         }
#     },

#     {
#         "mission": {
#             "type": "Disaster Management",
#             "objective": "Detect floods and provide updated imagery during emergencies"
#         },
#         "orbit": {
#             "type": "LEO",
#             "altitude_km": 600
#         },
#         "payload": {
#             "type": "Synthetic Aperture Radar",
#             "purpose": "Capture images during day, night, and cloudy conditions"
#         },
#         "subsystems": {
#             "power": "High-capacity solar panels and rechargeable batteries",
#             "communication": "High-data-rate X-band downlink",
#             "adcs": "High-precision three-axis stabilization",
#             "thermal": "Active and passive thermal control",
#             "computer": "Radar data-processing computer"
#         }
#     },

#     {
#         "mission": {
#             "type": "Weather Monitoring",
#             "objective": "Continuously monitor clouds, sandstorms, and regional weather systems"
#         },
#         "orbit": {
#             "type": "GEO",
#             "altitude_km": 35786
#         },
#         "payload": {
#             "type": "Multispectral weather imager",
#             "purpose": "Observe clouds, storms, and atmospheric conditions"
#         },
#         "subsystems": {
#             "power": "Large solar panels and rechargeable batteries",
#             "communication": "High-data-rate weather data downlink",
#             "adcs": "Precise Earth-pointing three-axis stabilization",
#             "thermal": "Active and passive thermal control",
#             "computer": "Weather data-processing computer"
#         }
#     }
# ]
# for recommendation in mission_recommendations:
#     print("\nNEW MISSION")

#     for section, details in recommendation.items():
#         print(section.upper())

#         for key, value in details.items():
#             print(key, ":", value)
#-----------------------------------------------------------------------
#Exercise 4
satellites = [
    {
        "name": "SaudiSat 5",
        "country": "Saudi Arabia",
        "mission_type": "Earth Observation",
        "orbit": "LEO",
        "mass_kg": 350,
        "launch_year": 2018,
        "is_active": True
    },

    {
        "name": "GPS III SV06",
        "country": "United States",
        "mission_type": "Navigation",
        "orbit": "MEO",
        "mass_kg": 3880,
        "launch_year": 2022,
        "is_active": True
    },

    {
        "name": "James Webb Space Telescope",
        "country": "United States",
        "mission_type": "Scientific Research",
        "orbit": "L2 Orbit",
        "mass_kg": 6200,
        "launch_year": 2021,
        "is_active": False
    }
]
heaviest = None

for satellite in satellites:
    if satellite["is_active"]:

        print(satellite["name"])

        if heaviest is None or satellite["mass_kg"] > heaviest["mass_kg"]:
            heaviest = satellite

print(
    "The heaviest active satellite is:",
    heaviest["name"],
    "with mass",
    heaviest["mass_kg"],
    "kg"
)