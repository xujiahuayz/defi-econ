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

- iOS

```zsh
python3 -m venv venv
```

- Windows

```
python -m venv venv
```

### Activate the virtual environment

- iOS

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

Please import the data folder `dominant_defi/data` to the project root path, and overwrite the current `data` folder on Github Repo.

## Run scripts

a minimum viable example to fetch data from thegraph and print the result on the screen

```zsh
python scripts/thegraph.py
```

fetch compound historical data and save in [`data/data_compound`](data/data_compound)

```zsh
python scripts/fetch_compound_historical_data.py
```

## Python Project Documentation

python project documentation is save in [`doc/`](doc/)

index html file as example [`doc/scripts/index.html`](doc/scripts/index.html)

To generate doc by `pdoc`:

```bash
pip install pdoc3
```

```bash
pdoc --html /your_scripts_path --output-dir ./doc
```

## Data Fetch Instructions

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
1. Do not declare constant variables in the MIDDLE of a function
