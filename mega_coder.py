import os
import random
import subprocess
import time
from dotenv import load_dotenv
import google.generativeai as genai
from colorama import init, Fore, Style
from tqdm import tqdm

init(autoreset=True)


def info(msg: str) -> None:
    print(Fore.CYAN + msg + Style.RESET_ALL)


def warn(msg: str) -> None:
    print(Fore.YELLOW + msg + Style.RESET_ALL)


def error(msg: str) -> None:
    print(Fore.RED + msg + Style.RESET_ALL)


def success(msg: str) -> None:
    print(Fore.GREEN + msg + Style.RESET_ALL)


def configure_gemini() -> None:
    load_dotenv()

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        error("ERROR: GEMINI_API_KEY missing from .env")
        exit(1)

    genai.configure(api_key=gemini_key)
    success("Gemini configured successfully!")


def show_menu() -> None:
    print(Fore.MAGENTA + "\nI'm Mega Coder. What would you like me to do today?\n")
    print("1. Develop a python program.")
    print("2. Fix/change something in a Github repository.")
    print("3. Look at my screen and give me realtime coding tips.\n")


def run_generated_code():
    """
    Runs the generated python file and measures its runtime in milliseconds.
    Returns (return_code, stdout, stderr, elapsed_ms).
    """
    try:
        start = time.time()
        result = subprocess.run(
            ["python3", "generated-code-gemini.py"],
            capture_output=True,
            text=True,
        )
        end = time.time()
        elapsed_ms = (end - start) * 1000.0
        return result.returncode, result.stdout, result.stderr, elapsed_ms
    except Exception as e:
        return -1, "", str(e), 0.0


def corrupt_code_randomly(code: str) -> str:
    """
    Randomly corrupts one character in the code ~30% of the time.
    Used only on initial generation to force failures per assignment.
    """
    if random.random() < 0.3 and code:
        idx = random.randint(0, len(code) - 1)
        corrupted = code[:idx] + "#" + code[idx + 1:]
        warn("[DEBUG] Random corruption injected into generated code.")
        return corrupted
    return code


def generate_program_with_gemini(description: str, model) -> str:
    """
    Ask Gemini to generate initial Python program with ASSERTS.
    Writes code into generated-code-gemini.py and returns it as string.
    """

    prompt = f"""
Write a Python program based on the following description:

\"\"\"{description}\"\"\"

Important requirements:
- The program must NOT use input()
- The program must NOT use command line arguments
- The code must be fully runnable as-is
- Include ASSERTS for correctness (so failures raise exceptions)
- Return ONLY valid Python code. No explanations, no comments, no markdown fences.
"""

    info("\nSending request to Gemini 2.5 Flash-Lite for initial code...\n")

    response = model.generate_content(prompt)
    code = response.text.replace("```python", "").replace("```", "").strip()

    code = corrupt_code_randomly(code)

    with open("generated-code-gemini.py", "w") as f:
        f.write(code)

    success("[SUCCESS] Initial code written to generated-code-gemini.py\n")
    return code


def fix_code_with_gemini(model, code: str, error_msg: str) -> str:
    """
    Send failing code + runtime error back to Gemini for fixing.
    No random corruption here – goal is to stabilize runtime correctness.
    """

    prompt = f"""
The following Python program failed when executed. Fix it so that it runs
successfully and keeps the same intended behavior and ASSERTS.

--- CODE START ---
{code}
--- CODE END ---

The error message when running it was:
{error_msg}

Fix all runtime issues. Return ONLY valid Python code. No explanations, no markdown.
"""

    response = model.generate_content(prompt)
    fixed = response.text.replace("```python", "").replace("```", "").strip()

    with open("generated-code-gemini.py", "w") as f:
        f.write(fixed)

    info("A runtime-fixed version of the code was written to generated-code-gemini.py")
    return fixed


def optimize_code_with_gemini(model, code: str) -> str:
    """
    Ask Gemini to generate a faster version of code, preserving ASSERTS exactly.
    Writes optimized code into file and returns it.
    """

    prompt = f"""
The following Python code runs correctly and contains ASSERTS that validate its logic.
Optimize the code to run FASTER, but keep ALL ASSERTS EXACTLY as they are.

- Do not remove or change the ASSERT statements.
- Keep the same behavior and outputs.
- Focus on algorithmic and structural optimizations.

Return ONLY the optimized Python code. No explanations, no markdown.

--- CODE START ---
{code}
--- CODE END ---
"""

    info("\nRequesting optimized (faster) version of the code from Gemini...\n")

    response = model.generate_content(prompt)
    optimized = response.text.replace("```python", "").replace("```", "").strip()

    with open("generated-code-gemini.py", "w") as f:
        f.write(optimized)

    success("Optimized code written to generated-code-gemini.py")
    return optimized


