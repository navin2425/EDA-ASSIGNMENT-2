"""
Exploratory Data Analysis and Deep Learning Customer Churn Pipeline
Course: U21ADP05 - Exploratory Data Analysis and Visualization (Assignment II)
Student: Navin J | Roll No: 24AD071 | III Year (V Sem), Dept. of AI & DS
KPR Institute of Engineering and Technology, Coimbatore
Course Coordinator: Mr. Rushikesh Kadam | Batch: 2023-2027
"""

import os
os.environ['MPLCONFIGDIR'] = os.path.abspath('outputs/.matplotlib')
os.makedirs(os.environ['MPLCONFIGDIR'], exist_ok=True)
import json
import random
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    classification_report, roc_curve, precision_recall_curve
)
from sklearn.inspection import permutation_importance
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

# Set random seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11

FIGURES_DIR = 'outputs/figures'
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs('outputs', exist_ok=True)


def load_and_preprocess_data(filepath='data/Telco-Customer-Churn.csv'):
    print("[1] Loading raw dataset...")
    df = pd.read_csv(filepath)
    raw_shape = df.shape
    print(f"    Raw Shape: {raw_shape[0]} rows, {raw_shape[1]} columns")

    # 1. TotalCharges clean
    df['TotalCharges_clean'] = df['TotalCharges'].replace(' ', np.nan)
    blank_count = df['TotalCharges_clean'].isna().sum()
    print(f"    Blank TotalCharges count: {blank_count} (tenure=0 customers)")
    # Impute 0.0 for tenure = 0
    df['TotalCharges_clean'] = pd.to_numeric(df['TotalCharges_clean']).fillna(0.0)

    # 2. Binary target
    df['Churn_binary'] = (df['Churn'] == 'Yes').astype(int)

    # 3. Derived Features
    # Tenure cohorts
    df['tenure_cohort'] = pd.cut(
        df['tenure'],
        bins=[-1, 12, 24, 48, 60, 73],
        labels=['0-12 Mo', '13-24 Mo', '25-48 Mo', '49-60 Mo', '61-72 Mo']
    )
    
    # Add-on services count (OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies)
    addon_services = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']
    df['services_count'] = (df[addon_services] == 'Yes').sum(axis=1)

    # Has partner and dependents (Family unit stability indicator)
    df['family_stability'] = ((df['Partner'] == 'Yes') & (df['Dependents'] == 'Yes')).astype(int)

    # Monthly charges to total charges ratio (approximate tenure verification or billing intensity)
    df['charge_ratio'] = df['MonthlyCharges'] / (df['TotalCharges_clean'] + 1.0)

    # High-risk month-to-month flag
    df['is_month_to_month'] = (df['Contract'] == 'Month-to-month').astype(int)

    # Has streaming bundle (both TV and Movies)
    df['streaming_bundle'] = ((df['StreamingTV'] == 'Yes') & (df['StreamingMovies'] == 'Yes')).astype(int)

    return df


def compute_exploratory_statistics(df):
    print("[2] Computing statistical moments & hypothesis tests...")
    num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges_clean']
    stats_summary = {}

    for c in num_cols:
        series = df[c]
        stats_summary[c] = {
            'mean': float(series.mean()),
            'std': float(series.std()),
            'median': float(series.median()),
            'iqr': float(series.quantile(0.75) - series.quantile(0.25)),
            'min': float(series.min()),
            'max': float(series.max()),
            'skewness': float(series.skew()),
            'kurtosis': float(series.kurtosis())
        }

    # Statistical tests
    chi2_results = {}
    cat_cols = ['gender', 'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService', 
                'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 
                'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 
                'Contract', 'PaperlessBilling', 'PaymentMethod', 'tenure_cohort']
    
    for c in cat_cols:
        ct = pd.crosstab(df[c], df['Churn'])
        chi2, p, dof, _ = stats.chi2_contingency(ct)
        n = ct.values.sum()
        r, k = ct.shape
        cramers_v = np.sqrt(chi2 / (n * min(r - 1, k - 1)))
        chi2_results[c] = {
            'chi2': float(chi2),
            'p_value': float(p),
            'dof': int(dof),
            'cramers_v': float(cramers_v)
        }

    ttest_results = {}
    for c in num_cols:
        g1 = df[df['Churn'] == 'Yes'][c]
        g2 = df[df['Churn'] == 'No'][c]
        t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=False)
        mw_stat, mw_p = stats.mannwhitneyu(g1, g2)
        pb_r, pb_p = stats.pointbiserialr(df['Churn_binary'], df[c])
        ttest_results[c] = {
            'welch_t': float(t_stat),
            't_p_value': float(p_val),
            'mann_whitney_u': float(mw_stat),
            'mw_p_value': float(mw_p),
            'point_biserial_r': float(pb_r),
            'pb_p_value': float(pb_p),
            'mean_churn': float(g1.mean()),
            'mean_nochurn': float(g2.mean())
        }

    return stats_summary, chi2_results, ttest_results


