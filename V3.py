import streamlit as st
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
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
        # สร้างไฟล์ PDF
        pdf_file = "work_order.pdf"
        c = canvas.Canvas(pdf_file, pagesize=A4)
        c.setFont("Helvetica", 14)
        c.drawString(100, 800, "📑 ใบสั่งงาน IK บริษัท อินะบาตะ ไทย จำกัด")
        c.drawString(100, 770, f"ผู้รับผิดชอบ: {driver}")
        c.drawString(100, 750, f"บริษัท: {company}")
        c.drawString(100, 730, f"ผู้ติดต่อ: {contact}")
        c.drawString(100, 710, f"เบอร์โทร: {phone}")
        c.drawString(100, 690, f"ผู้รับ: {receiver}")
        c.drawString(100, 670, f"หมายเหตุ: {note}")
        c.drawString(100, 650, f"วันที่: {datetime.date.today().isoformat()}")
        c.showPage()
        c.save()

        with open(pdf_file, "rb") as f:
            st.download_button("⬇️ ดาวน์โหลด PDF", f, file_name="work_order.pdf")

    else:
        st.error("❌ รหัสผิด! กรุณาลองใหม่")
