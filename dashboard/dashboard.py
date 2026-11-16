import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import st_folium
from pathlib import Path

st.set_page_config(page_title="Dashboard Kualitas Udara Beijing", page_icon="🌫️", layout="wide")

BASE_DIR = Path(__file__).parent
ACCENT, BASE, DARK = "#C0392B", "#9AA5B1", "#2C3E50"
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
KATEGORI = ["Baik (0–35)", "Sedang (35–75)", "Tidak sehat bagi sensitif (75–115)",
            "Tidak sehat (115–150)", "Sangat tidak sehat (150–250)", "Berbahaya (>250)"]
WARNA_KAT = ["#2E86AB", "#7FB3D5", "#F4D35E", "#F4A259", "#D1495B", "#6B0F1A"]


@st.cache_data
def load_data():
    df = pd.read_csv(BASE_DIR / "main_data.csv", parse_dates=["datetime"])
    df["station"] = df["station"].astype("category")
    df["hour"] = df["datetime"].dt.hour
    df["month"] = df["datetime"].dt.month
    df["musim"] = np.where(df["month"].isin([11, 12, 1, 2, 3]), "Pemanasan (Nov–Mar)", "Non-pemanasan (Apr–Okt)")
    df["kategori"] = pd.cut(df["PM2.5"], [0, 35, 75, 115, 150, 250, np.inf], labels=KATEGORI)
    df["kelas_angin"] = pd.cut(df["WSPM"], [-0.01, 1, 2, 3, 5, np.inf], labels=["≤1", "1–2", "2–3", "3–5", ">5"])
    coords = pd.read_csv(BASE_DIR / "station_locations.csv")
    return df, coords


df, coords = load_data()

st.sidebar.title("Filter")
tmin, tmax = df["datetime"].min().date(), df["datetime"].max().date()
rentang = st.sidebar.date_input("Rentang tanggal", (tmin, tmax), min_value=tmin, max_value=tmax)
semua = sorted(df["station"].cat.categories)
pilih = st.sidebar.multiselect("Stasiun", semua, default=semua)
st.sidebar.caption("Sumber: Beijing Multi-Site Air Quality (12 stasiun, Mar 2013 – Feb 2017). "
                    "Kategori PM2.5 mengikuti breakpoint 24 jam standar China HJ 633-2012.")

if len(rentang) != 2 or not pilih:
    st.info("Pilih rentang tanggal (awal dan akhir) serta minimal satu stasiun.")
    st.stop()

mask = (df["datetime"].dt.date >= rentang[0]) & (df["datetime"].dt.date <= rentang[1]) & df["station"].isin(pilih)
d = df[mask]
if d.empty:
    st.warning("Tidak ada data untuk filter ini.")
    st.stop()

st.title("🌫️ Dashboard Kualitas Udara Beijing (PM2.5)")
st.caption("Kapan, di mana, dan dalam kondisi apa PM2.5 paling tinggi? Gunakan filter di sisi kiri.")

bulanan = d.set_index("datetime")["PM2.5"].resample("MS").mean().dropna()
per_stasiun = d.groupby("station", observed=True)["PM2.5"].mean().sort_values(ascending=False)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rata-rata PM2.5", f"{d['PM2.5'].mean():.1f} µg/m³")
c2.metric("Jam > 115 µg/m³ (tidak sehat)", f"{(d['PM2.5'] > 115).mean():.1%}")
c3.metric("Bulan tertinggi", f"{bulanan.idxmax():%b %Y}", f"{bulanan.max():.0f} µg/m³", delta_color="off")
c4.metric("Stasiun tertinggi", per_stasiun.index[0], f"{per_stasiun.iloc[0]:.1f} µg/m³", delta_color="off")

tab1, tab2, tab3 = st.tabs(["📅 Tren & Musim", "📍 Stasiun & Peta", "🕒 Jam & Angin"])

