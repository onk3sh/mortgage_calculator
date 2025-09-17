"""
Main mortgage calculator application
"""
from helpers.mortgage_strategies import simulate_full_fixed, simulate_full_variable, simulate_split
from helpers.analysis_export import (calculate_metrics, print_summary, print_rate_progression,
                                     export_schedules, export_summary_analysis, print_final_comparison)
import config


# -----------------------------
# Main Execution
# -----------------------------
def main():
    print("Running mortgage simulations...")
    print(f"Loan Amount: ${config.LOAN_AMOUNT:,}")
    print(f"Horizon: {config.HORIZON_YEARS} years")
    print(f"Fixed Rate: {config.FIXED_INITIAL_RATE * 100:.2f}% → {config.FIXED_RENEWAL_RATE * 100:.2f}%")
    print(f"Variable: Prime {config.PRIME_RATE * 100:.2f}% - {config.VARIABLE_DISCOUNT_INITIAL * 100:.2f}%")

    if config.USE_RATE_CUTS:
        total_cuts = len(config.CUT_SCHEDULE) * config.RATE_CUT_AMOUNT
        print(f"Rate Cuts: {len(config.CUT_SCHEDULE)} cuts × 0.25% = {total_cuts * 100:.1f}% total")
        print(f"Cut schedule: Months {', '.join(map(str, config.CUT_SCHEDULE))}")
    else:
        print("Rate Cuts: None")

    print("\n" + "=" * 50)

    # Run simulations
    fixed_schedule = simulate_full_fixed(
        config.LOAN_AMOUNT, config.AMORTIZATION_YEARS, config.HORIZON_YEARS,
        config.FIXED_INITIAL_RATE, config.FIXED_TERM_YEARS, config.FIXED_RENEWAL_RATE
    )

    var_schedule_fixed_payment = simulate_full_variable(
        config.LOAN_AMOUNT, config.AMORTIZATION_YEARS, config.HORIZON_YEARS,
        config.PRIME_RATE, config.VARIABLE_DISCOUNT_INITIAL, config.VARIABLE_TERM_YEARS,
        config.VARIABLE_RENEWAL_DISCOUNT, True,  # Fixed payment
        config.USE_RATE_CUTS, config.CUT_SCHEDULE, config.RATE_CUT_AMOUNT
    )

    var_schedule_recalc_payment = simulate_full_variable(
        config.LOAN_AMOUNT, config.AMORTIZATION_YEARS, config.HORIZON_YEARS,
        config.PRIME_RATE, config.VARIABLE_DISCOUNT_INITIAL, config.VARIABLE_TERM_YEARS,
        config.VARIABLE_RENEWAL_DISCOUNT, False,  # Recalculated payment
        config.USE_RATE_CUTS, config.CUT_SCHEDULE, config.RATE_CUT_AMOUNT
    )

    split_schedule = simulate_split(
        config.LOAN_AMOUNT, config.SPLIT_RATIO, config.AMORTIZATION_YEARS, config.HORIZON_YEARS,
        config.FIXED_INITIAL_RATE, config.FIXED_TERM_YEARS, config.FIXED_RENEWAL_RATE,
        config.PRIME_RATE, config.VARIABLE_DISCOUNT_INITIAL, config.VARIABLE_TERM_YEARS,
        config.VARIABLE_RENEWAL_DISCOUNT, config.VARIABLE_FIXED_PAYMENT,
        config.USE_RATE_CUTS, config.CUT_SCHEDULE, config.RATE_CUT_AMOUNT
    )

    # Calculate metrics
    fixed_metrics = calculate_metrics(fixed_schedule, "Full Fixed", config.LOAN_AMOUNT)
    var_fixed_payment_metrics = calculate_metrics(var_schedule_fixed_payment, "Variable (Fixed Payment)", config.LOAN_AMOUNT)
    var_recalc_payment_metrics = calculate_metrics(var_schedule_recalc_payment, "Variable (Recalc Payment)", config.LOAN_AMOUNT)
    split_metrics = calculate_metrics(split_schedule, "50/50 Split", config.LOAN_AMOUNT)

    metrics_list = [fixed_metrics, var_fixed_payment_metrics, var_recalc_payment_metrics, split_metrics]

    # Print summaries
    for metrics in metrics_list:
        print_summary(metrics)

    # Print rate progressions
    print_rate_progression(var_schedule_fixed_payment, "Variable (Fixed Payment)")
    print_rate_progression(var_schedule_recalc_payment, "Variable (Recalc Payment)")
    print_rate_progression(split_schedule, "50/50 Split")

    # Export data
    if config.EXPORT_TO_CSV:
        export_schedules(fixed_schedule, var_schedule_fixed_payment, var_schedule_recalc_payment, split_schedule, config.OUTPUT_FOLDER)
        export_summary_analysis(
            metrics_list, config.LOAN_AMOUNT, config.AMORTIZATION_YEARS, config.HORIZON_YEARS,
            config.USE_RATE_CUTS, config.CUT_SCHEDULE, config.RATE_CUT_AMOUNT, config.OUTPUT_FOLDER
        )


    # Final comparison
    print_final_comparison(metrics_list, config.USE_RATE_CUTS, var_fixed_payment_metrics)


if __name__ == "__main__":
    main()