def generate_visualizations(df, stats_summary, chi2_results, ttest_results):
    print("[3] Generating high-resolution 300 DPI visualizations...")

    # -------------------------------------------------------------
    # Fig 1: Univariate Distributions (tenure, MonthlyCharges, TotalCharges)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    metrics = [
        ('tenure', 'Tenure (Months)', '#1f77b4'),
        ('MonthlyCharges', 'Monthly Charges ($)', '#ff7f0e'),
        ('TotalCharges_clean', 'Total Charges ($)', '#2ca02c')
    ]
    for ax, (col, xlabel, color) in zip(axes, metrics):
        sns.histplot(df[col], kde=True, ax=ax, color=color, bins=30, edgecolor='black', alpha=0.6)
        m = stats_summary[col]['mean']
        med = stats_summary[col]['median']
        sk = stats_summary[col]['skewness']
        kt = stats_summary[col]['kurtosis']
        ax.axvline(m, color='red', linestyle='--', linewidth=2, label=f'Mean: {m:.1f}')
        ax.axvline(med, color='blue', linestyle=':', linewidth=2, label=f'Median: {med:.1f}')
        ax.set_title(f'Distribution of {xlabel}\n(Skew: {sk:+.2f}, Kurt: {kt:+.2f})', fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Customer Count')
        ax.legend(loc='upper right')
    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig01_univariate_distributions.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 2: Categorical Distributions (Contract, InternetService, PaymentMethod, TechSupport)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    cat_features = [
        ('Contract', 'Contract Type'),
        ('InternetService', 'Internet Service Architecture'),
        ('PaymentMethod', 'Payment Method'),
        ('TechSupport', 'Technical Support Subscription')
    ]
    for ax, (col, title) in zip(axes.flatten(), cat_features):
        order = df[col].value_counts().index
        sns.countplot(data=df, x=col, hue='Churn', order=order, ax=ax, palette=['#2b5c8f', '#d95f02'])
        ax.set_title(f'{title} by Churn Status', fontweight='bold')
        ax.set_xlabel(title)
        ax.set_ylabel('Number of Customers')
        if col == 'PaymentMethod':
            ax.set_xticks(range(len(order)))
            ax.set_xticklabels(order, rotation=20, ha='right')
        ax.legend(title='Churn', loc='upper right')
        # Annotate percentages
        total_counts = df[col].value_counts()
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}',
                            (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom', fontsize=9, xytext=(0, 3),
                            textcoords='offset points')
    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig02_categorical_distributions.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 3: Outlier Detection Boxplots across Churn Classes
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    num_box = [
        ('tenure', 'Tenure (Months)', '#4575b4'),
        ('MonthlyCharges', 'Monthly Charges ($)', '#fdae61'),
        ('TotalCharges_clean', 'Total Charges ($)', '#d73027')
    ]
    for ax, (col, ylabel, _) in zip(axes, num_box):
        sns.boxplot(x='Churn', y=col, hue='Churn', data=df, ax=ax, palette=['#74add1', '#f46d43'], width=0.45, fliersize=4, legend=False)
        sns.stripplot(x='Churn', y=col, data=df.sample(600, random_state=42), ax=ax, color='black', alpha=0.15, jitter=0.2)
        ax.set_title(f'Boxplot & Outlier Detection: {ylabel}', fontweight='bold')
        ax.set_xlabel('Customer Churn Status')
        ax.set_ylabel(ylabel)
        # Add IQR statistics text box
        q1_no, q3_no = df[df['Churn']=='No'][col].quantile([0.25, 0.75])
        q1_yes, q3_yes = df[df['Churn']=='Yes'][col].quantile([0.25, 0.75])
        ax.text(0.03, 0.92, f'No Churn IQR: {q3_no-q1_no:.1f}\nChurn IQR: {q3_yes-q1_yes:.1f}',
                transform=ax.transAxes, fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig03_outlier_boxplots.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 4: Correlation Heatmap
    # -------------------------------------------------------------
    corr_cols = [
        'tenure', 'MonthlyCharges', 'TotalCharges_clean', 'services_count',
        'family_stability', 'is_month_to_month', 'streaming_bundle', 'Churn_binary'
    ]
    corr_labels = [
        'Tenure', 'Monthly Charges', 'Total Charges', 'Service Add-on Count',
        'Family Stability', 'Month-to-Month', 'Streaming Bundle', 'Churn (Binary)'
    ]
    corr_matrix = df[corr_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1,
        square=True, ax=ax, xticklabels=corr_labels, yticklabels=corr_labels,
        cbar_kws={'label': 'Pearson Correlation Coefficient'}
    )
    ax.set_title('Multivariate Correlation Heatmap of Key Numerical & Derived Attributes', fontweight='bold', pad=14)
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig04_correlation_heatmap.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 5: Pairplot / Joint Multidimensional Distributions
    # -------------------------------------------------------------
    pair_df = df[['tenure', 'MonthlyCharges', 'TotalCharges_clean', 'Churn']].copy()
    pair_df.columns = ['Tenure (Mo)', 'Monthly Charges ($)', 'Total Charges ($)', 'Churn']
    g = sns.pairplot(
        pair_df, hue='Churn', palette={'No': '#2b5c8f', 'Yes': '#d95f02'},
        diag_kind='kde', plot_kws={'alpha': 0.35, 's': 20, 'edgecolor': 'none'},
        corner=False
    )
    g.fig.subplots_adjust(top=0.94)
    g.fig.suptitle('Pairwise Feature Interactions and Density Distributions by Churn Status', fontweight='bold', fontsize=14)
    g.savefig(f'{FIGURES_DIR}/fig05_pairplot_kde.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 6: Bivariate Churn Rates Across Key Dimensions
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    dims = [
        ('Contract', 'Contract Type'),
        ('InternetService', 'Internet Service'),
        ('TechSupport', 'Tech Support'),
        ('PaymentMethod', 'Payment Method'),
        ('tenure_cohort', 'Tenure Cohort'),
        ('PaperlessBilling', 'Paperless Billing')
    ]
    for ax, (col, title) in zip(axes.flatten(), dims):
        rate = df.groupby(col, observed=True)['Churn_binary'].mean() * 100
        order = rate.index
        palette = ['#e41a1c' if r > 30 else '#377eb8' for r in rate]
        bars = ax.bar(range(len(rate)), rate.values, color=palette, edgecolor='black', alpha=0.85)
        ax.set_xticks(range(len(rate)))
        ax.set_xticklabels(order, rotation=25 if col in ['PaymentMethod', 'tenure_cohort'] else 0, ha='right' if col in ['PaymentMethod', 'tenure_cohort'] else 'center')
        ax.set_ylabel('Churn Rate (%)')
        ax.set_title(f'Churn Rate by {title}', fontweight='bold')
        ax.axhline(26.54, color='black', linestyle='--', linewidth=1.5, label='Overall Avg: 26.5%')
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f'{h:.1f}%', (bar.get_x() + bar.get_width() / 2., h),
                        ha='center', va='bottom', fontsize=9, xytext=(0, 2), textcoords='offset points')
        ax.legend(loc='upper right', fontsize=8)
    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig06_bivariate_churn_rates.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 7: Violin Plots: MonthlyCharges across Contract stratified by Churn
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.violinplot(
        x='Contract', y='MonthlyCharges', hue='Churn', data=df, split=True,
        palette={'No': '#4575b4', 'Yes': '#d73027'}, inner='quartile', ax=axes[0]
    )
    axes[0].set_title('Monthly Charges Distribution by Contract Type & Churn', fontweight='bold')
    axes[0].set_xlabel('Contract Type')
    axes[0].set_ylabel('Monthly Charges ($)')
    axes[0].legend(title='Churn', loc='upper right')

    sns.violinplot(
        x='InternetService', y='tenure', hue='Churn', data=df, split=True,
        palette={'No': '#4575b4', 'Yes': '#d73027'}, inner='quartile', ax=axes[1]
    )
    axes[1].set_title('Tenure Distribution by Internet Service & Churn', fontweight='bold')
    axes[1].set_xlabel('Internet Service')
    axes[1].set_ylabel('Tenure (Months)')
    axes[1].legend(title='Churn', loc='upper right')

    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig07_violin_plots.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 8: Probability Distribution Fitting & Q-Q Plots
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    
    # 1. Normal fit on tenure
    tenure_data = df['tenure'].values.astype(float)
    res_norm = stats.probplot(tenure_data, dist="norm")
    axes[0, 0].scatter(res_norm[0][0], res_norm[0][1], color='#1f77b4', alpha=0.3, s=12)
    axes[0, 0].plot(res_norm[0][0], res_norm[1][1] + res_norm[1][0] * res_norm[0][0], 'r--', linewidth=2)
    tenure_stdized = (tenure_data - tenure_data.mean()) / tenure_data.std()
    ks_norm = stats.kstest(tenure_stdized, 'norm')
    axes[0, 0].set_title(f'Normal Q-Q Plot: Tenure\n(KS-stat: {ks_norm.statistic:.4f}, p={ks_norm.pvalue:.1e})', fontweight='bold')
    axes[0, 0].set_xlabel('Theoretical Quantiles')
    axes[0, 0].set_ylabel('Sample Quantiles')

    # 2. Exponential fit on TotalCharges
    tc_data = df['TotalCharges_clean'].values.astype(float) + 1.0
    res_exp = stats.probplot(tc_data, dist="expon")
    axes[0, 1].scatter(res_exp[0][0], res_exp[0][1], color='#2ca02c', alpha=0.3, s=12)
    axes[0, 1].plot(res_exp[0][0], res_exp[1][1] + res_exp[1][0] * res_exp[0][0], 'r--', linewidth=2)
    tc_scaled = tc_data / tc_data.mean()
    ks_exp = stats.kstest(tc_scaled, 'expon')
    axes[0, 1].set_title(f'Exponential Q-Q Plot: Total Charges\n(KS-stat: {ks_exp.statistic:.4f}, p={ks_exp.pvalue:.1e})', fontweight='bold')
    axes[0, 1].set_xlabel('Theoretical Quantiles')
    axes[0, 1].set_ylabel('Sample Quantiles')

    # 3. Parametric curve overlays on MonthlyCharges (Normal vs KDE)
    mc_data = df['MonthlyCharges'].values
    x_grid = np.linspace(mc_data.min(), mc_data.max(), 200)
    mu, std = mc_data.mean(), mc_data.std()
    norm_pdf = stats.norm.pdf(x_grid, mu, std)
    sns.histplot(mc_data, stat='density', ax=axes[1, 0], color='#ff7f0e', alpha=0.4, bins=30, label='Empirical Density')
    axes[1, 0].plot(x_grid, norm_pdf, 'r-', linewidth=2.5, label=f'Fitted Normal (μ={mu:.1f}, σ={std:.1f})')
    axes[1, 0].set_title('Monthly Charges: Empirical vs Fitted Normal PDF', fontweight='bold')
    axes[1, 0].set_xlabel('Monthly Charges ($)')
    axes[1, 0].set_ylabel('Probability Density')
    axes[1, 0].legend()

    # 4. Bernoulli Fit on Churn
    p_churn = df['Churn_binary'].mean()
    p_nochurn = 1 - p_churn
    categories = ['No Churn (0)', 'Churn (1)']
    empirical_probs = [p_nochurn, p_churn]
    axes[1, 1].bar(categories, empirical_probs, color=['#2b5c8f', '#d95f02'], edgecolor='black', width=0.45, alpha=0.85)
    axes[1, 1].set_title(f'Bernoulli Distribution Model for Churn\n(Fitted Parameter p = {p_churn:.4f}, Var = {p_churn*p_nochurn:.4f})', fontweight='bold')
    axes[1, 1].set_ylabel('Probability Mass P(X=k)')
    for idx, pr in enumerate(empirical_probs):
        axes[1, 1].annotate(f'{pr*100:.2f}%\n(P={pr:.4f})', (idx, pr/2), ha='center', va='center', color='white', fontweight='bold')

    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig08_distribution_fitting_qq.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 9: Statistical Hypothesis Testing Summary Visual
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Chi-square Cramér's V ranking
    cv_series = pd.Series({k: v['cramers_v'] for k, v in chi2_results.items()}).sort_values(ascending=True)
    colors = ['#d73027' if v >= 0.3 else '#fdae61' if v >= 0.15 else '#4575b4' for v in cv_series.values]
    axes[0].barh(cv_series.index, cv_series.values, color=colors, edgecolor='black', alpha=0.85)
    axes[0].set_xlabel("Cramér's V Effect Size")
    axes[0].set_title("Categorical Feature Associations with Churn\n(Cramér's V from Pearson Chi-Square Test)", fontweight='bold')
    axes[0].axvline(0.3, color='red', linestyle='--', label='Strong Effect (>0.30)')
    axes[0].axvline(0.15, color='orange', linestyle=':', label='Moderate Effect (>0.15)')
    axes[0].legend(loc='lower right')

    # Continuous T-test / Point-Biserial Correlations
    pb_series = pd.Series({k: v['point_biserial_r'] for k, v in ttest_results.items()}).sort_values()
    bar_colors = ['#4575b4' if v < 0 else '#d73027' for v in pb_series.values]
    axes[1].bar(pb_series.index, pb_series.values, color=bar_colors, edgecolor='black', width=0.45, alpha=0.85)
    axes[1].axhline(0, color='black', linewidth=1)
    axes[1].set_ylabel('Point-Biserial Correlation r')
    axes[1].set_title('Continuous Feature Correlation with Churn Status\n(Welch T-Test p < 1e-70 for all 3)', fontweight='bold')
    for idx, (col_name, val) in enumerate(pb_series.items()):
        welch_t = ttest_results[col_name]['welch_t']
        axes[1].annotate(f'r = {val:+.3f}\nt = {welch_t:.1f}', (idx, val / 2), ha='center', va='center', color='white', fontweight='bold', fontsize=9)

    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig09_statistical_tests_summary.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 10: Derived Feature Analysis
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    
    # 1. Services count vs Churn rate
    svc_churn = df.groupby('services_count')['Churn_binary'].agg(['count', 'mean'])
    svc_churn['mean'] = svc_churn['mean'] * 100
    ax1 = axes[0]
    bars = ax1.bar(svc_churn.index, svc_churn['mean'], color='#1f77b4', edgecolor='black', alpha=0.8)
    ax1.axhline(26.54, color='red', linestyle='--', label='Overall Mean (26.5%)')
    ax1.set_xlabel('Number of Value-Added Subscribed Services (0 to 6)')
    ax1.set_ylabel('Churn Rate (%)')
    ax1.set_title('Impact of Value-Added Service Adoption on Churn Rate', fontweight='bold')
    ax1.legend(loc='upper right')
    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f'{h:.1f}%', (bar.get_x() + bar.get_width() / 2., h),
                     ha='center', va='bottom', fontsize=9, xytext=(0, 2), textcoords='offset points')

    # 2. Tenure Cohort vs Month-to-Month Contract interaction
    cohort_contract = df.groupby(['tenure_cohort', 'Contract'], observed=True)['Churn_binary'].mean().unstack() * 100
    cohort_contract.plot(kind='bar', ax=axes[1], colormap='viridis', edgecolor='black', alpha=0.85)
    axes[1].set_xlabel('Tenure Cohort')
    axes[1].set_ylabel('Churn Rate (%)')
    axes[1].set_title('Churn Rate across Tenure Cohorts by Contract Structure', fontweight='bold')
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=20, ha='right')
    axes[1].legend(title='Contract')

    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig10_derived_features_churn.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 11: Interactive Multi-Dimensional Visualization (Plotly)
    # -------------------------------------------------------------
    sample_df = df.sample(min(1500, len(df)), random_state=42)
    fig_plotly = px.scatter_3d(
        sample_df,
        x='tenure',
        y='MonthlyCharges',
        z='TotalCharges_clean',
        color='Churn',
        color_discrete_map={'No': '#1f77b4', 'Yes': '#ff7f0e'},
        symbol='Contract',
        size='services_count',
        size_max=12,
        opacity=0.7,
        hover_data=['PaymentMethod', 'InternetService'],
        title='Interactive 3D Feature Space: Tenure vs Monthly Charges vs Total Charges',
        labels={'tenure': 'Tenure (Months)', 'MonthlyCharges': 'Monthly ($)', 'TotalCharges_clean': 'Total ($)'}
    )
    fig_plotly.update_layout(
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(x=0.02, y=0.98),
        scene=dict(
            xaxis_title='Tenure (Months)',
            yaxis_title='Monthly Charges ($)',
            zaxis_title='Total Charges ($)'
        )
    )
    fig_plotly.write_html(f'{FIGURES_DIR}/fig11_interactive_3d_scatter.html')

    # Static rendering of 2D multi-dimensional scatter for PDF/DOCX
    fig, ax = plt.subplots(figsize=(10, 6.5))
    scatter = sns.scatterplot(
        data=sample_df, x='tenure', y='MonthlyCharges', hue='Churn',
        size='TotalCharges_clean', sizes=(20, 200), style='Contract',
        palette={'No': '#2b5c8f', 'Yes': '#d95f02'}, alpha=0.7, ax=ax
    )
    ax.set_title('Multi-Dimensional Customer Segmentation (Tenure, Charges, Contract & Churn)', fontweight='bold')
    ax.set_xlabel('Tenure (Months)')
    ax.set_ylabel('Monthly Charges ($)')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig11_multidimensional_scatter.png', dpi=300)
    plt.close()

    print("    Visualizations successfully saved to outputs/figures/")


