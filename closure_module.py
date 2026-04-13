def calculate_surplus(monthly_income, monthly_expenses, additional_income, current_emi):
    # convert additional income
    monthly_additional_income = additional_income / 12 if additional_income else 0

    # usable income
    usable_income = monthly_income + monthly_additional_income - monthly_expenses

    # available extra money
    available_extra = usable_income - current_emi

    return usable_income, available_extra

def calculate_new_tenure(P, r, emi, extra_payment):
    total_payment = emi + extra_payment
    months = 0

    while P > 0:
        interest = P * r
        principal = total_payment - interest

        if principal <= 0:
            return None

        P -= principal
        months += 1

        if months > 1000:
            return None

    return months

def calculate_interest(P, r, emi, months):
    total_paid = emi * months
    interest_paid = total_paid - P
    return interest_paid

def calculate_with_lumpsum(P, r, emi, yearly_lump):
    months = 0

    while P > 0:
        interest = P * r
        principal = emi - interest

        if principal <= 0:
            return None

        P -= principal
        months += 1

        # every 12 months → apply lump sum
        if months % 12 == 0 and yearly_lump > 0:
            P -= yearly_lump

        if months > 1000:
            return None

    return months

def calculate_combined_strategy(P, r, emi, extra_payment, yearly_lump):
    total_payment = emi + extra_payment
    months = 0

    while P > 0:
        interest = P * r
        principal = total_payment - interest

        if principal <= 0:
            return None

        P -= principal
        months += 1

        # apply yearly lump sum
        if months % 12 == 0 and yearly_lump > 0:
            P -= yearly_lump

        if months > 1000:
            return None

    return months

def calculate_correct_emi(P, r, n):
    if r == 0:
        return P / n
    return (P * r * (1 + r)**n) / ((1 + r)**n - 1)

def suggest_optimal_payment(P, r, emi, max_extra):
    best_extra = 0
    best_tenure = float('inf')

    # try different values (step = 500 or 1000)
    for extra in range(1000, int(max_extra)+1, 500):
        tenure = calculate_new_tenure(P, r, emi, extra)

        if tenure and tenure < best_tenure:
            best_tenure = tenure
            best_extra = extra

    return best_extra, best_tenure

def simulate_loan(P, r, emi):
    total_paid = 0
    total_interest = 0
    months = 0

    while P > 0:
        interest = P * r
        principal = emi - interest

        if principal <= 0:
            break

        if principal >= P:
            total_interest += interest
            total_paid += P + interest
            break

        P -= principal
        total_paid += emi
        total_interest += interest
        months += 1

    return total_paid, total_interest, months

def simulate_loan_with_lumpsum(P, r, emi, yearly_lump):
    total_paid = 0
    total_interest = 0
    months = 0

    while P > 0:
        interest = P * r
        principal = emi - interest

        if principal <= 0:
            break

        if principal >= P:
            total_interest += interest
            total_paid += P + interest
            break

        P -= principal
        total_paid += emi
        total_interest += interest
        months += 1

        if months % 12 == 0 and yearly_lump > 0:
            if yearly_lump >= P:
                total_paid += P
                break
            P -= yearly_lump
            total_paid += yearly_lump

    return total_paid, total_interest, months

def simulate_combined_strategy(P, r, emi, extra_payment, yearly_lump):
    total_paid = 0
    months = 0

    while P > 0:
        # apply yearly lump BEFORE EMI interest calculation
        if months % 12 == 0 and months != 0 and yearly_lump > 0:
            if yearly_lump >= P:
                total_paid += P
                break
            P -= yearly_lump
            total_paid += yearly_lump

        total_emi = emi + extra_payment

        interest = P * r
        principal = total_emi - interest

        if principal <= 0:
            break

        if principal >= P:
            total_paid += P + interest
            break

        P -= principal
        total_paid += total_emi
        months += 1

    return total_paid, months
