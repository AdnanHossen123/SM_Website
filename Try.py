
import requests



url = "https://raw.githubusercontent.com/CodesWithIshan/samsung_database/refs/heads/main/samsungM%26B_data.json"

req = requests.get(url)
if req.status_code == 200:
    repo_data = req.json()
else:
    print("Database destruction", req.status_code, "!!")
    exit()

repo_models = {item["model"].strip().upper() for item in repo_data}

input_data = input("Enter models (comma separated): ").split(",")

scraping = []

for model in input_data:
    model_clean = model.strip().upper()
    if model_clean in repo_models:
        print(f"{model_clean} -> exists")
    else:
        scraping.append(model_clean)