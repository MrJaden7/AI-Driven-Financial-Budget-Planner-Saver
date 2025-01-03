import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import google.generativeai as genai
import json

# Replace with your actual Gemini API key
GEMINI_API_KEY = "put api key here"
genai.configure(api_key=GEMINI_API_KEY)


def generate_gemini_advice(income, expenses, savings_goal):
    try:
        prompt = f"Provide personalized financial advice for a person with monthly income {income}, monthly expenses {expenses}, and a savings goal of {savings_goal}. Suggest ways to reduce expenses and increase savings."
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error interacting with Gemini API: {e}")
        return "Failed to generate advice."


def predict_savings(income, expenses, months):
    monthly_savings = income - expenses
    return monthly_savings * months if monthly_savings > 0 else 0


def load_data(file):
    try:
        data = pd.read_csv(file)
        # Ensure 'Date' column is in datetime format
        data['Date'] = pd.to_datetime(data['Date'])
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def calculate_totals(data):
    total_expenses = data['Amount'].sum()
    return total_expenses


def calculate_debt_schedule(principal, interest_rate, monthly_payment):
    schedule = []
    remaining_balance = principal
    month = 1
    while remaining_balance > 0:
        interest = (remaining_balance * (interest_rate / 100)) / 12
        principal_payment = monthly_payment - interest
        remaining_balance -= principal_payment
        schedule.append({
            "Month": month,
            "Interest": round(interest, 2),
            "Principal Payment": round(principal_payment, 2),
            "Remaining Balance": max(round(remaining_balance, 2), 0)
        })
        month += 1
        if remaining_balance <= 0:
            break
    return pd.DataFrame(schedule)


def generate_debt_optimization_plan(principal, interest_rate, monthly_payment):
    try:
        prompt = f"Provide suggestions on how to manage and repay a debt of ₹{principal} with an interest rate of {interest_rate}% and a monthly payment of ₹{monthly_payment}. Include strategies to accelerate debt repayment and reduce interest costs."
        model = genai.GenerativeModel("gemini-1.5-flash")  # Use correct model
        response = model.generate_content(prompt)  # Generate content
        return response.text.strip() if response.text else "No actionable advice generated."
    except Exception as e:
        st.error(f"Error generating debt optimization plan: {e}")
        return "Failed to generate debt optimization plan."



def analyze_investment_portfolio(investments):
    try:
        prompt = f"Given the following investments: {investments}, suggest ways to optimize the portfolio considering market trends and personal financial goals."
        model = genai.GenerativeModel("gemini-1.5-flash")  # Use correct model
        response = model.generate_content(prompt)  # Generate content
        return response.text.strip()
    except Exception as e:
        st.error(f"Error analyzing investment portfolio: {e}")
        return "Failed to analyze portfolio."


def generate_financial_report(income, expenses, investments):
    prompt = f"Create a detailed financial report for a person with income {income}, monthly expenses {expenses}, and the following investments: {investments}. Include recommendations for optimizing finances."
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)  
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating financial report: {e}")
        return "Failed to generate financial report."



st.set_page_config(page_title="AI Savings & Budget Planner", layout="wide")


st.sidebar.title("AI Savings & Budget Planner")
page = st.sidebar.radio("Navigation", [
    "Dashboard", "Expense Tracker", "Savings Goals", "AI Insights", "Debt Tracker", "Investment Portfolio", "Reports", "Advanced Analytics"
])


if "income" not in st.session_state:
    st.session_state.income = 0
if "expenses" not in st.session_state:
    st.session_state.expenses = 0
if "savings_goal" not in st.session_state:
    st.session_state.savings_goal = 0
if "debts" not in st.session_state:
    st.session_state.debts = []
if "investments" not in st.session_state:
    st.session_state.investments = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None


def initialize_data():
    if "income" not in st.session_state:
        st.session_state.income = 0
    if "expenses" not in st.session_state:
        st.session_state.expenses = 0
    if "savings_goal" not in st.session_state:
        st.session_state.savings_goal = 0
    if "debts" not in st.session_state:
        st.session_state.debts = []
    if "investments" not in st.session_state:
        st.session_state.investments = []
    if "uploaded_data" not in st.session_state:
        st.session_state.uploaded_data = None


initialize_data()

if page == "Dashboard":
    st.title("Dashboard: Financial Overview")
    uploaded_file = st.sidebar.file_uploader("Upload Your Financial Data (CSV)", type="csv")

    if uploaded_file is not None:
        st.session_state.uploaded_data = load_data(uploaded_file)

    if st.session_state.uploaded_data is not None:
        data = st.session_state.uploaded_data
        st.write("### Your Financial Data")
        st.dataframe(data)

        total_expenses = calculate_totals(data)
        st.session_state.expenses = total_expenses
        st.write(f"### Total Expenses: ₹{total_expenses}")

        
        st.write("### Expense Distribution")
        fig = px.pie(data, names="Category", values="Amount", title="Expense Distribution")
        st.plotly_chart(fig)

