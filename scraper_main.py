#[cite: 2]
import requests
from bs4 import BeautifulSoup
import json
import os
import re
import io
import shutil
from datetime import datetime
import pypdf

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
DATA_FILE   = "maintenance_data.json"       # Current execution data
BACKUP_FILE = "maintenance_data_prev.json"  # Previous execution data

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# -----------------------------------------------------------------------------
# DATA STORAGE
# -----------------------------------------------------------------------------

def load_previous_data():
    """
    Reads the data from the previous run for comparison.
    Falls back to the current DATA_FILE if no backup exists.
    """
    for path in [BACKUP_FILE, DATA_FILE]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}

def save_data(data):
    """
    Copies the existing DATA_FILE to BACKUP_FILE,
    then overwrites DATA_FILE with the new parsed data.
    This preserves state history for delta comparisons in the next run.
    """
    if os.path.exists(DATA_FILE):
        shutil.copy2(DATA_FILE, BACKUP_FILE)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -----------------------------------------------------------------------------
# SCRAPERS
# -----------------------------------------------------------------------------

def scrape_fluxys_ch():
    """
    Target string format: 'Updated on 06 February 2026'
    """
    url = "https://www.fluxys.com/en/natural-gas-and-biomethane/supplying-europe/switzerland/ch-maintenance"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    text = BeautifulSoup(r.text, "html.parser").get_text(separator=" ")
    match = re.search(r"[Uu]pdated\s+on\s+(\d{1,2}\s+\w+\s+\d{4})", text)
    if match:
        return match.group(1).strip()
    raise ValueError("Fluxys CH: 'Updated on' string not found.")

def scrape_fluxys_tenp():
    """
    Target string format: 'Last update of "Maintenance works 2026" overview: 11 February 2026'
    """
    url = "https://www.fluxys.com/en/natural-gas-and-biomethane/supplying-europe/germany/tenp-maintenance"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    text = BeautifulSoup(r.text, "html.parser").get_text(separator=" ")
    match = re.search(r"[Ll]ast\s+update\s+of.*?:\s*(\d{1,2}\s+\w+\s+\d{4})", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    raise ValueError("Fluxys TENP: 'Last update of' string not found.")

def scrape_snam():
    """
    Retrieves the operating plans file list from Snam AEM folderdocuments endpoint.
    Utilizes a timestamp parameter as a cache-buster to ensure fresh data.
    Logic: Tracks the sorted list of filenames to detect new document publications.
    """
    import time as _time
    timestamp = int(_time.time() * 1000)
    url = (
        "https://www.snam.it/content/snam/language-master/en/i-nostri-business/"
        "trasporto/informazioni-commerciali/piani-di-esercizio-e-interruzioni/"
        "jcr:content/root/responsivegrid/container_1434401628/"
        f"multi_file_download_.folderdocuments.json?language=en&timestamp={timestamp}"
    )
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()

    items = data.get("result", [])
    file_names = sorted(set(
        item["nameSingleDocument"]
        for item in items
        if item.get("nameSingleDocument")
    ))

    if not file_names:
        raise ValueError(f"Snam: Failed to retrieve file list from endpoint. URL: {url}")

    return file_names

def scrape_gasconnect():
    """
    Target string format: '(Last Update: 04.03.2026)'
    """
    url = "https://www.gasconnect.at/en/network-information/network-development/maintenance"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    text = BeautifulSoup(r.text, "html.parser").get_text(separator=" ")
    match = re.search(r"[Ll]ast\s+[Uu]pdate[:\s]+(\d{2}\.\d{2}\.\d{4})", text)
    if match:
        return match.group(1).strip()
    raise ValueError("Gasconnect: 'Last Update' string not found.")

def scrape_tag_pdf():
    """
    Extracts the publication/creation/modification date from the PDF metadata.
    If metadata is missing, it scans the raw text of the first page.
    """
    url = "https://www.taggmbh.at/wp-content/uploads/Maintenance_PROD_PDF.pdf"
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()

    reader = pypdf.PdfReader(io.BytesIO(r.content))
    meta = reader.metadata or {}

    for key in ["/CreationDate", "/ModDate", "/PublicationDate", "/pubdate", "/Date"]:
        val = meta.get(key)
        if val:
            return str(val).strip()

    try:
        first_page_text = reader.pages[0].extract_text() or ""
        match = re.search(
            r"(?:publication\s+date|published|date)[:\s]+(\d{1,2}[.\/\-]\d{1,2}[.\/\-]\d{2,4}|\w+\s+\d{4})",
            first_page_text,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).strip()
    except Exception:
        pass

    raise ValueError("TAG PDF: Date information not found in metadata or first page text.")

# -----------------------------------------------------------------------------
# MAIN CONTROL FLOW
# -----------------------------------------------------------------------------

SCRAPERS = {
    "Fluxys CH":   scrape_fluxys_ch,
    "Fluxys TENP": scrape_fluxys_tenp,
    "Snam":        scrape_snam,
    "Gasconnect":  scrape_gasconnect,
    "TAG PDF":     scrape_tag_pdf,
}

def check_all():
    previous = load_previous_data()
    current  = {}
    changes  = []
    errors   = []

    print(f"\n{'='*50}")
    print(f"Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Comparison source: {'[BACKUP]' if os.path.exists(BACKUP_FILE) else '[CURRENT JSON]'}")
    print(f"{'='*50}\n")

    for name, scraper in SCRAPERS.items():
        try:
            value = scraper()
            current[name] = value
            old_value = previous.get(name)

            if old_value is None:
                print(f"[INITIAL RECORD] {name}: {value}")
            elif old_value != value:
                print(f"[CHANGE DETECTED] {name}")
                print(f"  Old: {old_value}")
                print(f"  New: {value}")
                changes.append({
                    "source": name,
                    "old":    old_value,
                    "new":    value,
                })
            else:
                print(f"[OK] {name}: {value}")

        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            errors.append({"source": name, "error": str(e)})
            # Preserve old value on error to prevent false changes on next successful run
            if name in previous:
                current[name] = previous[name]

    # Backup existing state, then commit new data
    save_data(current)

    print(f"\n{'='*50}")
    print(f"Summary: {len(changes)} changes, {len(errors)} errors")
    print(f"{'='*50}\n")

    if changes:
        print("Modified sources:")
        for c in changes:
            print(f"  - {c['source']}")
            print(f"      Old: {c['old']}")
            print(f"      New: {c['new']}")
        print()

    return changes, errors

if __name__ == "__main__":
    changes, errors = check_all()
