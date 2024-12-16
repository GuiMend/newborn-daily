install:
	@echo "===> Installing..."
	@pip install -r requirements.txt
	@echo "===> Done."

run:
	@echo "===> Running..."
	@fastapi dev app/main.py

update_requirements:
	@echo "===> Updating requirements.txt with 'pip freeze' content..."
	@pip freeze > requirements.txt
	@echo "===> Done."