def prepare_datasets(df):
    print("[4] Splitting and scaling datasets (70/15/15 stratified)...")
    
    # Feature columns
    cat_cols_to_encode = [
        'gender', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
        'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
        'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract',
        'PaperlessBilling', 'PaymentMethod', 'tenure_cohort'
    ]
    num_cols_to_scale = ['tenure', 'MonthlyCharges', 'TotalCharges_clean', 'charge_ratio']
    passthrough_cols = ['SeniorCitizen', 'services_count', 'family_stability', 'is_month_to_month', 'streaming_bundle']

    X_raw_cat = df[cat_cols_to_encode]
    X_raw_num = df[num_cols_to_scale]
    X_raw_pass = df[passthrough_cols]
    y = df['Churn_binary'].values

    # Stratified split: 70% train, 15% val, 15% test
    X_train_cat, X_temp_cat, y_train, y_temp = train_test_split(
        X_raw_cat, y, test_size=0.30, random_state=SEED, stratify=y
    )
    X_train_num, X_temp_num = train_test_split(
        X_raw_num, test_size=0.30, random_state=SEED, stratify=y
    )
    X_train_pass, X_temp_pass = train_test_split(
        X_raw_pass, test_size=0.30, random_state=SEED, stratify=y
    )

    X_val_cat, X_test_cat, y_val, y_test = train_test_split(
        X_temp_cat, y_temp, test_size=0.50, random_state=SEED, stratify=y_temp
    )
    X_val_num, X_test_num = train_test_split(
        X_temp_num, test_size=0.50, random_state=SEED, stratify=y_temp
    )
    X_val_pass, X_test_pass = train_test_split(
        X_temp_pass, test_size=0.50, random_state=SEED, stratify=y_temp
    )

    # Fit Scaler strictly on train
    scaler = StandardScaler()
    X_train_num_scaled = scaler.fit_transform(X_train_num)
    X_val_num_scaled = scaler.transform(X_val_num)
    X_test_num_scaled = scaler.transform(X_test_num)

    # Fit One-Hot Encoder strictly on train
    ohe = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
    X_train_cat_encoded = ohe.fit_transform(X_train_cat)
    X_val_cat_encoded = ohe.transform(X_val_cat)
    X_test_cat_encoded = ohe.transform(X_test_cat)

    cat_feature_names = ohe.get_feature_names_out(cat_cols_to_encode).tolist()
    all_feature_names = num_cols_to_scale + passthrough_cols + cat_feature_names

    # Combine matrices
    X_train = np.hstack([X_train_num_scaled, X_train_pass.values, X_train_cat_encoded])
    X_val = np.hstack([X_val_num_scaled, X_val_pass.values, X_val_cat_encoded])
    X_test = np.hstack([X_test_num_scaled, X_test_pass.values, X_test_cat_encoded])

    print(f"    Train shape: {X_train.shape}, Val shape: {X_val.shape}, Test shape: {X_test.shape}")
    print(f"    Class balance - Train: {np.mean(y_train):.3f}, Val: {np.mean(y_val):.3f}, Test: {np.mean(y_test):.3f}")

    return (X_train, y_train, X_val, y_val, X_test, y_test, all_feature_names)


