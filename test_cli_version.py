import subprocess

try:
    result = subprocess.run(
        ["poetry", "run", "imednet", "--version"], capture_output=True, text=True, check=True
    )
    print("Success:", result.stdout)
except subprocess.CalledProcessError as e:
    print("Error:", e.stderr)
