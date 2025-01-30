# Makefile for Obfuscation and Execution Checks

# ================================
# Variables
# ================================

# Parent directory
DATASET_DIR := dataset

# Subdirectories under the parent directory
ORIGINAL_DIR := $(DATASET_DIR)/codeforces
PYMINIFIER_DIR := $(DATASET_DIR)/codeforces_pyminifier
PYTHON_MINIFIER_DIR := $(DATASET_DIR)/codeforces_python_minifier
PYTHON_OBFUSCATOR_DIR := $(DATASET_DIR)/codeforces_python_obfuscator
INPUT_DIR := $(DATASET_DIR)/codeforces_input
OUTPUT_DIR := $(DATASET_DIR)/codeforces_output

# Define color codes for better readability
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Scripts
OBFUSCATE_SCRIPT := scripts/obfuscate_files.py
CHECK_SCRIPT := scripts/check_execution.py
COMPUTE_SCORE_SCRIPT := scripts/compute_score.py

.PHONY: all score setup obfuscate obfuscate_pyminifier obfuscate_python_minifier \
        obfuscate_python_obfuscator check_pyminifier check_python_minifier \
        check_python_obfuscator check clean obfuscate_new obfuscate_pyminifier_new \
        obfuscate_python_minifier_new obfuscate_python_obfuscator_new compute_score \
        compute_score_pyminifier compute_score_python_minifier compute_score_python_obfuscator

# ================================
# Main Commands
# ================================

## ---------------------------------------------------------------------------
## make all
##   1) Clean the necessary folders
##   2) Create the folders
##   3) Obfuscate the files
##   4) Check files
##   5) Clean the necessary folder
##   6) Create the folders
##   7) Obfuscate the files with the flags
##   8) Run the score
##   9) Clean the necessary folders
## ---------------------------------------------------------------------------
all:
	@echo "$(YELLOW)[1] Cleaning folders...$(NC)"
	$(MAKE) clean
	@echo "$(YELLOW)[2] Creating folders...$(NC)"
	$(MAKE) setup
	@echo "$(YELLOW)[3] Obfuscating files...$(NC)"
	$(MAKE) obfuscate
	@echo "$(YELLOW)[4] Checking obfuscated files...$(NC)"
	$(MAKE) check
	@echo "$(YELLOW)[5] Cleaning folders...$(NC)"
	$(MAKE) clean
	@echo "$(YELLOW)[6] Creating folders...$(NC)"
	$(MAKE) setup
	@echo "$(YELLOW)[7] Obfuscating files with flags...$(NC)"
	$(MAKE) obfuscate_new
	@echo "$(YELLOW)[8] Running the score...$(NC)"
	$(MAKE) compute_score
	@echo "$(YELLOW)[9] Cleaning folders...$(NC)"
	$(MAKE) clean
	@echo "$(GREEN)All tasks completed successfully.$(NC)"

## ---------------------------------------------------------------------------
## make score
##   5) Clean the necessary folder
##   6) Create the folders
##   7) Obfuscate the files with the flags
##   8) Run the score
##   9) Clean the necessary folders
## ---------------------------------------------------------------------------
score:
	@echo "$(YELLOW)[5] Cleaning folders...$(NC)"
	$(MAKE) clean
	@echo "$(YELLOW)[6] Creating folders...$(NC)"
	$(MAKE) setup
	@echo "$(YELLOW)[7] Obfuscating files with flags...$(NC)"
	$(MAKE) obfuscate_new
	@echo "$(YELLOW)[8] Running the score...$(NC)"
	$(MAKE) compute_score
	@echo "$(YELLOW)[9] Cleaning folders...$(NC)"
	$(MAKE) clean
	@echo "$(GREEN)Score routine completed successfully.$(NC)"

# ================================
# Setup Target
# ================================

setup:
	@echo "$(YELLOW)Setting up directories...$(NC)"
	@mkdir -p $(ORIGINAL_DIR) \
	           $(PYMINIFIER_DIR) \
	           $(PYTHON_MINIFIER_DIR) \
	           $(PYTHON_OBFUSCATOR_DIR) \
	           $(INPUT_DIR) \
	           $(OUTPUT_DIR)
	@echo "$(GREEN)All directories are set up.$(NC)"

# ================================
# Obfuscation Targets
# ================================

obfuscate: obfuscate_pyminifier obfuscate_python_minifier obfuscate_python_obfuscator
	@echo "$(GREEN)All obfuscation steps completed.$(NC)"