class ChurnMLP(nn.Module):
    def __init__(self, in_features, hidden1=64, hidden2=32, hidden3=16, dropout1=0.3, dropout2=0.2):
        super(ChurnMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden1),
            nn.BatchNorm1d(hidden1),
            nn.ReLU(),
            nn.Dropout(dropout1),
            
            nn.Linear(hidden1, hidden2),
            nn.BatchNorm1d(hidden2),
            nn.ReLU(),
            nn.Dropout(dropout2),

            nn.Linear(hidden2, hidden3),
            nn.BatchNorm1d(hidden3),
            nn.ReLU(),
            nn.Dropout(0.1),

            nn.Linear(hidden3, 1)
        )

    def forward(self, x):
        return self.net(x).squeeze(1)


def train_mlp_model(X_train, y_train, X_val, y_val, in_features, epochs=70, batch_size=64, lr=0.001, pos_weight_val=2.77):
    # PyTorch Datasets
    train_dataset = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    val_dataset = TensorDataset(torch.FloatTensor(X_val), torch.FloatTensor(y_val))

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model = ChurnMLP(in_features)
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight_val]))
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}

    best_val_loss = float('inf')
    best_weights = None
    patience = 18
    patience_counter = 0

    for epoch in range(epochs):
        # Training
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * len(batch_y)
            preds = (torch.sigmoid(logits) >= 0.5).float()
            correct_train += (preds == batch_y).sum().item()
            total_train += len(batch_y)

        train_epoch_loss = running_loss / total_train
        train_epoch_acc = correct_train / total_train

        # Validation
        model.eval()
        val_loss = 0.0
        correct_val = 0
        total_val = 0

        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                logits = model(batch_x)
                loss = criterion(logits, batch_y)
                val_loss += loss.item() * len(batch_y)
                preds = (torch.sigmoid(logits) >= 0.5).float()
                correct_val += (preds == batch_y).sum().item()
                total_val += len(batch_y)

        val_epoch_loss = val_loss / total_val
        val_epoch_acc = correct_val / total_val

        history['train_loss'].append(train_epoch_loss)
        history['val_loss'].append(val_epoch_loss)
        history['train_acc'].append(train_epoch_acc)
        history['val_acc'].append(val_epoch_acc)

        if val_epoch_loss < best_val_loss:
            best_val_loss = val_epoch_loss
            best_weights = model.state_dict().copy()
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"    Early stopping triggered at epoch {epoch+1}")
                break

    if best_weights is not None:
        model.load_state_dict(best_weights)

    return model, history