def run_pylint_on_file(file_path: str = "generated-code-gemini.py"):
    """
    Runs pylint via `python3 -m pylint` on the generated file.
    Returns (has_issues: bool, full_report: str).
    """
    cmd = [
        "python3",
        "-m",
        "pylint",
        file_path,
        "--score=n",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = (result.stdout or "") + "\n" + (result.stderr or "")

    has_issues = result.returncode != 0

    return has_issues, output.strip()


def lint_and_fix_with_gemini(model, max_rounds: int = 3) -> None:
    """
    Runs pylint up to max_rounds times, using a single tqdm progress bar.
    On each round with issues, sends the code + pylint report to Gemini for fixes.
    Overwrites the file with improved code each time.

    At the end:
      - If no issues: print "Amazing. No lint errors/warnings"
      - Else: print "There are still lint errors/warnings"
    """

    info("\nStarting lint check & auto-fix using pylint + Gemini...\n")

    file_path = "generated-code-gemini.py"

    for round_idx in tqdm(
        range(1, max_rounds + 1),
        desc="Lint Fixing Progress",
        unit="round",
    ):
        has_issues, report = run_pylint_on_file(file_path)

        if not has_issues:
            success("\nAmazing. No lint errors/warnings.\n")
            return

        warn(f"\nLint issues detected (round {round_idx}/{max_rounds}). Fixing with Gemini...\n")

        with open(file_path, "r") as f:
            current_code = f.read()

        lint_prompt = f"""
The following Python code runs correctly but has lint warnings/errors according to pylint.

Your task:
- Fix ALL lint warnings and errors reported by pylint.
- Keep the SAME behavior and outputs.
- KEEP ALL ASSERT statements (do not remove or weaken them).
- Improve variable names, add missing docstrings if needed, remove unused variables,
  and fix formatting according to standard Python conventions.

Here is the code:

--- CODE START ---
{current_code}
--- CODE END ---

Here is the pylint report (these are the issues you MUST fix):

--- PYLINT REPORT START ---
{report}
--- PYLINT REPORT END ---

Return ONLY the fully fixed Python code. No explanations, no comments about changes,
no markdown. Just valid Python code.
"""

        response = model.generate_content(lint_prompt)
        fixed_code = response.text.replace("```python", "").replace("```", "").strip()

        with open(file_path, "w") as f:
            f.write(fixed_code)

        info("Wrote a lint-improved version of the code to generated-code-gemini.py\n")

    still_has_issues, _ = run_pylint_on_file(file_path)
    if still_has_issues:
        error("\nThere are still lint errors/warnings.\n")
    else:
        success("\nAmazing. No lint errors/warnings.\n")


def main() -> None:
    configure_gemini()

    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    while True:
        show_menu()
        choice = input(Fore.BLUE + "Choose an option (1/2/3): ").strip()

        if choice == "1":
            description = input(
                "\nDescribe me which python program you want me to develop:\n\n> "
            )

            info("\nGenerating program...")
            code = generate_program_with_gemini(description, model)

            for attempt in tqdm(
                range(1, 6),
                desc="Run & Fix Attempts",
                unit="attempt",
            ):
                info(f"\nRunning attempt {attempt}...")
                return_code, out, err, before_time = run_generated_code()

                if return_code == 0:
                    print(Fore.GREEN + "\n===== PROGRAM OUTPUT =====")
                    print(out)
                    success("\nThe generated code executed successfully!")

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

                    lint_and_fix_with_gemini(model)

                    return

                error("\nProgram failed!")
                print(err)

                if attempt == 5:
                    error(
                        "\nSorry master, I have failed you. I can’t create this program without issues."
                    )
                    return

                info("\nAsking Gemini to fix the code based on the error...")
                with open("generated-code-gemini.py", "r") as f:
                    current_code = f.read()
                code = fix_code_with_gemini(model, current_code, err)

            break

        elif choice == "2":
            warn("\nNot implemented yet.\n")

        elif choice == "3":
            warn("\nNot implemented yet.\n")

        else:
            error("\nInvalid choice. Please try again.\n")


if __name__ == "__main__":
    main()