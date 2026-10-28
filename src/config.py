"""
config.py - Project-wide configuration: paths, random seed, column groups and plot style.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "Telco-Customer-Churn.csv"
EDA_DIR = ROOT / "outputs" / "figures"
EVAL_DIR = ROOT / "outputs"
MODEL_DIR = ROOT / "models"

for d in (EDA_DIR, EVAL_DIR, MODEL_DIR):
    d.mkdir(parents=True, exist_ok=True)

SEED = 42
TARGET = "Churn_binary"
PASS_MARK = 0.5

# Column Groups
NUMERIC_COLS = ["tenure", "MonthlyCharges", "TotalCharges_clean"]
BINARY_COLS = ["gender", "SeniorCitizen", "Partner", "Dependents", "PhoneService", "PaperlessBilling"]
NOMINAL_COLS = ["MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup", 
                "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies", 
                "Contract", "PaymentMethod"]

BLUE = "#1f77b4"
ORANGE = "#ff7f0e"
GREEN = "#2ca02c"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"

def set_style():
    plt.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
        "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
        "axes.labelsize": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK,
        "text.color": INK, "xtick.color": INK2, "ytick.color": INK2,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7,
        "axes.axisbelow": True, "legend.frameon": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })

def save_fig(fig, path):
    fig.savefig(path, dpi=300)
    plt.close(fig)

