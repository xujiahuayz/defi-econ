# DeFi Economics

Clone this repository

```bash
git clone https://github.com/xujiahuayz/defi-econ.git
```

Navigate to the directory of the cloned repo

```bash
cd defi-econ
```

## Set up the repo

### Give execute permission to your script and then run `setup_repo.sh`

```
chmod +x setup_repo.sh
./setup_repo.sh
```

or follow the step-by-step instructions below

### Create a python virtual environment

- MacOS

```zsh
python3 -m venv venv
```

- Windows

```
python -m venv venv
```

### Activate the virtual environment

- MacOS

```zsh
. venv/bin/activate
```

- Windows (in Command Prompt, NOT Powershell)

```zsh
venv\Scripts\activate.bat
```

## Install the project in editable mode

```
pip install -e ".[dev]"
```

## Connect to a full node to fetch on-chain data

Connect to a full node using `ssh` with port forwarding flag `-L` on:

```zsh
ssh -L 8545:localhost:8545 satoshi.doc.ic.ac.uk
```

Assign URI value to `WEB3_PROVIDER_URI` in a new terminal:

```zsh
set -xg WEB3_PROVIDER_URI http://localhost:8545
```

---

## Import Data Folders

Please import the data folder `dominant_defi/data` from Dropbox (authorization required) to the project root path, and overwrite the current `data` folder on Github Repo.

## Run scripts



To trigger scripts, please run the following commands:

- First, create data folders

```zsh
mkdir data
cd data
mkdir data_compound
cd ..
```


- To fetch Uniswap data from the Uniswap V3 subgraph, run:
```zsh
python scripts/fetch_uni.py --start "YYYY-MM-DD" --end "YYYY-MM-DD
```


- run the following command to fetch defi-related data (coingecko code has been deprecated):
```zsh
python scripts/fetch_main.py --start "YYYY-MM-DD" --end "YYYY-MM-DD"
```


Notes: This script runs on a montly basis. This script will fetch defi-related data from the first day of the month specified by the --start to the end of the day of the month of specified by the --end. For example python scripts/fetch_main.py --start "2020-05-18" -- end "2023-01-31" will fetch the data from May 2020 to Jan 2023. Meanwhile, the script will automatically detect the unfinished fetching dates during the specified period. The data generated will be placed under ['data'](data)

- Second, run the following command to plot defi-related graphs:

```zsh
python scripts/plot_main.py --start "YYYY-MM-DD" --end "YYYY-MM-DD"
```

Notes: This script runs on a daily basis. This script will plot defi-related data from the date specified by the --start to the the day specified by the --end (different from fetch_main.py). For example python scripts/fetch_main.py --start "2020-05-18" -- end "2023-01-31" will plot the data from 2020-05-18 to 2023-01-31. The graphs generated will be placed under ['data/data_network'](data/data_network)

- Third, run the following command to generate results

```zsh
python scripts/result_main.py
```

Notes: This scripts will generate analytical graphs and tables based on existing data.
<!-- 
## Python Project Documentation

python project documentation is save in [`doc/`](doc/)

index html file as example [`doc/scripts/index.html`](doc/scripts/index.html)

To generate doc by `pdoc`:

```bash
pip install pdoc3
```

```bash
pdoc --html /your_scripts_path --output-dir ./doc
``` -->

<!-- ## Data Fetch Instructions

Guide in [`fetch_data_instruction.md`](fetch_data_instruction.md)

## Git Large File Storage (Git LFS)

All files in [`data/`](data/) are stored with `lfs`.

To initialize Git LFS:

```bash
git lfs install
```

```bash
git lfs track data/**/*
```

To pull data files, use

```bash
git lfs pull
```

## Synchronize with the repo

Always pull latest code first

```bash
git pull
```

Make changes locally, save. And then add, commit and push

```bash
git add [file-to-add]
git commit -m "update message"
git push
```

# Best practice

## Coding Style

We follow [PEP8](https://www.python.org/dev/peps/pep-0008/) coding format.
The most important rules above all:

1. Keep code lines length below 80 characters. Maximum 120. Long code lines are NOT readable.
1. We use snake_case to name function, variables. CamelCase for classes.
1. We make our code as DRY (Don't repeat yourself) as possible.
1. We give a description to classes, methods and functions.
1. Variables should be self explaining and just right long:
   - `implied_volatility` is preferred over `impl_v`
   - `implied_volatility` is preferred over `implied_volatility_from_broker_name`

## Do not

1. Do not place .py files at root level (besides setup.py)!
1. Do not upload big files > 100 MB.
1. Do not upload log files.
1. Do not declare constant variables in the MIDDLE of a function -->


