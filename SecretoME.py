import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import requests

# --- Konfigurasi ---
SHEET_ID = "1m6MW4u1WFbBMkxiZeqQwAAb7tvI7-BjP4iXmeOR8pX0"
WORKSHEET_NAME = "Sheet1"  # Ganti jika nama worksheet beda

# --- Scope API Google ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]

# --- Ambil credentials dari Streamlit Secrets ---
try:
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"Gagal autentikasi ke Google Sheets: {e}")
    st.stop()

# --- Buka Google Sheet ---
try:
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet = spreadsheet.worksheet(WORKSHEET_NAME)
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"Sheet dengan ID {SHEET_ID} tidak ditemukan. Pastikan ID benar dan dibagikan ke {creds_dict.get('client_email', 'unknown email')} dengan role Editor.")
    st.stop()
except gspread.exceptions.APIError as e:
    st.error(f"API Error: {e.response.text}")
    st.stop()
except Exception as e:
    st.error(f"Gagal membuka Google Sheet: {e}")
    st.stop()

# --- Inisialisasi Header jika Sheet Kosong ---
try:
    if sheet.row_count == 0 or sheet.get("A1:D1") == []:
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
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json().get("ip", "UNKNOWN")
    except:
        return "UNKNOWN"

if st.button("📩 Kirim Pesan"):
    if pesan.strip() == "":
        st.warning("Pesan tidak boleh kosong!")
    else:
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip_address = get_ip()
        try:
            sheet.append_row([pesan, waktu, ip_address])
            st.success("✅ Pesanmu berhasil dikirim!")
        except Exception as e:
            st.error(f"Gagal menyimpan data: {e}")

# --- Rekapan Pesan ---
st.subheader("📜 Daftar Pesan Anonim")
try:
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("Belum ada pesan masuk.")
except Exception as e:
    st.error(f"Gagal membaca data: {e}")
