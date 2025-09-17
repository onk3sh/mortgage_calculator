"""
Configuration loader for mortgage calculator
Loads configuration from environment variables via .env files
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment files
config_dir = Path(__file__).parent / "config"
base_env_file = config_dir / "base.env"
scenario_env_file = config_dir / "mortgage.env"

# Load base configuration first
if base_env_file.exists():
    load_dotenv(base_env_file)
    print(f"Loaded base configuration from: {base_env_file}")
else:
    print(f"Warning: Base configuration file not found at {base_env_file}")

# Load scenario-specific configuration (overrides base values)
if scenario_env_file.exists():
    load_dotenv(scenario_env_file, override=True)
    print(f"Loaded scenario configuration from: {scenario_env_file}")
else:
    print(f"Warning: Scenario configuration file not found at {scenario_env_file}")
    print("Using base configuration only")

def get_bool(env_var, default=True):
    """Convert environment variable to boolean"""
    value = os.getenv(env_var, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_float(env_var, default=0.0):
    """Convert environment variable to float"""
    return float(os.getenv(env_var, default))

def get_int(env_var, default=0):
    """Convert environment variable to int"""
    return int(os.getenv(env_var, default))

def get_list(env_var, default=None):
    """Convert comma-separated environment variable to list of ints"""
    if default is None:
        default = []
    value = os.getenv(env_var, "")
    if not value:
        return default
    return [int(x.strip()) for x in value.split(',') if x.strip()]

# -----------------------------
# Loan Parameters
# -----------------------------
LOAN_AMOUNT = get_int('LOAN_AMOUNT', 672000)
AMORTIZATION_YEARS = get_int('AMORTIZATION_YEARS', 30)
HORIZON_YEARS = get_int('HORIZON_YEARS', 3)

# -----------------------------
# Fixed Mortgage Parameters
# -----------------------------
FIXED_INITIAL_RATE = get_float('FIXED_INITIAL_RATE', 0.0389)
FIXED_TERM_YEARS = get_int('FIXED_TERM_YEARS', 3)
FIXED_RENEWAL_RATE = get_float('FIXED_RENEWAL_RATE', 0.032)

# -----------------------------
# Variable Mortgage Parameters
# -----------------------------
PRIME_RATE = get_float('PRIME_RATE', 0.0495)
VARIABLE_DISCOUNT_INITIAL = get_float('VARIABLE_DISCOUNT_INITIAL', 0.0085)
VARIABLE_TERM_YEARS = get_int('VARIABLE_TERM_YEARS', 5)
VARIABLE_RENEWAL_DISCOUNT = get_float('VARIABLE_RENEWAL_DISCOUNT', 0.0050)
VARIABLE_FIXED_PAYMENT = get_bool('VARIABLE_FIXED_PAYMENT', True)

# -----------------------------
# Rate Cut Scenarios
# -----------------------------
USE_RATE_CUTS = get_bool('USE_RATE_CUTS', True)
RATE_CUT_AMOUNT = get_float('RATE_CUT_AMOUNT', 0.0025)
CUT_SCHEDULE = get_list('CUT_SCHEDULE', [6, 12, 18, 24])

# -----------------------------
# Split Mortgage Configuration
# -----------------------------
SPLIT_RATIO = get_float('SPLIT_RATIO', 0.5)

# -----------------------------
# Export Settings
# -----------------------------
EXPORT_TO_CSV = get_bool('EXPORT_TO_CSV', True)
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'mortgage_analysis_output')