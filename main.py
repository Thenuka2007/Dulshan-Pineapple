import streamlit as st
import pandas as pd
import datetime
import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# පිටුවේ සැකසුම්
st.set_page_config(page_title="Dulshan Pineapple", layout="wide")

USER_EMAIL = "dulshanpineapple.com"
USER_PASSWORD = "dulshan"

# භාෂා සැකසුම් (Translations)
if "lang" not in st.session_state:
    st.session_state["lang"] = "Sinhala"

# භාෂා පරිවර්තන එකතුව
T = {
    "Sinhala": {
        "title": "🍍 දුල්ශාන් අන්නාසි ව්‍යාපාර කළමනාකරණය",
        "subtitle": "සුරක්ෂිත කළමනාකරණ පද්ධතිය",
        "login": "ඇතුළු වන්න",
        "logout": "ඉවත් වන්න",
        "tab_entry": "දත්ත ඇතුළත් කිරීම",
        "tab_reports": "වාර්තා සහ PDF",
        "tab_manage": "දත්ත කළමනාකරණය",
        "add_trans": "නව ගනුදෙනුවක් ඇතුළත් කරන්න",
        "date": "දිනය",
        "type": "ගනුදෙනු වර්ගය",
        "desc": "විස්තරය",
        "qty": "ඒකක ගණන (QTY - kg)",
        "unit_price": "ඒකකයක මිල (රු.)",
        "pay_method": "ගෙවීම් ක්‍රමය",
        "cheque_no": "චෙක්පත් අංකය (චෙක්පත් නම් පමණක්)",
        "cheque_date": "චෙක්පත් දිනය (චෙක්පත් නම් පමණක්)",
        "save_btn": "දත්ත සුරකින්න",
        "sales": "විකිණීම",
        "purchase": "මිලදී ගැනීම",
        "expenses": "වියදම්",
        "cash": "අත්පිට මුදල්",
        "cheque": "චෙක්පත්",
        "success_save": "දත්ත සාර්ථකව සුරැකිණි!",
        "total_amt": "මුළු මුදල",
        "select_month": "වාර්තාව අවශ්‍ය මාසය තෝරන්න",
        "tot_purchase": "මුළු මිලදී ගැනීම්",
        "tot_sales": "මුළු විකුණුම්",
        "net_profit": "ශුද්ධ ලාභය",
        "pdf_btn": "PDF වාර්තාව සාදන්න",
        "pdf_download": "PDF එක බාගත කරගන්න",
        "no_data": "තවමත් දත්ත ඇතුළත් කර නොමැත.",
        "delete_title": "වැරදුණු ගනුදෙනුවක් මකා දමන්න",
        "delete_select": "මකා දැමිය යුතු ගනුදෙනුව තෝරන්න",
        "delete_btn": "තෝරාගත් ගනුදෙනුව මකා දමන්න",
        "delete_success": "ගනුදෙනුව සාර්ථකව මකා දමන ලදී!"
    },
    "English": {
        "title": "🍍 Dulshan Pineapple Management",
        "subtitle": "Secure Management System",
        "login": "Login",
        "logout": "Logout",
        "tab_entry": "Data Entry",
        "tab_reports": "Reports & PDF",
        "tab_manage": "Manage Data",
        "add_trans": "Add New Transaction",
        "date": "Date",
        "type": "Transaction Type",
        "desc": "Description",
        "qty": "Quantity (QTY - kg)",
        "unit_price": "Unit Price (Rs.)",
        "pay_method": "Payment Method",
        "cheque_no": "Cheque Number (If Cheque)",
        "cheque_date": "Cheque Date (If Cheque)",
        "save_btn": "Save Data",
        "sales": "Sale",
        "purchase": "Purchase",
        "expenses": "Expenses",
        "cash": "Cash",
        "cheque": "Cheque",
        "success_save": "Data saved successfully!",
        "total_amt": "Total Amount",
        "select_month": "Select Month for Report",
        "tot_purchase": "Total Purchases",
        "tot_sales": "Total Sales",
        "net_profit": "Net Profit",
        "pdf_btn": "Generate PDF Report",
        "pdf_download": "Download PDF",
        "no_data": "No data available yet.",
        "delete_title": "Delete a Transaction",
        "delete_select": "Select Transaction to Delete",
        "delete_btn": "Delete Selected Transaction",
        "delete_success": "Transaction deleted successfully!"
    }
}

