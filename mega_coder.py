import os
import random
import subprocess
import time
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
    try:
        start = time.time()
        result = subprocess.run(
            ["python3", "generated-code-gemini.py"],
            capture_output=True,
            text=True
        )
        end = time.time()
        return result.returncode, result.stdout, result.stderr, (end - start) * 1000

    except Exception as e:
        return -1, "", str(e), 0


def corrupt_code_randomly(code: str) -> str:
    if random.random() < 0.3:
        idx = random.randint(0, len(code) - 1)
        corrupted = code[:idx] + "#" + code[idx + 1:]
        warn("[DEBUG] Random corruption injected into generated code.")
        return corrupted
    return code


def generate_program_with_gemini(description, model):
    prompt = f"""
Write a Python program based on the following description:

\"\"\"{description}\"\"\"

Important requirements:
- The program must NOT use input()
- The program must NOT use command line arguments
- The code must be fully runnable
- Include ASSERTS for correctness
- Return ONLY Python code
"""

    info("\nSending request to Gemini 2.5 Flash-Lite...\n")

    response = model.generate_content(prompt)
    code = response.text.replace("```python", "").replace("```", "").strip()

    code = corrupt_code_randomly(code)

    with open("generated-code-gemini.py", "w") as f:
        f.write(code)

    success("[SUCCESS] Code written to generated-code-gemini.py\n")
    return code


def fix_code_with_gemini(model, code, error_msg):
    prompt = f"""
Fix the following Python code. It failed when executed.

--- CODE START ---
{code}
--- CODE END ---

Error message:
{error_msg}

Fix everything completely. Return ONLY valid Python code.
"""

    response = model.generate_content(prompt)
    fixed = response.text.replace("```python", "").replace("```", "").strip()

    fixed = corrupt_code_randomly(fixed)

    with open("generated-code-gemini.py", "w") as f:
        f.write(fixed)

    return fixed

def optimize_code_with_gemini(model, code):
    prompt = f"""
The following Python code runs correctly and contains ASSERTS.
Optimize it to run FASTER but keep all asserts EXACTLY as they are.

Return ONLY optimized Python code.

--- CODE START ---
{code}
--- CODE END ---
"""

    response = model.generate_content(prompt)
    optimized = response.text.replace("```python", "").replace("```", "").strip()

    with open("generated-code-gemini.py", "w") as f:
        f.write(optimized)

    return optimized

def main():
    configure_gemini()

    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    while True:
        show_menu()
        choice = input(Fore.BLUE + "Choose an option (1/2/3): ").strip()

        if choice == "1":
            description = input("\nDescribe me which python program you want me to develop:\n\n> ")

            info("\nGenerating program...")
            code = generate_program_with_gemini(description, model)

            for attempt in range(1, 6):
                info(f"\nRunning attempt {attempt}...")
                return_code, out, err, before_time = run_generated_code()

                if return_code == 0:
                    print(Fore.GREEN + "\n===== PROGRAM OUTPUT =====")
                    print(out)
                    success("\nThe generated code executed successfully!")

                    info("\nRequesting optimized faster version of the code...")
                    optimize_code_with_gemini(model, code)

                    info("Running optimized version...")
                    rc2, out2, err2, after_time = run_generated_code()

                    if rc2 == 0 and after_time < before_time:
                        success(
                            f"\nCode running time optimized! "
                            f"It now runs in {after_time:.2f} ms, while before it was {before_time:.2f} ms"
                        )
                    else:
                        warn("\nOptimization did not improve the running time.")

                    return

                error("\nProgram failed!")
                print(err)

                if attempt == 5:
                    error("\nSorry master, I have failed you. I can’t create this program without issues.")
                    return

                info("\nAsking Gemini to fix the code...")
                code = fix_code_with_gemini(model, code, err)

            break

        elif choice == "2":
            warn("\nNot implemented yet.\n")

        elif choice == "3":
            warn("\nNot implemented yet.\n")

        else:
            error("\nInvalid choice. Please try again.\n")


if __name__ == "__main__":
    main()