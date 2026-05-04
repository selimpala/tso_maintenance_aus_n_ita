# European Gas Maintenance Unified Parser

This tool is a specialized data engineering utility designed to consolidate maintenance schedules from multiple European Transmission System Operators (TSOs) into a single, structured Excel report. 

It is particularly useful for fundamental analysts and gas traders who need to see a cross-border view of infrastructure constraints in a unified format.

## Supported Operators

The parser currently processes data (Excel or PDF depending on the source) from the following TSOs:
- **SNAM** (Italy)
- **FluxSwiss** (Switzerland)
- **TAG** (Austria)
- **Gas Connect Austria (GCA)** (Austria)
- **TENP** (Germany)

## Data Sources (Manual Download Links)

As some TSOs do not provide a direct machine-readable API for these files, you may need to manually download the latest maintenance schedules and place them in the configured `EXCEL_DIR` or `BASE_DIR`.

- **TAG GmbH (Austria):** [Maintenance Works](https://www.taggmbh.at/en/transmission-system/#wartungsarbeiten)
- **SNAM (Italy):** [Operating Interruption Plans](https://www.snam.it/en/our-businesses/transportation/business-information/operating-interruption-plans.html)
- **Fluxys CH (Switzerland):** [CH Maintenance](https://www.fluxys.com/en/natural-gas-and-biomethane/supplying-europe/switzerland/ch-maintenance)
- **Fluxys TENP (Germany):** [TENP Maintenance](https://www.fluxys.com/en/natural-gas-and-biomethane/supplying-europe/germany/tenp-maintenance)
- **Gas Connect Austria:** [Maintenance Schedule](https://www.gasconnect.at/en/network-information/network-development/maintenance)

## Requirements

- Python 3.8+
- `pandas`: For data manipulation.
- `openpyxl`: For advanced Excel writing and styling.
- `pdfplumber`: For extracting structured tables from PDF files.

Install dependencies via:
```bash
pip install pandas openpyxl pdfplumber