def run_hyperparameter_tuning(X_train, y_train, X_val, y_val, in_features):
    print("[5] Executing hyperparameter tuning grid search...")
    configs = [
        {'name': 'Config 1 (Baseline LR)', 'hidden1': 64, 'hidden2': 32, 'lr': 0.001, 'dropout1': 0.3, 'batch_size': 64},
        {'name': 'Config 2 (High LR)', 'hidden1': 64, 'hidden2': 32, 'lr': 0.01, 'dropout1': 0.3, 'batch_size': 64},
        {'name': 'Config 3 (Low LR, High Drop)', 'hidden1': 64, 'hidden2': 32, 'lr': 0.0005, 'dropout1': 0.5, 'batch_size': 64},
        {'name': 'Config 4 (Deeper [128-64])', 'hidden1': 128, 'hidden2': 64, 'lr': 0.001, 'dropout1': 0.3, 'batch_size': 32},
        {'name': 'Config 5 (Lightweight [32-16])', 'hidden1': 32, 'hidden2': 16, 'lr': 0.001, 'dropout1': 0.2, 'batch_size': 64},
    ]

    results = []
    for cfg in configs:
        model = nn.Sequential(
            nn.Linear(in_features, cfg['hidden1']),
            nn.BatchNorm1d(cfg['hidden1']),
            nn.ReLU(),
            nn.Dropout(cfg['dropout1']),
            nn.Linear(cfg['hidden1'], cfg['hidden2']),
            nn.BatchNorm1d(cfg['hidden2']),
            nn.ReLU(),
            nn.Linear(cfg['hidden2'], 1)
        )
        optimizer = optim.Adam(model.parameters(), lr=cfg['lr'], weight_decay=1e-4)
        criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([2.77]))

        train_dataset = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
        loader = DataLoader(train_dataset, batch_size=cfg['batch_size'], shuffle=True)

        for _ in range(35):
            model.train()
            for bx, by in loader:
                optimizer.zero_grad()
                out = model(bx).squeeze(1)
                loss = criterion(out, by)
                loss.backward()
                optimizer.step()

        model.eval()
        with torch.no_grad():
            val_logits = model(torch.FloatTensor(X_val)).squeeze(1)
            val_probs = torch.sigmoid(val_logits).numpy()
            val_preds = (val_probs >= 0.5).astype(int)

        acc = accuracy_score(y_val, val_preds)
        f1 = f1_score(y_val, val_preds)
        auc = roc_auc_score(y_val, val_probs)
        ap = average_precision_score(y_val, val_probs)

        results.append({
            'Configuration': cfg['name'],
            'Hidden Units': f"[{cfg['hidden1']}, {cfg['hidden2']}]",
            'Learning Rate': cfg['lr'],
            'Dropout': cfg['dropout1'],
            'Batch Size': cfg['batch_size'],
            'Val Accuracy': f"{acc*100:.2f}%",
            'Val F1-Score': f"{f1:.4f}",
            'Val ROC-AUC': f"{auc:.4f}",
            'Val PR-AUC': f"{ap:.4f}"
        })

    tuning_df = pd.DataFrame(results)
    print(tuning_df.to_string())
    tuning_df.to_csv('outputs/hyperparameter_tuning_results.csv', index=False)
    return tuning_df