with tab1:
    st.subheader("Bagaimana tren PM2.5 bulanan dan kapan puncaknya?")
    fig = go.Figure(go.Scatter(x=bulanan.index, y=bulanan.values, mode="lines+markers",
                               line=dict(color=DARK, width=2.5), marker=dict(size=5),
                               hovertemplate="%{x|%b %Y}: %{y:.1f} µg/m³<extra></extra>"))
    for y in range(bulanan.index.year.min(), bulanan.index.year.max() + 2):
        fig.add_vrect(x0=f"{y-1}-11-01", x1=f"{y}-03-31", fillcolor=ACCENT, opacity=0.08, line_width=0)
    fig.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="PM2.5 (µg/m³)", xaxis_title=None,
                      template="plotly_white")
    fig.update_xaxes(range=[bulanan.index.min(), bulanan.index.max()])
    st.plotly_chart(fig, width="stretch")
    st.caption("Blok merah muda = musim pemanasan (Nov–Mar).")

    col_a, col_b = st.columns(2)
    kal = d.groupby("month")["PM2.5"].mean().reindex(range(1, 13))
    warna = [ACCENT if m in (11, 12, 1, 2, 3) else BASE for m in kal.index]
    f2 = go.Figure(go.Bar(x=BULAN, y=kal.values, marker_color=warna, text=kal.round(0), textposition="outside",
                          hovertemplate="%{x}: %{y:.1f} µg/m³<extra></extra>"))
    f2.update_layout(title="Rata-rata per bulan kalender", height=360, template="plotly_white",
                     yaxis_title="PM2.5 (µg/m³)", margin=dict(l=0, r=0, t=40, b=0))
    col_a.plotly_chart(f2, width="stretch")

    bins = pd.to_datetime(["2013-03-01", "2014-03-01", "2015-03-01", "2016-03-01", "2017-03-01"])
    lab = ["Mar 2013–Feb 2014", "Mar 2014–Feb 2015", "Mar 2015–Feb 2016", "Mar 2016–Feb 2017"]
    per = d.assign(periode=pd.cut(d["datetime"], bins, labels=lab, right=False)).groupby("periode", observed=True)["PM2.5"].mean()
    f3 = go.Figure(go.Bar(x=per.index.astype(str), y=per.values, marker_color=[BASE] * (len(per) - 1) + [ACCENT],
                          text=per.round(1), textposition="outside"))
    judul = "Rata-rata PM2.5 per tahun pemantauan"
    if len(per) >= 2:
        judul += f" ({per.iloc[-1] / per.iloc[0] - 1:+.1%} awal → akhir)"
    f3.update_layout(title=judul, height=360, template="plotly_white", yaxis_title="PM2.5 (µg/m³)",
                     margin=dict(l=0, r=0, t=40, b=0))
    col_b.plotly_chart(f3, width="stretch")

    pem = d.groupby("musim")["PM2.5"].mean()
    if {"Pemanasan (Nov–Mar)", "Non-pemanasan (Apr–Okt)"} <= set(pem.index):
        st.info(f"**Insight:** musim pemanasan rata-rata **{pem['Pemanasan (Nov–Mar)'] / pem['Non-pemanasan (Apr–Okt)'] - 1:+.0%}** "
                f"lebih tinggi ({pem['Pemanasan (Nov–Mar)']:.0f} vs {pem['Non-pemanasan (Apr–Okt)']:.0f} µg/m³) dibanding Apr–Okt. "
                "Pusatkan intervensi dan kampanye kesehatan pada Oktober–Maret.")

