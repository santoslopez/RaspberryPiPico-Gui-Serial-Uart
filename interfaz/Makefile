# Definir el nombre del entorno virtual
VENV_NAME = .venv

.PHONY: clean

run:
	python index.py

clean:
	@rm -rf $(VENV_NAME)
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "flask_session" -exec rm -rf {} \;
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -name "__pycache__" -exec rm -r {} +
	find . -name ".DS_Store" -exec rm -f {} \;
	find . -name "*.log" -exec rm -f {} \;