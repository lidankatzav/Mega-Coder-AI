import os
from dotenv import load_dotenv
from openai import OpenAI

def main():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY_UPDATED")
    if not api_key:
        print("ERROR: api key is not set in .env file.")
        return
    
    client = OpenAI(api_key=api_key)

    prompt = (
        "Create a Python program that checks if a number is prime. "
        "Do not write explanations. Respond only with valid Python code."
    )

    try:
        response = client.responses.create(
            model="gpt-5-nano",
            input=prompt,
        )

        print("\n===== GENERATED CODE START =====\n")
        print(response.output_text)
        print("\n===== GENERATED CODE END =====\n")

    except Exception as e:
        print("Error while calling OpenAI API:")
        print(str(e))

if __name__ == "__main__":
    main()
