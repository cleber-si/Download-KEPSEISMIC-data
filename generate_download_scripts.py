import re
import requests
import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

BASE_URL       = "https://archive.stsci.edu/prepds/kepseismic/"
DOWNLOAD_DIR   = "download_files"
ROOT_DATA_DIR  = "KEP_DATA"

# Find the “0000xxxxx” links on the main page
GROUP_PATTERN  = re.compile(r"^\d{4}xxxxx$")
# Extract 9-digit KIC ID and filter width (e.g. “20”) from the filename
KIC_FILTER_RE  = re.compile(r".*kplr(\d{9})-(\d+)d_.*\.fits$", re.IGNORECASE)

def get_id_pages():
    resp = requests.get(BASE_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    anchors = soup.find_all("a", string=GROUP_PATTERN)
    urls = [urljoin(BASE_URL, a["href"]) for a in anchors]
    print(f">> Found {len(urls)} group pages")
    return urls

def get_fits_links(page_url):
    resp = requests.get(page_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    fits = []
    for a in soup.find_all("a", href=True):
        if a["href"].lower().endswith(".fits"):
            fits.append(urljoin(page_url, a["href"]))
    return fits

def make_per_group_scripts():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(ROOT_DATA_DIR,   exist_ok=True)

    id_pages = get_id_pages()
    total    = len(id_pages)

    for idx, page_url in enumerate(id_pages, start=1):
        # Derive group_id from the URL, e.g. “000700000” from “…/000700000.html”
        basename = os.path.basename(urlparse(page_url).path)
        group_id = os.path.splitext(basename)[0]

        print(f"[{idx}/{total}] Scanning group {group_id} …", end="", flush=True)
        fits_urls = get_fits_links(page_url)
        print(f" found {len(fits_urls)} files")

        # Path to this group's download script
        script_path = os.path.join(DOWNLOAD_DIR, f"{group_id}.sh")
        with open(script_path, "w") as fh:
            fh.write("#!/bin/bash\n\n")
            fh.write(f'ROOT="{ROOT_DATA_DIR}"\n\n')
            fh.write(f'echo "Downloading {len(fits_urls)} files for group {group_id}..."\n\n')

            for url in fits_urls:
                # Extract filename and parse out kicid + filter
                fname = os.path.basename(urlparse(url).path)
                m = KIC_FILTER_RE.match(fname)
                if m:
                    kicid, filt = m.groups()
                    subdir = f"{kicid}/{filt}d-filter"
                else:
                    # fallback if unexpected name
                    subdir = f"unknown/{fname}"

                # full local directory for this file
                local_dir = f'$ROOT/{group_id}/{subdir}'
                fh.write(f'mkdir -p "{local_dir}"\n')
                fh.write(f'wget -c -P "{local_dir}" "{url}"\n\n')

            fh.write(f'echo "Done with group {group_id}"\n')

        os.chmod(script_path, 0o755)
        print(f"    → Wrote script: {script_path}")

    print(f"\nAll done! Check '{DOWNLOAD_DIR}/' for your per-group scripts.")

if __name__ == "__main__":
    make_per_group_scripts()