def train_and_evaluate_all_models(X_train, y_train, X_val, y_val, X_test, y_test, feature_names):
    print("[6] Training baseline models (Logistic Regression, Random Forest) & Deep Learning MLP...")

    # 1. Logistic Regression
    lr_model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=SEED)
    lr_model.fit(X_train, y_train)
    lr_test_probs = lr_model.predict_proba(X_test)[:, 1]
    lr_test_preds = lr_model.predict(X_test)

    # 2. Random Forest
    rf_model = RandomForestClassifier(n_estimators=150, max_depth=8, class_weight='balanced', random_state=SEED)
    rf_model.fit(X_train, y_train)
    rf_test_probs = rf_model.predict_proba(X_test)[:, 1]
    rf_test_preds = rf_model.predict(X_test)

    # 3. Deep Learning MLP
    in_features = X_train.shape[1]
    mlp_model, history = train_mlp_model(X_train, y_train, X_val, y_val, in_features, epochs=70)
    
    mlp_model.eval()
    with torch.no_grad():
        mlp_test_logits = mlp_model(torch.FloatTensor(X_test))
        mlp_test_probs = torch.sigmoid(mlp_test_logits).numpy()
        mlp_test_preds = (mlp_test_probs >= 0.5).astype(int)

    # Metrics dictionary
    models_dict = {
        'Logistic Regression': (lr_test_preds, lr_test_probs),
        'Random Forest': (rf_test_preds, rf_test_probs),
        'Deep Learning MLP': (mlp_test_preds, mlp_test_probs)
    }

    metrics_table = []
    for name, (preds, probs) in models_dict.items():
        acc = accuracy_score(y_test, preds)
        rec = recall_score(y_test, preds)
        prec = precision_score(y_test, preds)
        f1 = f1_score(y_test, preds)
        auc = roc_auc_score(y_test, probs)
        ap = average_precision_score(y_test, probs)
        metrics_table.append({
            'Model': name,
            'Accuracy': f"{acc*100:.2f}%",
            'Precision': f"{prec:.4f}",
            'Recall (Sensitivity)': f"{rec:.4f}",
            'F1-Score': f"{f1:.4f}",
            'ROC-AUC': f"{auc:.4f}",
            'PR-AUC (Avg Prec)': f"{ap:.4f}"
        })

    eval_df = pd.DataFrame(metrics_table)
    print("\n=== FINAL TEST EVALUATION METRICS ===")
    print(eval_df.to_string())
    eval_df.to_csv('outputs/model_evaluation_metrics.csv', index=False)

    # Feature Importance (Random Forest MDI & Permutation)
    rf_importances = rf_model.feature_importances_
    perm_importance = permutation_importance(rf_model, X_val, y_val, n_repeats=5, random_state=SEED)
    perm_mean = perm_importance.importances_mean

    feat_df = pd.DataFrame({
        'Feature': feature_names,
        'RF_MDI_Importance': rf_importances,
        'Permutation_Importance': perm_mean
    }).sort_values(by='RF_MDI_Importance', ascending=False)
    feat_df.to_csv('outputs/feature_importance.csv', index=False)

    return lr_model, rf_model, mlp_model, history, models_dict, feat_df, eval_df


