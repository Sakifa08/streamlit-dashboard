import streamlit as st
import pandas as pd
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style='ticks')
plt.style.use('ggplot')

# Helper function untuk berbagai dataframe
def create_by_humidity_df(df):
    temp_cat_df = df.groupby("humidity").agg({"cnt": "mean"}).reset_index()
    temp_cat_df.columns = ["humidity", "avg_cnt"]
    return temp_cat_df

def create_hourly_df(df):
    hourly_df = df.groupby(by=["hours"]).agg({
        "cnt": "sum"
    }).reset_index()
    return hourly_df

def count_by_day_df(day_df):
    day_df_count_2011 = day_df.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))
    return day_df_count_2011
def total_registered_df(day_df):
   reg_df =  day_df.groupby(by="dteday").agg({
      "registered": "sum"
    })
   reg_df = reg_df.reset_index()
   reg_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
   return reg_df
def total_casual_df(day_df):
   cas_df =  day_df.groupby(by="dteday").agg({
      "casual": ["sum"]
    })
   cas_df = cas_df.reset_index()
   cas_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
   return cas_df
def sum_order (hour_df):
    sum_order_items_df = hour_df.groupby("hours").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# Load dataset
day_df = pd.read_csv("day_fix.csv")
hour_df = pd.read_csv("hour_fix.csv")

# Filter data
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo 
    st.image("RentalBike.jpg")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_df[(day_df["dteday"] >= str(start_date)) &
                       (day_df["dteday"] <= str(end_date))]

second_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                       (hour_df["dteday"] <= str(end_date))]

# #dataframe
sum_order_items_df = sum_order(second_df)
humidity_df = create_by_humidity_df(second_df)
day_df_count_2011 = count_by_day_df(main_df)
reg_df = total_registered_df(main_df)
cas_df = total_casual_df(main_df)
hour_df = create_hourly_df(second_df)

#header dan jumlah
st.header('Bike Sharing Dashboard :bike:')
st.subheader("Daily Orders")
kolom1, kolom2, kolom3 = st.columns(3)

with kolom1:
    total_sum = reg_df.register_sum.sum()
    st.metric("Total Registered", value=total_sum)

with kolom2:
    total_sum = cas_df.casual_sum.sum()
    st.metric("Total Casual", value=total_sum)

with kolom3:
    total_orders = day_df_count_2011.cnt.sum()
    st.metric("Total Sharing Bike", value=total_orders)

#pertanyaan 1
st.subheader("Faktor apa yang paling mempengaruhi jumlah penyewaan sepeda?")
fig, ax = plt.subplots(figsize=(16, 8))
correlation = main_df[['temp', 'atemp', 'humidity', 'windspeed', 'season', 'workingday', 'cnt']].corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)

plt.title('Korelasi antara Faktor dengan Jumlah Penyewaan Sepeda')
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

#pertanyaan 2
st.subheader("Perbedaan penyewaan di hari kerja vs akhir pekan")
# Buat plot
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x=['Akhir Pekan', 'Hari Kerja'], y=day_df.groupby('workingday')['cnt'].mean(), palette='coolwarm', ax=ax)
ax.set_title("Rata-rata Penyewaan Sepeda pada Hari Kerja vs Akhir Pekan")
ax.set_ylabel("Jumlah Penyewaan Sepeda")
st.pyplot(fig)

#pertanyaan 3
st.subheader("Bagaimana Pola Penyewaan Sepeda Berdasarkan Waktu (Harian, Mingguan, atau Bulanan)?")
# Pola Penyewaan Harian
st.subheader("Pola Penyewaan Harian")
fig, ax = plt.subplots(figsize=(9, 7))
sns.lineplot(x='day', y='cnt', data=day_df, marker='o', ci=None, ax=ax)
ax.set_xlabel("Hari dalam Sebulan")
ax.set_ylabel("Total Penyewaan")
ax.set_xticks(range(1, 32))
ax.grid()
st.pyplot(fig)

# Pola Penyewaan Mingguan
st.subheader("Pola Penyewaan Mingguan")
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x='weekday', y='cnt', data=day_df, estimator=sum, palette='Blues', ax=ax)
ax.set_xlabel("Hari dalam Seminggu")
ax.set_ylabel("Total Penyewaan")
ax.set_xticks(range(7))
ax.set_xticklabels(['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'])
st.pyplot(fig)

# Pola Penyewaan Bulanan
st.subheader("Pola Penyewaan Bulanan")
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x='month', y='cnt', data=day_df, estimator=sum, palette='viridis', ax=ax)
ax.set_xlabel("Bulan")
ax.set_ylabel("Total Penyewaan")
ax.set_xticks(range(12))
ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
st.pyplot(fig)

#pertanyaan 4
st.subheader("Pada jam berapa penyewaan sepeda paling banyak dan paling sedikit?")
# Hitung Rata-rata Penyewaan Sepeda per Jam
hourly_avg = hour_df.groupby('hours')['cnt'].mean()

# Plot Visualisasi
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x=hourly_avg.index, y=hourly_avg.values, marker="o", color='b', ax=ax)
ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Jam", fontsize=14)
ax.set_xlabel("Jam", fontsize=12)
ax.set_ylabel("Jumlah Penyewaan Sepeda", fontsize=12)
ax.set_xticks(range(0, 24))
ax.grid(True)
st.pyplot(fig)

#pertanyaan 5
st.subheader("Apakah perubahan suhu mempengaruhi jumlah penyewaan sepeda?")
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(x=day_df['temp'], y=day_df['cnt'], alpha=0.7, color='b', ax=ax)
ax.set_title("Pengaruh Suhu terhadap Penyewaan Sepeda", fontsize=14)
ax.set_xlabel("Suhu (°C)", fontsize=12)
ax.set_ylabel("Jumlah Penyewaan Sepeda", fontsize=12)
ax.grid(True)
st.pyplot(fig)



