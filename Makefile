.PHONY: validate check-links generate dev all

validate:
	python scripts/validate_papers.py

check-links:
	python scripts/check_links.py

generate:
	python scripts/generate_html.py

dev: generate
	python -m http.server 8080

all: validate check-links generate
