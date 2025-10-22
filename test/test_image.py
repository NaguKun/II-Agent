import base64
import requests

# Read and encode image
with open("chill.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()

# Prepare data URL
image_data = f"data:image/jpeg;base64,{encoded_string}"

# Send request
url = "http://localhost:8000/api/chat/message"
data = {
    "conversation_id": "68f7a4173ef8dee524e43767",
    "content": "What do you see in this image? Describe the scene in detail.",
    "image_data": image_data
}

response = requests.post(url, data=data)
print("Status Code:", response.status_code)
print("\nResponse:")
import json
print(json.dumps(response.json(), indent=2))
