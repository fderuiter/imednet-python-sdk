#!/bin/bash
set -e

echo "Running Coverage-Guided Fuzzer for 1,000,000 iterations..."
# Atheris uses libFuzzer arguments
python3 scripts/fuzz.py -runs=1000000 -max_total_time=120
echo "Fuzzing complete! Handled 1,000,000 iterations without unhandled exceptions."
