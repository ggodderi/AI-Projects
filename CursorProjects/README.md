# Space Invaders (Pygame)

A Python/Pygame implementation of Space Invaders.

## Requirements
- Python 3.11+
- Pygame 2.5+
- Pytest (for tests)

## Setup

Install dependencies (choose one):

**Option 1: Install globally (no virtual environment needed)**
```bash
pip install -r requirements.txt
```

**Option 2: Use virtual environment (optional, recommended)**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Test (Headless on Windows)
```bash
pytest -q
```

## Optional Features Included
- High scores (local JSON)
- Settings menu (config JSON)
- Controller support (optional; if detected)
