import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import requests

# --- Ambil konfigurasi dari secrets.toml ---
SHEET_ID = st.secrets["app_config"]["sheet_id"]
WORKSHEET_NAME = st.secrets["app_config"]["worksheet"]

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]

# --- Koneksi Google Sheets ---
@st.cache_resource
def get_worksheet():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    return spreadsheet.worksheet(WORKSHEET_NAME)

sheet = get_worksheet()

# --- Ambil IP & Lokasi ---
def get_ip_location():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        data = res.json()
        ip = data.get("ip", "UNKNOWN")
        loc = f"{data.get('city', 'UNKNOWN')}, {data.get('country', 'UNKNOWN')}"
        return ip, loc
    except:
        return "UNKNOWN", "UNKNOWN"

# --- Tampilan Form mirip WA Spam ---
st.title("💣 Fake WA Spam Form (Demo)")
st.caption("⚠️ Hanya tampilan, tidak benar-benar mengirim WA. Data tersimpan ke Google Sheets.")

with st.form("wa_form", clear_on_submit=True):
    nomor = st.text_input("📱 Nomor WhatsApp", placeholder="6281234567890")
    pesan = st.text_area("💬 Isi Pesan", placeholder="Tulis pesanmu di sini...")
    setuju = st.checkbox("✅ Saya setuju nomor, pesan, lokasi & IP dicatat")
    submit = st.form_submit_button("🚀 SPAM NOW!")

    if submit:
        if not nomor or not pesan:
            st.warning("Nomor dan pesan wajib diisi!")
        elif not setuju:
            st.warning("Anda harus menyetujui sebelum melanjutkan.")
        else:
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ip, lokasi = get_ip_location()
            try:
                sheet.append_row([nomor, pesan, waktu, ip, lokasi])
                st.success("✅ Data berhasil disimpan (WA tidak dikirim).")
            except Exception as e:
                st.error(f"Gagal menyimpan ke Google Sheets: {e}")
