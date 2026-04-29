#!/usr/bin/env bash
# Roda os 3 grupos em sequência (ou em paralelo se quiser)
# Uso: ./run_experiment.sh [--n 50] [--smoke]

set -e
cd "$(dirname "$0")"
source venv/bin/activate

N=50
SMOKE=0

for arg in "$@"; do
  case $arg in
    --n=*) N="${arg#*=}" ;;
    --smoke) SMOKE=1 ;;
  esac
done

if [ "$SMOKE" -eq 1 ]; then
  echo "=== SMOKE TEST (3 problems per group) ==="
  python runner.py --group A --n 3
  python runner.py --group B --n 3
  python runner.py --group C --n 3
else
  echo "=== RUNNING FULL EXPERIMENT (n=$N per group) ==="
  echo "Group A (control)..."
  python runner.py --group A --n $N

  echo "Group B (time + attempt)..."
  python runner.py --group B --n $N

  echo "Group C (attempt only)..."
  python runner.py --group C --n $N

  echo "=== ANALYZING ==="
  python analyze.py
fi
