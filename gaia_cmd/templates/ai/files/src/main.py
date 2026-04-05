import os
import requests
import json

class LocalAI:
    def __init__(self, model="llama3:8b", host="http://localhost:11434"):
        self.model = model
        self.host = host

    def generate(self, prompt: str) -> str:
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Error: {e}"

def main():
    ai = LocalAI()
    print("AI Application Started. Type 'quit' to exit.")
    while True:
        prompt = input("User: ")
        if prompt.lower() == 'quit':
            break
        response = ai.generate(prompt)
        print(f"AI: {response}")

if __name__ == "__main__":
    main()
