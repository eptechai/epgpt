OUT_DIR := ./generated

apply: ${OUT_DIR}/helmchart
	terraform apply

${OUT_DIR}/helmchart:
	@mkdir -p ${OUT_DIR}
	cp -r ../../0_helmchart ${OUT_DIR}/helmchart

.phony: ${OUT_DIR}/helmchart apply