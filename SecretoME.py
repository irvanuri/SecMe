import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import requests

# --- Konfigurasi Google Sheets ---
SHEET_ID = "1ZUjAzAqCEPfkc5Wicn278usNlsQ1wDkbCTsTWgNOjx0"
WORKSHEET_NAME = "Sheet"

# --- Scope API ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]

# --- Koneksi Google Sheets (cache biar ringan) ---
@st.cache_resource
def get_worksheet():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    return spreadsheet.worksheet(WORKSHEET_NAME)

sheet = get_worksheet()

# --- Ambil IP Address (cache per session) ---
@st.cache_data
def get_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=3)
        return response.json().get("ip", "UNKNOWN")
    except:
        return "UNKNOWN"

# --- Form Secreto ---
st.title("💌 Kirim Pesan Anonim")
st.caption("Tulis pesanmu secara anonim, pesanmu akan tersimpan di Google Sheet!")

pesan = st.text_area("Tulis pesanmu di sini...", height=150)

if st.button("📩 Kirim Pesan"):
    if pesan.strip() == "":
        st.warning("Pesan tidak boleh kosong!")
    else:
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip_address = get_ip()
        try:
            sheet.append_row([pesan, waktu, ip_address])
            st.success("✅ Pesanmu berhasil dikirim!")
            get_data.clear()  # hapus cache supaya data terbaru terbaca
        except Exception as e:
            st.error(f"Gagal menyimpan data: {e}")

# --- Fungsi Ambil Data dengan Cache ---
@st.cache_data(ttl=60)  # refresh otomatis tiap 60 detik
def get_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# --- Rekapan Pesan ---
st.subheader("📜 Daftar Pesan Anonim")
if st.button("🔄 Refresh Data"):
    get_data.clear()

try:
    df = get_data()
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("Belum ada pesan masuk.")
except Exception as e:
    st.error(f"Gagal membaca data: {e}")
