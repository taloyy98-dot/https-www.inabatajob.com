import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import datetime

# ====== ตั้งรหัสสำหรับพิมพ์ ======
PRINT_PASSWORD = "1234"

# ====== ฟอร์มกรอกข้อมูล ======
st.title("📑 ฟอร์มใบสั่งงาน IK บริษัท อินะบาตะ ไทย จำกัด")

with st.form("work_order_form"):
    driver = st.text_input("ผู้รับผิดชอบ (Driver)")
    company = st.text_input("บริษัท")
    contact = st.text_input("ผู้ติดต่อ")
    phone = st.text_input("เบอร์โทร")
    receiver = st.text_input("ผู้รับ")
    note = st.text_area("หมายเหตุ")
    submit = st.form_submit_button("💾 บันทึกข้อมูล")

# ====== บันทึกลง DB ======
if submit:
    conn = sqlite3.connect("work_orders.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS work_orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  driver TEXT, company TEXT, contact TEXT,
                  phone TEXT, receiver TEXT, note TEXT, date TEXT)''')
    c.execute("INSERT INTO work_orders (driver, company, contact, phone, receiver, note, date) VALUES (?,?,?,?,?,?,?)",
              (driver, company, contact, phone, receiver, note, datetime.date.today().isoformat()))
    conn.commit()
    conn.close()
    st.success("✅ บันทึกข้อมูลเรียบร้อย")

# ====== ปุ่มพิมพ์ พร้อมระบบใส่รหัส ======
st.subheader("🔒 พิมพ์ใบสั่งงาน")
password = st.text_input("กรอกรหัสเพื่อพิมพ์", type="password")
if st.button("🖨️ พิมพ์ใบสั่งงาน"):
    if password == PRINT_PASSWORD:
        # สร้างไฟล์ PDF ด้วย fpdf
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt="📑 ใบสั่งงาน IK บริษัท อินะบาตะ ไทย จำกัด", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"ผู้รับผิดชอบ: {driver}", ln=True)
        pdf.cell(200, 10, txt=f"บริษัท: {company}", ln=True)
        pdf.cell(200, 10, txt=f"ผู้ติดต่อ: {contact}", ln=True)
        pdf.cell(200, 10, txt=f"เบอร์โทร: {phone}", ln=True)
        pdf.cell(200, 10, txt=f"ผู้รับ: {receiver}", ln=True)
        pdf.multi_cell(0, 10, txt=f"หมายเหตุ: {note}")
        pdf.cell(200, 10, txt=f"วันที่: {datetime.date.today().isoformat()}", ln=True)

        pdf_file = "work_order.pdf"
        pdf.output(pdf_file)

        with open(pdf_file, "rb") as f:
            st.download_button("⬇️ ดาวน์โหลด PDF", f, file_name="work_order.pdf")

    else:
        st.error("❌ รหัสผิด! กรุณาลองใหม่")
