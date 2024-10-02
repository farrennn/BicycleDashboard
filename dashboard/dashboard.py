# Import semua packages/library yang digunakan
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

# Set style seaborn
sns.set(style='dark')

# Mengimpor data day.csv
day_df = pd.read_csv("day.csv") 

# Menampilkan informasi tentang day_df
day_df.info()

st.sidebar.image("logo.png", use_column_width=True)

# Menghapus kolom yang tidak diperlukan
drop_col = ['instant', 'windspeed']
for i in day_df.columns:
    if i in drop_col:
        day_df.drop(labels=i, axis=1, inplace=True)

# Mengubah nama judul kolom
day_df.rename(columns={
    'dteday': 'dateday',
    'yr': 'year',
    'mnth': 'month',
    'weathersit': 'weather_cond',
    'cnt': 'count'
}, inplace=True)

# Mengubah angka menjadi keterangan
day_df['month'] = day_df['month'].map({
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
})
day_df['season'] = day_df['season'].map({
    1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'
})
day_df['weekday'] = day_df['weekday'].map({
    0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'
})
day_df['weather_cond'] = day_df['weather_cond'].map({
    1: 'Clear/Partly Cloudy',
    2: 'Misty/Cloudy',
    3: 'Light Snow/Rain',
    4: 'Severe Weather'
})

# Menyiapkan dataframe untuk analisis lebih lanjut
def create_daily_rent_df(df):
    daily_rent_df = df.groupby(by='dateday').agg({'count': 'sum'}).reset_index()
    return daily_rent_df

def create_daily_casual_rent_df(df):
    daily_casual_rent_df = df.groupby(by='dateday').agg({'casual': 'sum'}).reset_index()
    return daily_casual_rent_df

def create_daily_registered_rent_df(df):
    daily_registered_rent_df = df.groupby(by='dateday').agg({'registered': 'sum'}).reset_index()
    return daily_registered_rent_df

# Menyiapkan komponen filter tanggal
min_date = pd.to_datetime(day_df['dateday']).dt.date.min()
max_date = pd.to_datetime(day_df['dateday']).dt.date.max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter berdasarkan rentang waktu yang dipilih
main_df = day_df[(day_df['dateday'] >= str(start_date)) & (day_df['dateday'] <= str(end_date))]

# Menyiapkan data berdasarkan filter
daily_rent_df = create_daily_rent_df(main_df)
daily_casual_rent_df = create_daily_casual_rent_df(main_df)
daily_registered_rent_df = create_daily_registered_rent_df(main_df)

# Membuat dashboard

# Membuat judul dashboard
st.header('Bike Rental Dashboard 🚲')

# Menampilkan jumlah casual, registered, dan total user
st.subheader('Daily Rentals Summary')
col1, col2, col3 = st.columns(3)

with col1:
    daily_rent_casual = daily_casual_rent_df['casual'].sum()
    st.metric('Casual Users', value=daily_rent_casual)

with col2:
    daily_rent_registered = daily_registered_rent_df['registered'].sum()
    st.metric('Registered Users', value=daily_rent_registered)

with col3:
    daily_rent_total = daily_rent_df['count'].sum()
    st.metric('Total Users', value=daily_rent_total)

# Membuat grafik sebaran bulanan
st.subheader('Monthly Rentals')
monthly_rent_df = main_df.groupby('month').agg({'count': 'sum'}).reindex(
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], fill_value=0)
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(monthly_rent_df.index, monthly_rent_df['count'], marker='o', linewidth=2, color='tab:blue')
ax.set_xlabel('Month', fontsize=14)
ax.set_ylabel('Total Rentals', fontsize=14)
st.pyplot(fig)

# Membuat grafik berdasarkan musim
st.subheader('Seasonal Rentals')
season_rent_df = main_df.groupby('season')[['registered', 'casual']].sum().reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='season', y='registered', data=season_rent_df, label='Registered', color='tab:blue', ax=ax)
sns.barplot(x='season', y='casual', data=season_rent_df, label='Casual', color='tab:orange', ax=ax)
ax.set_ylabel('Total Rentals', fontsize=14)
ax.legend()
st.pyplot(fig)

# Membuat grafik berdasarkan kondisi cuaca
st.subheader('Weather-wise Rentals')
weather_rent_df = main_df.groupby('weather_cond').agg({'count': 'sum'}).reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='weather_cond', y='count', data=weather_rent_df, palette='coolwarm', ax=ax)
ax.set_ylabel('Total Rentals', fontsize=14)
st.pyplot(fig)

# Menampilkan insight tentang perbedaan hari kerja dan akhir pekan
st.subheader('Weekday vs Weekend Rentals')
workingday_rent_df = main_df.groupby('workingday').agg({'count': 'sum'}).reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='workingday', y='count', data=workingday_rent_df, palette='muted', ax=ax)
ax.set_ylabel('Total Rentals', fontsize=14)
ax.set_xticklabels(['Weekend', 'Weekday'])
st.pyplot(fig)