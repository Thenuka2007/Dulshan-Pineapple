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

USER_EMAIL = "dulshan.com"
USER_PASSWORD = "dulshan"
ADMIN_PASSWORD = "thenuka@2007"  # වාර්තා බැලීමට අවශ්‍ය මුරපදය

# භාෂා පරිවර්තන එකතුව
T = {
    "Sinhala": {
        "title": "🍍 දුල්ශාන් අන්නාසි ව්‍යාපාර කළමනාකරණය",
        "subtitle": "සුරක්ෂිත කළමනාකරණ පද්ධතිය",
        "login": "ඇතුළු වන්න",
        "logout": "ඉවත් වන්න",
        "tab_entry": "දත්ත ඇතුළත් කිරීම",
        "tab_reports": "වාර්තා සහ වක්‍ර ප්‍රස්ථාර",
        "tab_manage": "දත්ත කළමනාකරණය",
        "add_trans": "නව ගනුදෙනුවක් ඇතුළත් කරන්න",
        "date": "දිනය",
        "type": "ගනුදෙනු වර්ගය",
        "desc": "විස්තරය (පාරිභෝගිකයා / සැපයුම්කරු / විස්තර)",
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
        "delete_success": "ගනුදෙනුව සාර්ථකව මකා දමන ලදී!",
        "p_types": "අන්නාසි වර්ග (Pineapple Types)",
        "qty_lbl": "ප්‍රමාණය (kg)",
        "price_lbl": "ඒකක මිල (රු.)",
        "admin_locked": "🔒 මෙම තොරතුරු බැලීමට Admin මුරපදය ඇතුළත් කරන්න",
        "admin_btn": "තහවුරු කරන්න",
        "wrong_pass": "මුරපදය වැරදියි!",
        "chart_title": "📊 මාසික ප්‍රගති වක්‍රය (ගැනුම්, විකුණුම්, වියදම් සහ ලාභය)"
    },
    "English": {
        "title": "🍍 Dulshan Pineapple Management",
        "subtitle": "Secure Management System",
        "login": "Login",
        "logout": "Logout",
        "tab_entry": "Data Entry",
        "tab_reports": "Reports & Charts",
        "tab_manage": "Manage Data",
        "add_trans": "Add New Transaction",
        "date": "Date",
        "type": "Transaction Type",
        "desc": "Description (Customer / Supplier / Details)",
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
        "delete_success": "Transaction deleted successfully!",
        "p_types": "Pineapple Types",
        "qty_lbl": "QTY (kg)",
        "price_lbl": "Unit Price (Rs.)",
        "admin_locked": "🔒 Enter Admin Password to View This Section",
        "admin_btn": "Verify",
        "wrong_pass": "Incorrect Password!",
        "chart_title": "📊 Monthly Progress Line Chart (Purchases, Sales, Expenses & Profit)"
    }
}

# සැසි සහ දත්ත ආරම්භ කිරීම
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "admin_verified" not in st.session_state:
    st.session_state["admin_verified"] = False

# භාෂාව මාරු කරන තෙක් නොවෙනස්ව තබා ගැනීම (Persistence)
if "lang" not in st.session_state:
    st.session_state["lang"] = "Sinhala"

REQUIRED_COLUMNS = [
    "ID", "Date", "Type", "Description", 
    "T1_QTY", "T1_Price", "T2_QTY", "T2_Price", 
    "T3_QTY", "T3_Price", "T4_QTY", "T4_Price", 
    "T5_QTY", "T5_Price", "Total Expenses/Other QTY", "Other Price",
    "Amount (Rs)", "Payment Method", "Cheque No", "Cheque Date"
]

if "data" not in st.session_state:
    if os.path.exists("dulshan_pineapple_backup.csv"):
        try:
            loaded_df = pd.read_csv("dulshan_pineapple_backup.csv")
            if all(col in loaded_df.columns for col in REQUIRED_COLUMNS):
                st.session_state["data"] = loaded_df
            else:
                st.session_state["data"] = pd.DataFrame(columns=REQUIRED_COLUMNS)
        except Exception:
            st.session_state["data"] = pd.DataFrame(columns=REQUIRED_COLUMNS)
    else:
        st.session_state["data"] = pd.DataFrame(columns=REQUIRED_COLUMNS)

# භාෂාව තෝරාගැනීමේ Sidebar එක (on_change මඟින් ස්ථාවරව තබා ගනී)
def on_lang_change():
    st.session_state["lang"] = st.session_state["sb_lang"]

