import os
import random
import subprocess
import time
from dotenv import load_dotenv
import google.generativeai as genai
from colorama import init, Fore, Style
from tqdm import tqdm
from gitingest import ingest

init(autoreset=True)


# ---------- Color helpers ----------
def info(msg: str):
    print(Fore.CYAN + msg + Style.RESET_ALL)


def warn(msg: str):
    print(Fore.YELLOW + msg + Style.RESET_ALL)


def error(msg: str):
    print(Fore.RED + msg + Style.RESET_ALL)


def success(msg: str):
    print(Fore.GREEN + msg + Style.RESET_ALL)


# ---------- Gemini initialization ----------
def configure_gemini():
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        error("ERROR: GEMINI_API_KEY missing from .env")
        exit(1)

    genai.configure(api_key=gemini_key)
    success("Gemini configured successfully!")


# ---------- Menu ----------
def show_menu():
    print(Fore.MAGENTA + "\nI'm Mega Coder. What would you like me to do today?\n")
    print("1. Develop a python program.")
    print("2. Fix/change something in a Github repository.")
    print("3. Look at my screen and give me realtime coding tips.\n")


# ---------- Code Execution ----------
def run_generated_code():
    try:
        start = time.time()
        result = subprocess.run(
            ["python3", "generated-code-gemini.py"],
            capture_output=True,
            text=True
        )
        end = time.time()
        elapsed_ms = (end - start) * 1000
        return result.returncode, result.stdout, result.stderr, elapsed_ms

    except Exception as e:
        return -1, "", str(e), 0.0


# ---------- Random corruption ----------
def corrupt_code_randomly(code: str) -> str:
    if random.random() < 0.3 and code:
        idx = random.randint(0, len(code) - 1)
        corrupted = code[:idx] + "#" + code[idx + 1:]
        warn("[DEBUG] Random corruption injected into generated code.")
        return corrupted
    return code


# ---------- Program generation ----------
def generate_program_with_gemini(description: str, model) -> str:
    prompt = f"""
Write a Python program based on the following description:

\"\"\"{description}\"\"\"

Important requirements:
- No input()
- No command line arguments
- Fully runnable as-is
- Include ASSERT statements for correctness
- Return ONLY valid Python code (no markdown)
"""

    info("\nRequesting initial code from Gemini 2.5 Flash-Lite...\n")

    response = model.generate_content(prompt)
    code = response.text.replace("```python", "").replace("```", "").strip()

    # initial corruption only
    code = corrupt_code_randomly(code)

    with open("generated-code-gemini.py", "w") as f:
        f.write(code)

    success("[SUCCESS] Code written to generated-code-gemini.py\n")
    return code


# ---------- Runtime fix ----------
def fix_code_with_gemini(model, code: str, error_msg: str) -> str:
    prompt = f"""
The following Python program failed when executed. Fix it while keeping the logic + asserts.

--- CODE START ---
{code}
--- CODE END ---

Runtime Error:
{error_msg}

Return ONLY valid Python code. No markdown, no explanations.
"""
    response = model.generate_content(prompt)
    fixed = response.text.replace("```python", "").replace("```", "").strip()

    with open("generated-code-gemini.py", "w") as f:
        f.write(fixed)

    return fixed


# ---------- Optimization ----------
def optimize_code_with_gemini(model, code: str) -> str:
    prompt = f"""
Optimize the following Python code to run FASTER.
Do NOT modify any ASSERT statements. Keep same behavior.

--- CODE START ---
{code}
--- CODE END ---

Return ONLY Python code.
"""
    response = model.generate_content(prompt)
    optimized = response.text.replace("```python", "").replace("```", "").strip()

    with open("generated-code-gemini.py", "w") as f:
        f.write(optimized)

    return optimized