# සැසිය ආරම්භ කිරීම
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# මූලික තීරු සකස් කිරීම
REQUIRED_COLUMNS = [
    "ID", "Date", "Type", "Description", "QTY (kg)", "Unit Price (Rs)", "Amount (Rs)", "Payment Method", "Cheque No", "Cheque Date"
]

# පැරණි ගොනුවක් ඇත්නම් කියවීම හෝ අලුතින් සෑදීම
if "data" not in st.session_state:
    if os.path.exists("dulshan_pineapple_backup.csv"):
        try:
            loaded_df = pd.read_csv("dulshan_pineapple_backup.csv")
            # තීරු නිවැරදිදැයි බලා නිවැරදි කිරීම
            if list(loaded_df.columns) == REQUIRED_COLUMNS:
                st.session_state["data"] = loaded_df
            else:
                st.session_state["data"] = pd.DataFrame(columns=REQUIRED_COLUMNS)
        except Exception:
            st.session_state["data"] = pd.DataFrame(columns=REQUIRED_COLUMNS)
    else:
        st.session_state["data"] = pd.DataFrame(columns=REQUIRED_COLUMNS)

# භාෂාව තෝරාගැනීමේ Sidebar එක
with st.sidebar:
    st.session_state["lang"] = st.selectbox("Language / භාෂාව", ["Sinhala", "English"])
    st.write("---")

lang = st.session_state["lang"]

