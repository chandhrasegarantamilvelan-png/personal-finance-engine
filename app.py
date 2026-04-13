import streamlit as st
import joblib
import time
from loan_module import calculate_emi, get_risk
from closure_module import (
    calculate_surplus,
    calculate_new_tenure,
    calculate_interest,
    calculate_with_lumpsum,
    calculate_combined_strategy,
    suggest_optimal_payment,
    simulate_loan,
    simulate_loan_with_lumpsum,
    simulate_combined_strategy
)

# app title
st.title("💼 Personal Finance Decision Engine")

# subtitle
st.subheader("Loan Decision Module")

# description
st.write("This tool helps you evaluate whether a loan is safe based on your financial profile.")

# module selector
module = st.selectbox(
    "Choose a Module",
    [
        "Select...",
        "Loan Decision Engine",
        "Loan Closure Planner",
        "Finance Health Score"
    ]
)
# selecting currency for user inputs and outputs
currency = st.selectbox(
"Select Currency",   # label shown in UI
["₹ INR", "$ USD", "€ EUR"]   # dropdown options
)

# extracting currency symbol from selected option
currency_symbol = currency.split()[0]

# show message if nothing selected
if module == "Select...":
    st.info("Please select a module to continue.")

elif module == "Loan Decision Engine":
    monthly_expenses = 0
    additional_income = 0

    col1, col2 = st.columns([2, 1])

    with col1:

        # user input - income
        monthly_income = st.number_input("Enter your Monthly Income (In-hand)",min_value=0)

        # display selected value
        st.write(f"Monthly Income: {currency_symbol}{monthly_income}")

        # user input - existing EMI
        existing_emi = st.number_input(
            f"Enter your Existing Monthly EMI ({currency_symbol})",
            min_value=0
        )

        # display existing EMI
        st.write(f"Existing EMI: {currency_symbol}{existing_emi:,.2f}")

        with col2:
            with st.expander("⚙ Advanced Settings"):

                monthly_expenses = st.number_input(
                    f"Monthly Expenses ({currency_symbol})",
                    min_value=0
                )

                additional_income = st.number_input(
                    f"Additional Annual Income ({currency_symbol})",
                    min_value=0
                )
        # user input - loan amount
        loan_amount = st.number_input(f"Enter Loan Amount ({currency_symbol})",min_value=0)

        # display selected value
        st.write(f"Required Loan Amount: {currency_symbol}{loan_amount:,.2f}")

        # user input - interest rate
        interest_rate = st.slider("Enter Interest Rate (%)",min_value=0.0,max_value=50.0,step=0.05)

        st.write(f"Interest Rate: {interest_rate}%")

        # user input - loan term
        loan_term = st.number_input(
            "Enter Loan Term (months)",
            min_value=1,
            step=1
        )
        
        st.write(f"Loan Term: {loan_term} months")

        # calculate monthly interest rate
        monthly_rate = interest_rate / (12 * 100)

        # calculate EMI
        if loan_term > 0:
            emi = calculate_emi(loan_amount, monthly_rate, loan_term)
        else:
            emi = 0

        # calculating total EMI (existing + new loan)
        total_emi = emi + existing_emi

        # display EMI
        st.subheader("📊 EMI Calculation")
        st.write(f"Monthly EMI: {currency_symbol}{emi:,.2f}")
        st.write(f"Total EMI (including existing loans): {currency_symbol}{total_emi:,.2f}")

        # calculate usable income after expenses
        monthly_additional_income = additional_income / 12 if additional_income else 0

        # calculate usable income including additional income
        usable_income = monthly_income + monthly_additional_income - monthly_expenses

        # calculate EMI to income ratio
        if usable_income > 0:
            emi_ratio = total_emi / usable_income
        else:
            emi_ratio = 0

        st.subheader("📈 Affordability Analysis")

        st.write(f"Monthly Income: {currency_symbol}{monthly_income:,.2f}")
        st.write(f"Usable Income (after expenses): {currency_symbol}{usable_income:,.2f}")
        st.write(f"EMI to Usable Income Ratio: {emi_ratio*100:.1f}%")

        # affordability status (visual indicator)
        if emi_ratio <= 0.3:
            st.success("Affordability Status: ✅ Safe")
        elif emi_ratio <= 0.5:
            st.warning("Affordability Status: ⚠ Moderate")
        else:
            st.error("Affordability Status: ❌ High Risk")

        # calculate risk
        risk = get_risk(emi_ratio)

        # display risk
        st.subheader("⚠ Risk Level")
        st.write(risk)

        # load trained model
        model = joblib.load("loan_model.pkl")

        st.subheader("🤖 Model Prediction")

        # create sample input for model (basic version)
        import pandas as pd

        input_data = pd.DataFrame([{
            'Age': 30,
            'Income': monthly_income,
            'LoanAmount': loan_amount,
            'CreditScore': 700,
            'MonthsEmployed': 60,
            'NumCreditLines': 3,
            'InterestRate': interest_rate,
            'LoanTerm': loan_term,
            'DTIRatio': 0.3
        }])

        # match training columns
        input_data = pd.get_dummies(input_data)
        input_data = input_data.reindex(columns=model.feature_names_in_, fill_value=0)

        # get probability
        prob = model.predict_proba(input_data)[0][1]

        st.write(f"Default Probability: {prob*100:.2f}%")

        st.subheader("📊 Final Decision")

        # decision logic
        if emi_ratio < 0.3 and prob < 0.2:
            decision = "✅ Safe to proceed"
        elif emi_ratio < 0.5 and prob < 0.4:
            decision = "⚠️ Proceed with caution"
        else:
            decision = "❌ Not recommended"


        if "Safe" in decision:
            st.success(decision)
        elif "caution" in decision:
            st.warning(decision)
        else:
            st.error(decision)

        # smart suggestion based on EMI burden
        if usable_income > 0 and total_emi > usable_income * 0.5:
            st.info("💡 Suggestion: Your EMI is taking a large portion of your usable income. Consider increasing the loan tenure to reduce monthly burden.") 

        # suggestion to reduce loan amount
        if emi_ratio > 0.4:
            st.info("💡 Suggestion: Consider reducing the loan amount to improve affordability.")

        # suggestion to negotiate interest rate
        if interest_rate > 12:
            st.info("💡 Suggestion: Try negotiating for a lower interest rate to reduce your EMI.") 

        # ideal EMI recommendation
        st.subheader("💡 Ideal Loan Recommendation")
        st.caption(
        "This recommendation is based on your usable income, existing EMIs, "
        "and a safe affordability threshold adjusted to your financial risk level."
        )
        
        # dynamic safe EMI limit based on affordability
        if emi_ratio <= 0.3:
            safe_emi_limit = 0.35 * monthly_income
        elif emi_ratio <= 0.5:
            safe_emi_limit = 0.30 * monthly_income
        else:
            safe_emi_limit = 0.20 * monthly_income

        # remaining EMI capacity
        available_emi = safe_emi_limit - existing_emi

        if available_emi > 0:
            st.success(f"✔ You can safely afford an EMI of up to {currency_symbol}{available_emi:,.2f}")

            # calculate max loan
            factor = ((1 + monthly_rate)**loan_term - 1) / (monthly_rate * (1 + monthly_rate)**loan_term)
            max_loan = available_emi * factor

            st.success(f"💰 Recommended Loan Amount: {currency_symbol}{max_loan:,.2f}")

        else:
            st.error("⚠ Your current EMI obligations are too high. Consider reducing existing loans before taking a new one.")


