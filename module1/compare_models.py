"""
Module 1: multi-model comparison.

Runs the same acceptance test (test_module1.py) against several local
Ollama models back-to-back and prints a comparison table. This is what
turns "I used qwen2.5" into "I benchmarked 2 models and picked qwen2.5
because it scored higher on tool-selection accuracy" -- a much stronger
thing to say in an interview.

Usage:
    ollama pull qwen2.5
    ollama pull llama3.1
    python compare_models.py
"""

from test_module1 import run_tests

MODELS_TO_COMPARE = ["qwen2.5", "llama3.1"]  # add/remove models you've pulled


def compare():
    scores = {}
    for model in MODELS_TO_COMPARE:
        print(f"\n{'=' * 50}")
        print(f"Testing model: {model}")
        print(f"{'=' * 50}\n")
        try:
            pass_rate = run_tests(model=model, log_path="results_module1.json")
            scores[model] = pass_rate
        except Exception as e:
            print(f"Could not test {model}: {e}")
            print(f"(Did you run 'ollama pull {model}'?)")
            scores[model] = None

    print(f"\n{'=' * 50}")
    print("COMPARISON SUMMARY")
    print(f"{'=' * 50}")
    for model, rate in scores.items():
        display = f"{rate:.0%}" if rate is not None else "N/A (not available)"
        print(f"  {model:<15} {display}")


if __name__ == "__main__":
    compare()