elif page == "Expense Tracker":
    st.title("Expense Tracker")
    st.write("### Add New Expense")
    
    
    if "expenses" not in st.session_state or not isinstance(st.session_state.expenses, list):
        st.session_state.expenses = []  
    
    
    with st.form("add_expense"):
        category = st.text_input("Category")  
        amount = st.number_input("Amount", min_value=0.0)  
        date = st.date_input("Date", value=datetime.now().date())  
        recurring = st.selectbox("Recurring", ["Yes", "No"])  
        
        submitted = st.form_submit_button("Add Expense")  
        
        if submitted:
            new_expense = {
                "Category": category,
                "Amount": amount,
                "Date": date,
                "Recurring": recurring
            }
            st.session_state.expenses.append(new_expense)  

            
            st.success(f"Expense of ₹{amount} added to {category} on {date}.")
    
    
    if len(st.session_state.expenses) > 0:
        st.write("### Current Expenses")
        expenses_df = pd.DataFrame(st.session_state.expenses)  
        st.dataframe(expenses_df)  

    
    total_expenses = sum(expense["Amount"] for expense in st.session_state.expenses)  
    st.write(f"### Total Expenses: ₹{total_expenses:.2f}")

    
    if len(st.session_state.expenses) > 0:
        category_expenses = pd.DataFrame(st.session_state.expenses).groupby("Category")["Amount"].sum().reset_index()
        fig = px.pie(category_expenses, names="Category", values="Amount", title="Expense Distribution")
        st.plotly_chart(fig)




elif page == "Savings Goals":
    st.title("Savings Goals")
    st.write("### Create a New Savings Goal")
    
    
    with st.form("savings_goal"):
        goal_name = st.text_input("Goal Name")
        target_amount = st.number_input("Target Amount", min_value=0.0)
        deadline = st.date_input("Deadline")
        submitted = st.form_submit_button("Save Goal")
        
        if submitted:
            st.session_state.savings_goal = target_amount  
            st.success(f"Goal '{goal_name}' for ₹{target_amount} saved with deadline {deadline}.")
    
    
    st.write(f"Current Savings Goal: ₹{st.session_state.savings_goal}")




elif page == "AI Insights":
    st.title("AI Insights")
    income = st.number_input("Monthly Income", min_value=0.0)
    expenses = st.number_input("Monthly Expenses", min_value=0.0)
    savings_goal = st.number_input("Savings Goal", min_value=0.0)

    if income > 0:
        if st.button("Generate AI Insights"):
            st.session_state.income = income
            st.session_state.expenses = expenses
            st.session_state.savings_goal = savings_goal
            st.write("### Personalized Financial Advice")
            advice = generate_gemini_advice(income, expenses, savings_goal)
            st.write(advice)

elif page == "Debt Tracker":
    st.title("Debt Tracker")
    st.write("### Manage Your Debts")
    with st.form("debt_form"):
        debt_name = st.text_input("Debt Name")
        principal = st.number_input("Principal Amount", min_value=0.0)
        interest_rate = st.number_input("Interest Rate (%)", min_value=0.0)
        monthly_payment = st.number_input("Monthly Payment", min_value=0.0)
        submitted = st.form_submit_button("Add Debt")
        if submitted:
            st.success(f"Debt '{debt_name}' of ₹{principal} at {interest_rate}% interest added.")
            st.session_state.debts.append({
                "debt_name": debt_name,
                "principal": principal,
                "interest_rate": interest_rate,
                "monthly_payment": monthly_payment
            })
            schedule = calculate_debt_schedule(principal, interest_rate, monthly_payment)
            st.dataframe(schedule)
            st.write("### Debt Optimization Plan")
            debt_optimization_plan = generate_debt_optimization_plan(principal, interest_rate, monthly_payment)
            st.write(debt_optimization_plan)

elif page == "Investment Portfolio":
    st.title("Investment Portfolio")
    st.write("### Track Your Investments")
    with st.form("investment_form"):
        investment_name = st.text_input("Investment Name")
        amount_invested = st.number_input("Amount Invested", min_value=0.0)
        current_value = st.number_input("Current Value", min_value=0.0)
        submitted = st.form_submit_button("Add Investment")
        
        if submitted:
            st.success(f"Investment '{investment_name}' added with current value ₹{current_value}.")
            st.session_state.investments.append({
                "investment_name": investment_name,
                "amount_invested": amount_invested,
                "current_value": current_value
            })
            
            
            investments = json.dumps(st.session_state.investments, ensure_ascii=False)
            portfolio_analysis = analyze_investment_portfolio(investments)
            
            
            st.write("### Portfolio Analysis")
            st.write(portfolio_analysis)


elif page == "Reports":
    st.title("Reports")
    st.write("### Monthly Financial Report")
    if st.button("Generate Report"):
        income = st.session_state.income
        expenses = st.session_state.expenses
        investments = json.dumps(st.session_state.investments, ensure_ascii=False)
        report = generate_financial_report(income, expenses, investments)
        st.write(report)

elif page == "Advanced Analytics":
    st.title("Advanced Analytics")
    st.write("### Predict Future Savings")
    income = st.session_state.income
    expenses = st.session_state.expenses
    months = st.number_input("Months to Predict", min_value=1, step=1)

    if st.button("Predict Savings"):
        future_savings = predict_savings(income, expenses, months)
        st.write(f"Projected savings over {months} months: ₹{future_savings:.2f}")