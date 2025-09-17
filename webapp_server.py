#!/usr/bin/env python3
"""
Simple web server for mortgage calculator dashboard
"""

from flask import Flask, render_template, jsonify, send_from_directory, request
import subprocess
import pandas as pd
import json
import os
import tempfile
from pathlib import Path
from helpers.mortgage_strategies import simulate_full_fixed, simulate_full_variable, simulate_split
from helpers.analysis_export import calculate_metrics

def calculate_home_value_projections(purchase_price, annual_appreciation, analysis_period,
                                   buying_closing_costs_rate, selling_closing_costs_rate,
                                   metrics_list):
    """Calculate home value projections and net cash on sale for each strategy"""

    # Calculate initial costs and down payment (assuming 20% down)
    down_payment_percent = 0.20
    down_payment = purchase_price * down_payment_percent
    buying_closing_costs = purchase_price * buying_closing_costs_rate
    total_initial_cash_investment = down_payment + buying_closing_costs

    # Calculate home value after appreciation
    home_value_at_sale = purchase_price * ((1 + annual_appreciation) ** analysis_period)

    # Calculate selling costs
    selling_closing_costs = home_value_at_sale * selling_closing_costs_rate

    # Calculate net proceeds before mortgage payoff
    gross_proceeds = home_value_at_sale - selling_closing_costs

    home_value_data = {}

    for metrics in metrics_list:
        strategy_name = metrics['Strategy']
        remaining_mortgage_balance = metrics['Ending Balance']

        # Net cash on sale = Gross proceeds - Remaining mortgage balance
        net_cash_on_sale = gross_proceeds - remaining_mortgage_balance

        # Total return on investment = Net cash - Initial cash investment
        total_return = net_cash_on_sale - total_initial_cash_investment

        # Return on investment percentage
        roi_percent = (total_return / total_initial_cash_investment) * 100 if total_initial_cash_investment > 0 else 0

        home_value_data[strategy_name] = {
            'homeValue': home_value_at_sale,
            'grossProceeds': gross_proceeds,
            'remainingBalance': remaining_mortgage_balance,
            'netCashOnSale': net_cash_on_sale,
            'buyingCosts': buying_closing_costs,
            'sellingCosts': selling_closing_costs,
            'downPayment': down_payment,
            'totalInitialInvestment': total_initial_cash_investment,
            'totalReturn': total_return,
            'roiPercent': roi_percent,
            'appreciation': home_value_at_sale - purchase_price,
            'equityBuiltThroughPayments': metrics['Equity Built ($)']
        }

    return home_value_data

app = Flask(__name__,
            template_folder='webapp/templates',
            static_folder='webapp/static')

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder, filename)

