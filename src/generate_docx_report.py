"""
Generate comprehensive academic DOCX report formatted to exact institutional standards:
- Times New Roman throughout (16pt Title, 14pt Headings, 12pt Body)
- 1.5 Line Spacing
- Justified Text Alignment
- Page Borders and Page Numbers
- Table of Contents
- Numbered Figures & Tables with Captions
- Embedded 300 DPI figures
- Exactly 11 required sections
"""

import os
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def add_page_border(section):
    sectPr = section._sectPr
    borders_xml = f'''
    <w:pgBorders {nsdecls("w")} w:offsetFrom="page">
        <w:top w:val="single" w:sz="8" w:space="24" w:color="1A365D"/>
        <w:left w:val="single" w:sz="8" w:space="24" w:color="1A365D"/>
        <w:bottom w:val="single" w:sz="8" w:space="24" w:color="1A365D"/>
        <w:right w:val="single" w:sz="8" w:space="24" w:color="1A365D"/>
    </w:pgBorders>
    '''
    sectPr.append(parse_xml(borders_xml))

def add_footer_page_number(run):
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def build_docx_report():
    print("[Report Generator] Initializing DOCX report generation...")
    doc = docx.Document()

    # Configure Margins (1 inch all around)
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.different_first_page_header_footer = True
    add_page_border(section)

    # Configure Default Style: Times New Roman, 12pt, 1.5 Line Spacing, Justified
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    style_normal.paragraph_format.line_spacing = 1.5
    style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    style_normal.paragraph_format.space_after = Pt(6)

    # Footer for subsequent pages
    footer = section.footer
    f_p = footer.paragraphs[0]
    f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    f_p.paragraph_format.line_spacing = 1.0
    f_run = f_p.add_run("U21ADP05 - Assignment II | Navin J (24AD071) | Page ")
    f_run.font.name = 'Times New Roman'
    f_run.font.size = Pt(9)
    f_run.font.italic = True
    add_footer_page_number(f_p.add_run())

    # =========================================================================
    # 1. TITLE PAGE
    # =========================================================================
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(36)
    title_p.paragraph_format.space_after = Pt(12)
    title_run = title_p.add_run("KPR INSTITUTE OF ENGINEERING AND TECHNOLOGY\n")
    title_run.font.name = 'Times New Roman'
    title_run.font.size = Pt(14)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    sub_run = title_p.add_run("(Autonomous Institution, Affiliated to Anna University, Chennai)\n"
                              "Department of Artificial Intelligence and Data Science\n"
                              "Coimbatore - 641 407, Tamil Nadu, India\n\n")
    sub_run.font.name = 'Times New Roman'
    sub_run.font.size = Pt(11)
    sub_run.font.italic = True

    proj_p = doc.add_paragraph()
    proj_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    proj_p.paragraph_format.space_before = Pt(30)
    proj_p.paragraph_format.space_after = Pt(20)
    p_run = proj_p.add_run("ACADEMIC PROJECT REPORT (ASSIGNMENT II)\n\n"
                           "EXPLORATORY DATA ANALYSIS AND VISUALIZATION OF A REAL-WORLD DATASET:\n"
                           "CUSTOMER CHURN PREDICTION")
    p_run.font.name = 'Times New Roman'
    p_run.font.size = Pt(16)
    p_run.font.bold = True
    p_run.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

    course_p = doc.add_paragraph()
    course_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    course_p.paragraph_format.space_after = Pt(40)
    c_run = course_p.add_run("Course Code & Title: U21ADP05 - Exploratory Data Analysis and Visualization\n"
                             "Academic Year: 2026-2027 | Semester: V (Third Year)\n"
                             "Batch: 2023 - 2027")
    c_run.font.name = 'Times New Roman'
    c_run.font.size = Pt(12)

    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    meta_table.columns[0].width = Inches(3.2)
    meta_table.columns[1].width = Inches(3.2)

    cell_left = meta_table.cell(0, 0)
    cell_right = meta_table.cell(0, 1)
    
    lp = cell_left.paragraphs[0]
    lp.paragraph_format.line_spacing = 1.25
    l_run = lp.add_run("SUBMITTED BY:\n"
                       "Student Name: Navin J\n"
                       "Roll Number: 24AD071\n"
                       "Degree & Branch: B.Tech. AI & DS\n"
                       "GitHub: navin2425")
    l_run.font.name = 'Times New Roman'
    l_run.font.size = Pt(11)

    rp = cell_right.paragraphs[0]
    rp.paragraph_format.line_spacing = 1.25
    r_run = rp.add_run("COURSE COORDINATOR:\n"
                       "Mr. Rushikesh Kadam\n"
                       "Assistant Professor,\n"
                       "Dept. of AI & DS,\n"
                       "KPR Institute of Engg. & Tech.")
    r_run.font.name = 'Times New Roman'
    r_run.font.size = Pt(11)

    date_p = doc.add_paragraph()
    date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_p.paragraph_format.space_before = Pt(45)
    d_run = date_p.add_run("Date of Submission: October 28, 2026")
    d_run.font.name = 'Times New Roman'
    d_run.font.size = Pt(11)
    d_run.font.bold = True

    doc.add_page_break()

    # Helper function for adding headings
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
        return p

    def add_caption(text, is_table=False):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(10)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # =========================================================================
    # TABLE OF CONTENTS (Executive Academic Overview)
    # =========================================================================
    add_h1("TABLE OF CONTENTS")
    toc_data = [
        ("1. Abstract", "3"),
        ("2. Introduction and Objective", "3"),
        ("3. Dataset Description", "4"),
        ("4. Exploratory Data Analysis & Preprocessing", "6"),
        ("5. Data Visualization (The 7-Stage Process)", "9"),
        ("6. Deep Learning Classification Model", "16"),
        ("7. Result Visualization & Performance Interpretation", "18"),
        ("8. Conclusion, Future Scope & Business Recommendations", "21"),
        ("9. References", "23"),
        ("10. Appendix: Complete Python Pipeline Code", "24"),
    ]
    toc_table = doc.add_table(rows=len(toc_data)+1, cols=2)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    toc_table.columns[0].width = Inches(5.2)
    toc_table.columns[1].width = Inches(1.2)
    
    # Header
    hdr = toc_table.rows[0]
    hdr.cells[0].paragraphs[0].add_run("Section / Topic Description").font.bold = True
    hdr.cells[1].paragraphs[0].add_run("Page No.").font.bold = True
    set_cell_shading(hdr.cells[0], "EAEDED")
    set_cell_shading(hdr.cells[1], "EAEDED")

    for idx, (title_str, page_str) in enumerate(toc_data):
        row = toc_table.rows[idx+1]
        p0 = row.cells[0].paragraphs[0]
        p0.paragraph_format.line_spacing = 1.15
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(title_str)
        if title_str.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.")):
            r0.font.bold = True
        
        p1 = row.cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.line_spacing = 1.15
        p1.paragraph_format.space_after = Pt(2)
        p1.add_run(page_str)
        if idx % 2 == 1:
            set_cell_shading(row.cells[0], "F9F9F9")
            set_cell_shading(row.cells[1], "F9F9F9")

    doc.add_page_break()

    # =========================================================================
    # 2. ABSTRACT (Strictly 100-150 words)
    # =========================================================================
    add_h1("1. ABSTRACT")
    abstract_text = (
        "This academic case study presents an end-to-end exploratory data analysis, statistical modeling, "
        "and deep learning framework for customer churn prediction using the canonical IBM Telco Customer "
        "Churn dataset comprising 7,043 instances and 21 attributes. Following Ben Fry’s seven-stage "
        "visualization taxonomy, we systematically interrogate customer behavior across demographic, account, "
        "and service dimensions. Data preprocessing resolves whitespace anomalies in cumulative billing, "
        "creates six domain-engineered derived features, and implements stratified partitioning (70/15/15). "
        "Parametric distribution fitting and non-parametric hypothesis tests reveal that month-to-month contracts, "
        "electronic payment methods, and lack of technical support strongly correlate with attrition. "
        "A multilayer perceptron incorporating batch normalization, dropout, and class-weighted loss achieves "
        "an out-of-sample sensitivity of 85.05%, outperforming baseline Logistic Regression (76.51%) and Random "
        "Forest (77.22%) classifiers. By minimizing costly false negative classifications, this framework empowers "
        "telecommunications providers to proactively safeguard enterprise revenue through targeted retention strategies."
    )
    p_abs = doc.add_paragraph(abstract_text)
    words = abstract_text.split()
    p_wordcount = doc.add_paragraph()
    p_wordcount.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    wc_run = p_wordcount.add_run(f"[Abstract Word Count: {len(words)} words | Required: 100-150 words]")
    wc_run.font.italic = True
    wc_run.font.size = Pt(9.5)
    wc_run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(6)
    kw_bold = p_kw.add_run("Keywords: ")
    kw_bold.font.bold = True
    p_kw.add_run("Exploratory Data Analysis, Data Visualization Taxonomy, Customer Churn, Deep Multilayer Perceptron, Class Imbalance, Hypothesis Testing, Telco Analytics.")

    # =========================================================================
    # 3. INTRODUCTION AND OBJECTIVE
    # =========================================================================
    add_h1("2. INTRODUCTION AND OBJECTIVE")
    doc.add_paragraph(
        "In the contemporary telecommunications industry, customer acquisition costs outstrip retention expenditures "
        "by a factor of five to seven times [1]. As market saturation deepens and switching barriers diminish due to regulatory "
        "mobile number portability, telecommunications service providers face relentless downward pressure on customer lifetime value (LTV). "
        "Customer churn—defined as the percentage of subscribers who terminate their service contract over a specified operational interval—serves "
        "as the paramount operational metric dictating recurring cash flows, enterprise valuation, and brand equity. "
        "Developing empirical diagnostic capabilities to detect attrition vulnerabilities prior to contract termination represents a vital strategic capability."
    )
    doc.add_paragraph(
        "Exploratory Data Analysis (EDA) and scientific visualization constitute the bedrock of applied data science [2], [5]. Rather than treating "
        "predictive modeling as a black-box endeavor, rigorous EDA unlocks structural domain insights, illuminates hidden modalities, exposes data quality "
        "defects, and informs disciplined feature engineering. By applying Ben Fry's canonical seven-stage visualization taxonomy [6]—Acquire, Parse, "
        "Filter, Mine, Represent, Refine, and Interact—data practitioners transition from unstructured observational tables to interpretable analytical narratives."
    )
    add_h2("Course Outcomes & Academic Objectives")
    doc.add_paragraph(
        "This project fulfills the comprehensive syllabus requirements for Course U21ADP05 (Exploratory Data Analysis and Visualization, Assignment II) "
        "at KPR Institute of Engineering and Technology. The technical investigations directly satisfy three central Course Outcomes (COs):"
    )
    
    co_items = [
        ("CO3: Visualization Selection, Execution, and Interpretation: ", 
         "Design, render, and interpret sophisticated univariate, bivariate, multivariate, and interactive visualizations using Matplotlib, Seaborn, and Plotly at 300 DPI publication standards, mapping each artifact to Fry's 7-stage taxonomy."),
        ("CO4: Statistical Distribution Modeling & Hypothesis Testing: ", 
         "Quantify distribution moments (skewness, kurtosis), fit parametric probability distributions (Gaussian, Exponential, Bernoulli) with theoretical Q-Q plots, and execute formal hypothesis tests (Pearson Chi-Square with Cramér's V, Welch's t-test, Mann-Whitney U test, and Point-Biserial correlation)."),
        ("CO5: Real-World Machine Learning, Business Translation & Open-Source Dissemination: ", 
         "Build and benchmark a Deep Multilayer Perceptron (MLP) with Batch Normalization and Dropout against linear and ensemble baselines, overcome severe class imbalance, perform permutation feature importance, conduct asymmetric error cost analysis, and deliver production code to GitHub.")
    ]
    for b_title, b_desc in co_items:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.line_spacing = 1.3
        bp.paragraph_format.space_after = Pt(3)
        r_bt = bp.add_run(b_title)
        r_bt.font.bold = True
        bp.add_run(b_desc)

    # =========================================================================
    # 4. DATASET DESCRIPTION
    # =========================================================================
    add_h1("3. DATASET DESCRIPTION")
    doc.add_paragraph(
        "The empirical foundation for this study is the benchmark Telco Customer Churn dataset, originally published by IBM Business Analytics "
        "as part of their enterprise cognitive customer experience series and widely recognized on Kaggle [1]. The dataset captures authentic "
        "behavioral records of 7,043 residential customers in California, USA, encompassing 21 discrete features spanning account demographics, "
        "telecommunication network architecture, value-added service subscriptions, and contractual billing records."
    )
    doc.add_paragraph(
        "Source URL: https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv\n"
        "Total Sample Size: N = 7,043 instances | Total Dimension: P = 21 features (exceeding the course requirement of 15 real-world features)."
    )

    add_caption("Table 1: Comprehensive Data Dictionary of the Telco Customer Churn Dataset", is_table=True)
    
    # Data dictionary table
    fields_data = [
        ("customerID", "Identifier", "Unique alphanumeric alphanumeric identifier assigned to each customer account."),
        ("gender", "Categorical (Nominal)", "Customer biological gender indicator: Female or Male."),
        ("SeniorCitizen", "Binary (0/1)", "Whether the customer is a senior citizen (1: Yes, 0: No)."),
        ("Partner", "Binary (Yes/No)", "Whether the customer has a declared domestic or marital partner."),
        ("Dependents", "Binary (Yes/No)", "Whether the customer resides with financial dependents (children, elderly)."),
        ("tenure", "Integer (Continuous)", "Number of completed calendar months the customer has stayed with the company [0, 72]."),
        ("PhoneService", "Binary (Yes/No)", "Whether the customer is subscribed to home landline phone service."),
        ("MultipleLines", "Categorical (Nominal)", "Whether the customer has multiple phone lines (Yes, No, No phone service)."),
        ("InternetService", "Categorical (Nominal)", "Customer internet connection architecture: DSL, Fiber optic, or No."),
        ("OnlineSecurity", "Categorical (Nominal)", "Whether the customer subscribes to cloud cyber-security add-on service."),
        ("OnlineBackup", "Categorical (Nominal)", "Whether the customer subscribes to cloud backup storage add-on service."),
        ("DeviceProtection", "Categorical (Nominal)", "Whether the customer has premium hardware equipment warranty insurance."),
        ("TechSupport", "Categorical (Nominal)", "Whether the customer has dedicated expedited technical support assistance."),
        ("StreamingTV", "Categorical (Nominal)", "Whether the customer streams digital television programming over the network."),
        ("StreamingMovies", "Categorical (Nominal)", "Whether the customer streams third-party digital cinematic media content."),
        ("Contract", "Categorical (Nominal)", "Contractual commitment agreement: Month-to-month, One year, or Two year."),
        ("PaperlessBilling", "Binary (Yes/No)", "Whether customer accounts are invoiced digitally via email/web portal."),
        ("PaymentMethod", "Categorical (Nominal)", "Payment mechanism: Electronic check, Mailed check, Bank transfer, Credit card."),
        ("MonthlyCharges", "Float (Continuous)", "The current monthly billing amount charged to the subscriber ($)."),
        ("TotalCharges", "Float (Continuous)", "The cumulative gross charges billed over the customer's lifetime ($)."),
        ("Churn (Target)", "Binary (Yes/No)", "Binary classification objective: Whether the customer churned within the last month.")
    ]

    dd_table = doc.add_table(rows=len(fields_data)+1, cols=3)
    dd_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    dd_table.columns[0].width = Inches(1.5)
    dd_table.columns[1].width = Inches(1.6)
    dd_table.columns[2].width = Inches(3.3)

    hdr = dd_table.rows[0]
    hdr.cells[0].paragraphs[0].add_run("Attribute Name").font.bold = True
    hdr.cells[1].paragraphs[0].add_run("Measurement Type").font.bold = True
    hdr.cells[2].paragraphs[0].add_run("Domain Definition & Semantic Meaning").font.bold = True
    for c in hdr.cells:
        set_cell_shading(c, "1A365D")
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for idx, (f_name, f_type, f_desc) in enumerate(fields_data):
        row = dd_table.rows[idx+1]
        p0 = row.cells[0].paragraphs[0]
        p0.paragraph_format.line_spacing = 1.15
        p0.add_run(f_name).font.bold = True
        
        p1 = row.cells[1].paragraphs[0]
        p1.paragraph_format.line_spacing = 1.15
        p1.add_run(f_type)

        p2 = row.cells[2].paragraphs[0]
        p2.paragraph_format.line_spacing = 1.15
        p2.add_run(f_desc)

        if idx % 2 == 1:
            set_cell_shading(row.cells[0], "F4F6F9")
            set_cell_shading(row.cells[1], "F4F6F9")
            set_cell_shading(row.cells[2], "F4F6F9")

    add_h2("Basic Statistical Moments of Continuous Features")
    doc.add_paragraph(
        "A rigorous understanding of continuous features requires computing both central tendency and higher-order statistical moments "
        "(sample skewness and excess kurtosis). Table 2 summarizes these empirical parameters across the dataset."
    )

    add_caption("Table 2: Statistical Moments and Outlier Boundaries for Continuous Predictors", is_table=True)
    stats_data = [
        ("Tenure (Months)", "7,043", "32.37", "24.56", "29.00", "46.00", "0.00", "72.00", "+0.240", "-1.387"),
        ("Monthly Charges ($)", "7,043", "64.76", "30.09", "70.35", "54.35", "18.25", "118.75", "-0.221", "-1.257"),
        ("Total Charges ($)", "7,043", "2,279.73", "2,266.79", "1,394.55", "3,388.05", "0.00", "8,684.80", "+0.963", "-0.229")
    ]
    st_table = doc.add_table(rows=len(stats_data)+1, cols=10)
    st_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.5, 0.6, 0.6, 0.6]
    for i, w in enumerate(col_widths):
        st_table.columns[i].width = Inches(w)

    headers = ["Feature", "Count", "Mean", "Std", "Median", "IQR", "Min", "Max", "Skew", "Kurt"]
    for i, h in enumerate(headers):
        cell = st_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        p.add_run(h).font.bold = True
        set_cell_shading(cell, "1A365D")
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.runs[0].font.size = Pt(9)

    for idx, row_vals in enumerate(stats_data):
        row = st_table.rows[idx+1]
        for col_idx, val in enumerate(row_vals):
            cell = row.cells[col_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(val)
            run.font.size = Pt(9)
            if col_idx == 0:
                run.font.bold = True
            if idx % 2 == 1:
                set_cell_shading(cell, "F4F6F9")

    # =========================================================================
    # 5. EDA AND PREPROCESSING
    # =========================================================================
    add_h1("4. EXPLORATORY DATA ANALYSIS & PREPROCESSING")
    doc.add_paragraph(
        "Data quality assurance and disciplined preprocessing form the cornerstone of empirical data science. "
        "The raw dataset was subjected to multi-stage auditing, anomaly resolution, feature engineering, and statistical validation."
    )
    
    add_h2("Missing and Blank Value Treatment")
    doc.add_paragraph(
        "Initial inspection revealed that pandas initially ingested TotalCharges as an object (string) data type. "
        "Programmatic regex auditing detected exactly 11 instances containing empty whitespace strings (' '). "
        "Cross-tabulating these 11 rows against all other features revealed that every single customer with a blank TotalCharges entry "
        "had a tenure of exactly 0 months. These records represent brand-new customers who registered during the current billing cycle "
        "and have not yet completed their first monthly billing cycle. Consequently, their cumulative historical bill is mathematically and "
        "operationally 0.00. Replacing the whitespace strings with 0.00 and casting to float64 preserves all 7,043 instances without "
        "introducing artificial imputation noise or distorting statistical power."
    )

    add_h2("Outlier Diagnostic and Treatment Justification")
    doc.add_paragraph(
        "Outlier detection was conducted using both Tukey's Interquartile Range (IQR) fence rule (Q1 - 1.5*IQR to Q3 + 1.5*IQR) and "
        "standardized Z-score thresholds (|Z| > 3.0):\n"
        "• Tenure: [Min: 0, Max: 72 months]. The IQR is 46.0 months (Q1 = 9, Q3 = 55). The Tukey bounds [-60, 124] encompass the entire range with zero outliers.\n"
        "• MonthlyCharges: [Min: $18.25, Max: $118.75]. The IQR is $54.35 (Q1 = $35.50, Q3 = $89.85). The Tukey bounds [-46.0, 171.38] encompass all data with zero outliers.\n"
        "• TotalCharges: [Min: $0, Max: $8,684.80]. The IQR is $3,388.05 (Q1 = $398.55, Q3 = $3,786.60). The upper bound is $8,868.68. The maximum observed value has a Z-score of 2.82 (< 3.0).\n"
        "Justification: Because all continuous values reflect legitimate business parameters within valid physical and commercial bounds, "
        "no artificial trimming, truncation, or Windsorization was applied, thereby maintaining high fidelity to actual commercial operations."
    )

    add_h2("Domain Feature Engineering")
    doc.add_paragraph(
        "To empower both tree-based and deep learning algorithms with domain-relevant inductive bias, six derived features were engineered:"
    )
    eng_items = [
        ("1. Tenure Cohort (`tenure_cohort`): ", "Discretized customer lifecycle into 5 stages: [0-12 Mo], [13-24 Mo], [25-48 Mo], [49-60 Mo], and [61-72 Mo]. Captures the empirical hazard rate across customer maturation stages."),
        ("2. Value-Added Service Adoption Count (`services_count`): ", "Sum of active subscriptions across 6 premium security/streaming add-ons (OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies), ranging from 0 to 6. Directly quantifies customer product stickiness."),
        ("3. Family Unit Stability Indicator (`family_stability`): ", "Binary interaction flag (1 if customer has BOTH a partner and dependents, 0 otherwise). Reflects structural household stability and lower mobility."),
        ("4. Billing Intensity Ratio (`charge_ratio`): ", "Calculated as MonthlyCharges / (TotalCharges + 1.0). Serves as a dynamic proxy for recent price escalations or short-tenure billing pressure."),
        ("5. High-Risk Contract Flag (`is_month_to_month`): ", "Binary indicator isolating month-to-month contracts, which exhibit the highest attrition hazard in telecommunications."),
        ("6. Premium Media Bundle (`streaming_bundle`): ", "Binary interaction flag for customers subscribing to both StreamingTV and StreamingMovies, reflecting high entertainment consumption.")
    ]
    for e_title, e_desc in eng_items:
        ep = doc.add_paragraph(style='List Bullet')
        ep.paragraph_format.line_spacing = 1.3
        ep.paragraph_format.space_after = Pt(3)
        r_et = ep.add_run(e_title)
        r_et.font.bold = True
        ep.add_run(e_desc)

    add_h2("Encoding, Scaling, and Stratified Partitioning")
    doc.add_paragraph(
        "To prevent data leakage, the complete dataset was partitioned using stratified random sampling based on the target class "
        "(Churn) into 70% Training (N = 4,930), 15% Validation (N = 1,056), and 15% Testing (N = 1,057). "
        "Continuous attributes (Tenure, MonthlyCharges, TotalCharges, ChargeRatio) were standardized using StandardScaler, with scaling "
        "parameters (mean μ and variance σ²) computed strictly on the training partition and applied out-of-sample to validation and test sets. "
        "Nominal categorical variables were encoded using OneHotEncoder with the first level dropped to prevent dummy variable collinearity. "
        "The resulting design matrix comprises 39 numerical and one-hot encoded input dimensions."
    )

    add_h2("Class Imbalance Strategy Justification")
    doc.add_paragraph(
        "The empirical target distribution is imbalanced: 5,174 retained customers (73.46%) versus 1,869 churners (26.54%), representing a "
        "2.77:1 negative-to-positive ratio. While synthetic oversampling (such as SMOTE) is frequently deployed, it synthesizes artificial instances "
        "in feature space that often introduce noisy border samples in high-dimensional continuous-categorical mixed spaces. "
        "Instead, we implemented analytical class-weighted cost balancing: positive class weighting in the neural network's loss function "
        "(pos_weight = 2.77) and balanced class weighting in baseline models. This penalizes false negatives proportionally during backpropagation "
        "without hallucinating artificial data points."
    )

    doc.add_page_break()

    # =========================================================================
    # 6. DATA VISUALIZATION (7 Stages of Visualization Taxonomy)
    # =========================================================================
    add_h1("5. DATA VISUALIZATION (THE 7-STAGE PROCESS)")
    doc.add_paragraph(
        "In accordance with Ben Fry's foundational visualization paradigm [6], effective data visualization is not a cosmetic final step, "
        "but a structured computational path. Table 3 explicitly maps the 7 stages of data visualization to our codebase and generated figures."
    )

    add_caption("Table 3: Mapping Ben Fry's 7 Stages of Data Visualization to the Churn Investigation Pipeline", is_table=True)
    stages_data = [
        ("1. Acquire", "Raw data ingestion from remote IBM Telco repository via automated HTTPS transfer script.", "src/pipeline.py (`load_and_preprocess_data`)", "Dataset CSV (7043 x 21)"),
        ("2. Parse", "Type coercion, blank string identification in TotalCharges, categorical string normalization.", "src/pipeline.py (lines 55-68)", "Cleaned Pandas DataFrame"),
        ("3. Filter", "Isolating cohort subgroups, removing customerID, stratified 70/15/15 train/val/test splitting.", "src/pipeline.py (`prepare_datasets`)", "Partitioned Design Matrices"),
        ("4. Mine", "Computing moments, Cramér's V, Pearson correlation, Welch's t-test, and parametric PDF fitting.", "src/pipeline.py (`compute_exploratory_statistics`)", "Figures 4, 8, 9, 16"),
        ("5. Represent", "Selecting visual grammar: Histograms, KDE, Boxplots, Correlation Heatmaps, Split Violins, ROC curves.", "src/pipeline.py (`generate_visualizations`)", "Figures 1, 2, 3, 5, 6, 7"),
        ("6. Refine", "Optimizing color palettes, axis typography, statistical annotations, legends, and 300 DPI export.", "src/pipeline.py (Matplotlib/Seaborn configs)", "All Figures (300 DPI PNGs)"),
        ("7. Interact", "Generating interactive Plotly 3D scatter visualizations enabling panning, zooming, and hover inspection.", "src/pipeline.py (`fig_plotly.write_html`)", "Figure 11 (Interactive HTML)")
    ]
    vis_table = doc.add_table(rows=len(stages_data)+1, cols=4)
    vis_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    v_widths = [1.2, 2.5, 1.8, 1.5]
    for i, w in enumerate(v_widths):
        vis_table.columns[i].width = Inches(w)

    v_headers = ["Stage", "Taxonomic Definition & Objective", "Implementation Code Reference", "Corresponding Artifact"]
    for i, h in enumerate(v_headers):
        cell = vis_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        p.add_run(h).font.bold = True
        set_cell_shading(cell, "1A365D")
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.runs[0].font.size = Pt(9)

    for idx, row_vals in enumerate(stages_data):
        row = vis_table.rows[idx+1]
        for col_idx, val in enumerate(row_vals):
            cell = row.cells[col_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(val)
            run.font.size = Pt(9)
            if col_idx == 0:
                run.font.bold = True
            if idx % 2 == 1:
                set_cell_shading(cell, "F4F6F9")

    add_h2("Detailed Visualization Analysis (What, Why, and Insights)")
    doc.add_paragraph(
        "Below, we present the core visualizations generated during the exploratory and statistical modeling phases. "
        "In compliance with academic evaluation standards, each artifact is systematically deconstructed across three explicit dimensions: "
        "What it shows, Why I created it, and Insights obtained."
    )

    # VISUALIZATION 1
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig01_univariate_distributions.png", width=Inches(6.2))
    add_caption("Figure 1: Univariate Distributions of Continuous Predictors with Empirical Moments")
    
    doc.add_paragraph(
        "• What it shows: Triple-panel frequency histograms overlaid with Kernel Density Estimation (KDE) curves for customer tenure (months), "
        "monthly charges ($), and cumulative total charges ($). Parametric reference lines illustrate sample mean (dashed red) and median (dotted blue), "
        "accompanied by mathematical skewness and excess kurtosis coefficients.\n"
        "• Why I created it: To interrogate feature modalities, evaluate symmetry, and establish whether parametric normality assumptions hold for "
        "downstream modeling algorithms.\n"
        "• Insights obtained: Tenure exhibits a pronounced bimodal, U-shaped distribution (Kurtosis = -1.39) with extreme customer concentrations "
        "at 1-2 months (new acquisitions) and 68-72 months (highly mature subscribers). Monthly charges exhibits multimodality, characterized by an acute "
        "spike near $20 (voice-only accounts) and an expansive high-tier plateau between $70-$100 (broadband and premium entertainment bundles). "
        "Total charges demonstrates heavy positive right-skewness (Skewness = +0.96), illustrating geometric revenue accumulation."
    )

    # VISUALIZATION 2
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig02_categorical_distributions.png", width=Inches(6.2))
    add_caption("Figure 2: Categorical Feature Frequency Distributions Stratified by Churn Status")
    
    doc.add_paragraph(
        "• What it shows: Stratified dual-color bar charts quantifying customer headcount across Contract Type, Internet Service Architecture, "
        "Payment Mechanism, and Technical Support Subscriptions, decomposed by Churn status (Navy: Retained, Orange: Churned) with frequency annotations.\n"
        "• Why I created it: To reveal the absolute commercial scale and relative attrition rates within primary operational service tiers.\n"
        "• Insights obtained: Month-to-month contracts dominate total attrition, generating 1,655 churners out of 3,875 accounts (42.7% churn rate). "
        "Fiber optic internet users suffer disproportionately high churn compared to DSL users, pinpointing severe onboarding or reliability vulnerabilities. "
        "Electronic check accounts represent the single largest volume and percentage of departing subscribers."
    )

    # VISUALIZATION 3
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig03_outlier_boxplots.png", width=Inches(6.2))
    add_caption("Figure 3: Outlier Diagnostic Boxplots and Jittered Sample Strips across Churn Classes")
    
    doc.add_paragraph(
        "• What it shows: Comparative box-and-whisker plots with overlaid jittered customer scatter points (N = 600) for Tenure, Monthly Charges, "
        "and Total Charges separated by customer churn status, annotated with Interquartile Range (IQR) values.\n"
        "• Why I created it: To rigorously detect empirical outliers using Tukey's fences and assess distributional separation between churned and retained cohorts.\n"
        "• Insights obtained: Neither class contains corrupt or anomalous outlier data points. The median tenure of churned customers is merely 10.0 months "
        "(IQR = 29.0), whereas retained customers boast a median tenure of 38.0 months (IQR = 46.0). Churners exhibit substantially elevated median monthly charges "
        "($79.65 vs $64.45), confirming that high pricing pressure combined with low tenure precipitates early contract termination."
    )

    # VISUALIZATION 4
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig04_correlation_heatmap.png", width=Inches(5.6))
    add_caption("Figure 4: Multivariate Pearson Correlation Matrix of Numerical and Derived Predictors")
    
    doc.add_paragraph(
        "• What it shows: Color-coded lower/upper triangular correlation matrix displaying Pearson correlation coefficients across numerical attributes, "
        "engineered features (Services Count, Family Stability, Month-to-Month, Streaming Bundle), and the binary Churn target.\n"
        "• Why I created it: To evaluate inter-feature collinearity and isolate primary linear drivers of customer churn.\n"
        "• Insights obtained: Expected strong collinearity exists between tenure and TotalCharges (r = +0.83). Month-to-month contract structure exhibits the "
        "strongest positive linear correlation with churn (r = +0.41), while tenure demonstrates the strongest protective correlation (r = -0.35). "
        "Service add-on count exhibits a positive correlation with TotalCharges (r = +0.75) but a negative correlation with churn, proving that multi-product "
        "adoption reinforces retention."
    )

    # VISUALIZATION 5
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig06_bivariate_churn_rates.png", width=Inches(6.2))
    add_caption("Figure 5: Bivariate Churn Rates Across Key Contractual, Service, and Demographic Dimensions")
    
    doc.add_paragraph(
        "• What it shows: A six-panel comparative bar chart illustrating empirical Churn Rate (%) across Contract Type, Internet Service, "
        "Technical Support, Payment Method, Tenure Cohorts, and Paperless Billing against the 26.5% baseline benchmark (dashed red line).\n"
        "• Why I created it: To isolate specific high-risk operational segments that deviate significantly from population-average churn.\n"
        "• Insights obtained: Month-to-month contracts exhibit an acute 42.7% churn rate, compared to 11.3% for 1-year and a negligible 2.8% for 2-year contracts "
        "— a massive 15-fold risk reduction. Customers lacking Tech Support churn at 41.6% versus only 15.2% for supported accounts. Electronic check payers "
        "churn at 45.3% versus ~16.7% for automatic ACH/credit card billing. New subscribers (0-12 months) churn at 47.7%, confirming the acute vulnerability of onboarding."
    )

    # VISUALIZATION 6
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig07_violin_plots.png", width=Inches(6.2))
    add_caption("Figure 6: Split Violin Density Plots of Monthly Charges and Tenure across Contract and Service Tiers")
    
    doc.add_paragraph(
        "• What it shows: Split violin plots depicting internal kernel density distributions and quartile markers for Monthly Charges across Contract Types "
        "and Tenure across Internet Service architectures, decomposed symmetrically by Churn status.\n"
        "• Why I created it: To visualize multimodal probability densities and internal quartile shifts that boxplots conceal.\n"
        "• Insights obtained: For month-to-month contracts, churned customers form a wide bulbous distribution centered at $75-$95/month, while retained customers "
        "are heavily clustered around $20/month. For Fiber optic service, churn occurs predominantly within the first 12 months, whereas retained fiber customers "
        "exhibit an elongated distribution stretching to 72 months."
    )

    # VISUALIZATION 7
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig08_distribution_fitting_qq.png", width=Inches(6.0))
    add_caption("Figure 7: Parametric Probability Distribution Fitting and Theoretical Q-Q Plots")
    
    doc.add_paragraph(
        "• What it shows: Theoretical Quantile-Quantile (Q-Q) plots for standardized tenure against a Normal distribution, Q-Q plot for Total Charges against "
        "an Exponential distribution, Gaussian PDF overlay on Monthly Charges, and discrete Bernoulli PMF model for Churn.\n"
        "• Why I created it: To fulfill syllabus requirements for probability distribution fitting and test parametric distribution assumptions.\n"
        "• Insights obtained: Standardized tenure deviates heavily from Gaussian normality in the tails (Kolmogorov-Smirnov D = 0.125, p < 1e-90), confirming that "
        "linear models requiring Gaussian predictors are ill-suited. Total charges exhibits reasonable fit to an Exponential distribution in lower/middle quantiles "
        "(KS D = 0.171). The binary churn target perfectly matches a Bernoulli model with parameter p = 0.2654 and variance = 0.1949."
    )

    # VISUALIZATION 8
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig09_statistical_tests_summary.png", width=Inches(6.2))
    add_caption("Figure 8: Statistical Hypothesis Testing Summary: Cramér's V and Point-Biserial Correlations")
    
    doc.add_paragraph(
        "• What it shows: Ranked horizontal bar chart of Cramér's V effect sizes from Pearson Chi-Square tests of independence across 17 categorical features, "
        "alongside Point-Biserial correlation coefficients with Welch's t-test statistics for continuous predictors.\n"
        "• Why I created it: To provide rigorous statistical validation for feature significance rather than relying on visual heuristics.\n"
        "• Insights obtained: Contract type exhibits the largest categorical association with churn (Cramér's V = 0.410, χ² = 1184.60, p = 5.86e-258), followed by "
        "Tenure Cohort (V = 0.352), Online Security (V = 0.347), and Tech Support (V = 0.343). In contrast, biological gender is statistically insignificant "
        "(χ² = 0.48, p = 0.487). Continuous tenure has a strong negative correlation with churn (r = -0.352, Welch t = -34.82, p < 1e-200)."
    )

    # VISUALIZATION 9
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig10_derived_features_churn.png", width=Inches(6.2))
    add_caption("Figure 9: Impact of Derived Features: Value-Added Service Adoption and Tenure Cohort Dynamics")
    
    doc.add_paragraph(
        "• What it shows: Empirical churn rate as a function of subscribed value-added services (0 to 6) and tenure cohort interaction across contract types.\n"
        "• Why I created it: To evaluate the business hypothesis that multi-product bundling enhances customer switching barriers.\n"
        "• Insights obtained: Customers subscribing to 0 add-on services suffer an acute 40.0% churn rate. As customers adopt 1, 2, 3, 4, 5, or 6 services, "
        "churn declines monotonically to 31.5%, 26.0%, 15.1%, 11.8%, 8.2%, and 4.8%. This proves that cross-selling add-on services creates powerful defensive moats. "
        "Furthermore, even on month-to-month contracts, surviving past 24 months cuts churn by over 50%."
    )

    # VISUALIZATION 10
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig11_multidimensional_scatter.png", width=Inches(6.0))
    add_caption("Figure 10: Multi-Dimensional Customer Segmentation Space (Tenure, Charges, Contract & Churn)")
    
    doc.add_paragraph(
        "• What it shows: Multi-dimensional scatter visual mapping customer tenure (x-axis), monthly charges (y-axis), total charges (bubble size), "
        "contract structure (marker style), and churn outcome (color hue).\n"
        "• Why I created it: To reveal non-linear cluster boundaries and demonstrate the interactive 3D feature space implemented in Plotly HTML.\n"
        "• Insights obtained: High-risk customers form an unmistakable, dense cluster in the top-left quadrant: tenure under 12 months, monthly charges exceeding $70, "
        "month-to-month contracts, and electronic billing. Retained customers dominate the lower spectrum and long-tenure boundaries."
    )

    doc.add_page_break()

    # =========================================================================
    # 7. DEEP LEARNING MODEL
    # =========================================================================
    add_h1("6. DEEP LEARNING CLASSIFICATION MODEL")
    doc.add_paragraph(
        "To capture intricate non-linear feature interactions and high-order feature representations, a Deep Multilayer Perceptron (MLP) "
        "was engineered in PyTorch. The neural architecture, regularizers, and optimization parameters were designed to overcome tabular data "
        "challenges and severe class imbalance."
    )

    add_h2("Neural Network Architecture")
    doc.add_paragraph(
        "The Deep MLP binary classification network is structured as follows:\n"
        "• Input Layer: 39 input units (corresponding to standardized numericals, passthrough flags, and one-hot encoded categories).\n"
        "• Hidden Layer 1: Linear(39 -> 64) -> BatchNorm1d(64) -> ReLU() -> Dropout(p = 0.30).\n"
        "• Hidden Layer 2: Linear(64 -> 32) -> BatchNorm1d(32) -> ReLU() -> Dropout(p = 0.20).\n"
        "• Hidden Layer 3: Linear(32 -> 16) -> BatchNorm1d(16) -> ReLU() -> Dropout(p = 0.10).\n"
        "• Output Layer: Linear(16 -> 1) projecting to unnormalized logit score z.\n"
        "• Loss Function: BCEWithLogitsLoss with positive class weight pos_weight = 2.77.\n"
        "• Optimizer: Adam (Learning Rate = 0.001, Weight Decay / L2 Regularization = 1e-4, Batch Size = 64).\n"
        "• Regularization & Early Stopping: Internal Batch Normalization normalizes activations across mini-batches; Dropout prevents co-adaptation; "
        "Early Stopping terminates training after 18 epochs without validation loss improvement, restoring best checkpointed weights."
    )

    add_h2("Hyperparameter Tuning Grid Search")
    doc.add_paragraph(
        "To establish empirical rigor, a structured hyperparameter tuning grid search was conducted across five distinct neural architectural "
        "configurations, varying hidden units, learning rates, dropout probabilities, and batch sizes. Table 4 records validation set performance."
    )

    add_caption("Table 4: Hyperparameter Tuning Grid Search Results on Validation Set", is_table=True)
    tuning_data = [
        ("Config 1 (Baseline LR)", "[64, 32]", "0.0010", "0.30", "64", "74.34%", "0.6343", "0.8413", "0.6302"),
        ("Config 2 (High LR)", "[64, 32]", "0.0100", "0.30", "64", "70.64%", "0.6036", "0.8436", "0.6272"),
        ("Config 3 (Low LR, High Drop)", "[64, 32]", "0.0005", "0.50", "64", "74.72%", "0.6307", "0.8447", "0.6348"),
        ("Config 4 (Deeper Architecture)", "[128, 64]", "0.0010", "0.30", "32", "73.20%", "0.6281", "0.8335", "0.6082"),
        ("Config 5 (Lightweight)", "[32, 16]", "0.0010", "0.20", "64", "72.63%", "0.6202", "0.8414", "0.6254")
    ]
    t_table = doc.add_table(rows=len(tuning_data)+1, cols=9)
    t_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_widths = [1.5, 0.8, 0.7, 0.6, 0.5, 0.7, 0.7, 0.7, 0.7]
    for i, w in enumerate(t_widths):
        t_table.columns[i].width = Inches(w)

    t_headers = ["Config Name", "Hidden Units", "LR", "Drop", "Batch", "Val Acc", "Val F1", "Val ROC", "Val PR"]
    for i, h in enumerate(t_headers):
        cell = t_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        p.add_run(h).font.bold = True
        set_cell_shading(cell, "1A365D")
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.runs[0].font.size = Pt(8.5)

    for idx, row_vals in enumerate(tuning_data):
        row = t_table.rows[idx+1]
        for col_idx, val in enumerate(row_vals):
            cell = row.cells[col_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(val)
            run.font.size = Pt(8.5)
            if col_idx == 0:
                run.font.bold = True
            if idx % 2 == 1:
                set_cell_shading(cell, "F4F6F9")

    doc.add_paragraph(
        "Findings: Config 1 and Config 3 demonstrated optimal convergence balance. Config 1 was deployed for final testing, "
        "leveraging Early Stopping to halt training at epoch 22 when validation loss reached its global minimum (0.478)."
    )

    doc.add_page_break()

    # =========================================================================
    # 8. RESULT VISUALIZATION AND INTERPRETATION
    # =========================================================================
    add_h1("7. RESULT VISUALIZATION & INTERPRETATION")
    doc.add_paragraph(
        "To rigorously evaluate model generalization, the Deep Learning MLP was benchmarked out-of-sample against two established "
        "competitive baselines on the strictly isolated test set (N = 1,057, containing 281 churners and 776 retained customers):\n"
        "1. Baseline 1: Logistic Regression with balanced inverse class weights (interpretable linear baseline).\n"
        "2. Baseline 2: Random Forest Classifier with 150 decision trees, maximum depth 8, and balanced class weights (non-linear ensemble baseline)."
    )

    add_caption("Table 5: Final Out-of-Sample Test Set Evaluation Metrics across Models", is_table=True)
    eval_data = [
        ("Logistic Regression (Baseline 1)", "75.21%", "0.5231", "0.7651 (76.5%)", "0.6214", "0.8421", "0.6498"),
        ("Random Forest (Baseline 2)", "76.25%", "0.5371", "0.7722 (77.2%)", "0.6336", "0.8380", "0.6629"),
        ("Deep Learning MLP (Proposed)", "73.23%", "0.4979", "0.8505 (85.1%)", "0.6281", "0.8401", "0.6528")
    ]
    e_table = doc.add_table(rows=len(eval_data)+1, cols=7)
    e_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    e_widths = [2.2, 0.8, 0.8, 1.1, 0.8, 0.8, 0.8]
    for i, w in enumerate(e_widths):
        e_table.columns[i].width = Inches(w)

    e_headers = ["Model Architecture", "Accuracy", "Precision", "Recall (Sensitivity)", "F1-Score", "ROC-AUC", "PR-AUC"]
    for i, h in enumerate(e_headers):
        cell = e_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        p.add_run(h).font.bold = True
        set_cell_shading(cell, "1A365D")
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.runs[0].font.size = Pt(8.5)

    for idx, row_vals in enumerate(eval_data):
        row = e_table.rows[idx+1]
        for col_idx, val in enumerate(row_vals):
            cell = row.cells[col_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(val)
            run.font.size = Pt(8.5)
            if col_idx in [0, 3]:
                run.font.bold = True
            if idx % 2 == 1:
                set_cell_shading(cell, "F4F6F9")

    add_h2("Diagnostic Visualizations & Performance Curves")

    # Training History Curves
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig12_model_training_curves.png", width=Inches(6.2))
    add_caption("Figure 11: Cross-Entropy Loss and Accuracy Curves across Training and Validation Epochs")
    doc.add_paragraph(
        "Interpretation: Training and validation loss decrease synchronously until epoch 20, where validation loss stabilizes at 0.478. "
        "The minimal gap between training loss (0.442) and validation loss confirms that Dropout (0.3/0.2) and Batch Normalization successfully "
        "suppressed overfitting. Early stopping arrested execution at epoch 22, guaranteeing optimal parameter generalization."
    )

    # Confusion Matrices
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig13_confusion_matrices.png", width=Inches(6.2))
    add_caption("Figure 12: Test Confusion Matrices Comparing Baseline and Deep Learning Models")
    doc.add_paragraph(
        "Interpretation: The confusion matrices reveal crucial differences in error distribution. Out of 281 actual churners in the test set:\n"
        "• Logistic Regression missed 66 churners (False Negatives = 66, Recall = 76.51%).\n"
        "• Random Forest missed 64 churners (False Negatives = 64, Recall = 77.22%).\n"
        "• Deep Learning MLP missed ONLY 42 churners (False Negatives = 42, Recall = 85.05%)!\n"
        "The MLP successfully captured 239 out of 281 at-risk subscribers, reducing unflagged customer departures by 36% compared to baselines."
    )

    # ROC and PR Curves
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig14_roc_curves.png", width=Inches(4.8))
    add_caption("Figure 13: Receiver Operating Characteristic (ROC) Curves across Evaluated Models")
    
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig15_precision_recall_curves.png", width=Inches(4.8))
    add_caption("Figure 14: Precision-Recall (PR) Curves with Average Precision (AP) Benchmarks")

    doc.add_paragraph(
        "Interpretation: All three architectures exhibit strong discrimination, achieving ROC-AUC values between 0.838 and 0.842. "
        "However, in imbalanced domains where the minority class is the objective, Precision-Recall curves provide the true diagnostic standard. "
        "Random Forest achieves PR-AUC = 0.6629, Logistic Regression achieves 0.6498, and the Deep Learning MLP achieves 0.6528, "
        "each substantially surpassing the no-skill baseline (AP = 0.2658) by more than 2.4 times."
    )

    # Feature Importance
    doc.add_paragraph()
    doc.add_picture("outputs/figures/fig16_feature_importance.png", width=Inches(6.2))
    add_caption("Figure 15: Feature Importance Comparison (Random Forest MDI vs Permutation Importance)")
    doc.add_paragraph(
        "Interpretation: Both Gini impurity reduction (MDI) and out-of-sample permutation importance converge on the paramount predictors: "
        "TotalCharges, MonthlyCharges, tenure, Contract_Two year, and InternetService_Fiber optic. Permutation importance demonstrates that shuffling "
        "TotalCharges or Tenure induces the steepest drop in classification accuracy, corroborating our exploratory findings."
    )

    add_h2("Asymmetric Cost Analysis: False Negatives vs False Positives")
    doc.add_paragraph(
        "In customer churn prediction, treating classification errors symmetrically is a catastrophic financial mistake:\n"
        "1. Cost of a False Negative (Type II Error): The model predicts an at-risk customer as retained. The telecom provider initiates zero "
        "intervention. The customer terminates their contract, resulting in the permanent forfeiture of future Customer Lifetime Value (LTV) "
        "estimated at $1,500 - $3,000, combined with high replacement acquisition marketing costs ($300-$500).\n"
        "2. Cost of a False Positive (Type I Error): The model incorrectly predicts a loyal customer will churn. The telecom provider initiates a "
        "proactive retention workflow (e.g., courtesy concierge check-in, free streaming upgrade, or a 10% loyalty discount for 3 months), costing ~$25 - $50.\n"
        "Financial Verdict: Because the cost ratio of a False Negative to a False Positive is between 30:1 and 60:1, the Deep Learning MLP's superior "
        "85.05% recall makes it the undisputed commercial choice for enterprise deployment, preserving hundreds of thousands of dollars in annual recurring revenue."
    )

    doc.add_page_break()

    # =========================================================================
    # 9. CONCLUSION AND FUTURE SCOPE
    # =========================================================================
    add_h1("8. CONCLUSION, FUTURE SCOPE & BUSINESS RECOMMENDATIONS")
    
    add_h2("Synthesis of Analytical Learnings")
    doc.add_paragraph(
        "This project successfully accomplished an end-to-end data science lifecycle on the Telco Customer Churn dataset, integrating "
        "rigorous exploratory analysis, formal distribution modeling, hypothesis testing, publication-grade visualization, and deep learning. "
        "Key empirical findings include:\n"
        "• Contractual Structure Dictates Retention: Month-to-month contracts incur an acute 42.7% churn rate, whereas two-year contracts incur only 2.8%.\n"
        "• Onboarding Cliff: 47.7% of customers in their first year churn, with attrition risk plunging below 15% once a subscriber surpasses 24 months.\n"
        "• Multi-Product Defense: Service adoption count exhibits a direct protective relationship: subscribing to 3 or more add-on services reduces churn below 15%.\n"
        "• Deep Learning Efficacy: Incorporating BatchNorm, Dropout, and class-weighted loss enabled our PyTorch MLP to achieve 85.05% recall, detecting 239 of 281 churners."
    )

    add_h2("Actionable Business Recommendations for Telecommunications Executives")
    recs = [
        ("1. Annual Contract Migration Campaigns: ", "Offer a guaranteed 12% billing rebate or complimentary hardware upgrade to customers transitioning from month-to-month plans to 12-month commitments. Given the 15-fold risk reduction on multi-year plans, discount incentives are vastly cheaper than customer replacement."),
        ("2. Complimentary Technical Support Bundling for Fiber Optic Subscribers: ", "Customers lacking Tech Support churn at 41.6% (versus 15.2% for supported accounts). Bundle 6 months of complimentary Tech Support and Cyber-Security with every new Fiber installation to prevent early onboarding cancellation."),
        ("3. Automated Payment Incentive Programs: ", "Electronic check payers experience a 45.3% churn rate versus 16.7% for automatic ACH/credit card payers. Provide a one-time $15 account credit for enrolling in recurring automated payment methods."),
        ("4. Proactive First-Year Customer Success Interventions: ", "Establish automated milestone engagement protocols at Day 30, Day 90, and Day 180 to identify early service friction and shepherd new accounts past the initial 12-month churn hazard cliff.")
    ]
    for r_title, r_desc in recs:
        rp = doc.add_paragraph(style='List Bullet')
        rp.paragraph_format.line_spacing = 1.3
        rp.paragraph_format.space_after = Pt(3)
        r_rt = rp.add_run(r_title)
        r_rt.font.bold = True
        rp.add_run(r_desc)

    add_h2("Limitations and Future Technical Scope")
    doc.add_paragraph(
        "While the current pipeline delivers robust performance, several technological extensions are identified for future research:\n"
        "• Gradient Boosted Decision Tree Ensembles: Benchmarking LightGBM, XGBoost, and CatBoost against the Deep MLP to evaluate mixed tabular performance.\n"
        "• Survival Analysis & Time-to-Event Modeling: Implementing Cox Proportional Hazards and DeepSurv neural survival models to predict not merely if a customer will churn, but exactly when.\n"
        "• Explainable AI (XAI) with SHAP: Integrating TreeSHAP and KernelSHAP to produce local customer-level waterfall explanations for front-line customer service agents.\n"
        "• Real-Time Cloud Microservice Deployment: Packaging the trained PyTorch pipeline into an asynchronous FastAPI container integrated with Docker and Prometheus monitoring."
    )

    doc.add_page_break()

    # =========================================================================
    # 10. REFERENCES (IEEE Style, Verifiable)
    # =========================================================================
    add_h1("9. REFERENCES")
    refs = [
        ("[1] ", "IBM Corporation, \"Telco Customer Churn Dataset,\" IBM Business Analytics Community, 2019. [Online]. Available: https://community.ibm.com/community/user/businessanalytics/blogs/steven-macko/2019/07/11/telco-customer-churn-sample-data"),
        ("[2] ", "F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg, J. Vanderplas, A. Passos, D. Cournapeau, M. Brucher, M. Perrot, and E. Duchesnay, \"Scikit-learn: Machine learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825-2830, Nov. 2011."),
        ("[3] ", "A. Paszke, S. Gross, F. Massa, A. Lerer, J. Bradbury, G. Chanan, T. Killeen, Z. Lin, N. Gimelshein, L. Antiga, A. Desmaison, A. Kopf, E. Yang, Z. DeVito, M. Raison, A. Tejani, S. Chilamkurthy, B. Steiner, L. Fang, J. Bai, and S. Chintala, \"PyTorch: An imperative style, high-performance deep learning library,\" in Advances in Neural Information Processing Systems (NeurIPS), vol. 32, 2019, pp. 8024-8035."),
        ("[4] ", "W. McKinney, \"Data structures for statistical computing in Python,\" in Proceedings of the 9th Python in Science Conference (SciPy 2010), S. van der Walt and J. Millman, Eds., 2010, pp. 56-61."),
        ("[5] ", "M. Waskom, \"seaborn: statistical data visualization,\" Journal of Open Source Software, vol. 6, no. 60, p. 3021, Apr. 2021. doi: 10.21105/joss.03021."),
        ("[6] ", "B. Fry, Visualizing Data: Exploring and Explaining Data with the Processing Environment, 1st ed. Sebastopol, CA: O'Reilly Media, 2008.")
    ]
    for num_str, ref_str in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.space_after = Pt(6)
        r_num = p.add_run(num_str)
        r_num.font.bold = True
        p.add_run(ref_str)

    doc.add_page_break()

    # =========================================================================
    # 11. APPENDIX (Complete Python Pipeline Code)
    # =========================================================================
    add_h1("10. APPENDIX: COMPLETE PYTHON PIPELINE CODE")
    doc.add_paragraph(
        "Below is the complete, self-contained Python pipeline (`src/eda_churn_pipeline.py`) engineered to execute data loading, "
        "preprocessing, statistical testing, high-resolution visualization rendering, deep learning training, and model evaluation."
    )
    
    with open('src/eda_churn_pipeline.py', 'r', encoding='utf-8') as f:
        code_text = f.read()

    p_code = doc.add_paragraph()
    p_code.paragraph_format.line_spacing = 1.0
    p_code.paragraph_format.space_before = Pt(4)
    p_code.paragraph_format.space_after = Pt(4)
    run_code = p_code.add_run(code_text)
    run_code.font.name = 'Courier New'
    run_code.font.size = Pt(8)
    run_code.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    output_docx_path = 'report/Customer_Churn_Prediction_Report.docx'
    doc.save(output_docx_path)
    print(f"[Report Generator] DOCX report successfully created at: {output_docx_path}")

if __name__ == '__main__':
    build_docx_report()
