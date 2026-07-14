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

# ආරක්ෂිතව මුරපද පරීක්ෂා කිරීම (Streamlit Secrets හරහා හෝ default අගයන්)
USER_EMAIL = st.secrets.get("USER_EMAIL", "dulshanpineapple.com")
USER_PASSWORD = st.secrets.get("USER_PASSWORD", "dulshanpineapple")

# සැසිය ආරම්භ කිරීම
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=[
        "ID", "Date (දිනය)", "Type (වර්ගය)", "Description (විස්තරය)", 
        "QTY (kg) (ප්‍රමාණය)", "Unit Price (Rs) (ඒකක මිල)", "Amount (Rs) (මුළු මුදල)", 
        "Payment Method (ගෙවීම් ක්‍රමය)", "Cheque No (චෙක් අංකය)", "Cheque Date (චෙක් දිනය)"
    ])

# 1. Login පිටුව
def login_page():
    st.markdown("<h2 style='text-align: center; color: #FFA500;'>🍍 Dulshan Pineapple (දුල්ශාන් අන්නාසි) 🍍</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Secure Management System / සුරක්ෂිත කළමනාකරණ පද්ධතිය</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email / ඊමේල් ලිපිනය")
        password = st.text_input("Password / මුරපදය", type="password")
        login_btn = st.button("Login / ඇතුළු වන්න", use_container_width=True)
        
        if login_btn:
            if email == USER_EMAIL and password == USER_PASSWORD:
                st.session_state["logged_in"] = True
                st.success("Logged in successfully! / සාර්ථකව ඇතුළු විය!")
                st.rerun()
            else:
                st.error("Invalid credentials! / ඇතුළත් කළ තොරතුරු වැරදියි!")

