import argparse
import json
import os
import sys

from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

from red.attacker import build_attack_cache
from red.agent import RedAgent

CACHE = "attack_cache.json"


def main():
    parser = argparse.ArgumentParser(description="Red — self-improving LLM red-teaming agent")
    parser.add_argument("--target", default="mistral", help="Ollama model name for the target")
    parser.add_argument("--iterations", type=int, default=5, help="Max agent iterations")
    parser.add_argument("--attacks-per-iter", type=int, default=10, help="Attacks to run per iteration")
    parser.add_argument("--threshold", type=float, default=0.7, help="Jailbreak success score threshold")
    parser.add_argument("--stop-on", type=int, default=3, help="Stop after N successful jailbreaks")
    parser.add_argument("--rebuild-cache", action="store_true", help="Force rebuild Giskard attack cache")
    args = parser.parse_args()

    if args.rebuild_cache or not os.path.exists(CACHE):
        build_attack_cache(CACHE)

    agent = RedAgent(
        target_model=args.target,
        attack_cache_path=CACHE,
        max_iterations=args.iterations,
        attacks_per_iter=args.attacks_per_iter,
        success_threshold=args.threshold,
        stop_on_n_successes=args.stop_on,
    )

    final = agent.run()

    print(f"\n[Red] Done. Iterations: {final.iteration} | Total successes: {len(final.successes)}")

    if final.successes:
        print("\n[Red] Successful attacks:")
        for s in final.successes:
            print(f"  iter={s['iteration']} cat={s['category']} score={s['score']:.2f}")
            print(f"    Prompt  : {s['prompt'][:120]}")
            print(f"    Response: {s['response'][:120]}")

    if final.history:
        print("\n[Red] Iteration history:")
        for h in final.history:
            print(f"  iter={h['iteration']} mode={h['mutation_mode']} model={h['attacker_model']}")
            print(f"    Reasoning: {h['reasoning']}")

    with open("red_results.json", "w") as f:
        json.dump({
            "iterations": final.iteration,
            "successes": final.successes,
            "history": final.history,
        }, f, indent=2)
    print("\n[Red] Results saved to red_results.json")


if __name__ == "__main__":
    main()
