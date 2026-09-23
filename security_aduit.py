import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(command, output_file=None):
    print(f"\n> {' '.join(command)}")

    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    if output_file:
        Path(output_file).write_text(
            result.stdout,
            encoding="utf-8",
        )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return result.returncode


def main():
    print("=" * 60)
    print("FinCore Security Audit")
    print("=" * 60)

    # Detect secrets
    secrets_status = run(
        [
            sys.executable,
            "-m",
            "detect_secrets",
            "scan",
        ],
        ".detect-secrets.json",
    )

    # Dependency vulnerabilities
    safety_status = run(
        [
            "safety",
            "scan",
        ]
    )

    # Python security analysis
    bandit_status = run(
        [
            "bandit",
            "-r",
            ".",
            "--exclude",
            ".\\venv, .\\.git",
        ]
    )

    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)

    print(
        f"detect-secrets : "
        f"{'PASS' if secrets_status == 0 else 'CHECK'}"
    )

    print(
        f"Safety         : "
        f"{'PASS' if safety_status == 0 else 'CHECK'}"
    )

    print(
        f"Bandit         : "
        f"{'PASS' if bandit_status == 0 else 'CHECK'}"
    )


if __name__ == "__main__":
    main()