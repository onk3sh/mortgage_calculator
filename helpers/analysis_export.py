"""
Analysis and export functions for mortgage calculations
"""
import os
import pandas as pd


def calculate_metrics(schedule, name, loan_amount):
    """Calculate comprehensive metrics for a mortgage strategy"""
    total_payment = schedule["Payment"].sum()
    total_interest = schedule["Interest Paid"].sum()
    total_principal = schedule["Principal Paid"].sum()
    end_balance = schedule.iloc[-1]["Balance"]
    equity_built = loan_amount - end_balance
    equity_percentage = (equity_built / loan_amount) * 100
    avg_rate = schedule["Rate"].mean()

    # Rate analysis
    min_rate = schedule["Rate"].min()
    max_rate = schedule["Rate"].max()

    return {
        "Strategy": name,
        "Total Payments": total_payment,
        "Total Interest": total_interest,
        "Total Principal Paid": total_principal,
        "Ending Balance": end_balance,
        "Equity Built ($)": equity_built,
        "Equity Built (%)": equity_percentage,
        "Average Rate (%)": avg_rate,
        "Min Rate (%)": min_rate,
        "Max Rate (%)": max_rate
    }


def print_summary(metrics):
    """Print formatted summary of mortgage metrics"""
    print(f"\n{metrics['Strategy']}:")
    print(f"  Total Payments: ${metrics['Total Payments']:,.0f}")
    print(f"  Total Interest: ${metrics['Total Interest']:,.0f}")
    print(f"  Total Principal: ${metrics['Total Principal Paid']:,.0f}")
    print(f"  Ending Balance: ${metrics['Ending Balance']:,.0f}")
    print(f"  Equity Built: ${metrics['Equity Built ($)']:,.0f} ({metrics['Equity Built (%)']:.2f}%)")
    print(f"  Average Rate: {metrics['Average Rate (%)']:.2f}%")
    if metrics['Min Rate (%)'] != metrics['Max Rate (%)']:
        print(f"  Rate Range: {metrics['Min Rate (%)']:.2f}% - {metrics['Max Rate (%)']:.2f}%")


def print_rate_progression(schedule, name):
    """Print rate progression for variable mortgages"""
    if "Variable" in name:
        print(f"\n{name} - Rate Progression:")
        prev_rate = None
        for _, row in schedule.iterrows():
            current_rate = row["Rate"]
            if prev_rate is None or abs(current_rate - prev_rate) > 0.01:
                print(f"  Month {int(row['Month'])}: {current_rate:.2f}%")
                prev_rate = current_rate


