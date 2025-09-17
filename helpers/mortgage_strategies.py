"""
Mortgage strategy simulation functions
"""
import pandas as pd
from .mortgage_calculations import monthly_payment, amortize_with_rate_changes, create_rate_path


def simulate_full_fixed(loan_amount, amortization_years, horizon_years,
                       fixed_initial_rate, fixed_term_years, fixed_renewal_rate):
    """Simulate full fixed mortgage with renewals"""
    schedule = pd.DataFrame()
    balance = loan_amount
    total_months = horizon_years * 12
    remaining_amort = amortization_years * 12
    month = 0

    while month < total_months and balance > 0:
        # Determine term length and rate
        term = min(fixed_term_years * 12, total_months - month)
        rate = fixed_initial_rate if month == 0 else fixed_renewal_rate

        # Create schedule for this term
        df = amortize_with_rate_changes(balance, rate, term, month, amortization_months=remaining_amort)
        schedule = pd.concat([schedule, df], ignore_index=True)

        # Update for next term
        balance = df.iloc[-1]["Balance"]
        remaining_amort -= term
        month += term

    return schedule


def simulate_full_variable(loan_amount, amortization_years, horizon_years,
                          prime_rate, variable_discount_initial, variable_term_years,
                          variable_renewal_discount, variable_fixed_payment,
                          use_rate_cuts, cut_schedule, rate_cut_amount):
    """Simulate full variable mortgage with rate cuts"""
    schedule = pd.DataFrame()
    balance = loan_amount
    total_months = horizon_years * 12
    remaining_amort = amortization_years * 12
    month = 0
    fixed_payment_amount = None

    # Create rate reduction path for prime rate cuts
    if use_rate_cuts:
        prime_reductions = create_rate_path(cut_schedule, rate_cut_amount, total_months)
        print(f"Rate cuts planned:")
        cumulative = 0
        for cut_month in cut_schedule:
            if cut_month <= total_months:
                cumulative += rate_cut_amount
                new_prime = prime_rate - cumulative
                print(f"  Month {cut_month}: -{rate_cut_amount * 100:.2f}% → Prime {new_prime * 100:.2f}%")
    else:
        prime_reductions = {}

    while month < total_months and balance > 0:
        # Determine discount and base rate for this term
        discount = variable_discount_initial if month == 0 else variable_renewal_discount
        base_rate = prime_rate - discount
        term = min(variable_term_years * 12, total_months - month)

        # Convert prime reductions to variable rate reductions
        variable_reductions = {}
        for m, prime_cut in prime_reductions.items():
            if m > month and m <= month + term:
                variable_reductions[m] = prime_cut

        # Set payment strategy
        if variable_fixed_payment and fixed_payment_amount is not None:
            payment = fixed_payment_amount
        else:
            payment = monthly_payment(balance, base_rate, remaining_amort)
            if variable_fixed_payment and fixed_payment_amount is None:
                fixed_payment_amount = payment

        # Create schedule for this term
        df = amortize_with_rate_changes(
            balance, base_rate, term, month,
            fixed_payment=payment if variable_fixed_payment else None,
            rate_reductions=variable_reductions,
            amortization_months=remaining_amort
        )

        schedule = pd.concat([schedule, df], ignore_index=True)

        # Update for next term
        balance = df.iloc[-1]["Balance"]
        remaining_amort -= term
        month += term

    return schedule