with tab2:
    st.subheader("Stasiun mana yang paling tercemar?")
    ring = (d.groupby("station", observed=True)["PM2.5"]
            .agg(rata2="mean", persen_tidak_sehat=lambda s: (s > 115).mean() * 100).reset_index()
            .merge(coords, on="station").sort_values("rata2"))
    col_a, col_b = st.columns([1, 1.2])

    warna = [ACCENT if s == ring["station"].iloc[-1] else (DARK if s == ring["station"].iloc[0] else BASE) for s in ring["station"]]
    f4 = go.Figure(go.Bar(y=ring["station"], x=ring["rata2"], orientation="h", marker_color=warna,
                          text=ring["rata2"].round(1), textposition="outside"))
    f4.update_layout(title="Rata-rata PM2.5 per stasiun (µg/m³)", height=440, template="plotly_white",
                     margin=dict(l=0, r=30, t=40, b=0))
    col_a.plotly_chart(f4, width="stretch")

    tanpa_peta = col_b.checkbox("Peta dasar tidak muncul? Tampilkan tanpa peta dasar", value=False)
    hover = {"rata2": ":.1f", "persen_tidak_sehat": ":.1f", "lat": False, "lon": False}
    skala = ["#2E86AB", "#F4D35E", "#C0392B"]
    label = {"rata2": "Rata-rata PM2.5", "persen_tidak_sehat": "% jam > 115"}
    if tanpa_peta:
        fm = px.scatter(ring, x="lon", y="lat", size="rata2", color="persen_tidak_sehat", text="station",
                        hover_name="station", hover_data=hover, color_continuous_scale=skala, size_max=28,
                        labels={**label, "lon": "Bujur", "lat": "Lintang"},
                        title="Sebaran stasiun (warna = % jam > 115 µg/m³)")
        fm.update_traces(textposition="top center")
        fm.update_layout(template="plotly_white")
    else:
        fm = None
    if fm is not None:
        fm.update_layout(height=440, margin=dict(l=0, r=0, t=40, b=0))
        col_b.plotly_chart(fm, width="stretch")
    else:
        peta = folium.Map(
            location=[ring["lat"].mean(), ring["lon"].mean()], zoom_start=10,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            attr="Tiles © Esri")
        for _, r in ring.iterrows():
            warna = "red" if r["persen_tidak_sehat"] > 25 else ("orange" if r["persen_tidak_sehat"] >= 22 else "green")
            folium.CircleMarker(
                location=[r["lat"], r["lon"]], radius=max(5, r["rata2"] / 6),
                color=warna, fill=True, fill_opacity=0.65,
                tooltip=(f"<b>{r['station']}</b><br>Rata-rata PM2.5: {r['rata2']:.1f} µg/m³"
                         f"<br>Jam > 115 µg/m³: {r['persen_tidak_sehat']:.1f}%")
            ).add_to(peta)
        if len(ring) > 1:
            peta.fit_bounds([[ring["lat"].min(), ring["lon"].min()], [ring["lat"].max(), ring["lon"].max()]])
        col_b.markdown("**Peta stasiun** (ukuran = rata-rata PM2.5; warna = % jam > 115 µg/m³: "
                       "🟢 <22%, 🟠 22–25%, 🔴 >25%)")
        with col_b:
            st_folium(peta, height=420, use_container_width=True, returned_objects=[])
    st.caption("Koordinat stasiun adalah perkiraan lokasi dan hanya dipakai untuk visualisasi peta.")

    kom = (pd.crosstab(d["station"], d["kategori"], normalize="index") * 100).reindex(ring["station"])
    f5 = go.Figure()
    for k, c in zip(KATEGORI, WARNA_KAT):
        if k in kom.columns:
            f5.add_bar(y=kom.index, x=kom[k], name=k, orientation="h", marker_color=c,
                       hovertemplate="%{y}<br>" + k + ": %{x:.1f}%<extra></extra>")
    f5.update_layout(barmode="stack", title="Komposisi kategori PM2.5 (% jam)", height=460, template="plotly_white",
                     xaxis=dict(range=[0, 100], ticksuffix="%"), legend=dict(orientation="h", y=-0.15),
                     margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(f5, width="stretch")

    if len(ring) > 1:
        t, r = ring.iloc[-1], ring.iloc[0]
        st.info(f"**Insight:** **{t['station']}** tertinggi ({t['rata2']:.1f} µg/m³; {t['persen_tidak_sehat']:.1f}% jam > 115) "
                f"dan **{r['station']}** terendah ({r['rata2']:.1f} µg/m³; {r['persen_tidak_sehat']:.1f}%): selisih {t['rata2'] / r['rata2'] - 1:+.0%}. "
                "Prioritaskan pengawasan di stasiun berwarna merah.")

with tab3:
    st.subheader("Jam berapa puncaknya, dan bagaimana pengaruh angin?")
    col_a, col_b = st.columns(2)

    pola = d.groupby(["musim", "hour"])["PM2.5"].mean().reset_index()
    f6 = px.line(pola, x="hour", y="PM2.5", color="musim",
                 color_discrete_map={"Pemanasan (Nov–Mar)": ACCENT, "Non-pemanasan (Apr–Okt)": BASE},
                 labels={"hour": "Jam", "PM2.5": "PM2.5 (µg/m³)", "musim": ""})
    f6.update_traces(line_width=3)
    f6.update_layout(title="Pola harian PM2.5", height=380, template="plotly_white", legend=dict(orientation="h", y=-0.2),
                     xaxis=dict(tickmode="linear", dtick=3), margin=dict(l=0, r=0, t=40, b=0))
    col_a.plotly_chart(f6, width="stretch")

    ang = d.groupby("kelas_angin", observed=True)["PM2.5"].mean()
    f7 = go.Figure(go.Bar(x=ang.index.astype(str), y=ang.values, text=ang.round(0), textposition="outside",
                          marker_color=[ACCENT, "#D98880", BASE, BASE, DARK][:len(ang)]))
    f7.update_layout(title="PM2.5 menurut kecepatan angin (m/s)", height=380, template="plotly_white",
                     xaxis_title="Kecepatan angin (m/s)", yaxis_title="PM2.5 (µg/m³)", margin=dict(l=0, r=0, t=40, b=0))
    col_b.plotly_chart(f7, width="stretch")

    jam = d.groupby("hour")["PM2.5"].mean()
    msg = f"**Insight:** puncak harian pada **{jam.idxmax():02d}:00** ({jam.max():.0f} µg/m³), terendah **{jam.idxmin():02d}:00** ({jam.min():.0f} µg/m³)."
    if len(ang) >= 2:
        msg += (f" PM2.5 turun **{ang.iloc[-1] / ang.iloc[0] - 1:+.0%}** dari angin {ang.index[0]} ke {ang.index[-1]} m/s."
                " Siapkan peringatan dini pada sore–malam dan saat angin lemah.")
    st.info(msg)

    urutan = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    wd = d.groupby("wd")["PM2.5"].mean().reindex(urutan)
    f8 = go.Figure(go.Barpolar(r=wd.values, theta=urutan, marker_color=[ACCENT if v > 95 else BASE for v in wd.fillna(0)]))
    f8.update_layout(title="PM2.5 menurut arah datangnya angin", height=420, template="plotly_white",
                     polar=dict(angularaxis=dict(direction="clockwise", rotation=90)), margin=dict(l=0, r=0, t=50, b=20))
    st.plotly_chart(f8, width="stretch")

st.caption("Proyek Analisis Data – Air Quality Dataset")