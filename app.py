import streamlit as st
import joblib

# app title
st.title("💼 Personal Finance Decision Engine")

# subtitle
st.subheader("Loan Decision Module")

# description
st.write("This tool helps you evaluate whether a loan is safe based on your financial profile.")

# user input - income
income = st.slider(
    "Select your Annual Income (₹)",
    min_value=100000,
    max_value=5000000,
    step=50000
)

# display selected value
st.write(f"Selected Income: ₹{income}")

# user input - loan amount
loan_amount = st.slider(
    "Select Loan Amount (₹)",
    min_value=50000,
    max_value=2000000,
    step=50000
)

# display selected value
st.write(f"Selected Loan Amount: ₹{loan_amount}")

# user input - interest rate
interest_rate = st.slider(
    "Select Interest Rate (%)",
    min_value=5.0,
    max_value=20.0,
    step=0.5
)

st.write(f"Interest Rate: {interest_rate}%")

# user input - loan term
loan_term = st.slider(
    "Select Loan Term (months)",
    min_value=6,
    max_value=120,
    step=6
)

st.write(f"Loan Term: {loan_term} months")

# calculate monthly interest rate
monthly_rate = interest_rate / (12 * 100)

# EMI calculation function
def calculate_emi(P, r, n):
    return (P * r * (1 + r)**n) / ((1 + r)**n - 1)

# calculate EMI
emi = calculate_emi(loan_amount, monthly_rate, loan_term)

# display EMI
st.subheader("📊 EMI Calculation")
st.write(f"Monthly EMI: ₹{emi:,.2f}")

# convert annual income to monthly
monthly_income = income / 12

# calculate EMI to income ratio
emi_ratio = emi / monthly_income

st.subheader("📈 Affordability Analysis")

st.write(f"Monthly Income: ₹{monthly_income:,.2f}")
st.write(f"EMI to Income Ratio: {emi_ratio*100:.1f}%")

# risk categorization
if emi_ratio <= 0.20:
    risk = "Safe"
elif emi_ratio <= 0.30:
    risk = "Low Risk"
elif emi_ratio <= 0.40:
    risk = "Moderate Risk"
elif emi_ratio <= 0.50:
    risk = "High Risk"
elif emi_ratio <= 0.75:
    risk = "Very High Risk"
else:
    risk = "Unsustainable"

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
    'Income': income,
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

st.write(decision)

if "Safe" in decision:
    st.success(decision)
elif "caution" in decision:
    st.warning(decision)
else:
    st.error(decision)