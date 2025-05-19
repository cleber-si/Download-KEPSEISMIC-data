import re, requests, os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

BASE_URL       = "https://archive.stsci.edu/prepds/kepseismic/"
DOWNLOAD_DIR   = "download_files"
ROOT_DATA_DIR  = "KEP_DATA"

# Choose layout: 
#   "group"  → KEP_DATA/{group}/{kic}/{filter}d-filter
#   "filter" → KEP_DATA/{filter}d-filter/{kic}
LAYOUT = "filter"  

GROUP_PATTERN  = re.compile(r"^\d{4}xxxxx$")
KIC_FILTER_RE  = re.compile(r".*kplr(\d{9})-(\d+)d_.*\.fits$", re.IGNORECASE)

def get_id_pages():
    r = requests.get(BASE_URL); r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    anchors = soup.find_all("a", string=GROUP_PATTERN)
    urls = [urljoin(BASE_URL, a["href"]) for a in anchors]
    print(f">> Found {len(urls)} group pages")
    return urls

def get_fits_links(page_url):
    r = requests.get(page_url); r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    return [
        urljoin(page_url, a["href"])
        for a in soup.find_all("a", href=True)
        if a["href"].lower().endswith(".fits")
    ]

def make_per_group_scripts():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(ROOT_DATA_DIR,   exist_ok=True)
    id_pages = get_id_pages()

    for idx, page_url in enumerate(id_pages, start=1):
        group_id = os.path.splitext(os.path.basename(urlparse(page_url).path))[0]
        print(f"[{idx}/{len(id_pages)}] Scanning group {group_id} …", end="", flush=True)
        fits_urls = get_fits_links(page_url)
        print(f" found {len(fits_urls)} files")

        script = os.path.join(DOWNLOAD_DIR, f"{group_id}.sh")
        with open(script, "w") as fh:
            fh.write("#!/usr/bin/env bash\n\n")
            fh.write(f'ROOT="{ROOT_DATA_DIR}"\n\n')
            fh.write(f'echo "Downloading {len(fits_urls)} for group {group_id}..."\n\n')

            for url in fits_urls:
                fname = os.path.basename(urlparse(url).path)
                m = KIC_FILTER_RE.match(fname)
                if m:
                    kicid, filt = m.groups()
                else:
                    # fallback
                    kicid, filt = "unknown", "unknown"

                if LAYOUT == "group":
                    subpath = f"{group_id}/{kicid}/{filt}d-filter"
                else:  # filter-first
                    subpath = f"{filt}d-filter/{kicid}"

                fh.write(f'mkdir -p "$ROOT/{subpath}"\n')
                fh.write(f'wget -c -P "$ROOT/{subpath}" "{url}"\n\n')

            fh.write(f'echo "Done with group {group_id}"\n')

        os.chmod(script, 0o755)
        print(f"    → Wrote {script}")

    print(f"\nAll done! Scripts in '{DOWNLOAD_DIR}/' (layout={LAYOUT}).")

if __name__ == "__main__":
    make_per_group_scripts()
