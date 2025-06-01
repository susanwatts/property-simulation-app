
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

st.title("Single Property Investment Simulator")

# Sidebar for parameters
st.sidebar.header("Simulation Parameters")

initial_loan = st.sidebar.number_input("Initial Loan Balance", value=618919.64)
monthly_installment = st.sidebar.number_input("Monthly Installment (Initial)", value=6096.28)
service_fee = st.sidebar.number_input("Monthly Service Fee", value=69.00)
loan_term = st.sidebar.number_input("Loan Term (Months)", value=219)
bond_annual_rate = st.sidebar.number_input("Interest Rate (Bond, Annual)", value=0.0955)
rental_income = st.sidebar.number_input("Initial Rental Income", value=6500.0)
rent_escalation = st.sidebar.number_input("Rental Escalation Rate", value=0.04)
levy = st.sidebar.number_input("Initial Levy", value=1060.0)
rates = st.sidebar.number_input("Initial Rates", value=200.0)
expense_escalation = st.sidebar.number_input("Expense Escalation Rate", value=0.04)
capital_growth = st.sidebar.number_input("Capital Growth Rate", value=0.05)
bank_annual_rate = st.sidebar.number_input("Bank Interest Rate (Annual)", value=0.05)
income_goal_start = st.sidebar.number_input("Income Goal (Month 1)", value=130000.0)
income_goal_escalation = st.sidebar.number_input("Income Goal Escalation Rate", value=0.04)
age_start = st.sidebar.number_input("Current Age", value=42)
age_end = st.sidebar.number_input("End Age", value=105)

# Derived values
simulation_months = (int(age_end) - int(age_start) + 1) * 12
bond_monthly_rate = (1 + bond_annual_rate) ** (1 / 12) - 1
bank_monthly_rate = (1 + bank_annual_rate) ** (1 / 12) - 1

# Run simulation
data = []
remaining_balance = initial_loan
cumulative_shortfall = 0
break_even = False

for month in range(1, simulation_months + 1):
    year_index = (month - 1) // 12
    age = int(age_start) + year_index

    rent = rental_income * (1 + rent_escalation) ** year_index
    levy_amt = levy * (1 + expense_escalation) ** year_index
    rates_amt = rates * (1 + expense_escalation) ** year_index
    capital_value = initial_loan * (1 + capital_growth) ** year_index
    goal_income = income_goal_start * (1 + income_goal_escalation) ** year_index
    fee = service_fee * (1 + expense_escalation) ** year_index if month <= loan_term else 0

    if month <= loan_term:
        interest = remaining_balance * bond_monthly_rate
        principal = monthly_installment - interest
        remaining_balance -= principal
        bond_payment = monthly_installment
    else:
        interest = 0
        principal = 0
        bond_payment = 0

    total_cost = bond_payment + fee + levy_amt + rates_amt
    net_outflow = total_cost - rent

    if not break_even and net_outflow > 0:
        cumulative_shortfall = (cumulative_shortfall + net_outflow) * (1 + bank_monthly_rate)
    else:
        break_even = True
        cumulative_shortfall *= (1 + bank_monthly_rate)

    data.append([
        month, age, round(bond_payment, 2), round(fee, 2), round(levy_amt, 2), round(rates_amt, 2),
        round(rent, 2), round(goal_income, 2), round(capital_value, 2), round(net_outflow, 2),
        round(cumulative_shortfall, 2)
    ])

# Convert to DataFrame
columns = [
    "Month", "Age", "Bond Payment", "Service Fee", "Levy", "Rates",
    "Rental Income", "Goal Income", "Capital Value", "Net Outflow",
    "Hypothetical Investment Value"
]
df = pd.DataFrame(data, columns=columns)

# Display table
st.subheader("Simulation Results")
st.dataframe(df, use_container_width=True)

# Plot
st.subheader("📈 Investment Growth Over Time")
fig, ax = plt.subplots()
ax.plot(df["Month"], df["Hypothetical Investment Value"], label="Investment Value", color="green")
ax.set_xlabel("Month")
ax.set_ylabel("Value (ZAR)")
ax.set_title("Hypothetical Investment Growth")
ax.legend()
st.pyplot(fig)

# Download
filename = f"property_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
st.download_button(
    label="📥 Download Excel File",
    data=df.to_excel(index=False, engine='openpyxl'),
    file_name=filename,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
