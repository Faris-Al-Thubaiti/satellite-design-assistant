satellite_name = "FarisSat"
mission_type = "Earth Observation"
altitude_km = 511.0
mass_kg = 100.511
is_active = True

# Engineering calculations

satellite_orbit_speed_km_s = (
    7.9 * (6371 / (6371 + altitude_km)) ** 0.5
)

satellite_earth_weight_n = mass_kg * 9.81
satellite_moon_weight_n = mass_kg * 1.62

# Display satellite information

print("Satellite name:", satellite_name)
print("Mission type:", mission_type)
print(f"Altitude: {altitude_km} km")
print(f"Mass: {mass_kg} kg")

if is_active:
    print("The satellite is active")
else:
    print("The satellite is inactive")

print(
    "Approximate orbital speed: "
    f"{satellite_orbit_speed_km_s} km/s"
)

print(
    "Satellite weight on Earth: "
    f"{satellite_earth_weight_n} N"
)

print(
    "Satellite weight on the Moon: "
    f"{satellite_moon_weight_n} N"
)

# User input

user_input_satellite = input(
    "Enter the name of the satellite: "
)

user_input_altitude = input(
    "Enter the altitude in km: "
)

print(f"The satellite name is {user_input_satellite}")
print(f"The altitude is {user_input_altitude} km")
# Exercise 4: Classify the orbit based on altitude

user_altitude_km = float(
    input("Enter the satellite altitude in km: ")
)

if user_altitude_km < 0:
    print("Invalid altitude")

elif user_altitude_km < 2000:
    print("The satellite is in Low Earth Orbit (LEO)")

elif user_altitude_km < 35686:
    print("The satellite is in Medium Earth Orbit (MEO)")

elif user_altitude_km <= 35886:
    print("The satellite is approximately at GEO altitude")

else:
    print("The altitude is above the GEO region")