with st.sidebar:
    st.selectbox("Language / භාෂාව", ["Sinhala", "English"], 
                 key="sb_lang", index=0 if st.session_state["lang"] == "Sinhala" else 1, 
                 on_change=on_lang_change)
    st.write("---")

lang = st.session_state["lang"]

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

def main_app():
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title(T[lang]["title"])
    with col2:
        if st.button(T[lang]["logout"]):
            st.session_state["logged_in"] = False
            st.session_state["admin_verified"] = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs([T[lang]["tab_entry"], T[lang]["tab_reports"], T[lang]["tab_manage"]])

    # Tab 1: දත්ත ඇතුළත් කිරීම (පාස්වර්ඩ් අවශ්‍ය නැත)
    with tab1:
        st.subheader(T[lang]["add_trans"])
        with st.form("entry_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                date = st.date_input(T[lang]["date"], datetime.date.today())
                trans_type = st.selectbox(T[lang]["type"], [T[lang]["sales"], T[lang]["purchase"], T[lang]["expenses"]])
            with col_b:
                desc = st.text_input(T[lang]["desc"])
                pay_method = st.selectbox(T[lang]["pay_method"], [T[lang]["cash"], T[lang]["cheque"]])

            st.write(f"### {T[lang]['p_types']}")
            t_inputs = {}
            for i in range(1, 6):
                c1, c2, c3 = st.columns([2, 3, 3])
                with c1:
                    st.markdown(f"<div style='padding-top:25px;'><b>Type {i}</b></div>", unsafe_allow_html=True)
                with c2:
                    t_inputs[f"T{i}_QTY"] = st.text_input(f"{T[lang]['qty_lbl']} - T{i}", value="0", key=f"t{i}_q")
                with c3:
                    t_inputs[f"T{i}_Price"] = st.text_input(f"{T[lang]['price_lbl']} - T{i}", value="0", key=f"t{i}_p")
            
            st.write("---")
            c1, c2, c3 = st.columns([2, 3, 3])
            with c1:
                st.markdown("<div style='padding-top:25px;'><b>Expenses / Other</b></div>", unsafe_allow_html=True)
            with c2:
                other_qty_in = st.text_input(f"{T[lang]['qty_lbl']} / Items", value="0", key="oth_q")
            with c3:
                other_price_in = st.text_input(f"{T[lang]['price_lbl']} / Amount", value="0", key="oth_p")

            st.write("---")
            col_c, col_d = st.columns(2)
            with col_c:
                cheque_no = st.text_input(T[lang]["cheque_no"])
            with col_d:
                cheque_date = st.date_input(T[lang]["cheque_date"], datetime.date.today())

            submit = st.form_submit_button(T[lang]["save_btn"], use_container_width=True)
            
            if submit:
                def to_num(val, is_float=True):
                    try: return float(val) if is_float else int(float(val))
                    except ValueError: return 0.0 if is_float else 0

                t_data = {}
                for i in range(1, 6):
                    t_data[f"T{i}_QTY"] = to_num(t_inputs[f"T{i}_QTY"], is_float=True)
                    t_data[f"T{i}_Price"] = to_num(t_inputs[f"T{i}_Price"], is_float=False)
                
                oth_qty = to_num(other_qty_in, is_float=True)
                oth_price = to_num(other_price_in, is_float=False)

                calculated_amount = 0.0
                for i in range(1, 6):
                    calculated_amount += t_data[f"T{i}_QTY"] * t_data[f"T{i}_Price"]
                
                if trans_type == T[lang]["expenses"]:
                    calculated_amount += oth_price
                else:
                    calculated_amount += (oth_qty * oth_price) if oth_qty > 0 else oth_price
                
                final_cheque_no = cheque_no if pay_method == T[lang]["cheque"] else "-"
                final_cheque_date = cheque_date.strftime("%Y-%m-%d") if pay_method == T[lang]["cheque"] else "-"
                unique_id = int(datetime.datetime.now().timestamp())
                
                new_row = {
                    "ID": unique_id, "Date": date.strftime("%Y-%m-%d"), "Type": trans_type, "Description": desc,
                    "T1_QTY": t_data["T1_QTY"], "T1_Price": t_data["T1_Price"],
                    "T2_QTY": t_data["T2_QTY"], "T2_Price": t_data["T2_Price"],
                    "T3_QTY": t_data["T3_QTY"], "T3_Price": t_data["T3_Price"],
                    "T4_QTY": t_data["T4_QTY"], "T4_Price": t_data["T4_Price"],
                    "T5_QTY": t_data["T5_QTY"], "T5_Price": t_data["T5_Price"],
                    "Total Expenses/Other QTY": oth_qty, "Other Price": oth_price,
                    "Amount (Rs)": calculated_amount, "Payment Method": pay_method, "Cheque No": final_cheque_no, "Cheque Date": final_cheque_date
                }
                
                new_row_df = pd.DataFrame([new_row])[REQUIRED_COLUMNS]
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row_df], ignore_index=True)
                st.success(f"{T[lang]['success_save']} {T[lang]['total_amt']}: Rs. {calculated_amount:,.2f}")
                st.session_state["data"].to_csv("dulshan_pineapple_backup.csv", index=False)

    # ආරක්ෂිත පියවර (Admin Password Verification)
    def check_admin_access():
        if not st.session_state["admin_verified"]:
            st.write(f"### {T[lang]['admin_locked']}")
            admin_pass = st.text_input("Admin Password", type="password", key="admin_pwd_field")
            if st.button(T[lang]["admin_btn"], key="admin_btn_key"):
                if admin_pass == ADMIN_PASSWORD:
                    st.session_state["admin_verified"] = True
                    st.rerun()
                else:
                    st.error(T[lang]["wrong_pass"])
            return False
        return True

    # Tab 2: මාසික වාර්තා සහ වක්‍ර ප්‍රස්ථාර (මුරපදයෙන් ආරක්ෂිතයි)
    with tab2:
        if check_admin_access():
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

                # වක්‍ර ප්‍රස්ථාරය (Line Chart) සෑදීම
                st.write(f"### {T[lang]['chart_title']}")
                chart_df = df_temp.groupby(['YearMonth', 'Type'])['Amount (Rs)'].sum().unstack(fill_value=0)
                
                # භාෂාව අනුව තීරු ගැලපීම
                sales_col = T[lang]["sales"] if T[lang]["sales"] in chart_df.columns else None
                pur_col = T[lang]["purchase"] if T[lang]["purchase"] in chart_df.columns else None
                exp_col = T[lang]["expenses"] if T[lang]["expenses"] in chart_df.columns else None
                
                s_val = chart_df[sales_col] if sales_col is not None else 0
                p_val = chart_df[pur_col] if pur_col is not None else 0
                e_val = chart_df[exp_col] if exp_col is not None else 0
                chart_df[T[lang]["net_profit"]] = s_val - (p_val + e_val)
                
                st.line_chart(chart_df, use_container_width=True)

                def generate_pdf(dataframe, month_name):
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                    elements = []
                    styles = getSampleStyleSheet()
                    title = Paragraph(f"<b>DULSHAN PINEAPPLE REPORT - {month_name}</b>", styles["Title"])
                    elements.append(title)
                    elements.append(Spacer(1, 20))
                    summary_cols = ["Date", "Type", "Description", "Amount (Rs)", "Payment Method"]
                    pdf_df = dataframe[summary_cols]
                    table_data = [list(pdf_df.columns)] + pdf_df.values.tolist()
                    t = Table(table_data)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.orange),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0,0), (-1,-1), 9),
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
                        label=T[lang]["pdf_download"], data=pdf_data,
                        file_name=f"Dulshan_Pineapple_Report_{selected_month}.pdf", mime="application/pdf"
                    )
            else:
                st.info(T[lang]["no_data"])

    # Tab 3: දත්ත කළමනාකරණය (මුරපදයෙන් ආරක්ෂිතයි)
    with tab3:
        if check_admin_access():
            st.subheader(T[lang]["tab_manage"])
            df = st.session_state["data"]
            
            if not df.empty and len(df) > 0:
                st.dataframe(df, use_container_width=True)
                st.write("---")
                st.subheader(T[lang]["delete_title"])
                
                delete_id = st.selectbox(T[lang]["delete_select"], options=df["ID"].tolist(),
                                        format_func=lambda x: f"ID: {x} | {df[df['ID'] == x]['Date'].values[0]} - {df[df['ID'] == x]['Description'].values[0]} | Rs. {df[df['ID'] == x]['Amount (Rs)'].values[0]:,.2f}")
                
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
