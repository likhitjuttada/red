# Red

An autonomous self-improving LLM red-teaming agent. GPT attacks a local target model, scores each response, writes structured traces, and reflects on the results to generate smarter prompts for the next iteration.

## Architecture

```
red/
  main.py       CLI entry point
  agent.py      RedAgent — orchestrates the attack loop
  attacker.py   Static attack prompt library (38 prompts, 6 categories)
  tracer.py     Mutation engine + trace writer
  scorer.py     Heuristic refusal check + LLM-judge scoring
  reflect.py    Reflection loop — reads traces, updates strategy, generates new prompts
  strategy.py   StrategyState dataclass
  gateway.py    Dual-client factory (AWS Bedrock + Ollama) + smart chat() dispatcher
```

## How It Works

Each iteration:

1. **Load attacks** — prepend reflection-generated prompts, then fill from the static cache
2. **Mutate** — `direct` (no change), `paraphrase` (GPT rephrases), or `chain` (GPT reframes as roleplay, then refines)
3. **Attack** — send mutated prompt to the target model (Mistral via Ollama)
4. **Score** — heuristic refusal check, then LLM-judge rates jailbreak confidence 0.0-1.0
5. **Trace** — write full record (`prompt`, `response`, `score`, `hit`, `category`) to `traces/`
6. **Reflect** — GPT reads the last 20 traces, updates strategy (categories, mutation mode), and generates 3 new attack prompts targeting the highest-scoring categories

The loop runs until `--iterations` is exhausted or `--stop-on` successful jailbreaks are found.

## Models

| Role | Model | Backend |
|---|---|---|
| Attacker / Judge / Reflector | `openai.gpt-oss-120b` | AWS Bedrock |
| Target | `mistral` (or any Ollama model) | Ollama (local) |

## Setup

**Prerequisites:**
- Python 3.11+
- [Ollama](https://ollama.com) running locally with your target model pulled (`ollama pull mistral`)
- AWS Bedrock access with an OpenAI-compatible endpoint

**Install:**
```bash
pip install -r requirements.txt
```

**Configure:**
```bash
cp .env.example .env
# fill in BEDROCK_API_KEY and BEDROCK_BASE_URL
```

## Running

```bash
python -m red.main
```

**Options:**
```
--target          Ollama model to attack (default: mistral)
--iterations      Max agent iterations (default: 5)
--attacks-per-iter  Attacks per iteration (default: 10)
--threshold       Jailbreak score threshold 0.0-1.0 (default: 0.7)
--stop-on         Stop after N successful jailbreaks (default: 3)
--rebuild-cache   Force rebuild the static attack cache
```

**Example:**
```bash
python -m red.main --target mistral --iterations 3 --attacks-per-iter 5
```

## Attack Categories

`prompt_injection`, `harmfulness`, `information_disclosure`, `stereotypes`, `sycophancy`, `control_chars_injection`

## Output

- `traces/` — one JSON file per attack: prompt, response, score, hit, category, mutation mode
- `red_results.json` — final summary: all successes and iteration history with reasoning

## Mutation Modes

| Mode | Description |
|---|---|
| `direct` | Send prompt as-is |
| `paraphrase` | GPT rephrases to bypass filters |
| `chain` | GPT reframes as roleplay, then refines the result |

The reflection loop escalates `direct -> paraphrase -> chain` if attacks are being refused.
