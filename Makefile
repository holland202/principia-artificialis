.PHONY: help synthetic real real-test clean report check index test notes

help:
	@echo "Principia Artificialis — Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  synthetic   — Run all synthetic demos (Notes #041, #042, #043)"
	@echo "  real        — Attempt real model evaluation (requires GPU/transformers)"
	@echo "  report      — Show last saved report"
	@echo "  clean       — Remove temporary files"
	@echo "  notes       — Run every note's reference script (as CI does)"
	@echo "  check       — Number audit: prose vs script output (note062)"
	@echo "  index       — Regenerate NOTES_INDEX.md"
	@echo "  test        — Governance suite (expect 33/33)"

synthetic:
	@echo "Running all synthetic demos..."
	python scripts/run_all_notes.py

real: synthetic
	@echo "Attempting real model evaluation..."
	python -c "from scripts.run_all_notes import run_real_if_available; print(run_real_if_available())"

real-test: real
	@echo "Real model test complete (if dependencies installed)."

report:
	@cat results/last_run_report.json 2>/dev/null || echo "No report found. Run 'make synthetic' first."

clean:
	rm -f results/last_run_report.json
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned."

# Added 2026-09-27. Until then every recipe line above lacked its tab, so `make` stopped at line 4
# ("missing separator") and none of the documented make targets had ever run.
notes:
	@for f in scripts/note*_reference.py; do echo "=== $$f"; case "$$f" in *note060*) python "$$f" --selftest ;; *note061*) python "$$f" . ;; *) python "$$f" ;; esac || exit 1; done

check:
	python scripts/check_numbers.py

index:
	python scripts/make_index.py

test:
	python sovereign_core/test_sovereign.py
