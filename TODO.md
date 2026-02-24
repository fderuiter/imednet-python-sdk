# Project Roadmap: Specification Sheet Generator

This document outlines the tasks required to automate the creation of a comprehensive specification sheet from iMednet Data Dictionary exports and aCRF PDFs.

## Phase 1: Preparation & Analysis
- [ ] **Locate Input Data**: Verify the existence and location of `acrfs/` (PDFs), `data-dictionary/` (CSVs), and `SRS/` (Sample Excel). *Currently missing in repo root.*
- [ ] **Analyze Data Dictionary**: Inspect the full CSV export to understand all available fields (Forms, Fields, Variables, Codelists).
- [ ] **Analyze aCRF PDFs**: Determine if text/metadata extraction from PDFs is feasible or if manual mapping is required.
    - [ ] Research Python PDF libraries (`pypdf`, `pdfplumber`) for extracting form names/page numbers.
- [ ] **Analyze Sample Specification Sheet**:
    - [ ] Open the sample Excel in `SRS/`.
    - [ ] Document the exact column structure, formatting rules (colors, fonts), and sheet organization.

## Phase 2: Implementation - Data Ingestion
- [ ] **Create Data Dictionary Parser**:
    - [ ] Implement a class to read `FORMS.csv`, `QUESTIONS.csv`, `CHOICES.csv`, etc.
    - [ ] Link variables to forms and choices to variables.
    - [ ] Handle edge cases (e.g., calculated fields, logic).
- [ ] **Create aCRF Processor**:
    - [ ] Implement a prototype to extract relevant info (e.g., Form Name, Page Number) from PDFs.
    - [ ] Map extracted info to the Data Dictionary forms.

## Phase 3: Implementation - Excel Generation
- [ ] **Setup Excel Writer**:
    - [ ] Initialize a new Excel workbook using `openpyxl` or `pandas` (with `xlsxwriter`).
- [ ] **Implement Formatting Logic**:
    - [ ] Create style definitions (headers, borders, alternating rows) matching the `SRS` sample.
- [ ] **Develop Sheet Generator**:
    - [ ] Write logic to create a separate sheet for each Form/aCRF.
    - [ ] Populate sheets with combined data from Data Dictionary and aCRF.

## Phase 4: Integration & CLI
- [ ] **Create CLI Command**:
    - [ ] Add a new command (e.g., `imednet spec-gen`) to the `imednet` CLI.
    - [ ] Arguments: `--dd-path`, `--acrf-path`, `--output`.
- [ ] **Orchestrate Workflow**:
    - [ ] Connect Ingestion -> Transformation -> Generation steps.

## Phase 5: Verification
- [ ] **Run on Sample Data**: Generate a spec sheet using the provided samples.
- [ ] **Compare with SRS**: Manually verify that the output matches the `SRS` sample in structure and content.
- [ ] **Refine**: Adjust formatting and logic as needed.
