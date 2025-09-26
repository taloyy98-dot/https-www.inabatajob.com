import streamlit as st
import pandas as pd
import sqlite3
from fpdf import FPDF

# ==========================
# ฟังก์ชันสร้าง PDF
# ==========================
def generate_pdf(row):
    pdf = FPDF()
    pdf.add_page()

    # โหลดฟอนต์ไทย (ต้องมีไฟล์ THSarabunNew.ttf อยู่ในโฟลเดอร์เดียวกัน)
    pdf.add_font("THSarabunNew", "", "THSarabunNew.ttf", uni=True)
    pdf.set_font("THSarabunNew", size=16)

    # หัวข้อ
    pdf.cell(0, 10, "📋 ใบสั่งงาน", ln=True, align="C")
    pdf.ln(10)

    # เติมข้อมูลจาก row
    for col in row.index:
        text = f"{col}: {row[col]}"
        pdf.multi_cell(w=190, h=8, txt=text)

    # คืนค่า PDF เป็น bytes (แก้ bytearray error)
    pdf_bytes = pdf.output(dest="S")
    return bytes(pdf_bytes)


# ==========================
# ส่วนหลักของแอป
# ==========================
st.title("📊 ระบบจัดการใบสั่งงาน")

# เชื่อมต่อฐานข้อมูล SQLite
try:
    conn = sqlite3.connect("my_database.db")
    query = "SELECT * FROM work_orders ORDER BY id DESC LIMIT 10"
    df = pd.read_sql_query(query, conn)
    conn.close()
except Exception as e:
    st.error(f"❌ ไม่สามารถดึงข้อมูลจากฐานข้อมูลได้: {e}")
    df = pd.DataFrame()

# แสดงตาราง
if not df.empty:
    st.subheader("📑 ข้อมูลใบสั่งงานล่าสุด")
    st.dataframe(df)

    # เลือกแถวล่าสุด
    latest_row = df.iloc[0]
    pdf_file = generate_pdf(latest_row)

    # ปุ่มดาวน์โหลด PDF
    st.download_button(
        label="🖨️ พิมพ์ / ดาวน์โหลด PDF",
        data=pdf_file,
        file_name="work_order.pdf",
        mime="application/pdf"
    )
else:
    st.info("ℹ️ ไม่มีข้อมูลในฐานข้อมูล")
