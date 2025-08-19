import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import requests

# --- Konfigurasi ---
SHEET_ID = "1m6MW4u1WFbBMkxiZeqQwAAb7tvI7-BjP4iXmeOR8pX0"
WORKSHEET_NAME = "Sheeet"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]

# --- Autentikasi & koneksi Google Sheet (cache resource) ---
@st.cache_resource
def get_gsheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet = spreadsheet.worksheet(WORKSHEET_NAME)
    return sheet

sheet = get_gsheet_client()

# --- Inisialisasi Header jika Sheet Kosong ---
try:
    if sheet.row_count == 0 or sheet.get("A1:C1") == []:
        sheet.append_row(["Pesan", "Waktu", "IP Address"])
except Exception as e:
    st.error(f"Gagal inisialisasi header: {e}")
    st.stop()

# --- UI Mirip Secreto ---
st.title("💌 Kirim Pesan Anonim")
st.caption("Tulis pesanmu secara anonim, pesan akan tersimpan di Google Sheet!")

pesan = st.text_area("Tulis pesanmu di sini...", height=150)

# --- Ambil IP Address ---
def get_ip():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        data = response.json()
        return data.get("ip", "UNKNOWN"), data.get("city", "UNKNOWN"), data.get("country", "UNKNOWN")
    except:
        return "UNKNOWN", "UNKNOWN", "UNKNOWN"

# --- Submit Pesan ---
if st.button("📩 Kirim Pesan"):
    if pesan.strip() == "":
        st.warning("Pesan tidak boleh kosong!")
    else:
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip, city, country = get_ip()
        ip_info = f"{ip} ({city}, {country})"
        try:
            sheet.append_row([pesan, waktu, ip_info])
            st.success("✅ Pesanmu berhasil dikirim!")
        except Exception as e:
            st.error(f"Gagal menyimpan data: {e}")

# --- Ambil Data dari Sheet (cache 30 detik) ---
@st.cache_data(ttl=30)
def load_data():
    return pd.DataFrame(sheet.get_all_records())

# --- Rekapan Pesan ---
st.subheader("📜 Daftar Pesan Anonim (20 terakhir)")
try:
    df = load_data()
    if not df.empty:
        st.dataframe(df.tail(20))  # hanya tampilkan 20 pesan terakhir
    else:
        st.info("Belum ada pesan masuk.")
except Exception as e:
    st.error(f"Gagal membaca data: {e}")
