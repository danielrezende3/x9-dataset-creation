# ========================================================
# Obfuscation Pipeline Makefile
# ========================================================
# Targets:
#   all          - Run full pipeline (setup, obfuscate, check, score)
#   setup        - Create directory structure
#   obfuscate*   - Run specific obfuscation methods
#   check*       - Verify execution consistency
#   score        - Clean & rerun pipeline with scoring
#   clean        - Remove generated artifacts
# ========================================================

# -------------------------------
# 1. Configuration
# -------------------------------
# Directory Structure
DATASET_DIR := dataset
ORIGINAL_DIR := $(DATASET_DIR)/codeforces
PYMINIFIER_DIR := $(DATASET_DIR)/codeforces_pyminifier
PYTHON_MINIFIER_DIR := $(DATASET_DIR)/codeforces_python_minifier
PYTHON_OBFUSCATOR_DIR := $(DATASET_DIR)/codeforces_python_obfuscator
INPUT_DIR := $(DATASET_DIR)/codeforces_input
OUTPUT_DIR := $(DATASET_DIR)/codeforces_output

# Script Paths
OBFUSCATE_SCRIPT := scripts/obfuscate_files.py
CHECK_SCRIPT := scripts/check_execution.py
COMPUTE_SCORE_SCRIPT := scripts/compute_score.py

# Terminal Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

# -------------------------------
# 2. Main Targets
# -------------------------------
.PHONY: all setup clean score

all: setup obfuscate check score
	@echo "$(GREEN)[√] Full pipeline completed$(NC)"

score: clean setup obfuscate_new compute_score
	@echo "$(GREEN)[√] Scoring pipeline completed$(NC)"

clean:
	@echo "$(YELLOW)[!] Cleaning artifacts...$(NC)"
	@rm -rf $(PYMINIFIER_DIR) $(PYTHON_MINIFIER_DIR) $(PYTHON_OBFUSCATOR_DIR)
	@echo "$(GREEN)[√] Cleanup complete$(NC)"

setup:
	@echo "$(YELLOW)[!] Initializing directories...$(NC)"
	@mkdir -p $(ORIGINAL_DIR) $(PYMINIFIER_DIR) $(PYTHON_MINIFIER_DIR) \
	           $(PYTHON_OBFUSCATOR_DIR) $(INPUT_DIR) $(OUTPUT_DIR)
	@echo "$(GREEN)[√] Directory structure ready$(NC)"

# -------------------------------
# 3. Obfuscation Targets
# -------------------------------
.PHONY: obfuscate obfuscate_new

obfuscate: obfuscate_pyminifier obfuscate_python_minifier obfuscate_python_obfuscator
	@echo "$(GREEN)[√] All obfuscations completed$(NC)"

obfuscate_new: obfuscate_pyminifier_new obfuscate_python_minifier_new obfuscate_python_obfuscator_new
	@echo "$(GREEN)[√] New obfuscation cycle completed$(NC)"

# Individual obfuscation methods
define OBFUSCATE_TEMPLATE
obfuscate_$(1):
	@echo "$(YELLOW)[!] Running $(2) obfuscation...$(NC)"
	@mkdir -p $(3)
	python $(OBFUSCATE_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                          --obfuscated_folder $(3) \
	                          --method $(2) \
	                          --include_original \
	                          --include_suffix
	@echo "$(GREEN)[√] $(2) obfuscation done$(NC)"
endef

$(eval $(call OBFUSCATE_TEMPLATE,pyminifier_new,pyminifier,$(PYMINIFIER_DIR)))
$(eval $(call OBFUSCATE_TEMPLATE,python_minifier_new,python_minifier,$(PYTHON_MINIFIER_DIR)))
$(eval $(call OBFUSCATE_TEMPLATE,python_obfuscator_new,python_obfuscator,$(PYTHON_OBFUSCATOR_DIR)))

# -------------------------------
# 4. Verification Targets
# -------------------------------
.PHONY: check compute_score

check: check_pyminifier check_python_minifier check_python_obfuscator
	@echo "$(GREEN)[√] All execution checks passed$(NC)"

compute_score: compute_score_pyminifier compute_score_python_minifier compute_score_python_obfuscator
	@echo "$(GREEN)[√] All scores computed$(NC)"

# Execution check template
define CHECK_TEMPLATE
check_$(1):
	@echo "$(YELLOW)[!] Verifying $(1)...$(NC)"
	python $(CHECK_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                      --input_folder $(INPUT_DIR) \
	                      --output_folder $(OUTPUT_DIR) \
	                      --obfuscated_folder $(2)
	@echo "$(GREEN)[√] $(1) verification done$(NC)"
endef

$(eval $(call CHECK_TEMPLATE,pyminifier,$(PYMINIFIER_DIR)))
$(eval $(call CHECK_TEMPLATE,python_minifier,$(PYTHON_MINIFIER_DIR)))
$(eval $(call CHECK_TEMPLATE,python_obfuscator,$(PYTHON_OBFUSCATOR_DIR)))

# Score computation template
define SCORE_TEMPLATE
compute_score_$(1):
	@echo "$(YELLOW)[!] Calculating $(1) scores...$(NC)"
	python $(COMPUTE_SCORE_SCRIPT) $(2)
	@echo "$(GREEN)[√] $(1) scores ready$(NC)"
endef

$(eval $(call SCORE_TEMPLATE,pyminifier,$(PYMINIFIER_DIR)))
$(eval $(call SCORE_TEMPLATE,python_minifier,$(PYTHON_MINIFIER_DIR)))
$(eval $(call SCORE_TEMPLATE,python_obfuscator,$(PYTHON_OBFUSCATOR_DIR)))