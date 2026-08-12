import streamlit as st
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# 1. ฐานข้อมูล 36 เดือนย้อนหลัง (ฝังไว้ในระบบ)
historical_data = {
    "น้ำยาล้างรถ (ลิตร)": [20, 25, 40, 50, 45, 40, 20, 15, 5, 10, 10, 25, 25, 30, 50, 65, 55, 50, 25, 15, 8, 12, 15, 30, 35, 40, 60, 80, 70, 65, 30, 20, 10, 15, 15, 40],
    "เคลือบภายใน (ลิตร)": [14.88, 13.44, 18.6, 19.8, 18.6, 16.2, 3.72, 1.86, 0.9, 2.76, 12.6, 16.74, 18.6, 16.8, 22.32, 23.4, 22.32, 19.8, 5.58, 2.76, 1.32, 3.72, 16.2, 20.46, 22.32, 20.16, 26.04, 27.0, 26.04, 23.4, 7.44, 3.72, 1.8, 5.58, 19.8, 24.18],
    "เช็ดกระจก (ลิตร)": [9.92, 8.96, 12.4, 13.2, 12.4, 10.8, 2.48, 1.24, 0.6, 1.84, 8.4, 11.16, 12.4, 11.2, 14.88, 15.6, 14.88, 13.2, 3.72, 1.84, 0.88, 2.48, 10.8, 13.64, 14.88, 13.44, 17.36, 18.0, 17.36, 15.6, 4.96, 2.48, 1.2, 3.72, 13.2, 16.12],
    "ลงล้อ (ลิตร)": [4.96, 4.48, 6.2, 6.6, 6.2, 5.4, 1.24, 0.62, 0.3, 0.92, 4.2, 5.58, 6.2, 5.6, 7.44, 7.8, 7.44, 6.6, 1.86, 0.92, 0.44, 1.24, 5.4, 6.82, 7.44, 6.72, 8.68, 9.0, 8.68, 7.8, 2.48, 1.24, 0.6, 1.86, 6.6, 8.06]
}

# 2. ตั้งค่าหน้าตาเว็บไซต์
st.set_page_config(page_title="ระบบพยากรณ์การสั่งซื้อ", page_icon="📦")
st.title("📦 ระบบพยากรณ์การสั่งซื้อสินค้าล่วงหน้า")
st.markdown("ระบบจะคำนวณปริมาณการสั่งซื้อในเดือนถัดไป โดยใช้ **Winter's Model** จากประวัติการใช้งานย้อนหลัง 3 ปี")

# 3. ส่วนรับข้อมูลจากผู้ใช้
st.header("กรอกข้อมูลของเดือนปัจจุบัน")
selected_product = st.selectbox("เลือกผลิตภัณฑ์ที่ต้องการคำนวณ:", list(historical_data.keys()))
current_usage = st.number_input(f"กรอกปริมาณการใช้ {selected_product} ในเดือนนี้:", min_value=0.0, step=1.0)

# 4. ปุ่มกดคำนวณและประมวลผล
if st.button("คำนวณยอดพยากรณ์", type="primary"):
    with st.spinner('กำลังประมวลผลด้วย Winter\'s Model...'):
        
        # ถ้าระบบนี้ใช้กรอกเพื่อพยากรณ์ "เดือนถัดไป" จะต้องนำยอดเดือนนี้ไปต่อท้าย
        full_data = historical_data[selected_product] + [current_usage]
        ts_data = pd.Series(full_data)
        
        # 4.1 ล็อคค่าพารามิเตอร์ทั้ง 3 ตัวตามที่ Excel คำนวณไว้
        if selected_product == "ลงล้อ (ลิตร)":
            alpha_val = 0.9
            beta_val = 0.99
            gamma_val = 0.99
        else:
            alpha_val = 0.5
            beta_val = 0.01
            gamma_val = 0.99
            
        try:
            # 4.2 บังคับให้โมเดลรันตามค่าคงที่ของเรา 100% (optimized=False)
            model = ExponentialSmoothing(
                ts_data, 
                trend='add', 
                seasonal='add', 
                seasonal_periods=12
            ).fit(
                smoothing_level=alpha_val, 
                smoothing_trend=beta_val, 
                smoothing_seasonal=gamma_val, 
                optimized=False
            )
            
            # พยากรณ์ 1 เดือนล่วงหน้า
            forecast = model.forecast(1).iloc[0]
            
            # แสดงผลลัพธ์
            st.success("✅ คำนวณเสร็จสิ้น!")
            st.metric(label=f"ยอดความต้องการใช้เดือนหน้า ({selected_product})", value=f"{forecast:.2f} ลิตร")
            
            st.write("📈 กราฟแสดงแนวโน้มการใช้งานรวม")
            st.line_chart(ts_data)
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการคำนวณ: {e}")

