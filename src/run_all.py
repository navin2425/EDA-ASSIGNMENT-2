"""
run_all.py - Complete reproduction script running all pipeline modules end-to-end.
"""
import os
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from eda_churn_pipeline import main as run_pipeline
from diagrams import generate_diagram1, generate_diagram2, generate_sample_style_figures

if __name__ == '__main__':
    print("[RUN ALL] Executing full Customer Churn Investigation Pipeline...")
    run_pipeline()
    generate_diagram1()
    generate_diagram2()
    generate_sample_style_figures()
    print("[RUN ALL] Completed successfully!")

