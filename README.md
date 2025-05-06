# Kepler FITS Downloader

## Overview

This project automates the process of scraping the STScI `kepseismic` archive and generating shell scripts to download all available FITS files, organized by Kepler Input Catalog (KIC) group and filter. More information can be found in [here](https://archive.stsci.edu/prepds/kepseismic/#dataaccess).

## Prerequisites

* **Python 3.x**
* **pip** package manager
* Python libraries:

  * `requests`
  * `beautifulsoup4`

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Install dependencies**:

   ```bash
   pip install requests beautifulsoup4
   ```

## Project Structure

```
└── project_root/
    ├── generate_download_scripts.py   # Main Python script to create per-group .sh files
    ├── download_files/                # Generated shell scripts (one per KIC group)
    │   ├── 000700000.sh
    │   ├── 000800000.sh
    │   └── ...
    ├── run_all_downloads.sh           # Master script to run all per-group downloads
    ├── KEP_DATA/                      # Root folder where FITS files will be saved
    └── README.md                      # This documentation file
```

## Usage

1. **Generate per-group download scripts**:

   ```bash
   python generate_download_scripts.py
   ```

   This will create individual `*.sh` files inside the `download_files/` directory.

2. **(Optional) Review scripts**:
   Inspect any `download_files/<group_id>.sh` to confirm the download commands.

3. **Run the master download script**:

   ```bash
   chmod +x run_all_downloads.sh
   ./run_all_downloads.sh
   ```

   This executes each per-group script in sequence, downloading FITS files into `KEP_DATA/{group_id}/{kic_id}/{filter}d-filter/`.

   **Careful:** There are 161,961 unique KIC IDs in the dataset, which I estimate it sums ~859 GB of data.

## Directory Layout of Downloads

After running, `KEP_DATA/` will contain:

```
KEP_DATA/
└── <group_id>/
    └── <kic_id>/
        ├── 20d-filter/
        │   └── <filename>.fits
        ├── 55d-filter/
        │   └── <filename>.fits
        └── 80d-filter/
            └── <filename>.fits
```

## Customization

* **BASE\_URL**: Change the target URL in `generate_download_scripts.py` if the data source moves.
* **Filters**: The script recognizes `20`, `55`, and `80` day filters by default. Adjust `KIC_FILTER_RE` if new naming patterns appear.

## Contributing

Contributions, issues, and feature requests are welcome! Please open an issue or submit a pull request.

## License

This project is released under the [MIT License](LICENSE).
