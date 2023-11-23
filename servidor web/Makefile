run:
	python index.py

clean:
	rm -rf myenv
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "flask_session" -exec rm -rf {} \;
	find . -name "__pycache__" -exec rm -rf {} \;
	find . -name ".DS_Store" -exec rm -f {} \;
	find . -name "*.log" -exec rm -f {} \;