def simulate_split(loan_amount, split_ratio, amortization_years, horizon_years,
                  fixed_initial_rate, fixed_term_years, fixed_renewal_rate,
                  prime_rate, variable_discount_initial, variable_term_years,
                  variable_renewal_discount, variable_fixed_payment,
                  use_rate_cuts, cut_schedule, rate_cut_amount):
    """Simulate 50/50 split between fixed and variable"""
    # Calculate each portion separately
    fixed_portion = loan_amount * split_ratio
    variable_portion = loan_amount * (1 - split_ratio)

    # Simulate each portion
    fixed_schedule = simulate_portion_fixed(
        fixed_portion, amortization_years, horizon_years,
        fixed_initial_rate, fixed_term_years, fixed_renewal_rate
    )
    var_schedule = simulate_portion_variable(
        variable_portion, amortization_years, horizon_years,
        prime_rate, variable_discount_initial, variable_term_years,
        variable_renewal_discount, variable_fixed_payment,
        use_rate_cuts, cut_schedule, rate_cut_amount
    )

    # Combine the schedules
    schedule = pd.DataFrame()
    schedule["Month"] = fixed_schedule["Month"]
    schedule["Payment"] = fixed_schedule["Payment"] + var_schedule["Payment"]
    schedule["Principal Paid"] = fixed_schedule["Principal Paid"] + var_schedule["Principal Paid"]
    schedule["Interest Paid"] = fixed_schedule["Interest Paid"] + var_schedule["Interest Paid"]
    schedule["Balance"] = fixed_schedule["Balance"] + var_schedule["Balance"]

    # Calculate blended rate
    schedule["Rate"] = (
            (fixed_schedule["Rate"] * fixed_portion + var_schedule["Rate"] * variable_portion) /
            (fixed_portion + variable_portion)
    )

    return schedule


def simulate_portion_fixed(portion_amount, amortization_years, horizon_years,
                          fixed_initial_rate, fixed_term_years, fixed_renewal_rate):
    """Simulate fixed portion of split mortgage"""
    schedule = pd.DataFrame()
    balance = portion_amount
    total_months = horizon_years * 12
    remaining_amort = amortization_years * 12
    month = 0

    while month < total_months and balance > 0:
        term = min(fixed_term_years * 12, total_months - month)
        rate = fixed_initial_rate if month == 0 else fixed_renewal_rate

        df = amortize_with_rate_changes(balance, rate, term, month, amortization_months=remaining_amort)
        schedule = pd.concat([schedule, df], ignore_index=True)

        balance = df.iloc[-1]["Balance"]
        remaining_amort -= term
        month += term

    return schedule


def simulate_portion_variable(portion_amount, amortization_years, horizon_years,
                             prime_rate, variable_discount_initial, variable_term_years,
                             variable_renewal_discount, variable_fixed_payment,
                             use_rate_cuts, cut_schedule, rate_cut_amount):
    """Simulate variable portion of split mortgage"""
    schedule = pd.DataFrame()
    balance = portion_amount
    total_months = horizon_years * 12
    remaining_amort = amortization_years * 12
    month = 0
    fixed_payment_amount = None

    # Use same rate cuts as full variable
    if use_rate_cuts:
        prime_reductions = create_rate_path(cut_schedule, rate_cut_amount, total_months)
    else:
        prime_reductions = {}

    while month < total_months and balance > 0:
        discount = variable_discount_initial if month == 0 else variable_renewal_discount
        base_rate = prime_rate - discount
        term = min(variable_term_years * 12, total_months - month)

        # Convert prime reductions to variable rate reductions
        variable_reductions = {}
        for m, prime_cut in prime_reductions.items():
            if m > month and m <= month + term:
                variable_reductions[m] = prime_cut

        if variable_fixed_payment and fixed_payment_amount is not None:
            payment = fixed_payment_amount
        else:
            payment = monthly_payment(balance, base_rate, remaining_amort)
            if variable_fixed_payment and fixed_payment_amount is None:
                fixed_payment_amount = payment

        df = amortize_with_rate_changes(
            balance, base_rate, term, month,
            fixed_payment=payment if variable_fixed_payment else None,
            rate_reductions=variable_reductions,
            amortization_months=remaining_amort
        )

        schedule = pd.concat([schedule, df], ignore_index=True)
        balance = df.iloc[-1]["Balance"]
        remaining_amort -= term
        month += term

    return schedule