elif module == "Loan Closure Planner":
    st.subheader("🏁 Loan Closure Planner")

    st.write("Plan how to close your loan faster and reduce interest burden.")

    # inputs
    current_loan = st.number_input(
        f"Current Loan Amount ({currency_symbol})",
        min_value=0
    )

    interest_rate = st.slider(
        "Interest Rate (%)",
        0.0,
        50.0,
        step=0.1
    )
    
    current_emi = st.number_input(
        f"Current EMI ({currency_symbol})",
        min_value=0
    )

    total_tenure = st.number_input(
        "Total Loan Tenure (months)",
        min_value=1
    )

    months_paid = st.number_input(
        "Months Already Paid",
        min_value=0,
        max_value=total_tenure
    )


    monthly_income = st.number_input("Monthly Income", min_value=0)
    monthly_expenses = st.number_input("Monthly Expenses", min_value=0)
    additional_income = st.number_input("Additional Annual Income", min_value=0)

    # calculating usable income and available extra
    usable_income, available_extra = calculate_surplus(
        monthly_income,
        monthly_expenses,
        additional_income,
        current_emi
    )

    # extra monthly payment
    extra_payment = st.number_input(
        f"Extra Monthly Payment ({currency_symbol})",
        min_value=0,
        max_value=int(available_extra) if available_extra > 0 else 0
    )

    # yearly lump sum
    yearly_lump = st.number_input(
        f"Yearly Lump Sum Payment ({currency_symbol})",
        min_value=0
    )
    lump_mode = st.radio(
        "When will you apply the lump sum?",
        ["At year-end (12th month)", "Apply immediately (recommended for short-term loans)"]
    )

    # calculate monthly rate
    monthly_rate = interest_rate / (12 * 100)

    # total loan payable calculation
    total_payment = current_emi * total_tenure
    

    # amount already paid
    amount_paid = current_emi * months_paid

    # calculate remaining principal using EMI formula
    P = current_loan
    r = monthly_rate

    for _ in range(months_paid):
        interest = P * r
        principal = current_emi - interest
        P -= principal

    remaining_principal = P
    remaining_months = total_tenure - months_paid

    total_interest = total_payment - current_loan

    simple_interest = current_loan * (interest_rate/100) * (total_tenure/12)
    approx_total = current_loan + simple_interest

    expected_emi = calculate_emi(
        current_loan,
        monthly_rate,
        total_tenure
    )

    if abs(expected_emi - current_emi) > 200:  # tolerance ₹200
        st.warning(
            f"⚠️ Your EMI may not align with loan details.\n\n"
            f"Expected EMI: {currency_symbol}{expected_emi:,.0f}"
        )

    new_tenure = calculate_new_tenure(
        remaining_principal,
        monthly_rate,
        current_emi,
        extra_payment
    )
    
    original_total_payment = current_emi * remaining_months
    
    st.subheader("📊 Loan Status Overview")

    st.write(f"Total Loan Payable: {currency_symbol}{total_payment:,.2f}")
    st.write(f"Total Interest: {currency_symbol}{total_interest:,.2f}")
    st.write(f"Amount Paid So Far: {currency_symbol}{amount_paid:,.2f}")

    st.success(
        f"💰 Remaining Payable: {currency_symbol}{remaining_principal:,.2f}"
    )

    st.write(f"Remaining Tenure: {remaining_months} months")

    st.subheader("💰 Available Surplus")

    if available_extra > 0:
        st.success(
            f"💰 You have **{currency_symbol}{available_extra:,.2f}** available every month after expenses and EMIs."
        )    
    else:
        st.error("You currently have no surplus. Increasing EMI may not be advisable.")
    st.subheader("⚙️ Choose Your Strategy")

    # suggested safe max
    st.caption(f"You can safely use up to {currency_symbol}{available_extra:,.2f} per month.")
    
    st.subheader("📉 Loan Closure Impact Overview")
    st.caption("Explore how different repayment strategies affect your loan tenure and total interest paid.")
    
    # original interest
    original_interest = calculate_interest(
        remaining_principal,
        monthly_rate,
        current_emi,
        remaining_months
    )

    # simulate original loan
    original_total_payment, original_interest, _ = simulate_loan(
        remaining_principal,
        monthly_rate,
        current_emi
    )

    new_total_payment, new_interest, sim_months = simulate_loan(
        remaining_principal,
        monthly_rate,
        current_emi + extra_payment
    )

    interest_saved = original_interest - new_interest
    new_tenure = sim_months

    st.markdown("### 💳 With Extra Monthly Payment")

    if new_tenure:
        reduction = max(0, remaining_months - new_tenure)

        st.success(
            f"You can close your loan in **{new_tenure} months** "
            f"and save **{currency_symbol}{interest_saved:,.0f}** in interest.\n\n"
            f"📉 You finish your loan **{reduction} months earlier**."
        )


    lump_tenure = calculate_with_lumpsum(
        remaining_principal,
        monthly_rate,
        current_emi,
        yearly_lump
    )

    # simulate lump sum strategy
    if lump_mode == "Apply immediately (recommended for short-term loans)":
        # apply lump at start
        adjusted_principal = remaining_principal - yearly_lump

        # safety check
        if adjusted_principal <= 0:
            lump_total_payment = yearly_lump
            lump_interest = 0
            sim_months = 1
        else:
            lump_total_payment, lump_interest, sim_months = simulate_loan(
                adjusted_principal,
                monthly_rate,
                current_emi
            )
    else:
        # default yearly lump logic
        lump_total_payment, lump_interest, sim_months = simulate_loan_with_lumpsum(
            remaining_principal,
            monthly_rate,
            current_emi,
            yearly_lump
        )

    lump_saved = original_interest - lump_interest
    lump_tenure = sim_months

    lump_saved = original_interest - lump_interest
    lump_tenure = sim_months

    st.markdown("### 📅 With Yearly Lump Sum")

    if lump_tenure:
        reduction =max(0, remaining_months - lump_tenure) 

        st.success(
            f"You can close your loan in **{lump_tenure} months** "
            f"and save **{currency_symbol}{lump_saved:,.0f}** in interest.\n\n"
            f"📉 You finish your loan **{reduction} months earlier**."
        )
    # calculate alternate scenario for comparison

    if yearly_lump > 0:

        # simulate immediate lump (alternative)
        alt_principal = remaining_principal - yearly_lump

        if alt_principal > 0:
            alt_total, alt_interest, _ = simulate_loan(
                alt_principal,
                monthly_rate,
                current_emi
            )
        else:
            alt_interest = 0

        # compare based on selected mode
        if lump_mode == "At year-end (12th month)":
            extra_saving = lump_interest - alt_interest

            if extra_saving > 0:
                st.info(
                    f"💡 If you apply the lump sum immediately instead of waiting, "
                    f"you could save an additional **{currency_symbol}{extra_saving:,.0f}** in interest."
                )

        else:  # immediate mode selected
            extra_loss = alt_interest - lump_interest

            if extra_loss > 0:
                st.info(
                    f"💡 Delaying this lump sum to year-end would cost you approximately "
                    f"**{currency_symbol}{extra_loss:,.0f}** more in interest."
                )
    st.divider()

    st.markdown("### 🧠 Insight")

    if lump_mode == "Apply immediately (recommended for short-term loans)":
        st.success("✅ You chose to apply the lump sum immediately — this maximizes interest savings.")
    else:
        st.warning("⚠️ You chose to apply the lump sum at year-end — this may reduce its effectiveness.")
      

    combined_total_payment, sim_months = simulate_combined_strategy(
        remaining_principal,
        monthly_rate,
        current_emi,
        extra_payment,
        yearly_lump
    )

    combined_saved = original_total_payment - combined_total_payment
    combined_tenure = sim_months

    st.markdown("### 🚀 Combined Strategy (Monthly + Yearly)")

    if combined_tenure:
        reduction = max(0, remaining_months - combined_tenure)
        if combined_tenure == new_tenure:
            st.info(
                "ℹ️ In this case, your increased monthly payment closes the loan before the yearly lump sum is applied. "
                "So the combined strategy performs the same as the monthly strategy."
            )
            st.success(
                f"You can close your loan in **{combined_tenure} months** "
                f"and save **{currency_symbol}{combined_saved:,.0f}** in interest.\n\n"
                f"📉 You finish your loan **{reduction} months earlier**."
            )
    
    # ensure values exist safely
    interest_saved = locals().get('interest_saved', 0)
    lump_saved = locals().get('lump_saved', 0)
    combined_saved = locals().get('combined_saved', 0)

    # prevent negative values (rounding / edge cases)
    interest_saved = max(0, interest_saved)
    lump_saved = max(0, lump_saved)
    combined_saved = max(0, combined_saved)

    # calculate savings in months
    monthly_score = interest_saved
    lump_score = lump_saved
    combined_score = combined_saved 
    
    # determine best strategy
    strategy_scores = {
        "Monthly Extra Payment": monthly_score,
        "Yearly Lump Sum": lump_score,
        "Combined Strategy": combined_score
    }

    # filter only valid strategies
    valid_strategies = {k: v for k, v in strategy_scores.items() if v > 0}

    if valid_strategies:
        best_strategy = max(valid_strategies, key=valid_strategies.get)
    else:
        best_strategy = None

    optimal_extra, optimal_tenure = suggest_optimal_payment(
        remaining_principal,
        monthly_rate,
        current_emi,
        available_extra * 0.8  # leave buffer
    )

    if best_strategy:
        st.markdown("## 🏆 Best Strategy for You")
        st.caption(
        "💡 Monthly extra payments reduce your loan tenure faster, while lump sum payments reduce total interest more significantly."
    )

        if best_strategy == "Monthly Extra Payment":
            best_value = interest_saved
            best_months = max(0, remaining_months - new_tenure)

        elif best_strategy == "Yearly Lump Sum":
            best_value = lump_saved
            best_months = max(0, remaining_months - lump_tenure)

        else:
            best_value = combined_saved
            best_months = max(0, remaining_months - combined_tenure)

        st.success(
            f"🎯 **{best_strategy} is the most effective option for you**\n\n"
            f"💰 You save **{currency_symbol}{best_value:,.0f}** in interest\n"
            f"⏳ You close your loan **{best_months} months earlier**"
        )
    else:
        st.warning("No strategy provides meaningful improvement with current inputs.")
    

    import pandas as pd

    # round tenure
    new_tenure = int(round(new_tenure)) if new_tenure else 0
    lump_tenure = int(round(lump_tenure)) if lump_tenure else 0
    combined_tenure = int(round(combined_tenure)) if combined_tenure else 0

    # calculate months saved
    monthly_saving = max(0, remaining_months - new_tenure)
    lump_saving = max(0, remaining_months - lump_tenure)
    combined_saving = max(0, remaining_months - combined_tenure)

    # round savings (money)
    interest_saved = int(round(interest_saved))
    lump_saved = int(round(lump_saved))
    combined_saved = int(round(combined_saved))
    
    comparison_data = pd.DataFrame({
        "Strategy": ["Monthly", "Lump Sum", "Combined"],
        "Tenure (months)": [new_tenure, lump_tenure, combined_tenure],
        "Months Saved": [monthly_saving, lump_saving, combined_saving],
        "Interest Saved": [
            f"{currency_symbol}{interest_saved:,.0f}",
            f"{currency_symbol}{lump_saved:,.0f}",
            f"{currency_symbol}{combined_saved:,.0f}"
        ]
    })

    st.subheader("📊 Strategy Comparison")
    st.dataframe(comparison_data)  

    best_idx = comparison_data["Interest Saved"].str.replace(r"[^\d]", "", regex=True).astype(int).idxmax()

    st.success(f"🏆 Best Strategy: **{comparison_data.loc[best_idx, 'Strategy']}**")  

