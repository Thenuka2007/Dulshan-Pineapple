import streamlit as st
import pandas as pd
import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# පිටුවේ සැකසුම්
st.set_page_config(page_title="Dulshan Pineapple", layout="wide")

USER_EMAIL = "dulshanpineapple.com"
USER_PASSWORD = "dulshanpineapple"

# සැසිය ආරම්භ කිරීම
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "data" not in st.session_state:
    # නව තීරු: Unit Price එකතු කර ඇත
    st.session_state["data"] = pd.DataFrame(columns=["Date", "Type", "Description", "QTY (kg)", "Unit Price (Rs)", "Amount (Rs)"])

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

    tab1, tab2, tab3 = st.tabs(["Data Entry", "Monthly Reports", "View All Data"])

    # Tab 1: දත්ත ඇතුළත් කිරීම
    with tab1:
        st.subheader("Add Transaction")
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("Date", datetime.date.today())
            trans_type = st.selectbox("Type", ["Purchase", "Sale", "Expenses"])
            desc = st.text_input("Description")
            
            # නව කොටස්: ඒකක ගණන සහ ඒකකයක මිල
            qty = st.number_input("QTY (kg) / ඒකක ගණන", min_value=0.0, step=0.1, value=0.0)
            unit_price = st.number_input("Unit Price (Rs) / ඒකකයක මිල", min_value=0.0, step=1.0, value=0.0)
            
            submit = st.form_submit_button("Add Data")
            
            if submit:
                # ස්වයංක්‍රීයව වැඩි වී මුළු මුදල හැදේ (වෙනත් වියදමක් නම් ඒකක ගණන 0 විය හැක, එවිට unit_price එකම මුළු මුදල වේ)
                if qty > 0:
                    calculated_amount = qty * unit_price
                else:
                    calculated_amount = unit_price  # වියදම් සඳහා Qty එක 0 නම් කෙලින්ම මිල ඇතුලත් කල හැක
                
                new_row = {
                    "Date": date.strftime("%Y-%m-%d"),
                    "Type": trans_type,
                    "Description": desc,
                    "QTY (kg)": qty,
                    "Unit Price (Rs)": unit_price,
                    "Amount (Rs)": calculated_amount
                }
                st.session_state["data"] = pd.concat([st.session_state["data"], pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"දත්ත ඇතුළත් විය! මුළු මුදල: රු. {calculated_amount:,.2f}")
                st.session_state["data"].to_csv("dulshan_pineapple_backup.csv", index=False)

    # Tab 2: මාසික වාර්තා සහ PDF ලබා ගැනීම
    with tab2:
        st.subheader("Monthly Reports")
        df = st.session_state["data"]
        
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'])
            df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
            available_months = sorted(df['YearMonth'].unique(), reverse=True)
            
            selected_month = st.selectbox("Select Month for Report", available_months)
            
            filtered_df = df[df['YearMonth'] == selected_month].copy()
            filtered_df['Date'] = filtered_df['Date'].dt.strftime('%Y-%m-%d')
            filtered_df = filtered_df.drop(columns=['YearMonth'])
            
            purchases = filtered_df[filtered_df["Type"] == "Purchase"]["Amount (Rs)"].sum()
            sales = filtered_df[filtered_df["Type"] == "Sale"]["Amount (Rs)"].sum()
            expenses = filtered_df[filtered_df["Type"] == "Expenses"]["Amount (Rs)"].sum()
            net_profit = sales - (purchases + expenses)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Purchases", f"Rs. {purchases:,.2f}")
            col2.metric("Total Sales", f"Rs. {sales:,.2f}")
            col3.metric("Expenses", f"Rs. {expenses:,.2f}")
            col4.metric("Net Profit", f"Rs. {net_profit:,.2f}")

            def generate_pdf(dataframe, month_name):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                title = Paragraph(f"<b>DULSHAN PINEAPPLE - REPORT FOR {month_name}</b>", styles["Title"])
                elements.append(title)
                elements.append(Spacer(1, 20))
                
                table_data = [["Date", "Type", "Description", "QTY", "Unit Price", "Amount"]] + dataframe[["Date", "Type", "Description", "QTY (kg)", "Unit Price (Rs)", "Amount (Rs)"]].values.tolist()
                t = Table(table_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.orange),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                    ('GRID', (0,0), (-1,-1), 1, colors.black)
                ]))
                elements.append(t)
                doc.build(elements)
                buffer.seek(0)
                return buffer

            if st.button("Generate & Download PDF"):
                pdf_data = generate_pdf(filtered_df, selected_month)
                st.download_button(
                    label="Click here to Download PDF",
                    data=pdf_data,
                    file_name=f"Dulshan_Pineapple_Report_{selected_month}.pdf",
                    mime="application/pdf"
                )
        else:
            st.info("No data available yet.")

    # Tab 3: සියලුම දත්ත බැලීම
    with tab3:
        st.subheader("All Inserted Data")
        st.dataframe(st.session_state["data"], use_container_width=True)

if st.session_state["logged_in"]:
    main_app()
else:
    login_page()
