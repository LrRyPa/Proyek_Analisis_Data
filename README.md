# Proyek Analisis Data: Air Quality Dataset 

Analisis kualitas udara (PM2.5) dari 12 stasiun di Beijing periode Maret 2013 – Februari 2017, lengkap dengan dashboard interaktif menggunakan Streamlit.

**Dashboard online:** https://proyek-kualitas-udara.streamlit.app

## Struktur Proyek
```
Proyek_Analisis_Data/
├── dashboard/
│   ├── dashboard.py            
│   ├── main_data.csv           
│   └── station_locations.csv   
├── data/                       
├── notebook.ipynb              
├── requirements.txt
├── README.md
└── url.txt                     
└── url.txt                     
```

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
Lalu pasang library:
```
pip install -r requirements.txt
```

## Run Streamlit App
Jalankan dari folder utama proyek:
```
streamlit run dashboard/dashboard.py
```

## Sumber Data
Beijing Multi-Site Air Quality Data (PRSA), 12 stasiun, data per jam Maret 2013 – Februari 2017.
