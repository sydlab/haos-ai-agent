from datetime import datetime
from agent import run_supervision_check

if __name__ == "__main__":
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\nHome Assistant AI Agent — health check — {now}\n")

    summary = run_supervision_check()

    print("\n" + "=" * 60)
    print(summary)
    print("=" * 60 + "\n")
