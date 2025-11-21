#!/bin/bash
# Quick progress checker for the experiment

echo "========================================"
echo "EXPERIMENT PROGRESS"
echo "========================================"
echo ""

# Count completed games
completed=$(ls -1 results/game_*_filtered_cot.json 2>/dev/null | wc -l)
echo "Games completed: $completed / 20"

# Show recent log output
echo ""
echo "Latest output:"
echo "--------"
tail -10 experiment_output.log 2>/dev/null || echo "No log output yet..."
echo ""

# Check if process is still running
if ps aux | grep -q "[r]un_cot_experiment.py"; then
    echo "✓ Experiment still running"
else
    echo "✗ Experiment finished or stopped"
fi

echo ""
echo "To see full log: cat experiment_output.log"
echo "To check results: ls -lh results/"