# 2. ප්‍රධාන මෘදුකාංග පිටුව
def main_app():
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("🍍 Dulshan Pineapple Management")
    with col2:
        if st.button("Logout / ඉවත් වන්න"):
            st.session_state["logged_in"] = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs([
        "Data Entry / දත්ත ඇතුළත් කිරීම", 
        "Reports & PDF / වාර්තා සහ PDF", 
        "Manage Data / දත්ත මකා දැමීම සහ බැලීම"
    ])

    # Tab 1: දත්ත ඇතුළත් කිරීම
    with tab1:
        st.subheader("Add New Transaction / නව ගනුදෙනුවක් ඇතුළත් කරන්න")
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("Date / දිනය", datetime.date.today())
            trans_type = st.selectbox("Type / වර්ගය", ["Sale / විකිණීම", "Purchase / මිලදී ගැනීම", "Expenses / වියදම්"])
            desc = st.text_input("Description / විස්තරය")
            
            qty = st.number_input("QTY (kg) / ඒකක ගණන", min_value=0.0, step=0.1, value=0.0)
            unit_price = st.number_input("Unit Price (Rs) / ඒකකයක මිල", min_value=0.0, step=1.0, value=0.0)
            
            pay_method = st.selectbox("Payment Method / ගෙවීම් ක්‍රමය", ["Cash / අත්පිට මුදල්", "Cheque / චෙක්පත්"])
            
            # චෙක්පත් විස්තර (චෙක්පත් තෝරාගතහොත් පමණක් ඇතුළත් කිරීමට)
            cheque_no = st.text_input("If Cheque, Cheque No / චෙක්පත් අංකය (චෙක්පත් නම් පමණක්)")
            cheque_date = st.date_input("If Cheque, Cheque Date / චෙක්පත් දිනය", datetime.date.today())
            
            submit = st.form_submit_button("Save Data / දත්ත සුරකින්න")
            
            if submit:
                # මුළු මුදල ගණනය කිරීම
                if qty > 0:
                    calculated_amount = qty * unit_price
                else:
                    calculated_amount = unit_price
                
                # චෙක්පත් නොවේ නම් විස්තර හිස් කිරීම
                final_cheque_no = cheque_no if pay_method == "Cheque / චෙක්පත්" else "-"
                final_cheque_date = cheque_date.strftime("%Y-%m-%d") if pay_method == "Cheque / චෙක්පත්" else "-"
                
                # අද්විතීය ID එකක් සෑදීම
                unique_id = int(datetime.datetime.now().timestamp())
                
                new_row = {
                    "ID": unique_id,
                    "Date (දිනය)": date.strftime("%Y-%m-%d"),
                    "Type (වර්ගය)": trans_type,
                    "Description (විස්තරය)": desc,
                    "QTY (kg) (ප්‍රමාණය)": qty,
                    "Unit Price (Rs) (ඒකක මිල)": unit_price,
                    "Amount (Rs) (මුළු මුදල)": calculated_amount,
                    "Payment Method (ගෙවීම් ක්‍රමය)": pay_method,
                    "Cheque No (චෙක් අංකය)": final_cheque_no,
                    "Cheque Date (චෙක් දිනය)": final_cheque_date
                }
                st.session_state["data"] = pd.concat([st.session_state["data"], pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Saved! Total Amount: Rs. {calculated_amount:,.2f} / දත්ත සුරැකිණි!")
                st.session_state["data"].to_csv("dulshan_pineapple_backup.csv", index=False)

    # Tab 2: මාසික වාර්තා සහ PDF
    with tab2:
        st.subheader("Monthly Reports / මාසික වාර්තා")
        df = st.session_state["data"]
        
        if not df.empty:
            # දින අනුව ගොනු සකස් කිරීම
            df_temp = df.copy()
            df_temp['Date_Parsed'] = pd.to_datetime(df_temp['Date (දිනය)'])
            df_temp['YearMonth'] = df_temp['Date_Parsed'].dt.to_period('M').astype(str)
            available_months = sorted(df_temp['YearMonth'].unique(), reverse=True)
            
            selected_month = st.selectbox("Select Month for Report / වාර්තාව අවශ්‍ය මාසය තෝරන්න", available_months)
            
            filtered_df = df_temp[df_temp['YearMonth'] == selected_month].copy()
            filtered_df = filtered_df.drop(columns=['Date_Parsed', 'YearMonth'])
            
            purchases = filtered_df[filtered_df["Type (වර්ගය)"] == "Purchase / මිලදී ගැනීම"]["Amount (Rs) (මුළු මුදල)"].sum()
            sales = filtered_df[filtered_df["Type (වර්ගය)"] == "Sale / විකිණීම"]["Amount (Rs) (මුළු මුදල)"].sum()
            expenses = filtered_df[filtered_df["Type (වර්ගය)"] == "Expenses / වියදම්"]["Amount (Rs) (මුළු මුදල)"].sum()
            net_profit = sales - (purchases + expenses)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Purchases / මුළු මිලදී ගැනීම්", f"Rs. {purchases:,.2f}")
            col2.metric("Total Sales / මුළු විකුණුම්", f"Rs. {sales:,.2f}")
            col3.metric("Expenses / වියදම්", f"Rs. {expenses:,.2f}")
            col4.metric("Net Profit / ශුද්ධ ලාභය", f"Rs. {net_profit:,.2f}")

            def generate_pdf(dataframe, month_name):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                title = Paragraph(f"<b>DULSHAN PINEAPPLE REPORT - {month_name}</b>", styles["Title"])
                elements.append(title)
                elements.append(Spacer(1, 20))
                
                # PDF එකට අනවශ්‍ය ID තීරුව ඉවත් කර වගුව හැදීම
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

            if st.button("Generate PDF / PDF වාර්තාව සකසන්න"):
                pdf_data = generate_pdf(filtered_df, selected_month)
                st.download_button(
                    label="Download PDF / PDF එක බාගත කරගන්න",
                    data=pdf_data,
                    file_name=f"Dulshan_Pineapple_Report_{selected_month}.pdf",
                    mime="application/pdf"
                )
        else:
            st.info("No data available yet. / තවමත් දත්ත ඇතුළත් කර නොමැත.")

    # Tab 3: දත්ත බැලීම සහ මකා දැමීම
    with tab3:
        st.subheader("All Transactions / සියලුම ගනුදෙනු විස්තර")
        df = st.session_state["data"]
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            st.write("---")
            st.subheader("Delete a Transaction / වැරදුණු ගනුදෙනුවක් මකා දමන්න")
            
            # මකා දැමීම සඳහා ID එක තෝරා ගැනීම
            delete_id = st.selectbox("Select Date & Description to Delete / මකා දැමිය යුතු ගනුදෙනුව තෝරන්න", 
                                    options=df["ID"].tolist(),
                                    format_func=lambda x: f"ID: {x} | {df[df['ID'] == x]['Date (දිනය)'].values[0]} - {df[df['ID'] == x]['Description (විස්තරය)'].values[0]}")
            
            if st.button("Delete Selected Transaction / තෝරාගත් ගනුදෙනුව මකා දමන්න", type="primary"):
                st.session_state["data"] = df[df["ID"] != delete_id]
                st.success("Transaction deleted successfully! / ගනුදෙනුව සාර්ථකව මකා දමන ලදී!")
                st.session_state["data"].to_csv("dulshan_pineapple_backup.csv", index=False)
                st.rerun()
        else:
            st.info("No data available yet. / තවමත් දත්ත ඇතුළත් කර නොමැත.")

if st.session_state["logged_in"]:
    main_app()
else:
    login_page()
