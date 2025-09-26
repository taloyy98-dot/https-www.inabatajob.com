import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from fpdf import FPDF
import base64

# ===== ตั้งค่าหน้า =====
st.set_page_config(page_title="ฟอร์มใบสั่งงาน IK", page_icon="📄", layout="centered")

# ===== Header =====
st.markdown(
    """
    <div style="text-align: center; padding: 20px;">
        <h1 style="color:#2E86C1;">📋 ฟอร์มใบสั่งงาน</h1>
        <h2 style="color:#117A65;">บริษัท อินะบาตะ ไทย จำกัด</h2>
        <hr style="margin-top:20px; margin-bottom:20px;">
    </div>
    """,
    unsafe_allow_html=True
)

# ===== DB Setup =====
conn = sqlite3.connect("work_orders.db", check_same_thread=False)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS work_orders")  # reset กัน schema error
c.execute("""
CREATE TABLE work_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assigned_to TEXT,
    order_date TEXT,
    time TEXT,
    contact TEXT,
    company TEXT,
    department TEXT,
    address TEXT,
    phone TEXT,
    ordered_by TEXT,
    receiver TEXT,
    receive_date TEXT,
    checklist TEXT,
    remark TEXT
)
""")
conn.commit()

# ===== ฟอร์มกรอกข้อมูล =====
with st.form("work_order_form", clear_on_submit=True):
    assigned_to = st.text_input("มอบหมายให้", "DRIVER TXE")
    order_date = st.date_input("วันที่สั่งงาน", date.today())
    time = st.text_input("เวลา")
    contact = st.text_input("ติดต่อ")
    company = st.text_input("บริษัท", "STI PRECISION")
    department = st.text_input("แผนก")
    address = st.text_area("ที่อยู่")
    phone = st.text_input("โทร")
    ordered_by = st.text_input("ผู้สั่งงาน", "SIRAPAT")
    receiver = st.text_input("ผู้รับ")
    receive_date = st.date_input("วันที่ (รับงาน)", date.today())

    st.markdown("### ☑ รายการ")
    checklist_options = [
        "ส่งของ/เอกสาร/ตัวอย่าง",
        "รับของ/เอกสาร/ตัวอย่าง",
        "เซ็นรับใบกำกับภาษี รับสำเนากลับ 2 ใบ",
        "เซ็นรับใบกำกับภาษีและวางบิล รับต้นฉบับใบวางบิล และสำเนาใบกำกับภาษีกลับ 1 ใบ",
        "วางบิล รับต้นฉบับใบวางบิลกลับ",
        "รับเช็ค ________ ใบ",
        "อื่นๆ ________________________"
    ]
    checklist = st.multiselect("เลือก Checklist", checklist_options)

    remark = st.text_area("📝 หมายเหตุ / Remark")

    submitted = st.form_submit_button("✅ บันทึกข้อมูล")
    if submitted:
        c.execute("""
        INSERT INTO work_orders (
            assigned_to, order_date, time, contact, company, department,
            address, phone, ordered_by, receiver, receive_date, checklist, remark
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            assigned_to, str(order_date), time, contact, company, department,
            address, phone, ordered_by, receiver, str(receive_date),
            ", ".join(checklist), remark
        ))
        conn.commit()
        st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")

# ===== ดูข้อมูลที่บันทึกไว้ =====
st.markdown("---")
st.subheader("📑 ข้อมูลที่บันทึกไว้")

query = """
SELECT 
    id,
    ordered_by,
    assigned_to,
    order_date,
    time,
    contact,
    company,
    department,
    address,
    phone,
    receiver,
    receive_date,
    checklist,
    remark
FROM work_orders
ORDER BY id DESC
"""
df = pd.read_sql_query(query, conn)

if not df.empty:
    df = df.drop(columns=["id"])
    df = df.rename(columns={
        "ordered_by": "ผู้สั่งงาน",
        "assigned_to": "มอบหมายให้",
        "order_date": "วันที่สั่งงาน",
        "time": "เวลา",
        "contact": "ติดต่อ",
        "company": "บริษัท",
        "department": "แผนก",
        "address": "ที่อยู่",
        "phone": "โทร",
        "receiver": "ผู้รับ",
        "receive_date": "วันที่รับงาน",
        "checklist": "เช็คลิสต์",
        "remark": "หมายเหตุ"
    })
    st.dataframe(df, use_container_width=True)

    # ปุ่มพิมพ์ PDF
    def generate_pdf(row):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)

        pdf.cell(200, 10, txt="📋 ใบสั่งงาน", ln=True, align="C")
        pdf.ln(10)

        for col in row.index:
            text = f"{col}: {row[col]}"
            pdf.multi_cell(0, 10, text)

        return pdf.output(dest="S").encode("latin1")

    latest_row = df.iloc[0]
    pdf_data = generate_pdf(latest_row)

    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="work_order.pdf">🖨️ พิมพ์/ดาวน์โหลด PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    st.info("ยังไม่มีข้อมูลที่บันทึกไว้")
