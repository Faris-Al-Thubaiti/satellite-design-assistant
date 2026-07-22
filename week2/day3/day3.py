import json
import requests
import time
import os
def main():
    file_name = "astronauts.json"

    data = load_cache(file_name, 3600)

    if data is None:
        print("Fetching new data from API...")

        data = safe_api_call(
            "http://api.open-notify.org/astros.json"
        )

        if data is None:
            print("Could not retrieve astronaut data")
            return 1

        save_cache(file_name, data)
        print("New data saved to cache")

    else:
        print("Using cached data")

    print("\nAstronauts currently in space:")

    for astronaut in data["people"]:
        print("-", astronaut["name"])

    return 0
   
def safe_read_json(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("File not found")

    except json.JSONDecodeError:
        print("Invalid JSON")

    except Exception as e:
        print("Unexpected error:", e)

def safe_api_call(sourceLink):
    try:
        response = requests.get(sourceLink)
        response.raise_for_status()
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return None

def load_cache(filename, max_age):
    if os.path.exists(filename):
        current_time = time.time()
        modified_time = os.path.getmtime(filename)

        file_age = current_time - modified_time

        print("Cache age:", file_age, "seconds")

        if file_age < max_age:
            print("Cache is fresh")

            cached_data = safe_read_json(filename)

            return cached_data

        else:
            print("Cache is expired")
            return None

    else:
        print("Cache file does not exist")
        return None

def save_cache(filename, data):

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
main()