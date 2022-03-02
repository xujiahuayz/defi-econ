# DeFiEcon

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

## Git Large File Storage (Git LFS)

All files in [`data/`](data/) are stored with `lfs`.

To initialize Git LFS:

```
git lfs install
```

```
git lfs track data/**/*
```

To pull data files, use

```
git lfs pull
```


## Synchronize with the repo

Always pull latest code first

```zsh
git pull
```

Make changes locally, save. And then add, commit and push

```zsh
git add .
git commit -m "update message"
git push
```
