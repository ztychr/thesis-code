# thesis-code


## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements
pre-commit install-hooks
cp .env.example .env
```

## Generate Files
```bash
cd utils
python gen_files.py <path>
```

## Run Server
```bash
cd server/
flask run
```
