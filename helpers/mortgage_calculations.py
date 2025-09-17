"""
Core mortgage calculation functions
"""
import pandas as pd


def monthly_payment(principal, annual_rate, months):
    """Calculate monthly payment for given principal, rate, and amortization"""
    if annual_rate == 0:
        return principal / months
    # Semi-annual compounding adjustment for Canadian mortgages
    monthly_rate = (1 + annual_rate / 2) ** (1 / 6) - 1
    return principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)


def create_rate_path(cut_schedule, cut_amount, total_months):
    """Create a dictionary mapping month to cumulative prime rate reduction"""
    rate_reductions = {}
    cumulative_cut = 0

    for month in range(1, total_months + 1):
        if month in cut_schedule:
            cumulative_cut += cut_amount
        rate_reductions[month] = cumulative_cut

    return rate_reductions


def amortize_with_rate_changes(principal, initial_rate, months, start_month=0,
                               fixed_payment=None, rate_reductions=None, amortization_months=None):
    """
    Create amortization schedule with rate changes
    rate_reductions: dict of {month: total_rate_reduction}
    """
    schedule = []
    current_principal = principal

    # Calculate initial payment if not provided
    if fixed_payment is None:
        # Use amortization period for payment calculation, not term length
        payment_months = amortization_months if amortization_months else months
        payment = monthly_payment(principal, initial_rate, payment_months)
    else:
        payment = fixed_payment

    for m in range(1, months + 1):
        month_number = start_month + m

        # Determine current rate (apply any cumulative cuts)
        rate_reduction = rate_reductions.get(month_number, 0) if rate_reductions else 0
        current_rate = max(initial_rate - rate_reduction, 0)

        # Calculate monthly rate and payment details
        monthly_rate = (1 + current_rate / 2) ** (1 / 6) - 1
        interest = current_principal * monthly_rate

        # For fixed payment variable mortgages, payment stays constant
        # For regular mortgages, payment could be recalculated with new rate
        if fixed_payment is None and rate_reduction > 0:
            # Recalculate payment with new rate for remaining amortization months
            remaining_amort_months = (amortization_months if amortization_months else months) - m + 1
            payment = monthly_payment(current_principal, current_rate, remaining_amort_months)

        principal_paid = payment - interest
        current_principal -= principal_paid

        schedule.append({
            "Month": month_number,
            "Payment": payment,
            "Principal Paid": principal_paid,
            "Interest Paid": interest,
            "Balance": current_principal,
            "Rate": current_rate * 100  # Store as percentage
        })

    return pd.DataFrame(schedule)