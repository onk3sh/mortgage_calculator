# 🏠 Canadian Mortgage Calculator

A comprehensive web-based mortgage calculator designed for Canadian mortgages with realistic scenarios, interactive charts, and detailed analysis capabilities.

## ✨ Features

### 🎯 Core Functionality
- **Interactive Web Dashboard** with Chart.js integration and zoom/pan functionality
- **Flexible Analysis Periods** - Analyze mortgage scenarios from 1 to 25 years
- **Canadian Mortgage Standards** - Semi-annual compounding with realistic parameters
- **Home Value Projections** - Calculate net cash on sale with transaction costs
- **Multiple Mortgage Strategies** - Fixed, Variable (Fixed Payment), Variable (Recalc Payment), Split

### 📊 Analysis Capabilities
- **Rate Cut Scenarios** - Realistic maximum of 4 cuts at 0.25% each
- **Payment Frequency Options** - Monthly, bi-weekly, accelerated payments
- **Prepayment Features** - One-time, monthly, and annual prepayments
- **Transaction Cost Modeling** - 1.5% buying costs, 5% selling costs, 5% annual appreciation
- **Real-time Validation** - Form validation with dynamic limits based on amortization

### 🔧 Technical Features
- **Environment-based Configuration** - Separate configs for different scenarios
- **RESTful API Design** - Clean endpoints for scenario data management
- **Responsive Design** - Works on desktop and mobile devices
- **Auto-opening Forms** - Transparent parameter display for user clarity

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/onk3sh/mortgage_calculator.git
   cd mortgage_calculator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python webapp_server.py
   ```

4. **Open in browser**
   Navigate to `http://localhost:8080`

## 📋 Usage

### Web Dashboard
The web interface provides:
- **Predefined Scenarios**: Conservative (2 rate cuts) and Aggressive (4 rate cuts)
- **Custom Analysis**: Full control over all mortgage parameters
- **Interactive Charts**: Balance progression, payment breakdown, home value projections
- **Multiple Views**: Net cash on sale, total return, home value growth, strategy comparison

### Command Line Interface
Run predefined scenarios:
```bash
python run_scenario.py conservative  # 2 rate cuts scenario
python run_scenario.py aggressive    # 4 rate cuts scenario
```

### Configuration
Modify scenarios by editing files in the `config/` directory:
- `base.env` - Common mortgage parameters
- `conservative.env` - Conservative scenario overrides
- `aggressive.env` - Aggressive scenario overrides

## 🏗️ Project Structure

```
mortgage_calculator/
├── webapp_server.py           # Flask web server
├── run_scenario.py           # CLI scenario runner
├── main.py                   # Core analysis engine
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── webapp/
│   ├── templates/
│   │   └── index.html       # Main web interface
│   └── static/
│       └── dashboard.js     # Frontend JavaScript
├── helpers/
│   ├── mortgage_calculations.py  # Core calculations
│   ├── mortgage_strategies.py   # Strategy implementations
│   └── analysis_export.py      # Results processing
├── config/
│   ├── base.env             # Base configuration
│   ├── conservative.env     # Conservative scenario
│   └── aggressive.env       # Aggressive scenario
└── scenarios/               # Generated analysis results
    ├── .gitkeep            # Keeps directory in git
    ├── conservative_scenario_output/
    ├── aggressive_scenario_output/
    └── high_loan_scenario_output/
```

## 🔧 Configuration

### Base Parameters (config/base.env)
```env
LOAN_AMOUNT=672000
AMORTIZATION_YEARS=25
HORIZON_YEARS=3
FIXED_INITIAL_RATE=0.0399
PRIME_RATE=0.0495
VARIABLE_DISCOUNT_INITIAL=0.0085
```

### Scenario Customization
- **Conservative**: 2 rate cuts at months 6, 12
- **Aggressive**: 4 rate cuts at months 6, 12, 18, 24
- **Custom**: User-defined parameters via web form

## 📊 API Endpoints

### Scenario Management
- `POST /run_scenario/{scenario}` - Execute predefined scenario
- `GET /data/{scenario}/summary` - Get scenario summary data
- `GET /data/{scenario}/details` - Get detailed payment schedule
- `GET /scenarios` - List available scenarios and status

### Custom Analysis
- `POST /run_custom_scenario` - Run analysis with custom parameters

Example custom scenario request:
```json
{
  "purchase_price": 840000,
  "down_payment_percent": 20,
  "amortization_years": 25,
  "analysis_period": 5,
  "fixed_rate": 0.0399,
  "prime_rate": 0.0495,
  "enable_rate_cuts": true,
  "cut_schedule": "6,12,18,24"
}
```

## 🧮 Mortgage Calculation Details

### Canadian Mortgage Standards
- **Compounding**: Semi-annual compounding for Canadian mortgages
- **Payment Calculation**: Accurate monthly payment calculation with proper rate conversion
- **Amortization**: Standard 25-year amortization period
- **Rate Structure**: Realistic fixed and variable rate scenarios

### Payment Frequencies
- **Monthly**: 12 payments per year
- **Bi-weekly**: 26 payments per year
- **Accelerated Bi-weekly**: 26 payments + 1 extra monthly payment annually
- **Accelerated Monthly**: 12 payments + 1 extra payment annually

### Rate Cut Logic
- Maximum 4 rate cuts of 0.25% each
- Cuts applied at specified months (e.g., 6, 12, 18, 24)
- Affects variable rate mortgages and variable portion of split mortgages

## 🎨 Charts and Visualizations

### Interactive Features
- **Zoom and Pan**: Navigate through payment schedules
- **Multiple Views**: Switch between balance, payments, and home value charts
- **Strategy Comparison**: Side-by-side analysis of different approaches
- **Home Value Analysis**: Net cash projections with appreciation modeling

### Chart Types
1. **Balance Progression**: Mortgage balance over time by strategy
2. **Payment Breakdown**: Principal vs interest over time
3. **Home Value Projections**: Multiple views (net cash, total return, growth)
4. **Strategy Comparison**: Best vs worst performers

## 🔍 Home Value Analysis

### Transaction Cost Modeling
- **Purchase Costs**: 1.5% of home value (legal, inspection, etc.)
- **Selling Costs**: 5% of home value (realtor, legal, staging, etc.)
- **Down Payment**: 20% standard (configurable)
- **Appreciation**: 5% annual (configurable)

### Calculations
- **Net Cash on Sale**: Home value - selling costs - remaining mortgage
- **Total Return**: Net cash - initial investment (down payment + purchase costs)
- **ROI Percentage**: Total return / initial investment × 100

## 🧪 Testing

### Scenario Testing
The application includes comprehensive test scenarios:
- 3-year analysis with realistic rate cuts
- 7-year extended analysis
- 25-year full amortization analysis
- Custom parameter validation

### API Testing
Test endpoints with curl:
```bash
# Test custom scenario
curl -X POST http://localhost:8080/run_custom_scenario \
  -H "Content-Type: application/json" \
  -d '{"purchase_price": 840000, "analysis_period": 5, ...}'

# Get scenario data
curl http://localhost:8080/data/conservative/summary
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Chart.js** for interactive charting capabilities
- **Flask** for the lightweight web framework
- **Canadian mortgage standards** for realistic calculation parameters

## 📞 Support

For questions or issues:
1. Check existing [GitHub Issues](https://github.com/onk3sh/mortgage_calculator/issues)
2. Create a new issue with detailed description
3. Include steps to reproduce any bugs

---

**Built with ❤️ for Canadian homebuyers and mortgage professionals**