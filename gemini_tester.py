import os
from dotenv import load_dotenv
import google.generativeai as genai

def main():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not set in .env file.")
        return

    genai.configure(api_key=api_key)

    prompt = (
        "Create a Python program that checks if a number is prime. "
        "Do not write explanations. Respond only with valid Python code."
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)

        print("\n===== GENERATED CODE START =====\n")
        print(response.text)
        print("\n===== GENERATED CODE END =====\n")

    except Exception as e:
        print("Error calling Gemini API:")
        print(str(e))


if __name__ == "__main__":
    main()