def generate_evaluation_visualizations(history, models_dict, y_test, feat_df):
    print("[7] Generating model evaluation graphics (Loss, Accuracy, CM, ROC, PR, Feature Importance)...")

    # -------------------------------------------------------------
    # Fig 12: MLP Training History (Loss & Accuracy vs Epoch)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    epochs_range = range(1, len(history['train_loss']) + 1)
    
    # Loss
    axes[0].plot(epochs_range, history['train_loss'], 'b-', linewidth=2, label='Training Loss')
    axes[0].plot(epochs_range, history['val_loss'], 'r--', linewidth=2, label='Validation Loss')
    axes[0].set_title('Cross-Entropy Loss vs Epoch (Deep Learning MLP)', fontweight='bold')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Weighted Binary Cross-Entropy Loss')
    axes[0].legend(loc='upper right')
    
    # Accuracy
    axes[1].plot(epochs_range, [a * 100 for a in history['train_acc']], 'b-', linewidth=2, label='Training Accuracy')
    axes[1].plot(epochs_range, [a * 100 for a in history['val_acc']], 'r--', linewidth=2, label='Validation Accuracy')
    axes[1].set_title('Classification Accuracy vs Epoch (Deep Learning MLP)', fontweight='bold')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy (%)')
    axes[1].legend(loc='lower right')

    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig12_model_training_curves.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 13: Confusion Matrices for All 3 Models
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, (name, (preds, _)) in zip(axes, models_dict.items()):
        cm = confusion_matrix(y_test, preds)
        cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        annotations = np.empty_like(cm).astype(str)
        for i in range(2):
            for j in range(2):
                annotations[i, j] = f"{cm[i, j]}\n({cm_norm[i, j]*100:.1f}%)"

        sns.heatmap(cm, annot=annotations, fmt='', cmap='Blues', cbar=False, ax=ax,
                    xticklabels=['Retained (0)', 'Churned (1)'],
                    yticklabels=['Retained (0)', 'Churned (1)'])
        ax.set_title(f'Confusion Matrix: {name}', fontweight='bold')
        ax.set_xlabel('Predicted Label')
        ax.set_ylabel('True Label')
        # Cost highlight
        fn = cm[1, 0]
        fp = cm[0, 1]
        ax.text(0.05, -0.15, f'False Negatives (Missed Churners): {fn}\nFalse Positives (False Alarms): {fp}',
                transform=ax.transAxes, fontsize=9, bbox=dict(boxstyle='round', facecolor='#fee0d2', alpha=0.7))

    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig13_confusion_matrices.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 14: ROC Curves Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    colors = {'Logistic Regression': '#4575b4', 'Random Forest': '#31a354', 'Deep Learning MLP': '#e41a1c'}
    
    for name, (_, probs) in models_dict.items():
        fpr, tpr, _ = roc_curve(y_test, probs)
        auc_val = roc_auc_score(y_test, probs)
        ax.plot(fpr, tpr, label=f'{name} (AUC = {auc_val:.4f})', linewidth=2.2, color=colors[name])

    ax.plot([0, 1], [0, 1], 'k--', linewidth=1.5, label='Random Guess (AUC = 0.5000)')
    ax.set_title('Receiver Operating Characteristic (ROC) Curves Comparison', fontweight='bold', pad=12)
    ax.set_xlabel('False Positive Rate (1 - Specificity)')
    ax.set_ylabel('True Positive Rate (Sensitivity / Recall)')
    ax.legend(loc='lower right', frameon=True)
    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig14_roc_curves.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 15: Precision-Recall Curves Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    baseline_ap = np.mean(y_test)
    for name, (_, probs) in models_dict.items():
        prec, rec, _ = precision_recall_curve(y_test, probs)
        ap_val = average_precision_score(y_test, probs)
        ax.plot(rec, prec, label=f'{name} (PR-AUC / AP = {ap_val:.4f})', linewidth=2.2, color=colors[name])

    ax.axhline(baseline_ap, color='black', linestyle='--', linewidth=1.5, label=f'No-Skill Baseline (AP = {baseline_ap:.4f})')
    ax.set_title('Precision-Recall (PR) Curves across Classifier Architectures', fontweight='bold', pad=12)
    ax.set_xlabel('Recall (True Positive Rate)')
    ax.set_ylabel('Precision (Positive Predictive Value)')
    ax.legend(loc='upper right', frameon=True)
    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig15_precision_recall_curves.png', dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Fig 16: Feature Importance Comparison
    # -------------------------------------------------------------
    top15 = feat_df.head(15).iloc[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # MDI Importance
    axes[0].barh(top15['Feature'], top15['RF_MDI_Importance'], color='#1f77b4', edgecolor='black', alpha=0.85)
    axes[0].set_title('Random Forest Feature Importance (MDI / Gini Gain)', fontweight='bold')
    axes[0].set_xlabel('Mean Decrease in Impurity')

    # Permutation Importance
    axes[1].barh(top15['Feature'], top15['Permutation_Importance'], color='#ff7f0e', edgecolor='black', alpha=0.85)
    axes[1].set_title('Permutation Feature Importance on Validation Set', fontweight='bold')
    axes[1].set_xlabel('Mean Decrease in Accuracy')

    plt.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/fig16_feature_importance.png', dpi=300)
    plt.close()

    print("    Evaluation visualizations successfully saved to outputs/figures/")


def main():
    print("================================================================================")
    print("TELCO CUSTOMER CHURN PREDICTION - COMPLETE EDA & DEEP LEARNING PIPELINE")
    print("Author: Navin J (Roll No: 24AD071) | Dept of AI & DS, KPRIET")
    print("================================================================================")
    df = load_and_preprocess_data()
    stats_summary, chi2_results, ttest_results = compute_exploratory_statistics(df)
    generate_visualizations(df, stats_summary, chi2_results, ttest_results)
    
    X_train, y_train, X_val, y_val, X_test, y_test, feature_names = prepare_datasets(df)
    tuning_df = run_hyperparameter_tuning(X_train, y_train, X_val, y_val, X_train.shape[1])
    lr_model, rf_model, mlp_model, history, models_dict, feat_df, eval_df = train_and_evaluate_all_models(
        X_train, y_train, X_val, y_val, X_test, y_test, feature_names
    )
    generate_evaluation_visualizations(history, models_dict, y_test, feat_df)
    
    # Save all summary stats into JSON for exact referencing in report & notebook
    full_summary = {
        'stats_summary': stats_summary,
        'chi2_results': chi2_results,
        'ttest_results': ttest_results,
        'model_eval': eval_df.to_dict(orient='records'),
        'hyperparameter_tuning': tuning_df.to_dict(orient='records'),
        'top_features': feat_df.head(10).to_dict(orient='records')
    }
    with open('outputs/pipeline_summary.json', 'w') as f:
        json.dump(full_summary, f, indent=4)
        
    print("\n[SUCCESS] Pipeline executed completely without errors. All outputs generated!")


if __name__ == '__main__':
    main()

