import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

# --- Konfigurasi ---
SHEET_ID = "1m6MW4u1WFbBMkxiZeqQwAAb7tvI7-BjP4iXmeOR8pX0"
WORKSHEET_NAME = "Sheet1"  # pastikan sesuai nama aslinya

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]

# --- Autentikasi & koneksi Google Sheet ---
@st.cache_resource
def get_gsheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet = spreadsheet.worksheet(WORKSHEET_NAME)
    return sheet

sheet = get_gsheet_client()

# --- UI Mirip Secreto ---
st.title("💌 Kirim Pesan Anonim")

pesan = st.text_area("Tulis pesanmu di sini...", height=150)

# --- Ambil IP user langsung dari browser ---
client_ip = streamlit_js_eval(
    js_expressions="await fetch('https://api.ipify.org?format=json').then(r=>r.json()).then(d=>d.ip)"
)

# --- Submit Pesan ---
if st.button("📩 Kirim Pesan"):
    if not pesan.strip():
        st.warning("Pesan tidak boleh kosong!")
    elif not client_ip:
        st.error("⚠️ Gagal mendapatkan IP user. Coba refresh halaman.")
    else:
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            sheet.append_row([pesan, waktu, client_ip])
            st.success("✅ Pesanmu berhasil dikirim!")
        except Exception as e:
            st.error(f"Gagal menyimpan data: {e}")

# --- Rekapan Pesan ---
try:
    df = pd.DataFrame(sheet.get_all_records())
    if not df.empty:
        st.subheader("📜 Daftar Pesan Anonim (20 terakhir)")
        st.dataframe(df.tail(20))
    else:
        st.info("Belum ada pesan masuk.")
except Exception as e:
    st.error(f"Gagal membaca data: {e}")
