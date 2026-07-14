import streamlit as st
import pandas as pd
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

# පිටුවේ සැකසුම් (Page Configuration)
st.set_page_config(page_title="Dulshan Pineapple - Management System", page_icon="🍍", layout="wide")

# පරිශීලක අක්තපත්‍ර (Credentials - මෙතැනින් ඔබට Email සහ Password වෙනස් කළ හැක)
USER_EMAIL = dulshan@pineapple.com
USER_PASSWORD = mysecretpassword123

# සැසිය ආරම්භ කිරීම (Session State)
if logged_in not in st.get_state()
    st.session_state[logged_in] = False
if data not in st.get_state()
    # ආදර්ශ දත්ත කිහිපයක් සමඟ ආරම්භක දත්ත ගොනුව (මෙය Auto Backup වේ)
    st.session_state[data] = pd.DataFrame(columns=[දිනය, වර්ගය (මිලදී ගැනීමවිකිණීම), විස්තරය, ප්‍රමාණය (kg), මුළු මුදල (රු.)])

# 1. Login පිටුව
def login_page()
    st.markdown(h2 style='text-align center; color #FFA500;'🍍 දුල්ශාන් අන්නාසි (Dulshan Pineapple) 🍍h2, unsafe_allow_type=True)
    st.markdown(h4 style='text-align center;'කළමනාකරණ පද්ධතියට ඇතුළු වීමh4, unsafe_allow_type=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2
        email = st.text_input(ඊමේල් ලිපිනය (Email))
        password = st.text_input(මුරපදය (Password), type=password)
        login_btn = st.button(ඇතුළු වන්න (Login), use_container_width=True)
        
        if login_btn
            if email == USER_EMAIL and password == USER_PASSWORD
                st.session_state[logged_in] = True
                st.success(සාර්ථකව ඇතුළු විය!)
                st.rerun()
            else
                st.error(ඇතුළත් කළ ඊමේල් ලිපිනය හෝ මුරපදය වැරදියි!)

# 2. ප්‍රධාන මෘදුකාංග පිටුව
def main_app()
    # Header
    col1, col2 = st.columns([8, 2])
    with col1
        st.title(🍍 දුල්ශාන් අන්නාසි කළමනාකරණ පද්ධතිය)
    with col2
        if st.button(පද්ධතියෙන් ඉවත් වන්න (Logout))
            st.session_state[logged_in] = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs([දත්ත ඇතුළත් කිරීම, වාර්තා සහ බැකප්, දත්ත ලේඛනය])

    # Tab 1 දත්ත ඇතුළත් කිරීම
    with tab1
        st.subheader(දෛනික ගනුදෙනු ඇතුළත් කරන්න)
        with st.form(entry_form, clear_on_submit=True)
            date = st.date_input(දිනය, datetime.date.today())
            trans_type = st.selectbox(ගනුදෙනු වර්ගය, [මිලදී ගැනීම (Purchase), විකිණීම (Sale), වෙනත් වියදම්])
            desc = st.text_input(විස්තරය (උදා අන්නාසි කිලෝ 100 ක් මිලදී ගැනීම, වාහන කුලිය))
            qty = st.number_input(ප්‍රමාණය (කිලෝග්‍රෑම් වලින් - අවශ්‍ය නම් පමණි), min_value=0.0, step=0.1)
            amount = st.number_input(මුළු මුදල (රුපියල්), min_value=0.0, step=100.0)
            
            submit = st.form_submit_button(දත්ත ඇතුළත් කරන්න)
            
            if submit
                new_row = {
                    දිනය date.strftime(%Y-%m-%d),
                    වර්ගය (මිලදී ගැනීමවිකිණීම) trans_type,
                    විස්තරය desc,
                    ප්‍රමාණය (kg) qty,
                    මුළු මුදල (රු.) amount
                }
                st.session_state[data] = pd.concat([st.session_state[data], pd.DataFrame([new_row])], ignore_index=True)
                st.success(දත්ත සාර්ථකව ඇතුළත් කරන ලදී!)
                # Auto Backup (දේශීය ගොනුවක් ලෙස සුරැකීම)
                st.session_state[data].to_csv(dulshan_pineapple_backup.csv, index=False)

    # Tab 2 වාර්තා සහ PDF ලබා ගැනීම
    with tab2
        st.subheader(මාසික වාර්තා ලබා ගැනීම (PDF))
        
        # දත්ත පවතීදැයි බැලීම
        df = st.session_state[data]
        if not df.empty
            # සාරාංශ ගණනය කිරීම්
            purchases = df[df[වර්ගය (මිලදී ගැනීමවිකිණීම)] == මිලදී ගැනීම (Purchase)][මුළු මුදල (රු.)].sum()
            sales = df[df[වර්ගය (මිලදී ගැනීමවිකිණීම)] == විකිණීම (Sale)][මුළු මුදල (රු.)].sum()
            expenses = df[df[වර්ගය (මිලදී ගැනීමවිකිණීම)] == වෙනත් වියදම්][මුළු මුදල (රු.)].sum()
            net_profit = sales - (purchases + expenses)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric(මුළු මිලදී ගැනීම්, fරු. {purchases,.2f})
            col2.metric(මුළු විකුණුම්, fරු. {sales,.2f})
            col3.metric(වෙනත් වියදම්, fරු. {expenses,.2f})
            col4.metric(ශුද්ධ ලාභයඅලාභය, fරු. {net_profit,.2f})

            # PDF එකක් සෑදීම
            def generate_pdf(dataframe)
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                # මාතෘකාව
                title = Paragraph(bDULSHAN PINEAPPLE - MONTHLY REPORTb, styles[Title])
                elements.append(title)
                elements.append(Spacer(1, 20))
                
                # දත්ත වගුව
                data = [list(dataframe.columns)] + dataframe.values.tolist()
                t = Table(data)
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

            pdf_data = generate_pdf(df)
            st.download_button(
                label=PDF වාර්තාව බාගත කරගන්න (Download PDF),
                data=pdf_data,
                file_name=fDulshan_Pineapple_Report_{datetime.date.today().strftime('%Y-%m')}.pdf,
                mime=applicationpdf
            )
            
            # Auto Backup බාගත කිරීම
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=දත්ත ගොනුව සුරක්ෂිතව බාගත කරගන්න (Backup Data File),
                data=csv,
                file_name=dulshan_pineapple_backup.csv,
                mime=textcsv
            )
        else
            st.info(වාර්තා සෑදීමට තරම් ප්‍රමාණවත් දත්ත තවමත් ඇතුළත් කර නැත.)

    # Tab 3 දැනට ඇතුළත් කර ඇති සියලුම දත්ත බැලීම
    with tab3
        st.subheader(දැනට පවතින සියලුම දත්ත)
        st.dataframe(st.session_state[data], use_container_width=True)

# ක්‍රියාත්මක වීමේ පාලනය
if st.session_state[logged_in]
    main_app()
else
    login_page()