obfuscate_pyminifier:
	@echo "$(YELLOW)Running pyminifier obfuscation...$(NC)"
	python $(OBFUSCATE_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                          --obfuscated_folder $(PYMINIFIER_DIR) \
	                          --method pyminifier
	@echo "$(GREEN)pyminifier obfuscation done.$(NC)"

obfuscate_python_minifier:
	@echo "$(YELLOW)Running python_minifier obfuscation...$(NC)"
	python $(OBFUSCATE_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                          --obfuscated_folder $(PYTHON_MINIFIER_DIR) \
	                          --method python_minifier
	@echo "$(GREEN)python_minifier obfuscation done.$(NC)"

obfuscate_python_obfuscator:
	@echo "$(YELLOW)Running python_obfuscator obfuscation...$(NC)"
	python $(OBFUSCATE_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                          --obfuscated_folder $(PYTHON_OBFUSCATOR_DIR) \
	                          --method python_obfuscator
	@echo "$(GREEN)python_obfuscator obfuscation done.$(NC)"

# ================================
# Execution Check Targets
# ================================

check: check_pyminifier check_python_minifier check_python_obfuscator
	@echo "$(GREEN)All execution checks completed.$(NC)"

check_pyminifier:
	@echo "$(YELLOW)Running execution check for pyminifier...$(NC)"
	python $(CHECK_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                       --input_folder $(INPUT_DIR) \
	                       --output_folder $(OUTPUT_DIR) \
	                       --obfuscated_folder $(PYMINIFIER_DIR)
	@echo "$(GREEN)Execution check for pyminifier done.$(NC)"

check_python_minifier:
	@echo "$(YELLOW)Running execution check for python_minifier...$(NC)"
	python $(CHECK_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                       --input_folder $(INPUT_DIR) \
	                       --output_folder $(OUTPUT_DIR) \
	                       --obfuscated_folder $(PYTHON_MINIFIER_DIR)
	@echo "$(GREEN)Execution check for python_minifier done.$(NC)"

check_python_obfuscator:
	@echo "$(YELLOW)Running execution check for python_obfuscator...$(NC)"
	python $(CHECK_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                       --input_folder $(INPUT_DIR) \
	                       --output_folder $(OUTPUT_DIR) \
	                       --obfuscated_folder $(PYTHON_OBFUSCATOR_DIR)
	@echo "$(GREEN)Execution check for python_obfuscator done.$(NC)"

# ================================
# Clean Target
# ================================

clean:
	@echo "$(YELLOW)Cleaning up directories...$(NC)"
	@rm -rf $(PYMINIFIER_DIR) \
	        $(PYTHON_MINIFIER_DIR) \
	        $(PYTHON_OBFUSCATOR_DIR) \
	        dolos-* \
	        results* \
	        results/
	@echo "$(GREEN)Cleanup completed.$(NC)"


# ================================
# Obfuscation with Additional Flags
# ================================

obfuscate_new: obfuscate_pyminifier_new obfuscate_python_minifier_new obfuscate_python_obfuscator_new
	@echo "$(GREEN)All new obfuscation steps completed.$(NC)"

obfuscate_pyminifier_new:
	@echo "$(YELLOW)Running pyminifier obfuscation with additional flags...$(NC)"
	@mkdir -p $(PYMINIFIER_DIR)
	python $(OBFUSCATE_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                          --obfuscated_folder $(PYMINIFIER_DIR) \
	                          --method pyminifier \
	                          --include_original \
	                          --include_suffix
	@echo "$(GREEN)pyminifier obfuscation with additional flags done.$(NC)"

obfuscate_python_minifier_new:
	@echo "$(YELLOW)Running python_minifier obfuscation with additional flags...$(NC)"
	@mkdir -p $(PYTHON_MINIFIER_DIR)
	python $(OBFUSCATE_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                          --obfuscated_folder $(PYTHON_MINIFIER_DIR) \
	                          --method python_minifier \
	                          --include_original \
	                          --include_suffix
	@echo "$(GREEN)python_minifier obfuscation with additional flags done.$(NC)"

obfuscate_python_obfuscator_new:
	@echo "$(YELLOW)Running python_obfuscator obfuscation with additional flags...$(NC)"
	@mkdir -p $(PYTHON_OBFUSCATOR_DIR)
	python $(OBFUSCATE_SCRIPT) --original_folder $(ORIGINAL_DIR) \
	                          --obfuscated_folder $(PYTHON_OBFUSCATOR_DIR) \
	                          --method python_obfuscator \
	                          --include_original \
	                          --include_suffix
	@echo "$(GREEN)python_obfuscator obfuscation with additional flags done.$(NC)"

# ================================
# Compute Score
# ================================

compute_score: compute_score_pyminifier compute_score_python_minifier compute_score_python_obfuscator
	@echo "$(GREEN)All compute_score steps completed.$(NC)"

compute_score_pyminifier:
	@echo "$(YELLOW)Running compute_score for pyminifier...$(NC)"
	python $(COMPUTE_SCORE_SCRIPT) $(PYMINIFIER_DIR)
	@echo "$(GREEN)compute_score for pyminifier done.$(NC)"

compute_score_python_minifier:
	@echo "$(YELLOW)Running compute_score for python_minifier...$(NC)"
	python $(COMPUTE_SCORE_SCRIPT) $(PYTHON_MINIFIER_DIR)
	@echo "$(GREEN)compute_score for python_minifier done.$(NC)"

compute_score_python_obfuscator:
	@echo "$(YELLOW)Running compute_score for python_obfuscator...$(NC)"
	python $(COMPUTE_SCORE_SCRIPT) $(PYTHON_OBFUSCATOR_DIR)
	@echo "$(GREEN)compute_score for python_obfuscator done.$(NC)"
