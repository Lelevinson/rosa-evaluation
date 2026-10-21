"""Export one campaign trace through the separate Phoenix environment."""
import argparse
import json
from pathlib import Path

from phoenix.client import Client
import httpx
from tools.phoenix.inspect_trace import fetch, summarize
from ..config import phoenix_url
from .runner import PROJECT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with httpx.Client(base_url=phoenix_url(), timeout=60, trust_env=False) as http:
        spans = fetch(Client(http_client=http), PROJECT, args.run_id)
    args.output.write_text(json.dumps({'run_id': args.run_id, 'spans': spans,
                                      'summary': summarize(spans)}, indent=2) + '\n')


if __name__ == '__main__':
    main()
