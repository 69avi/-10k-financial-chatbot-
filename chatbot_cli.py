"""
chatbot_cli.py  —  Rule-based CLI chatbot (original prototype)
Kept for reference and backward compatibility with the BCG task submission.
Run with: python chatbot_cli.py
"""

import pandas as pd
from engine import answer_query

def run_cli():
    print("=" * 60)
    print("   GFC Financial Chatbot — CLI Mode")
    print("   (For full UI run: streamlit run app.py)")
    print("=" * 60)
    print("Type 'help' for sample questions, 'exit' to quit.\n")

    df = pd.read_csv("data/sample_financials.csv")

    HELP_MSG = """
Available query types:
  • "What is Apple's revenue?"
  • "Compare Apple and Tesla net income"
  • "Show revenue growth for all companies"
  • "Which company has the highest profit margin?"
  • "What is Microsoft's EPS in 2023?"
  • "Show summary dashboard"  (opens in browser)
  • exit
"""

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            print("Bot: Goodbye! 👋")
            break
        if user_input.lower() in ("help", "?"):
            print(HELP_MSG)
            continue

        answer, chart = answer_query(user_input, df)
        print(f"\nBot:\n{answer}\n")

        if chart:
            show = input("📊 Chart available — open in browser? (y/n): ").strip().lower()
            if show == "y":
                chart.show()
            print()

if __name__ == "__main__":
    run_cli()
