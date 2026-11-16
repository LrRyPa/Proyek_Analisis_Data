# Proyek Analisis Data: Air Quality Dataset ✨

Analisis kualitas udara (PM2.5) dari 12 stasiun pemantau di Beijing periode Maret 2013 – Februari 2017, lengkap dengan dashboard interaktif menggunakan Streamlit.

**Dashboard online:** https://proyek-kualitas-udara.streamlit.app

## Struktur Proyek
```
Proyek_Analisis_Data/
├── dashboard/
│   ├── dashboard.py            # aplikasi Streamlit
│   ├── main_data.csv           # data bersih hasil notebook
│   └── station_locations.csv   # koordinat perkiraan tiap stasiun
├── data/                       # 12 file CSV mentah (PRSA_Data_*.csv)
├── notebook.ipynb              # proses analisis data lengkap
├── requirements.txt
├── README.md
└── url.txt                     # URL dashboard di Streamlit Cloud
```

## Pertanyaan Bisnis
Isi bagian ini sesuai pertanyaan di `notebook.ipynb`, misalnya:
1. Berapa persen rata-rata PM2.5 pada musim pemanasan (Nov–Mar) lebih tinggi dibanding Apr–Okt selama Mar 2013 – Feb 2017?
2. Stasiun mana yang memiliki persentase jam dengan PM2.5 di atas 115 µg/m³ paling tinggi dan paling rendah?
3. Berapa persen penurunan rata-rata PM2.5 saat angin >5 m/s dibanding ≤1 m/s?

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
git clone https://github.com/LrRyPa/Proyek_Analisis_Data.git
cd Proyek_Analisis_Data
python -m venv venv
```
Aktifkan virtual environment:
```
# Windows (PowerShell)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```
Lalu pasang pustaka:
```
pip install -r requirements.txt
```

## Run Streamlit App
Jalankan dari folder utama proyek:
```
streamlit run dashboard/dashboard.py
```
Jika perintah `streamlit` tidak dikenali (misalnya di Windows), gunakan:
```
python -m streamlit run dashboard/dashboard.py
```
Dashboard terbuka di `http://localhost:8501`.

## Menjalankan Notebook
Notebook dapat dijalankan di Google Colab atau Jupyter. Letakkan 12 file CSV di folder `data/` (atau sesuaikan path pada sel *Gathering Data*), lalu jalankan semua sel. Tambahkan pustaka berikut bila belum ada: `matplotlib`, `seaborn`, dan `jupyter`.

## Sumber Data
Beijing Multi-Site Air Quality Data (PRSA), 12 stasiun pemantau, data per jam Maret 2013 – Februari 2017.