# ---------- Pylint ----------
def run_pylint_on_file(filepath="generated-code-gemini.py"):
    cmd = ["python3", "-m", "pylint", filepath, "--score=n"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = (result.stdout or "") + (result.stderr or "")
    has_issues = result.returncode != 0
    return has_issues, output.strip()


def lint_and_fix_with_gemini(model, max_rounds=3):
    info("\nStarting pylint lint check...\n")

    for round_idx in tqdm(range(1, max_rounds + 1), desc="Lint Fixing Progress"):
        has_issues, report = run_pylint_on_file()

        if not has_issues:
            success("\nAmazing. No lint errors/warnings.\n")
            return

        warn(f"Lint issues detected (round {round_idx}/{max_rounds}). Fixing...\n")

        with open("generated-code-gemini.py", "r") as f:
            code = f.read()

        prompt = f"""
Fix ALL pylint issues in the following code.

Here is the code:
--- CODE START ---
{code}
--- CODE END ---

Here is the pylint report (MUST fix everything):
--- PYLINT REPORT START ---
{report}
--- PYLINT REPORT END ---

Rules:
- Fix every lint warning/error
- Keep ASSERT statements unchanged
- Keep program behavior unchanged
- Return ONLY Python code
"""
        response = model.generate_content(prompt)
        fixed = response.text.replace("```python", "").replace("```", "").strip()

        with open("generated-code-gemini.py", "w") as f:
            f.write(fixed)

    # After max rounds:
    still_issues, _ = run_pylint_on_file()
    if still_issues:
        error("\nThere are still lint errors/warnings.\n")
    else:
        success("\nAmazing. No lint errors/warnings.\n")


# ---------- GitIngest Integration ----------
def handle_github_option():
    """
    Handle option 2: ingest repo + ask Gemini 2.5 Pro to fix/explain.
    """

    info("\nGive me the full url of a public Github repository:\n")
    repo_url = input("> ").strip()

    info("\nTell me what you want me to fix/change/explain in that repository:\n")
    user_instruction = input("> ").strip()

    info("\nIngesting repository with GitIngest (please wait)...\n")

    try:
        repo_str = ingest(repo_url)
        success("Repository ingested successfully!\n")

        pro_model = genai.GenerativeModel("gemini-2.5-pro")

        prompt = f"""
The user wants the following change/explanation in the repository:

\"\"\"{user_instruction}\"\"\"

Here is the repository content:

--- REPO CONTENT START ---
{repo_str}
--- REPO CONTENT END ---

Your task:
- Analyze the repository
- Provide fixes, improvements, or explanations
- Keep answer clean, structured, and technical

Respond now:
"""

        response = pro_model.generate_content(prompt)

        print(Fore.GREEN + "\n===== GEMINI 2.5 PRO RESPONSE =====\n")
        print(response.text)
        print("\n====================================\n")

        success("Request completed.\n")

    except Exception as e:
        error(f"[ERROR] Failed to ingest repository or call Gemini: {e}\n")


# ---------- Main ----------
def main():
    configure_gemini()
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    while True:
        show_menu()
        choice = input(Fore.BLUE + "Choose an option (1/2/3): ").strip()

        if choice == "1":
            description = input(
                "\nDescribe me which python program you want me to develop:\n\n> "
            )

            info("Generating program...")
            code = generate_program_with_gemini(description, model)

            # Runtime fix attempts
            for attempt in tqdm(range(1, 6), desc="Run & Fix Attempts"):
                rc, out, err, before = run_generated_code()

                if rc == 0:
                    success("Program executed successfully!")
                    print(out)

                    # Optimization
                    optimize_code_with_gemini(model, code)
                    rc2, out2, err2, after = run_generated_code()

                    if rc2 == 0 and after < before:
                        success(
                            f"Runtime optimized! Before: {before:.2f} ms → After: {after:.2f} ms"
                        )
                    else:
                        warn("Optimization didn't improve speed.")

                    # Lint phase
                    lint_and_fix_with_gemini(model)

                    return

                error("Program failed!")
                print(err)

                if attempt == 5:
                    error("Sorry master, I have failed you. Cannot create a working program.")
                    return

                code = fix_code_with_gemini(model, code, err)

        elif choice == "2":
            handle_github_option()

        elif choice == "3":
            warn("Not implemented yet.\n")

        else:
            error("Invalid choice. Try again.\n")


if __name__ == "__main__":
    main()
