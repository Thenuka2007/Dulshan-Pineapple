import streamlit as st
import pandas as pd
import datetime
import io

# පිටුවේ සැකසුම් (Page Configuration)
st.set_page_config(page_title="Dulshan Pineapple", layout="wide")

# පරිශීලක තොරතුරු
USER_EMAIL = "dulshan@pineapple.com"
USER_PASSWORD = "mysecretpassword123"

# සැසිය ආරම්භ කිරීම (Session State)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=["Date", "Type", "Description", "QTY (kg)", "Amount (Rs)"])

# 1. Login පිටුව
def login_page():
    st.subheader("Dulshan Pineapple - Management System")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_btn = st.button("Login", use_container_width=True)
        
        if login_btn:
            if email == USER_EMAIL and password == USER_PASSWORD:
                st.session_state["logged_in"] = True
                st.success("Success!")
                st.rerun()
            else:
                st.error("Invalid email or password!")

# 2. ප්‍රධාන මෘදුකාංග පිටුව
def main_app():
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("Dulshan Pineapple")
    with col2:
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["Data Entry", "Reports", "View Data"])

    # Tab 1: දත්ත ඇතුළත් කිරීම
    with tab1:
        st.subheader("Add Transaction")
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("Date", datetime.date.today())
            trans_type = st.selectbox("Type", ["Purchase", "Sale", "Expenses"])
            desc = st.text_input("Description")
            qty = st.number_input("QTY (kg)", min_value=0.0, step=0.1)
            amount = st.number_input("Amount (Rs)", min_value=0.0, step=100.0)
            
            submit = st.form_submit_button("Add Data")
            
            if submit:
                new_row = {
                    "Date": date.strftime("%Y-%m-%d"),
                    "Type": trans_type,
                    "Description": desc,
                    "QTY (kg)": qty,
                    "Amount (Rs)": amount
                }
                st.session_state["data"] = pd.concat([st.session_state["data"], pd.DataFrame([new_row])], ignore_index=True)
                st.success("Data added successfully!")
                st.session_state["data"].to_csv("dulshan_pineapple_backup.csv", index=False)

    # Tab 2: වාර්තා ලබා ගැනීම
    with tab2:
        st.subheader("Reports")
        df = st.session_state["data"]
        if not df.empty:
            purchases = df[df["Type"] == "Purchase"]["Amount (Rs)"].sum()
            sales = df[df["Type"] == "Sale"]["Amount (Rs)"].sum()
            expenses = df[df["Type"] == "Expenses"]["Amount (Rs)"].sum()
            net_profit = sales - (purchases + expenses)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Purchases", f"Rs. {purchases:,.2f}")
            col2.metric("Total Sales", f"Rs. {sales:,.2f}")
            col3.metric("Expenses", f"Rs. {expenses:,.2f}")
            col4.metric("Net Profit", f"Rs. {net_profit:,.2f}")

            # CSV Backup බාගත කිරීම (මෙය excel මගින් PDF කරගත හැක)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Data (Backup File)",
                data=csv,
                file_name="dulshan_pineapple_backup.csv",
                mime="text/csv"
            )
        else:
            st.info("No data available yet.")

    # Tab 3: දැනට ඇතුළත් කර ඇති සියලුම දත්ත බැලීම
    with tab3:
        st.subheader("All Data")
        st.dataframe(st.session_state["data"], use_container_width=True)

# ක්‍රියාත්මක වීම
if st.session_state["logged_in"]:
    main_app()
else:
    login_page()
