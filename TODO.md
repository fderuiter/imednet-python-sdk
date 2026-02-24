# Specification Sheet Generator

This project aims to automate the creation of comprehensive specification sheets from iMednet Data Dictionary exports and Annotated Case Report Forms (ACRFs).

## Inputs
- `acrfs/`: Directory containing PDF files of ACRFs (Case Report Forms).
- `data-dictionary/`: Directory containing CSV exports from iMednet (`FORMS.csv`, `QUESTIONS.csv`, `CHOICES.csv`, `BUSINESS_LOGIC.csv`).
- `SRS/`: Directory containing an example Excel file (`Sample Reference Sheet`) which defines the desired output format.

## Outputs
- A single Excel workbook (`Specification_Sheet.xlsx`) containing:
    - Separate worksheets for each form.
    - Data populated from the Data Dictionary.
    - Formatting applied to match the `SRS` example.

## Implementation Plan

### Phase 1: Preparation & Setup
- [ ] **Dependency Management**:
    - [ ] Add `pdfplumber` or `pypdf` to `pyproject.toml` for PDF processing.
    - [ ] Ensure `pandas` and `openpyxl` are installed.
- [ ] **Input Verification**:
    - [ ] Locate `acrfs/` directory and verify PDF files exist.
    - [ ] Locate `data-dictionary/` directory and verify CSV files exist.
    - [ ] Locate `SRS/` directory and identify the example Excel file.
- [ ] **Schema Analysis**:
    - [ ] Inspect the SRS Excel file to identify required columns (e.g., Variable Name, Label, Type, Codelist, Logic).
    - [ ] Map Data Dictionary columns (`Variable Name`, `Label`, `Type`) to SRS columns.

### Phase 2: Data Ingestion
- [ ] **Load Data Dictionary**:
    - [ ] Read `FORMS.csv` to get form metadata (FormOID, FormName).
    - [ ] Read `QUESTIONS.csv` to get variable details (VariableOID, Label, Type).
    - [ ] Read `CHOICES.csv` to get codelists for categorical variables.
    - [ ] Read `BUSINESS_LOGIC.csv` (optional) for edit checks/skip logic.
- [ ] **Load ACRFs**:
    - [ ] Iterate through PDF files in `acrfs/`.
    - [ ] (Optional) Extract text/metadata from PDFs if needed to supplement Data Dictionary (e.g., Page Numbers, Section Headers).

### Phase 3: Data Processing
- [ ] **Merge Data**:
    - [ ] Join Questions with Forms on FormOID.
    - [ ] Join Choices with Questions on VariableOID.
    - [ ] Aggregate choices into a single string (e.g., "1=Yes, 2=No") if required by SRS.
- [ ] **Transform Data**:
    - [ ] Format Variable Types (e.g., map "Date/Time Precision" to "Date").
    - [ ] Clean labels/descriptions.
    - [ ] Format logic rules from `BUSINESS_LOGIC.csv` into readable text.

### Phase 4: Report Generation
- [ ] **Initialize Workbook**: Create a new Excel workbook using `openpyxl`.
- [ ] **Generate Sheets**:
    - [ ] For each Form in the Data Dictionary:
        - [ ] Create a new worksheet named after the Form (e.g., "AE", "DM").
        - [ ] Write the header row based on the SRS template.
        - [ ] Iterate through variables for that form and write data rows.
        - [ ] Populate columns: Variable Name, Label, Type, Length, Codelist, etc.
- [ ] **Apply Formatting**:
    - [ ] Match SRS styles:
        - [ ] Font (Family, Size, Bold headers).
        - [ ] Borders (Header borders, cell borders).
        - [ ] Background colors (Header fill).
        - [ ] Column widths (Auto-fit or fixed width).
        - [ ] Text wrapping/alignment.

### Phase 5: Verification & Delivery
- [ ] **Quality Check**:
    - [ ] Verify all forms are generated.
    - [ ] specific check for key variables (e.g., SubjectID).
    - [ ] Check formatting against `SRS/` example.
- [ ] **Review**:
    - [ ] Open the generated Excel file and manually inspect a few sheets.