elif module == "Finance Health Score":
    st.subheader("📊 Finance Health Score")

    st.write("Evaluate your financial health across income, expenses, assets, and investments.")

    # 💰 Income
    st.markdown("### 💰 Income")

    monthly_income = st.number_input("Monthly Income", min_value=0)

    additional_monthly_income = st.number_input(
        "Additional Monthly Income (optional)", min_value=0
    )

    additional_yearly_income = st.number_input(
        "Additional Yearly Income (bonus, rent, etc.)", min_value=0
    )

    # 💸 Expenses
    st.markdown("### 💸 Expenses")
    monthly_expenses = st.number_input("Monthly Expenses", min_value=0)

    # 🧾 Obligations (Debt)
    st.markdown("### 🧾 Obligations")
    monthly_emi = st.number_input("Loan EMI", min_value=0)
    other_obligations = st.number_input("Other Monthly Obligations", min_value=0)

    # 💧 Liquid Assets
    st.markdown("### 💧 Liquid Assets")
    cash_in_hand = st.number_input("Cash in Hand", min_value=0)
    bank_balance = st.number_input("Bank Balance", min_value=0)

    # 🏠 Assets
    st.markdown("### 🏠 Assets")
    property_value = st.number_input("Property Value", min_value=0)

    gold_grams = st.number_input("Gold (grams)", min_value=0)
    gold_rate = st.number_input("Gold Price per Gram", min_value=0)

    # 📈 Investments
    st.markdown("### 📈 Investments")
    mutual_funds = st.number_input("Mutual Funds", min_value=0)
    stocks = st.number_input("Stocks", min_value=0)
    pf = st.number_input("Provident Fund (PF)", min_value=0)
    other_investments = st.number_input("Other Investments", min_value=0)

    col1, col2, col3 = st.columns([1, 2, 1])

    st.markdown(
        """
        <style>
        div.stButton > button {
            background-color: #4CAF50;
            color: white;
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 10px;
            border: none;
        }

        div.stButton > button:hover {
            background-color: #45a049;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    with col2:
        calculate_score = st.button("🚀 Check My Financial Health Score")
    
    if calculate_score:

        # =========================
        # ⚠️ Input Validation (Flexible)
        # =========================

        if monthly_income <= 0:
            st.warning("⚠️ Please enter your monthly income to calculate your score.")
            st.stop()

        if monthly_expenses <= 0:
            st.warning("⚠️ Please enter your monthly expenses to calculate your score.")
            st.stop()
            
        # =========================
        # 📊 Aggregated Values
        # =========================

        # 💰 Income
        monthly_additional_from_yearly = additional_yearly_income / 12 if additional_yearly_income else 0

        total_income = (
            monthly_income +
            additional_monthly_income +
            monthly_additional_from_yearly
        )

        # 🧾 Obligations
        total_obligations = monthly_emi + other_obligations

        # 💸 Net Savings
        net_savings = total_income - monthly_expenses - total_obligations

        # 💧 Liquid Assets
        total_liquid_assets = cash_in_hand + bank_balance

        # 🏠 Assets
        gold_value = gold_grams * gold_rate
        total_assets = property_value + gold_value

        # 📈 Investments
        total_investments = mutual_funds + stocks + pf + other_investments


        # =========================
        # 📐 Derived Ratios
        # =========================

        savings_rate = net_savings / total_income if total_income > 0 else 0
        debt_ratio = total_obligations / total_income if total_income > 0 else 0
        emergency_months = total_liquid_assets / monthly_expenses if monthly_expenses > 0 else 0
        investment_ratio = total_investments / total_assets if total_assets > 0 else 0
        asset_income_ratio = total_assets / (total_income * 12) if total_income > 0 else 0

        # =========================
        # 📊 Normalized Scores (%)
        # =========================

        savings_pct = min(savings_rate / 0.30, 1.0) * 100
        debt_pct = max(0, (1 - debt_ratio / 0.50)) * 100
        emergency_pct = min(emergency_months / 6, 1.0) * 100
        investment_pct = min(investment_ratio / 0.40, 1.0) * 100
        networth_pct = min(asset_income_ratio / 5, 1.0) * 100

        # =========================
        # ⚖️ Weighted Scores
        # =========================

        savings_score = (savings_pct / 100) * 25
        debt_score = (debt_pct / 100) * 25
        emergency_score = (emergency_pct / 100) * 20
        investment_score = (investment_pct / 100) * 15
        networth_score = (networth_pct / 100) * 15

        base_score = (
            savings_score +
            debt_score +
            emergency_score +
            investment_score +
            networth_score
        )

        # =========================
        # 🏅 Consistency Bonus
        # =========================

        min_metric = min(
            savings_pct,
            debt_pct,
            emergency_pct,
            investment_pct,
            networth_pct
        )

        bonus_score = min(int(min_metric // 10), 10)

        # =========================
        # 🎯 Final Score
        # =========================

        final_score = base_score + bonus_score
        final_score = min(final_score, 110)  # cap


        with st.spinner("Analyzing your financial health..."):
            time.sleep(1.5)

        st.markdown("## 🎯 Your Financial Health Score")

        if final_score >= 90:
            bg_color = "#d4edda"  # green
        elif final_score >= 70:
            bg_color = "#fff3cd"  # yellow
        else:
            bg_color = "#f8d7da"  # red

        st.markdown(
            """
            <style>
            .fade-in {
                animation: fadeIn 1.2s ease-in;
            }

            @keyframes fadeIn {
                from {opacity: 0; transform: translateY(10px);}
                to {opacity: 1; transform: translateY(0);}
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        score_placeholder = st.empty()

        animated_score = 0
        target = int(final_score)

        for i in range(0, target + 1, max(1, target // 30)):
            animated_score = i

            score_placeholder.markdown(
                f"""
                <div class="fade-in" style="
                    text-align: center;
                    padding: 30px;
                    border-radius: 15px;
                    background: {bg_color};
                    box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
                ">
                    <h2>🎯 Your Financial Health Score</h2>
                    <h1 style="font-size: 60px;">
                        {animated_score} / 110
                    </h1>
                </div>
                """,
                unsafe_allow_html=True
            )

            time.sleep(0.02)

        score_placeholder.markdown(
            f"""
            <div class="fade-in" style="
                text-align: center;
                padding: 30px;
                border-radius: 15px;
                background: {bg_color};
                box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
            ">
                <h2>🎯 Your Financial Health Score</h2>
                <h1 style="font-size: 60px;">
                    {int(final_score)} / 110
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("📊 Detailed Financial Analysis"):    

            if final_score >= 90:
                st.success("🟢 Excellent financial health")
            elif final_score >= 70:
                st.info("🟡 Good financial health")
            elif final_score >= 50:
                st.warning("🟠 Needs improvement")
            else:
                st.error("🔴 Financial risk — immediate attention needed")

            

            import pandas as pd

            breakdown = pd.DataFrame({
                "Category": [
                    "Savings",
                    "Debt",
                    "Emergency Fund",
                    "Investments",
                    "Net Worth"
                ],
                "Score": [
                    int(savings_score),
                    int(debt_score),
                    int(emergency_score),
                    int(investment_score),
                    int(networth_score)
                ],
                "Performance (%)": [
                    int(savings_pct),
                    int(debt_pct),
                    int(emergency_pct),
                    int(investment_pct),
                    int(networth_pct)
                ]
            })

            st.subheader("📊 Score Breakdown")
            st.dataframe(breakdown)

            st.subheader("🏅 Consistency Bonus")

            st.info(
                f"Your weakest financial metric is **{int(min_metric)}%**, "
                f"giving you a consistency bonus of **{bonus_score}/10**.\n\n"
                f"💡 Improving your lowest area will boost your score the fastest."
            )

            # find weakest category
            categories = {
                "Savings": savings_pct,
                "Debt": debt_pct,
                "Emergency Fund": emergency_pct,
                "Investments": investment_pct,
                "Net Worth": networth_pct
            }

            weakest_area = min(categories, key=categories.get)

            st.subheader("💡 Key Insight")

            st.warning(
                f"Your weakest area is **{weakest_area}**.\n\n"
                f"👉 Improving this will have the biggest impact on your financial health score."
            )


