SHELL := /bin/bash

.PHONY: smoke
smoke:
	@chmod +x scripts/smoke.sh
	@API_BASE?=http://127.0.0.1:8000
	@echo "Running smoke against $${API_BASE}"
	@API_BASE=$${API_BASE} ./scripts/smoke.sh


