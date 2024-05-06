.PHONY: create-env
create-env: ## Build the docker image.
	conda create --name chatbot python=3.11.3

.PHONY: install-deps
install-deps: ## Build the docker image.
	pip install -r requirements.txt

.PHONY: run-in
run-in:
	streamlit run main.py