def export_schedules(fixed_schedule, var_schedule_fixed_payment, var_schedule_recalc_payment, split_schedule, output_folder):
    """Export all schedules to CSV files"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Export individual schedules
    fixed_schedule.to_csv(f"{output_folder}/fixed_mortgage_schedule.csv", index=False)
    var_schedule_fixed_payment.to_csv(f"{output_folder}/variable_fixed_payment_schedule.csv", index=False)
    var_schedule_recalc_payment.to_csv(f"{output_folder}/variable_recalc_payment_schedule.csv", index=False)
    split_schedule.to_csv(f"{output_folder}/split_mortgage_schedule.csv", index=False)

    # Export combined comparison
    combined = pd.concat([
        fixed_schedule.assign(Strategy="Full Fixed"),
        var_schedule_fixed_payment.assign(Strategy="Variable (Fixed Payment)"),
        var_schedule_recalc_payment.assign(Strategy="Variable (Recalc Payment)"),
        split_schedule.assign(Strategy="50/50 Split")
    ])
    combined.to_csv(f"{output_folder}/all_strategies_comparison.csv", index=False)

    print(f"\nSchedules exported to '{output_folder}' folder:")
    print("- fixed_mortgage_schedule.csv")
    print("- variable_fixed_payment_schedule.csv")
    print("- variable_recalc_payment_schedule.csv")
    print("- split_mortgage_schedule.csv")
    print("- all_strategies_comparison.csv")


def export_summary_analysis(metrics_list, loan_amount, amortization_years, horizon_years,
                           use_rate_cuts, cut_schedule, rate_cut_amount, output_folder):
    """Export summary analysis and insights"""
    summary_df = pd.DataFrame(metrics_list)
    summary_df.to_csv(f"{output_folder}/mortgage_strategy_summary.csv", index=False)

    # Create detailed analysis
    analysis = []
    best_equity = max(metrics_list, key=lambda x: x['Equity Built (%)'])
    lowest_interest = min(metrics_list, key=lambda x: x['Total Interest'])
    lowest_payment = min(metrics_list, key=lambda x: x['Total Payments'])

    analysis.append(f"MORTGAGE STRATEGY ANALYSIS ({horizon_years}-Year Horizon)")
    analysis.append("=" * 60)
    analysis.append(f"Initial Loan Amount: ${loan_amount:,}")
    analysis.append(f"Amortization Period: {amortization_years} years")
    analysis.append("")

    analysis.append("BEST PERFORMERS:")
    analysis.append(f"• Highest Equity Built: {best_equity['Strategy']} - {best_equity['Equity Built (%)']:.2f}%")
    analysis.append(
        f"• Lowest Total Interest: {lowest_interest['Strategy']} - ${lowest_interest['Total Interest']:,.0f}")
    analysis.append(f"• Lowest Total Payments: {lowest_payment['Strategy']} - ${lowest_payment['Total Payments']:,.0f}")
    analysis.append("")

    # Compare strategies
    fixed_metrics = next(m for m in metrics_list if m['Strategy'] == 'Full Fixed')
    var_fixed_metrics = next(m for m in metrics_list if m['Strategy'] == 'Variable (Fixed Payment)')
    var_recalc_metrics = next(m for m in metrics_list if m['Strategy'] == 'Variable (Recalc Payment)')
    split_metrics = next(m for m in metrics_list if m['Strategy'] == '50/50 Split')

    analysis.append("STRATEGY COMPARISONS:")
    analysis.append(
        f"• Variable (Fixed) vs Fixed Interest Savings: ${fixed_metrics['Total Interest'] - var_fixed_metrics['Total Interest']:,.0f}")
    analysis.append(
        f"• Variable (Recalc) vs Fixed Interest Savings: ${fixed_metrics['Total Interest'] - var_recalc_metrics['Total Interest']:,.0f}")
    analysis.append(
        f"• Variable (Fixed) vs Fixed Equity Difference: {var_fixed_metrics['Equity Built (%)'] - fixed_metrics['Equity Built (%)']:+.2f}%")
    analysis.append(
        f"• Variable (Recalc) vs Fixed Equity Difference: {var_recalc_metrics['Equity Built (%)'] - fixed_metrics['Equity Built (%)']:+.2f}%")
    analysis.append(f"• Split Strategy Balance: {split_metrics['Equity Built (%)']:.2f}% equity built")

    if use_rate_cuts:
        total_cuts = len(cut_schedule) * rate_cut_amount
        analysis.append("")
        analysis.append("RATE CUT IMPACT:")
        analysis.append(f"• Total rate cuts: {total_cuts * 100:.1f}% over {max(cut_schedule)} months")
        analysis.append(
            f"• Variable rate benefit: {var_fixed_metrics['Max Rate (%)'] - var_fixed_metrics['Min Rate (%)']:.2f}% rate reduction")

    with open(f"{output_folder}/analysis_summary.txt", 'w') as f:
        f.write('\n'.join(analysis))

    print("- mortgage_strategy_summary.csv")
    print("- analysis_summary.txt")


def print_final_comparison(metrics_list, use_rate_cuts, var_metrics):
    """Print final comparison summary"""
    print(f"\n{'=' * 60}")
    print("FINAL COMPARISON SUMMARY")
    print(f"{'=' * 60}")
    print(f"Best Equity Builder: {max(metrics_list, key=lambda x: x['Equity Built (%)'])['Strategy']}")
    print(f"Lowest Total Cost: {min(metrics_list, key=lambda x: x['Total Payments'])['Strategy']}")
    print(f"Lowest Interest Paid: {min(metrics_list, key=lambda x: x['Total Interest'])['Strategy']}")

    if use_rate_cuts:
        print(f"\nRate cut impact:")
        print(f"Variable rate: {var_metrics['Max Rate (%)']:.2f}% → {var_metrics['Min Rate (%)']:.2f}%")
        print(f"Total benefit: {var_metrics['Max Rate (%)'] - var_metrics['Min Rate (%)']:.2f}% rate reduction")