# 1. Login පිටුව
def login_page():
    st.markdown(f"<h2 style='text-align: center; color: #FFA500;'>{T[lang]['title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{T[lang]['subtitle']}</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_btn = st.button(T[lang]["login"], use_container_width=True)
        
        if login_btn:
            if email == USER_EMAIL and password == USER_PASSWORD:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid credentials! / ඇතුළත් කළ තොරතුරු වැරදියි!")

# 2. ප්‍රධාන මෘදුකාංග පිටුව
def main_app():
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title(T[lang]["title"])
    with col2:
        if st.button(T[lang]["logout"]):
            st.session_state["logged_in"] = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs([T[lang]["tab_entry"], T[lang]["tab_reports"], T[lang]["tab_manage"]])

    # Tab 1: දත්ත ඇතුළත් කිරීම
    with tab1:
        st.subheader(T[lang]["add_trans"])
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input(T[lang]["date"], datetime.date.today())
            trans_type = st.selectbox(T[lang]["type"], [T[lang]["sales"], T[lang]["purchase"], T[lang]["expenses"]])
            desc = st.text_input(T[lang]["desc"])
            
            qty = st.number_input(T[lang]["qty"], min_value=0.0, step=0.1, value=0.0)
            unit_price = st.number_input(T[lang]["unit_price"], min_value=0.0, step=1.0, value=0.0)
            
            pay_method = st.selectbox(T[lang]["pay_method"], [T[lang]["cash"], T[lang]["cheque"]])
            
            cheque_no = st.text_input(T[lang]["cheque_no"])
            cheque_date = st.date_input(T[lang]["cheque_date"], datetime.date.today())
            
            submit = st.form_submit_button(T[lang]["save_btn"])
            
            if submit:
                # මුළු මුදල ගණනය
                if qty > 0:
                    calculated_amount = qty * unit_price
                else:
                    calculated_amount = unit_price
                
                final_cheque_no = cheque_no if pay_method == T[lang]["cheque"] else "-"
                final_cheque_date = cheque_date.strftime("%Y-%m-%d") if pay_method == T[lang]["cheque"] else "-"
                
                unique_id = int(datetime.datetime.now().timestamp())
                
                new_row = pd.DataFrame([{
                    "ID": unique_id,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Type": trans_type,
                    "Description": desc,
                    "QTY (kg)": qty,
                    "Unit Price (Rs)": unit_price,
                    "Amount (Rs)": calculated_amount,
                    "Payment Method": pay_method,
                    "Cheque No": final_cheque_no,
                    "Cheque Date": final_cheque_date
                }])
                
                # පවතින දත්ත ලැයිස්තුවට එකතු කිරීම
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                st.success(f"{T[lang]['success_save']} {T[lang]['total_amt']}: Rs. {calculated_amount:,.2f}")
                st.session_state["data"].to_csv("dulshan_pineapple_backup.csv", index=False)

    # Tab 2: මාසික වාර්තා සහ PDF
    with tab2:
        st.subheader(T[lang]["tab_reports"])
        df = st.session_state["data"]
        
        if not df.empty and len(df) > 0:
            df_temp = df.copy()
            df_temp['Date_Parsed'] = pd.to_datetime(df_temp['Date'])
            df_temp['YearMonth'] = df_temp['Date_Parsed'].dt.to_period('M').astype(str)
            available_months = sorted(df_temp['YearMonth'].unique(), reverse=True)
            
            selected_month = st.selectbox(T[lang]["select_month"], available_months)
            
            filtered_df = df_temp[df_temp['YearMonth'] == selected_month].copy()
            filtered_df = filtered_df.drop(columns=['Date_Parsed', 'YearMonth'])
            
            purchases = filtered_df[filtered_df["Type"] == T[lang]["purchase"]]["Amount (Rs)"].sum()
            sales = filtered_df[filtered_df["Type"] == T[lang]["sales"]]["Amount (Rs)"].sum()
            expenses = filtered_df[filtered_df["Type"] == T[lang]["expenses"]]["Amount (Rs)"].sum()
            net_profit = sales - (purchases + expenses)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric(T[lang]["tot_purchase"], f"Rs. {purchases:,.2f}")
            col2.metric(T[lang]["tot_sales"], f"Rs. {sales:,.2f}")
            col3.metric(T[lang]["expenses"], f"Rs. {expenses:,.2f}")
            col4.metric(T[lang]["net_profit"], f"Rs. {net_profit:,.2f}")

            def generate_pdf(dataframe, month_name):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                title = Paragraph(f"<b>DULSHAN PINEAPPLE REPORT - {month_name}</b>", styles["Title"])
                elements.append(title)
                elements.append(Spacer(1, 20))
                
                pdf_df = dataframe.drop(columns=["ID"])
                table_data = [list(pdf_df.columns)] + pdf_df.values.tolist()
                
                t = Table(table_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.orange),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING', (0,0), (-1,0), 6),
                    ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.black)
                ]))
                elements.append(t)
                doc.build(elements)
                buffer.seek(0)
                return buffer

            if st.button(T[lang]["pdf_btn"]):
                pdf_data = generate_pdf(filtered_df, selected_month)
                st.download_button(
                    label=T[lang]["pdf_download"],
                    data=pdf_data,
                    file_name=f"Dulshan_Pineapple_Report_{selected_month}.pdf",
                    mime="application/pdf"
                )
        else:
            st.info(T[lang]["no_data"])

    # Tab 3: දත්ත බැලීම සහ මකා දැමීම
    with tab3:
        st.subheader(T[lang]["tab_manage"])
        df = st.session_state["data"]
        
        if not df.empty and len(df) > 0:
            st.dataframe(df, use_container_width=True)
            
            st.write("---")
            st.subheader(T[lang]["delete_title"])
            
            delete_id = st.selectbox(T[lang]["delete_select"], 
                                    options=df["ID"].tolist(),
                                    format_func=lambda x: f"ID: {x} | {df[df['ID'] == x]['Date'].values[0]} - {df[df['ID'] == x]['Description'].values[0]}")
            
            if st.button(T[lang]["delete_btn"], type="primary"):
                st.session_state["data"] = df[df["ID"] != delete_id]
                st.success(T[lang]["delete_success"])
                st.session_state["data"].to_csv("dulshan_pineapple_backup.csv", index=False)
                st.rerun()
        else:
            st.info(T[lang]["no_data"])

if st.session_state["logged_in"]:
    main_app()
else:
    login_page()
