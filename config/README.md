# Mortgage Calculator Configuration

This folder contains configuration files for the mortgage calculator using a hierarchical configuration system with common base values and scenario-specific overrides.

## Configuration Structure

### Hierarchical Loading
1. **`base.env`**: Common configuration values (loan amount, rates, etc.)
2. **`mortgage.env`**: Scenario-specific overrides (rate cuts, output folder, etc.)

### Quick Start

1. **Choose a Scenario**: Copy one of the example files to `mortgage.env`
2. **Run Analysis**: Execute `python main.py` from the main directory
3. **Customize**: Edit `base.env` for common values or `mortgage.env` for scenario-specific values

## Configuration Files

### `base.env` (Base Configuration)
Contains common values shared across all scenarios:
- Fixed amortization period: **25 years**
- Loan parameters and mortgage rates
- Split ratios and export settings

### `mortgage.env` (Active Scenario)
Contains only scenario-specific values that override base configuration.

### Rate Cut Scenarios

All scenarios assume rate cuts will occur (realistic expectation):

- **`conservative.env`**: 2 cuts of 0.25% each (months 12, 30) - Gradual approach
- **`aggressive.env`**: 4 cuts of 0.25% each (months 6, 12, 18, 24) - Front-loaded cuts
- **`high_loan.env`**: $1M loan with 5-year analysis period

## Easy Scenario Switching

### Using the Scenario Runner (Recommended):
```bash
# Conservative scenario (2 cuts)
python run_scenario.py conservative

# Aggressive scenario (4 cuts)
python run_scenario.py aggressive

# High loan scenario ($1M)
python run_scenario.py high_loan
```

### Manual Switching:
```bash
# Conservative (2 cuts)
cp config/conservative.env config/mortgage.env && python main.py

# Aggressive (4 cuts)
cp config/aggressive.env config/mortgage.env && python main.py

# High loan ($1M)
cp config/high_loan.env config/mortgage.env && python main.py
```

## Configuration Parameters

### Loan Parameters
- `LOAN_AMOUNT`: Total loan amount in dollars
- `AMORTIZATION_YEARS`: Loan amortization period (25 or 30 years typical)
- `HORIZON_YEARS`: Analysis period (how many years to simulate)

### Fixed Mortgage
- `FIXED_INITIAL_RATE`: Initial fixed rate (e.g., 0.0389 = 3.89%)
- `FIXED_TERM_YEARS`: Fixed term length (3 or 5 years typical)
- `FIXED_RENEWAL_RATE`: Rate assumption for renewal

### Variable Mortgage
- `PRIME_RATE`: Current prime rate
- `VARIABLE_DISCOUNT_INITIAL`: Initial discount below prime
- `VARIABLE_TERM_YEARS`: Variable term length
- `VARIABLE_RENEWAL_DISCOUNT`: Renewal discount below prime
- `VARIABLE_FIXED_PAYMENT`: true = keep payments constant, false = recalculate

### Rate Cut Scenarios
- `USE_RATE_CUTS`: true/false to enable rate cuts
- `RATE_CUT_AMOUNT`: Size of each rate cut (e.g., 0.0025 = 0.25%)
- `CUT_SCHEDULE`: Comma-separated months for cuts (e.g., 6,12,18,24)

### Split Mortgage
- `SPLIT_RATIO`: Percentage fixed (0.5 = 50% fixed, 50% variable)

### Export Settings
- `EXPORT_TO_CSV`: true/false to export CSV files
- `OUTPUT_FOLDER`: Folder name for output files

## Tips

1. **Rate Format**: Use decimal format (0.0389 = 3.89%)
2. **Boolean Values**: Use `true` or `false` (lowercase)
3. **Lists**: Use comma-separated values (no spaces)
4. **Comments**: Lines starting with `#` are ignored
5. **Backup**: Keep copies of working configurations

## Troubleshooting

- **File Not Found**: Ensure `mortgage.env` exists in the config folder
- **Invalid Values**: Check number formats and boolean values
- **Missing Parameters**: All parameters must be present in the file