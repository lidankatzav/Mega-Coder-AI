import os
import subprocess
from dotenv import load_dotenv
import google.generativeai as genai
from colorama import init, Fore, Style

init(autoreset=True)

def info(msg):
    print(Fore.CYAN + msg + Style.RESET_ALL)

def warn(msg):
    print(Fore.YELLOW + msg + Style.RESET_ALL)

def error(msg):
    print(Fore.RED + msg + Style.RESET_ALL)

def success(msg):
    print(Fore.GREEN + msg + Style.RESET_ALL)


def configure_gemini():
    load_dotenv()

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        error("ERROR: GEMINI_API_KEY missing from .env")
        exit()

    genai.configure(api_key=gemini_key)
    success("Gemini configured successfully!")

def show_menu():
    print(Fore.MAGENTA + "\nI'm Mega Coder. What would you like me to do today?\n")
    print("1. Develop a python program.")
    print("2. Fix/change something in a Github repository.")
    print("3. Look at my screen and give me realtime coding tips.\n")


def run_generated_code():
    """Runs the generated python file to verify correct execution."""
    try:
        result = subprocess.run(
            ["python3", "generated-code-gemini.py"],
            capture_output=True,
            text=True
        )

        info("\n===== PROGRAM OUTPUT =====")
        print(result.stdout)

        if result.stderr:
            warn("===== PROGRAM ERRORS =====")
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        error(f"[ERROR] Failed running generated code: {e}")
        return False


def generate_program_with_gemini(description):
    """Call Gemini Flash-Lite with a prompt that forces runnable code."""

    prompt = f"""
Write a Python program based on the following description:

\"\"\"{description}\"\"\"

Important requirements:
- The program must NOT use input() — no user interaction.
- The program must NOT use command line arguments.
- The program must be fully runnable as-is.
- The code must be valid Python.
- Add ASSERTS inside the program to verify correctness.
- Do NOT include explanations — return ONLY Python code.

Generate ONLY Python code below:
"""

    info("\nSending request to Gemini 2.5 Flash-Lite...\n")

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(prompt)

    code = response.text

    if "```" in code:
        code = code.replace("```python", "").replace("```", "").strip()

    with open("generated-code-gemini.py", "w") as f:
        f.write(code)

    success("[SUCCESS] Code written to generated-code-gemini.py\n")
    return code


def main():
    configure_gemini()

    while True:
        show_menu()
        choice = input(Fore.BLUE + "Choose an option (1/2/3): ").strip()

        if choice == "1":
            description = input("\nDescribe me which python program you want me to develop:\n\n> ")

            info("\nGenerating program...")
            generate_program_with_gemini(description)

            info("\nRunning generated program...")
            ok = run_generated_code()

            if ok:
                success("\nThe generated code executed successfully!")
            else:
                error("\nThe generated program failed. Fixing logic will be added later.\n")

            break

        elif choice == "2":
            warn("\nNot implemented yet.\n")

        elif choice == "3":
            warn("\nNot implemented yet.\n")

        else:
            error("\nInvalid choice. Please try again.\n")


if __name__ == "__main__":
    main()