@app.route('/run_scenario/<scenario>', methods=['POST'])
def run_scenario(scenario):
    """Run a mortgage scenario"""
    try:
        # Valid scenarios
        valid_scenarios = ['conservative', 'aggressive']
        if scenario not in valid_scenarios:
            return jsonify({'error': 'Invalid scenario'}), 400

        # Run the scenario
        result = subprocess.run(
            ['python', 'run_scenario.py', scenario],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return jsonify({'success': True, 'message': f'{scenario} scenario completed'})
        else:
            return jsonify({
                'error': f'Scenario failed: {result.stderr}',
                'stdout': result.stdout
            }), 500

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Scenario execution timed out'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data/<scenario>/summary')
def get_summary_data(scenario):
    """Get summary data for a scenario"""
    try:
        # Map scenario to folder name
        folder_map = {
            'conservative': 'scenarios/conservative_scenario_output',
            'aggressive': 'scenarios/aggressive_scenario_output'
        }

        folder = folder_map.get(scenario)
        if not folder:
            return jsonify({'error': 'Invalid scenario'}), 400

        # Read the summary CSV
        summary_file = Path(folder) / 'mortgage_strategy_summary.csv'
        if not summary_file.exists():
            return jsonify({'error': f'Summary file not found for {scenario}'}), 404

        # Load and process the data
        df = pd.read_csv(summary_file)

        # Convert to JSON-friendly format
        summary_data = []
        for _, row in df.iterrows():
            summary_data.append({
                'Strategy': row['Strategy'],
                'Total Payments': float(row['Total Payments']),
                'Total Interest': float(row['Total Interest']),
                'Total Principal Paid': float(row['Total Principal Paid']),
                'Ending Balance': float(row['Ending Balance']),
                'Equity Built ($)': float(row['Equity Built ($)']),
                'Equity Built (%)': float(row['Equity Built (%)']),
                'Average Rate (%)': float(row['Average Rate (%)']),
                'Min Rate (%)': float(row['Min Rate (%)']),
                'Max Rate (%)': float(row['Max Rate (%)'])
            })

        # Calculate home value data for predefined scenarios
        # Scenario-specific parameters
        scenario_params = {
            'conservative': {'loan_amount': 672000, 'analysis_period': 3},
            'aggressive': {'loan_amount': 672000, 'analysis_period': 3}
        }

        params = scenario_params.get(scenario, {'loan_amount': 672000, 'analysis_period': 3})
        loan_amount = params['loan_amount']
        analysis_period = params['analysis_period']
        down_payment_percent = 20  # Assume 20% down payment
        purchase_price = loan_amount / (1 - down_payment_percent / 100)
        annual_appreciation = 0.05  # 5% default

        home_value_data = calculate_home_value_projections(
            purchase_price, annual_appreciation, analysis_period,
            0.015, 0.05, summary_data  # 1.5% buying, 5% selling costs
        )

        return jsonify({
            'summary': summary_data,
            'homeValueData': home_value_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data/<scenario>/details')
def get_details_data(scenario):
    """Get detailed schedule data for a scenario"""
    try:
        # Map scenario to folder name
        folder_map = {
            'conservative': 'scenarios/conservative_scenario_output',
            'aggressive': 'scenarios/aggressive_scenario_output'
        }

        folder = folder_map.get(scenario)
        if not folder:
            return jsonify({'error': 'Invalid scenario'}), 400

        # Read the comparison CSV (contains all strategies)
        details_file = Path(folder) / 'all_strategies_comparison.csv'
        if not details_file.exists():
            return jsonify({'error': f'Details file not found for {scenario}'}), 404

        # Load and process the data
        df = pd.read_csv(details_file)

        # Convert to JSON-friendly format
        data = []
        for _, row in df.iterrows():
            data.append({
                'Month': int(row['Month']),
                'Payment': float(row['Payment']),
                'Principal Paid': float(row['Principal Paid']),
                'Interest Paid': float(row['Interest Paid']),
                'Balance': float(row['Balance']),
                'Rate': float(row['Rate']),
                'Strategy': row['Strategy']
            })

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data/<scenario>/analysis')
def get_analysis_data(scenario):
    """Get analysis summary text for a scenario"""
    try:
        # Map scenario to folder name
        folder_map = {
            'conservative': 'scenarios/conservative_scenario_output',
            'aggressive': 'scenarios/aggressive_scenario_output'
        }

        folder = folder_map.get(scenario)
        if not folder:
            return jsonify({'error': 'Invalid scenario'}), 400

        # Read the analysis text file
        analysis_file = Path(folder) / 'analysis_summary.txt'
        if not analysis_file.exists():
            return jsonify({'error': f'Analysis file not found for {scenario}'}), 404

        with open(analysis_file, 'r') as f:
            content = f.read()

        return jsonify({'content': content})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scenarios')
def list_scenarios():
    """List available scenarios and their status"""
    scenarios = ['conservative', 'aggressive']

    folder_map = {
        'conservative': 'conservative_scenario_output',
        'aggressive': 'aggressive_scenario_output'
    }

    status = {}
    for scenario in scenarios:
        folder = folder_map[scenario]
        summary_file = Path(folder) / 'mortgage_strategy_summary.csv'
        status[scenario] = {
            'available': summary_file.exists(),
            'folder': folder
        }

    return jsonify(status)

@app.route('/run_custom_scenario', methods=['POST'])
def run_custom_scenario():
    """Run a custom mortgage scenario with user-provided parameters"""
    try:
        # Get form data
        data = request.get_json()

        # Extract parameters
        purchase_price = data['purchase_price']
        down_payment_percent = data['down_payment_percent']
        loan_amount = purchase_price * (1 - down_payment_percent / 100)

        amortization_years = data['amortization_years']
        analysis_period = data['analysis_period']

        fixed_rate = data['fixed_rate']
        fixed_term = data['fixed_term']
        fixed_renewal_rate = data['fixed_renewal_rate']

        prime_rate = data['prime_rate']
        variable_discount = data['variable_discount']
        variable_term = data['variable_term']
        renewal_discount = data['renewal_discount']

        enable_rate_cuts = data['enable_rate_cuts']
        rate_cut_amount = data['rate_cut_amount'] if enable_rate_cuts else 0
        cut_schedule = []
        if enable_rate_cuts and data['cut_schedule']:
            cut_schedule = [int(x.strip()) for x in data['cut_schedule'].split(',') if x.strip()]

        split_ratio = data['split_ratio']
        fixed_payment = data['fixed_payment']

        # Run simulations
        print(f"Running custom scenario: Loan ${loan_amount:,.0f}, {analysis_period}yr analysis")

        # Full Fixed
        fixed_schedule = simulate_full_fixed(
            loan_amount, amortization_years, analysis_period,
            fixed_rate, fixed_term, fixed_renewal_rate
        )

        # Variable Fixed Payment
        var_schedule_fixed_payment = simulate_full_variable(
            loan_amount, amortization_years, analysis_period,
            prime_rate, variable_discount, variable_term,
            renewal_discount, True,  # Fixed payment
            enable_rate_cuts, cut_schedule, rate_cut_amount
        )

        # Variable Recalc Payment
        var_schedule_recalc_payment = simulate_full_variable(
            loan_amount, amortization_years, analysis_period,
            prime_rate, variable_discount, variable_term,
            renewal_discount, False,  # Recalculated payment
            enable_rate_cuts, cut_schedule, rate_cut_amount
        )

        # Split Mortgage
        split_schedule = simulate_split(
            loan_amount, split_ratio, amortization_years, analysis_period,
            fixed_rate, fixed_term, fixed_renewal_rate,
            prime_rate, variable_discount, variable_term,
            renewal_discount, fixed_payment,
            enable_rate_cuts, cut_schedule, rate_cut_amount
        )

        # Calculate metrics
        fixed_metrics = calculate_metrics(fixed_schedule, "Full Fixed", loan_amount)
        var_fixed_payment_metrics = calculate_metrics(var_schedule_fixed_payment, "Variable (Fixed Payment)", loan_amount)
        var_recalc_payment_metrics = calculate_metrics(var_schedule_recalc_payment, "Variable (Recalc Payment)", loan_amount)
        split_metrics = calculate_metrics(split_schedule, "50/50 Split", loan_amount)

        # Prepare summary data
        summary_data = []
        for metrics in [fixed_metrics, var_fixed_payment_metrics, var_recalc_payment_metrics, split_metrics]:
            summary_data.append({
                'Strategy': metrics['Strategy'],
                'Total Payments': metrics['Total Payments'],
                'Total Interest': metrics['Total Interest'],
                'Total Principal Paid': metrics['Total Principal Paid'],
                'Ending Balance': metrics['Ending Balance'],
                'Equity Built ($)': metrics['Equity Built ($)'],
                'Equity Built (%)': metrics['Equity Built (%)'],
                'Average Rate (%)': metrics['Average Rate (%)'],
                'Min Rate (%)': metrics['Min Rate (%)'],
                'Max Rate (%)': metrics['Max Rate (%)']
            })

        # Prepare detailed data (combine all schedules)
        details_data = []

        # Add all schedules
        schedules = [
            (fixed_schedule, "Full Fixed"),
            (var_schedule_fixed_payment, "Variable (Fixed Payment)"),
            (var_schedule_recalc_payment, "Variable (Recalc Payment)"),
            (split_schedule, "50/50 Split")
        ]

        for schedule, strategy_name in schedules:
            # Convert DataFrame to list of records if needed
            if hasattr(schedule, 'iterrows'):
                # It's a DataFrame
                for _, row in schedule.iterrows():
                    details_data.append({
                        'Month': int(row['Month']),
                        'Payment': float(row['Payment']),
                        'Principal Paid': float(row['Principal Paid']),
                        'Interest Paid': float(row['Interest Paid']),
                        'Balance': float(row['Balance']),
                        'Rate': float(row['Rate']),
                        'Strategy': strategy_name
                    })
            else:
                # It's a list of dictionaries
                for entry in schedule:
                    details_data.append({
                        'Month': entry['Month'],
                        'Payment': entry['Payment'],
                        'Principal Paid': entry['Principal Paid'],
                        'Interest Paid': entry['Interest Paid'],
                        'Balance': entry['Balance'],
                        'Rate': entry['Rate'],
                        'Strategy': strategy_name
                    })

        # Calculate home value data
        annual_appreciation = data.get('annual_appreciation', 0.05)  # Default 5%
        buying_closing_costs_rate = 0.015  # 1.5%
        selling_closing_costs_rate = 0.05  # 5%

        home_value_data = calculate_home_value_projections(
            purchase_price, annual_appreciation, analysis_period,
            buying_closing_costs_rate, selling_closing_costs_rate,
            [fixed_metrics, var_fixed_payment_metrics, var_recalc_payment_metrics, split_metrics]
        )

        return jsonify({
            'success': True,
            'summary': summary_data,
            'details': details_data,
            'homeValueData': home_value_data,
            'parameters': {
                'loan_amount': loan_amount,
                'analysis_period': analysis_period,
                'enable_rate_cuts': enable_rate_cuts,
                'cut_schedule': cut_schedule,
                'annual_appreciation': annual_appreciation,
                'purchase_price': purchase_price
            }
        })

    except Exception as e:
        print(f"Custom scenario error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Failed to run custom scenario: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Starting Mortgage Calculator Web Dashboard...")
    print("Open http://localhost:8080 in your browser")
    app.run(debug=True, host='0.0.0.0', port=8080)