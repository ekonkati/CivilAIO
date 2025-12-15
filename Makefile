.PHONY: install lint test run

install:
pip install -r requirements.txt

lint:
python -m compileall app

test:
pytest -q

run:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
