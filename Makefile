# ============================================================
#  E-Commerce Churn Prediction — Makefile de Automatización
#  Uso: make <target>
# ============================================================

PYTHON     := python
PIP        := pip
PYTEST     := pytest
BLACK      := black
ISORT      := isort
FLAKE8     := flake8
SRC_DIR    := src
TEST_DIR   := tests
PIPE_DIR   := pipelines

.DEFAULT_GOAL := help

# ─── AYUDA ────────────────────────────────────────────────────────────────────
.PHONY: help
help:  ## Muestra este mensaje de ayuda
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║   E-Commerce Churn Prediction — Comandos Disponibles        ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ─── INSTALACIÓN ──────────────────────────────────────────────────────────────
.PHONY: install
install:  ## Instala dependencias de producción
	$(PIP) install -r requirements.txt

.PHONY: install-dev
install-dev:  ## Instala dependencias de desarrollo + producción
	$(PIP) install -r requirements-dev.txt
	pre-commit install

.PHONY: create-dirs
create-dirs:  ## Crea directorios necesarios que pueden no existir
	mkdir -p data/raw data/interim data/processed/train_test_splits data/exports
	mkdir -p models/registry models/champion
	mkdir -p reports/figures/eda reports/figures/modeling reports/figures/shap
	mkdir -p logs

# ─── PIPELINE PRINCIPAL ───────────────────────────────────────────────────────
.PHONY: run
run:  ## Ejecuta el pipeline completo (EDA → Train → Export)
	$(PYTHON) $(PIPE_DIR)/run_full_pipeline.py

.PHONY: train
train:  ## Ejecuta solo el pipeline de entrenamiento
	$(PYTHON) $(PIPE_DIR)/run_training_pipeline.py

.PHONY: infer
infer:  ## Ejecuta solo inferencia con el modelo champion
	$(PYTHON) $(PIPE_DIR)/run_inference_pipeline.py

.PHONY: export
export:  ## Exporta resultados a Supabase y CSV
	$(PYTHON) $(PIPE_DIR)/run_export_pipeline.py

.PHONY: eda
eda:  ## Ejecuta pipeline de análisis exploratorio
	$(PYTHON) $(PIPE_DIR)/run_eda_pipeline.py

# ─── CALIDAD DE CÓDIGO ────────────────────────────────────────────────────────
.PHONY: format
format:  ## Aplica black + isort al código fuente
	$(BLACK) $(SRC_DIR)/ $(PIPE_DIR)/ --line-length=100
	$(ISORT) $(SRC_DIR)/ $(PIPE_DIR)/ --profile=black

.PHONY: lint
lint:  ## Verifica estilo de código con flake8
	$(FLAKE8) $(SRC_DIR)/ $(PIPE_DIR)/ --max-line-length=100 --extend-ignore=E203,W503

.PHONY: check
check: format lint  ## Formatea y verifica el código

# ─── TESTS ────────────────────────────────────────────────────────────────────
.PHONY: test
test:  ## Ejecuta todos los tests con cobertura
	$(PYTEST) $(TEST_DIR)/ -v --tb=short

.PHONY: test-unit
test-unit:  ## Ejecuta solo tests unitarios
	$(PYTEST) $(TEST_DIR)/unit/ -v -m unit

.PHONY: test-integration
test-integration:  ## Ejecuta solo tests de integración (requiere .env)
	$(PYTEST) $(TEST_DIR)/integration/ -v -m integration

.PHONY: test-data
test-data:  ## Ejecuta tests de calidad de datos
	$(PYTEST) $(TEST_DIR)/data_quality/ -v

.PHONY: coverage
coverage:  ## Genera reporte de cobertura HTML
	$(PYTEST) $(TEST_DIR)/ --cov=$(SRC_DIR) --cov-report=html:reports/coverage
	@echo "✅ Reporte en reports/coverage/index.html"

# ─── NOTEBOOKS ────────────────────────────────────────────────────────────────
.PHONY: notebooks
notebooks:  ## Ejecuta todos los notebooks secuencialmente
	jupyter nbconvert --to notebook --execute notebooks/01_eda.ipynb --output notebooks/01_eda.ipynb
	jupyter nbconvert --to notebook --execute notebooks/02_churn_definition.ipynb --output notebooks/02_churn_definition.ipynb
	jupyter nbconvert --to notebook --execute notebooks/03_feature_engineering.ipynb --output notebooks/03_feature_engineering.ipynb
	jupyter nbconvert --to notebook --execute notebooks/04_modeling_experiments.ipynb --output notebooks/04_modeling_experiments.ipynb
	jupyter nbconvert --to notebook --execute notebooks/05_shap_interpretability.ipynb --output notebooks/05_shap_interpretability.ipynb

.PHONY: export-reports
export-reports:  ## Exporta notebooks a HTML
	jupyter nbconvert --to html notebooks/*.ipynb --output-dir=reports/

# ─── DOCKER ───────────────────────────────────────────────────────────────────
.PHONY: docker-build
docker-build:  ## Construye la imagen Docker
	docker build -t churn-prediction:latest -f infra/environment/Dockerfile .

.PHONY: docker-run
docker-run:  ## Ejecuta el pipeline dentro de Docker
	docker run --env-file .env -v $(PWD)/data:/app/data -v $(PWD)/models:/app/models churn-prediction:latest

# ─── BASE DE DATOS ────────────────────────────────────────────────────────────
.PHONY: db-deploy
db-deploy:  ## Despliega el schema en Supabase
	$(PYTHON) -c "from src.export.schema_deployer import deploy_schema; deploy_schema()"

.PHONY: db-migrate
db-migrate:  ## Ejecuta migraciones SQL pendientes
	@echo "Ejecutando migraciones..."
	@for f in sql/migrations/*.sql; do echo "Migrando: $$f"; done

# ─── LIMPIEZA ─────────────────────────────────────────────────────────────────
.PHONY: clean
clean:  ## Elimina archivos temporales y cachés
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

.PHONY: clean-data
clean-data:  ## Elimina datos procesados (NO elimina raw/)
	rm -f data/interim/*.parquet
	rm -f data/processed/*.parquet
	rm -f data/processed/train_test_splits/*.parquet
	rm -f data/exports/*.csv
	@echo "⚠️  Datos procesados eliminados. Ejecuta 'make run' para regenerarlos."

.PHONY: clean-models
clean-models:  ## Elimina artefactos de modelos entrenados
	rm -f models/champion/*.pkl
	@echo "⚠️  Modelos champion eliminados. Ejecuta 'make train' para regenerarlos."

# ─── ESTADO ───────────────────────────────────────────────────────────────────
.PHONY: status
status:  ## Muestra el estado actual del pipeline
	@echo "=== Estado del Proyecto ==="
	@echo "Dataset raw: $$(ls -lh data/raw/*.csv 2>/dev/null | awk '{print $$5, $$9}' || echo 'NO ENCONTRADO')"
	@echo "Datos procesados: $$(ls data/processed/*.parquet 2>/dev/null | wc -l) archivos"
	@echo "Modelo champion: $$(ls models/champion/*.pkl 2>/dev/null || echo 'NO ENTRENADO')"
	@echo "Último log: $$(tail -1 logs/pipeline.log 2>/dev/null || echo 'Sin logs')"
