# European Gas Infrastructure Maintenance Tracker

An automated web scraping and state-monitoring pipeline designed to track maintenance schedule updates across critical European natural gas transmission system operators (TSOs). 

This tool is built for energy market analysts, traders, and data engineers who require real-time visibility into planned outages and capacity restrictions that impact pipeline flows and localized price spreads.

## Core Features

- **Automated Update Detection:** Queries target websites and endpoints, extracting internal timestamps and published dates to identify when new maintenance plans are released.
- **Delta Comparison Logic:** Maintains a local JSON state cache (`maintenance_data.json`)[cite: 3]. On every execution, it compares the freshly scraped data against the previous run to isolate and log only new changes.
- **Multi-Format Extraction:** Capable of scraping standard HTML text patterns, parsing dynamic JSON responses from hidden API endpoints (e.g., Snam's document management system), and extracting embedded metadata directly from PDF binaries (e.g., TAG GmbH).
- **Resilient Error Handling:** In the event of a connection timeout or DOM structural change, the script retains the last known good state for that specific operator, preventing cascade failures and false-positive delta alerts on subsequent runs.

## Monitored Operators

Currently, the script tracks maintenance publications for the following grids:
1. **Fluxys CH** (Transitgas pipeline in Switzerland)
2. **Fluxys TENP** (Trans Europa Naturgas Pipeline in Germany)
3. **Snam** (Italian network operating plans)
4. **Gas Connect Austria** (Austrian transmission system)
5. **TAG GmbH** (Trans Austria Gas pipeline)

## Installation

Ensure you have Python 3.8+ installed. Clone the repository and install the required dependencies[cite: 4]:

```bash
pip install -r requirements.txt
