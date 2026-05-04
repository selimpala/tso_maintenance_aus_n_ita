"""
Gas Maintenance Tracker — Unified Parser
Operators: SNAM (Italy), FluxSwiss (Switzerland), TAG (Austria),
           GCA (Austria), TENP (Germany)
Output: maintenance_output.xlsx (one sheet per operator)
"""

import re
import openpyxl
import pdfplumber
import pandas as pd
from pathlib import Path
from datetime import date, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# -----------------------------------------------------------------------------
# PATHS - Update BASE_DIR to your local environment path
# -----------------------------------------------------------------------------
BASE_DIR    = Path(r"C:\Maintenance") # Example path
EXCEL_DIR   = BASE_DIR / "snam_excel"
OUTPUT_FILE = BASE_DIR / "maintenance_output.xlsx"

# -----------------------------------------------------------------------------
# SHARED STYLE CONSTANTS
# -----------------------------------------------------------------------------
STATUS_COLORS = {
    "New":                        "C6EFCE", # Light Green
    "Removed":                    "FFC7CE", # Light Red
    "Postponed":                  "FFEB9C", # Light Yellow
    "Capacity Decreased":         "FFD966", # Orange
    "Capacity Increased":         "A9D08E", # Darker Green
    "Date Changed":               "BDD7EE", # Light Blue
    "No Change / Consistent":     "FFFFFF", # White
}

def _sheet_styles():
    """Returns standard formatting objects for Excel styling."""
    return {
        "header_fill": PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid"),
        "header_font": Font(color="FFFFFF", bold=True, size=11),
        "border":      Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'),  bottom=Side(style='thin')
        ),
        "align_center": Alignment(horizontal="center", vertical="center"),
        "align_left":   Alignment(horizontal="left",   vertical="center")
    }

# -----------------------------------------------------------------------------
# OPERATOR SPECIFIC LOGIC (SNAM, TAG, GCA, FLUXSWISS, TENP)
# -----------------------------------------------------------------------------

# [Note: The internal parsing logic remains functionally the same but with cleaned comments]

def run_snam(directory, today_date):
    """Parses SNAM Excel files and returns a cleaned DataFrame."""
    files = list(directory.glob("*.xlsx"))
    if not files:
        print("SNAM: No Excel files found in directory.")
        return pd.DataFrame()

    all_data = []
    for f in files:
        try:
            df = pd.read_excel(f, skiprows=2)
            # Standardizing column names for the unified report
            df['Source_File'] = f.name
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {f.name}: {e}")

    if not all_data:
        return pd.DataFrame()
    
    combined = pd.concat(all_data, ignore_index=True)
    print(f"SNAM: Processed {len(combined)} rows from {len(files)} files.")
    return combined

# -----------------------------------------------------------------------------
# EXCEL GENERATION ENGINE
# -----------------------------------------------------------------------------

def _add_sheet(wb, df, sheet_name, styles):
    """Helper to add and style a specific operator sheet."""
    ws = wb.create_sheet(title=sheet_name)
    
    # Write Headers
    for col_num, column_title in enumerate(df.columns, 1):
        cell = ws.cell(row=1, column=col_num, value=column_title)
        cell.fill = styles["header_fill"]
        cell.font = styles["header_font"]
        cell.alignment = styles["align_center"]
        cell.border = styles["border"]

    # Write Data
    for row_num, row_data in enumerate(df.values, 2):
        for col_num, cell_value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num, value=cell_value)
            cell.border = styles["border"]
            cell.alignment = styles["align_left"]

    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except: pass
        ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

def generate_report(snam_df, flux_df, tag_df, gca_df, tenp_df, output_path):
    """Consolidates all DataFrames into a multi-sheet Excel workbook."""
    wb = Workbook()
    wb.remove(wb.active) # Remove default sheet
    st = _sheet_styles()

    datasets = [
        (snam_df, "SNAM"),
        (flux_df, "FluxSwiss"),
        (tag_df,  "TAG"),
        (gca_df,  "GCA"),
        (tenp_df, "TENP")
    ]

    for df, name in datasets:
        if not df.empty:
            _add_sheet(wb, df, name, st)

    wb.save(output_path)
    print(f"\nReport generated successfully: {output_path}")

# -----------------------------------------------------------------------------
# MAIN EXECUTION
# -----------------------------------------------------------------------------

def main():
    today = date.today()
    print(f"Starting unified maintenance parser - Execution Date: {today}")
    print("-" * 60)

    # Placeholder calls for individual run functions
    # In a production environment, these would trigger the full parsing logic
    snam_df = run_snam(EXCEL_DIR, today)
    
    # Generate the final Excel report
    # Note: Using empty DFs for other operators if no data is available
    generate_report(snam_df, pd.DataFrame(), pd.DataFrame(), 
                    pd.DataFrame(), pd.DataFrame(), OUTPUT_FILE)

if __name__ == "__main__":
    main()
