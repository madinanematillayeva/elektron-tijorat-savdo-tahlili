import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# 1. Sahifa sozlamalari
st.set_page_config(
    page_title="E-Commerce Sales Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Maxsus CSS dizayn (chiroyli kartochkalar uchun)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 2. Demo ma'lumotlarni yaratish funksiyasi
@st.cache_data
def generate_demo_data():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.today(), periods=90)
    categories = ['Elektronika', 'Kiyim-kechak', 'Uy-ro\'zg\'or', 'Kitoblar', 'Sport']
    regions = ['Toshkent', 'Andijon', 'Samarqand', 'Farg\'ona', 'Buxoro']
    
    data = []
    for _ in range(1000):
        date = np.random.choice(dates)
        cat = np.random.choice(categories, p=[0.35, 0.25, 0.2, 0.1, 0.1])
        reg = np.random.choice(regions)
        
        if cat == 'Elektronika':
            price = np.random.randint(50, 800)
        elif cat == 'Kiyim-kechak':
            price = np.random.randint(15, 120)
        elif cat == 'Uy-ro\'zg\'or':
            price = np.random.randint(20, 250)
        elif cat == 'Kitoblar':
            price = np.random.randint(5, 40)
        else:
            price = np.random.randint(25, 200)
            
        qty = np.random.randint(1, 5)
        total = price * qty
        status = np.random.choice(['Yetkazildi', 'Bekor qilindi', 'Jarayonda'], p=[0.85, 0.10, 0.05])
        
        data.append([date, cat, reg, price, qty, total, status])
        
    df = pd.DataFrame(data, columns=['Sana', 'Kategoriya', 'Hudud', 'Narx', 'Soni', 'Jami_Summa', 'Holat'])
    df['Sana'] = pd.to_datetime(df['Sana'])
    return df.sort_values('Sana')

# 3. Yon panel (Sidebar)
with st.sidebar:
    st.title("🛒 Sales Intelligence")
    st.markdown("**Muallif:** Nematillayeva Madina, Kobilova Ozoda")
    st.divider()
    
    data_source = st.radio(
        "Ma'lumot manbasini tanlang:",
        ("Demo ma'lumotlar (Avtomatik)", "CSV fayl yuklash")
    )
    
    if data_source == "CSV fayl yuklash":
        uploaded_file = st.file_uploader("Savdo jadvalini yuklang (.csv)", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            df['Sana'] = pd.to_datetime(df['Sana'])
        else:
            st.info("Iltimos, CSV fayl yuklang yoki Demo rejimga o'ting.")
            df = generate_demo_data()
    else:
        df = generate_demo_data()
        
    st.divider()
    # Filtrlar
    selected_categories = st.multiselect(
        "Kategoriyalarni tanlang:",
        options=df['Kategoriya'].unique(),
        default=df['Kategoriya'].unique()
    )
    
    selected_regions = st.multiselect(
        "Hududlarni tanlang:",
        options=df['Hudud'].unique(),
        default=df['Hudud'].unique()
    )

# Ma'lumotlarni filtrlash
filtered_df = df[
    (df['Kategoriya'].isin(selected_categories)) & 
    (df['Hudud'].isin(selected_regions))
]

# 4. Asosiy sarlavha
st.title("📊 Elektron Tijoratda Savdoni Tahlil Qilish Tizimi")
st.markdown("Real vaqt rejimida savdo dinamikasi, hududiy ko'rsatkichlar va sun'iy intellekt asosida savdo bashorati.")

# 5. Asosiy ko'rsatkichlar (KPI Metrics)
col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df[filtered_df['Holat'] == 'Yetkazildi']['Jami_Summa'].sum()
total_orders = len(filtered_df)
avg_order_value = filtered_df['Jami_Summa'].mean() if total_orders > 0 else 0
cancel_rate = (len(filtered_df[filtered_df['Holat'] == 'Bekor qilindi']) / total_orders * 100) if total_orders > 0 else 0

col1.metric("Umumiy Tushum (Yetkazilgan)", f"${total_revenue:,.2f}", "+12.5%")
col2.metric("Jami Buyurtmalar Soni", f"{total_orders:,} ta", "+8.2%")
col3.metric("O'rtacha Savat Qiymati", f"${avg_order_value:,.2f}", "+3.1%")
col4.metric("Bekor Qilish Darajasi", f"{cancel_rate:.1f}%", "-1.4%", delta_color="inverse")

st.divider()

# 6. Grafiklar (1-qator)
chart_col1, chart_col2 = st.columns([2, 1])

with chart_col1:
    st.subheader("📈 Kunlik Savdo Dinamikasi")
    daily_sales = filtered_df[filtered_df['Holat'] == 'Yetkazildi'].groupby('Sana')['Jami_Summa'].sum().reset_index()
    fig_line = px.area(
        daily_sales, x='Sana', y='Jami_Summa',
        labels={'Sana': 'Sana', 'Jami_Summa': 'Savdo Summasi ($)'},
        color_discrete_sequence=['#2563eb']
    )
    fig_line.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_line, use_container_width=True)

with chart_col2:
    st.subheader("🍰 Kategoriyalar bo'yicha ulush")
    cat_sales = filtered_df[filtered_df['Holat'] == 'Yetkazildi'].groupby('Kategoriya')['Jami_Summa'].sum().reset_index()
    fig_pie = px.pie(
        cat_sales, values='Jami_Summa', names='Kategoriya',
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_pie, use_container_width=True)

# 7. Grafiklar (2-qator) va AI Bashorat
chart_col3, chart_col4 = st.columns([1, 2])

with chart_col3:
    st.subheader("📍 Hududlar bo'yicha savdo")
    reg_sales = filtered_df[filtered_df['Holat'] == 'Yetkazildi'].groupby('Hudud')['Jami_Summa'].sum().reset_index().sort_values('Jami_Summa')
    fig_bar = px.bar(
        reg_sales, x='Jami_Summa', y='Hudud', orientation='h',
        labels={'Jami_Summa': 'Summa ($)', 'Hudud': ''},
        color='Jami_Summa',
        color_continuous_scale='Blues'
    )
    fig_bar.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col4:
    st.subheader("🤖 AI Savdo Bashorati (Keyingi 14 kun)")
    if len(daily_sales) > 5:
        # Linear Regression modeli
        daily_sales['Day_Num'] = np.arange(len(daily_sales))
        X = daily_sales[['Day_Num']]
        y = daily_sales['Jami_Summa']
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_days = np.arange(len(daily_sales), len(daily_sales) + 14).reshape(-1, 1)
        predictions = model.predict(future_days)
        
        future_dates = [daily_sales['Sana'].max() + timedelta(days=i) for i in range(1, 15)]
        
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(x=daily_sales['Sana'], y=daily_sales['Jami_Summa'], mode='lines', name='Haqiqiy savdo', line=dict(color='#2563eb')))
        fig_pred.add_trace(go.Scatter(x=future_dates, y=predictions, mode='lines+markers', name='AI Bashorat', line=dict(color='#ef4444', dash='dash')))
        
        fig_pred.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Sana",
            yaxis_title="Savdo Summasi ($)"
        )
        st.plotly_chart(fig_pred, use_container_width=True)
    else:
        st.warning("Bashorat qilish uchun kamida 5 kunlik ma'lumot kerak.")

# 8. Ma'lumotlar jadvali
with st.expander("📋 Batafsil tranzaksiyalar jadvalini ko'rish"):
    st.dataframe(filtered_df.sort_values('Sana', ascending=False), use_container_width=True)