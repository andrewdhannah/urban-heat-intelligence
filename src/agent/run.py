"""
S1 CLI — Run the heat agent on the primary question

Usage:
    python -m src.agent.run                    # LIVE mode
    python -m src.agent.run --mode replay      # REPLAY mode
    python -m src.agent.run --question "..."   # Custom question
"""

import json
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.agent.adapter import FortyGuardAdapter
from src.agent.controller import HeatAgent


def main():
    parser = argparse.ArgumentParser(description="Heat Risk Agent")
    parser.add_argument("--mode", choices=["live", "replay"], default="live")
    parser.add_argument("--question", default="What's the heat risk in Phoenix right now?")
    parser.add_argument("--location", default="Phoenix, AZ")
    parser.add_argument("--output", choices=["json", "text"], default="text")
    args = parser.parse_args()

    # Create adapter
    adapter = FortyGuardAdapter(mode=args.mode)

    # Create agent
    agent = HeatAgent(adapter, mode=args.mode)

    # Run
    result = agent.answer(args.question, args.location)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print_text_output(result)


def print_text_output(result):
    """Print human-readable output."""
    answer = result["answer"]
    chain = result["evidence_chain"]

    print("=" * 60)
    print("HEAT RISK ANSWER")
    print("=" * 60)
    print()
    print(f"MODE: {answer['mode'].upper()}")
    print(f"OBSERVATION: {answer.get('observation_time', 'unknown')}")
    print()
    print("SUMMARY:")
    print(f"  {answer['summary']}")
    print()

    conditions = answer.get("conditions", {})
    if conditions:
        print("CONDITIONS:")
        print(f"  Area mean temperature: {conditions.get('area_mean_temperature_celsius')}°C")
        print(f"  Area max temperature:  {conditions.get('area_max_temperature_celsius')}°C")
        print(f"  Area min temperature:  {conditions.get('area_min_temperature_celsius')}°C")
        print(f"  Area temp range:       {conditions.get('area_temperature_range_celsius')}°C")
        print(f"  Heatmap features:      {conditions.get('feature_count')}")
        print()
        rep = conditions.get("representative_location", {})
        if rep:
            print("  Representative location:")
            print(f"    Heat index:          {rep.get('heat_index_celsius')}°C")
            print(f"    Apparent temp:       {rep.get('apparent_temperature_celsius')}°C")
            print(f"    Measured temp:       {rep.get('measured_temperature_celsius')}°C")
            print(f"    Humidity:            {rep.get('relative_humidity_percent')}%")
        print()
        measured = conditions.get("measured_result", {})
        if measured:
            print("  MEASURED RESULT:")
            print(f"    Apparent vs measured delta: {measured.get('apparent_vs_measured_delta_celsius')}°C")
            print(f"    {measured.get('interpretation', '')}")

    print()
    print("WHY THIS ANSWER:")
    print(f"  {answer.get('why_this_answer', '')}")
    print()

    sources = answer.get("sources", [])
    if sources:
        print("SOURCES:")
        for s in sources:
            print(f"  - {s['provider']} {s['endpoint']} ({s['mode']})")
    print()

    print("EVIDENCE CHAIN:")
    for i, node in enumerate(chain):
        step = node.get("step", "unknown")
        data = node.get("data", {})
        print(f"  {i+1}. {step}")
        for k, v in data.items():
            if isinstance(v, dict):
                print(f"     {k}: {json.dumps(v)[:100]}")
            else:
                print(f"     {k}: {v}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
