from pathlib import Path
import json
import pandas as pd
import streamlit as st

from src.data_processing import INPUT_PATH, OUTPUT_PATH, clean_dataset
from src.analytics import AUDIO_FEATURES, filter_tracks, genre_summary, key_insights
from src.charts import genre_bar, popularity_histogram, scatter, correlation_heatmap, feature_distribution, explicit_donut

st.set_page_config(page_title="Analisis Musik Spotify", page_icon="♫", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "Gelap"

is_light = st.session_state.theme == "Terang"
if is_light:
    app_bg, sidebar_bg, panel_bg, border_color, text_color, muted_color = "#f4f6f8", "#ffffff", "#ffffff", "#dfe3e8", "#1f2933", "#667085"
else:
    app_bg, sidebar_bg, panel_bg, border_color, text_color, muted_color = "#0d0d0d", "#111111", "#181818", "#282828", "#f4f4f4", "#a7a7a7"

st.markdown(f"""
<style>
:root {{color-scheme:{'light' if is_light else 'dark'};}}
html, body, [data-testid="stAppViewContainer"] {{background:{app_bg} !important;}}
[data-testid="stAppViewContainer"] * {{caret-color:#1ed760;}}
[data-testid="stMain"] {{background:{app_bg} !important;}}
[data-testid="stMainBlockContainer"] {{padding-top:2rem; padding-bottom:2rem; max-width:1500px; color:{text_color};}}
[data-testid="stHeader"] {{background:{app_bg} !important;}}
[data-testid="stSidebar"] {{background:{sidebar_bg} !important; border-right:1px solid {border_color};}}
[data-testid="stSidebarContent"] {{background:{sidebar_bg} !important;}}
[data-testid="stSidebar"] *, [data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3, [data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] label, [data-testid="stAppViewContainer"] span {{color:{text_color};}}
[data-testid="stMetric"] {{background:{panel_bg}; border:1px solid {border_color}; border-radius:14px; padding:16px; box-shadow:0 8px 24px rgba(0,0,0,.18);}}
[data-testid="stMetricLabel"] {{color:{muted_color} !important;}}
[data-testid="stMetricValue"] {{color:{text_color} !important; font-size:2rem;}}
[data-testid="stTabs"] [role="tablist"] {{gap:4px; border-bottom:1px solid {border_color};}}
[data-testid="stTabs"] [role="tab"] {{border-radius:8px 8px 0 0; padding:8px 16px; background:transparent;}}
[data-testid="stTabs"] [aria-selected="true"] {{background:#1ed760 !important; color:#07150b !important;}}
[data-testid="stTabs"] [aria-selected="true"] * {{color:#07150b !important;}}
.stApp {{background:{app_bg} !important; color:{text_color} !important;}}
.insight {{background:{panel_bg}; color:{text_color}; border-left:3px solid #1ed760; border-radius:8px; padding:10px 14px; margin-bottom:8px;}}
.caption, small {{color:{muted_color} !important;}}
[data-baseweb="select"] > div, [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stTextInput"] div[data-baseweb="input"] {{background:{panel_bg} !important; border-color:{border_color} !important;}}
[data-baseweb="select"] span, [data-baseweb="input"] input, [data-testid="stTextInput"] input {{color:{text_color} !important;}}
[data-testid="stDataFrame"] {{background:{panel_bg}; border:1px solid {border_color}; border-radius:8px;}}
[data-baseweb="segmented"] {{background:{panel_bg} !important; border:1px solid {border_color};}}
[data-baseweb="slider"] {{color:#1ed760 !important;}}
[data-testid="stAlert"] {{background:{panel_bg} !important; border-color:{border_color} !important; color:{text_color} !important;}}
[data-testid="stToolbar"] {{background:{app_bg} !important;}}
.student-profile {{padding:10px 0 4px;}}
.student-profile .student-name {{font-weight:700; font-size:0.95rem; letter-spacing:.02em; color:{text_color};}}
.student-profile .student-meta {{font-size:0.82rem; line-height:1.5; color:{muted_color};}}
.student-profile strong {{color:{text_color};}}
.sidebar-profile {{margin-top:24px; padding-top:14px; border-top:1px solid {border_color};}}
.sidebar-profile .student-name {{font-weight:700; font-size:.9rem; color:{text_color};}}
.sidebar-profile div {{font-size:.82rem; line-height:1.55; color:{muted_color};}}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    source = OUTPUT_PATH if OUTPUT_PATH.exists() else INPUT_PATH
    df = pd.read_csv(source)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns="Unnamed: 0")
    if "duration_min" not in df.columns and "duration_ms" in df.columns:
        df["duration_min"] = df["duration_ms"] / 60000
    for column in ["artists", "album_name", "track_name"]:
        if column in df.columns:
            df[column] = df[column].fillna("Unknown")
    return df


try:
    df = load_data()
except Exception as exc:
    st.error("Dataset tidak dapat dimuat. Letakkan `dataset.csv` dalam folder `data/`, lalu jalankan `python src/data_processing.py`.")
    st.stop()

genres = sorted(df["track_genre"].dropna().astype(str).unique())
pop_min, pop_max = int(df["popularity"].min()), int(df["popularity"].max())
dur_min = float(df["duration_min"].min())
dur_max = float(df["duration_min"].max())

initial_filter_state = {
    "genres": [],
    "popularity": (pop_min, pop_max),
    "explicit_filter": "Semua",
    "duration_filter": (0.0, float(dur_max)),
}
for key, value in initial_filter_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

def reset_filters():
    for key, value in initial_filter_state.items():
        st.session_state[key] = value

with st.sidebar:
    st.markdown("### ANALISIS MUSIK")
    st.caption("Jelajahi katalog lagu Spotify")
    st.segmented_control("Tampilan", ["Gelap", "Terang"], key="theme")
    selected_genres = st.multiselect("Genre Musik", genres, key="genres", placeholder="Semua Genre")
    popularity = st.slider("Rentang Popularitas", pop_min, pop_max, key="popularity")
    explicit = st.segmented_control("Konten Eksplisit", ["Semua", "Eksplisit", "Tidak Eksplisit"], key="explicit_filter")
    duration = st.slider("Durasi (menit)", 0.0, float(dur_max), step=0.5, key="duration_filter")
    st.button("Atur Ulang Filter", use_container_width=True, on_click=reset_filters)
    st.divider()
    st.caption("Filter diterapkan secara konsisten pada seluruh dashboard.")
    st.markdown("""
    <div class="sidebar-profile">
      <div class="student-name">RAFFI KURNIAWAN</div>
      <div>NIM 241041001</div>
      <div>Manajemen Informatika</div>
    </div>
    """, unsafe_allow_html=True)

filtered = filter_tracks(df, selected_genres, popularity, explicit, duration)

def tampilkan_grafik(fig):
    if is_light:
        fig.update_layout(template="plotly_white", paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", font=dict(color="#1f2933", family="Inter, Arial"))
    st.plotly_chart(fig, use_container_width=True)

def kpi(label, value, help_text=""):
    st.metric(label, value, help=help_text)

st.title("Dashboard Analisis Musik Spotify")
st.caption("Tinjauan popularitas lagu, pola genre, dan karakteristik audio berdasarkan filter yang dipilih.")
st.markdown("""
<div class="student-profile">
  <div class="student-name">RAFFI KURNIAWAN</div>
  <div class="student-meta"><strong>NIM</strong>&nbsp; 241041001 &nbsp;•&nbsp; <strong>Program Studi</strong>&nbsp; Manajemen Informatika</div>
</div>
""", unsafe_allow_html=True)

if filtered.empty:
    st.warning("Tidak ada lagu yang sesuai dengan kombinasi filter saat ini. Coba perluas pilihan genre, popularitas, durasi, atau konten eksplisit.", icon="!")
    st.stop()

overview, genres_tab, audio_tab, tracks_tab, notes_tab = st.tabs(["Ringkasan", "Eksplorasi Genre", "Karakteristik Audio", "Eksplorasi Lagu", "Informasi Data"])

with overview:
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Lagu", f"{len(filtered):,}", "Jumlah lagu setelah seluruh filter diterapkan")
    with c2: kpi("Rata-rata Popularitas", f"{filtered['popularity'].mean():.1f}", "Skor popularitas Spotify, bukan jumlah pemutaran")
    with c3: kpi("Rata-rata Energi", f"{filtered['energy'].mean():.3f}", "Rata-rata tingkat intensitas pada rentang 0 hingga 1")
    with c4: kpi("Jumlah Genre Unik", f"{filtered['track_genre'].nunique():,}", "Jumlah genre dalam data yang telah difilter")

    st.markdown("#### Temuan Utama")
    for insight in key_insights(filtered):
        st.markdown(f'<div class="insight">{insight}</div>', unsafe_allow_html=True)

    left, right = st.columns([1.15, 1])
    with left:
        tampilkan_grafik(genre_bar(genre_summary(filtered), top_n=15))
        st.caption("Genre diurutkan berdasarkan rata-rata popularitas pada sampel yang difilter; jumlah lagu ditampilkan saat menunjuk grafik.")
    with right:
        tampilkan_grafik(popularity_histogram(filtered))
        st.caption("Popularitas merupakan skor dari dataset, bukan jumlah pemutaran.")

    tampilkan_grafik(explicit_donut(filtered))

with genres_tab:
    summary = genre_summary(filtered)
    c1, c2 = st.columns([1, 3])
    with c1:
        top_n = st.slider("Jumlah genre yang ditampilkan", 5, min(30, len(summary)), min(15, len(summary)))
        metric = st.radio("Urutkan berdasarkan", ["Jumlah Lagu", "Rata-rata Popularitas"])
    by = "track_count" if metric == "Jumlah Lagu" else "avg_popularity"
    with c2:
        tampilkan_grafik(genre_bar(summary, by=by, top_n=top_n, title=f"{top_n} genre teratas — {metric}"))
    table = summary.rename(columns={"track_genre":"Genre Musik", "track_count":"Jumlah Lagu", "avg_popularity":"Rata-rata Popularitas", "avg_energy":"Rata-rata Energi", "avg_danceability":"Rata-rata Kemudahan untuk Menari"})
    st.dataframe(table.head(top_n).round(3), use_container_width=True, hide_index=True)
    st.caption("Setiap perbandingan dihitung dari data hasil filter saat ini. Genre dengan sampel kecil dapat memberikan hasil yang kurang stabil.")

with audio_tab:
    c1, c2 = st.columns([2, 1])
    with c1:
        feature_labels = {"popularity": "Popularitas", "energy": "Energi", "danceability": "Kemudahan untuk Menari", "valence": "Nuansa Positif Musik", "acousticness": "Karakteristik Akustik"}
        color_feature = st.selectbox("Warna Titik Berdasarkan", ["popularity", "energy", "danceability", "valence", "acousticness"], format_func=lambda value: feature_labels[value])
    with c2:
        max_points = st.selectbox("Ukuran Sampel Diagram", [1000, 3000, 5000], index=2)
    tampilkan_grafik(scatter(filtered, color_feature=color_feature, max_points=max_points))
    st.caption("Titik diagram dipilih secara acak agar tampilan responsif; sampel ini bukan subset analisis yang terpisah.")
    c1, c2 = st.columns([1.25, 1])
    with c1:
        tampilkan_grafik(correlation_heatmap(filtered))
        st.caption("Korelasi hanya menunjukkan hubungan antarvariabel dan tidak membuktikan sebab-akibat.")
    with c2:
        feature_names = {"energy": "Energi", "valence": "Nuansa Positif Musik", "danceability": "Kemudahan untuk Menari", "acousticness": "Karakteristik Akustik"}
        feature = st.selectbox("Karakteristik Distribusi", ["energy", "valence", "danceability", "acousticness"], index=0, format_func=lambda value: feature_names[value])
        tampilkan_grafik(feature_distribution(filtered, feature))

with tracks_tab:
    search = st.text_input("Cari Nama Lagu atau Artis", placeholder="Nama lagu atau artis")
    matching_table = filtered.copy()
    if search:
        mask = matching_table["track_name"].astype(str).str.contains(search, case=False, na=False) | matching_table["artists"].astype(str).str.contains(search, case=False, na=False)
        matching_table = matching_table[mask]

    if matching_table.empty:
        st.info("Data Tidak Ditemukan: tidak ada lagu yang cocok dengan pencarian ini.")
    else:
        matching_table = matching_table.sort_values("popularity", ascending=False)
        rows = st.slider("Jumlah baris yang ditampilkan", 1, len(matching_table), len(matching_table), 1)
        table = matching_table.head(rows).rename(columns={"track_name":"Nama Lagu", "artists":"Artis", "track_genre":"Genre Musik", "duration_min":"Durasi (menit)", "popularity":"Popularitas", "energy":"Energi", "danceability":"Kemudahan untuk Menari", "tempo":"Tempo Musik"})
        columns = ["Nama Lagu", "Artis", "Genre Musik", "Popularitas", "Energi", "Kemudahan untuk Menari", "Tempo Musik", "Durasi (menit)"]
        table = table[columns]
        st.caption(f"Menampilkan {len(table):,} dari {len(matching_table):,} lagu yang cocok.")
        st.dataframe(table.round({"Durasi (menit)": 2, "Energi": 3, "Kemudahan untuk Menari": 3, "Tempo Musik": 1}), use_container_width=True, hide_index=True)

with notes_tab:
    st.markdown("### Sumber Data")
    st.markdown("Dashboard ini menggunakan [Spotify Tracks Dataset di Kaggle](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset). Pastikan izin penggunaan dan lisensi sumber sebelum memublikasikan dataset turunan dalam skala besar.")
    st.markdown("### Definisi Metrik")
    st.markdown("- **Popularitas:** skor dari 0–100 yang disediakan dataset; bukan jumlah pemutaran.\n- **Energi:** ukuran intensitas atau aktivitas musik yang umumnya berada pada rentang 0–1.\n- **Kemudahan untuk Menari:** ukuran kesesuaian lagu untuk menari yang umumnya berada pada rentang 0–1.\n- **Nuansa Positif Musik:** ukuran nuansa positif musik yang umumnya berada pada rentang 0–1.\n- **Konten Eksplisit:** penanda apakah lagu dikategorikan eksplisit pada data sumber.\n- **Tempo Musik:** kecepatan irama lagu yang umumnya dinyatakan dalam ketukan per menit.")
    st.markdown("### Pemrosesan Data")
    report_path = Path("data/data_quality.json")
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        st.json(report)
    else:
        st.info("Jalankan `python src/data_processing.py` untuk menghasilkan laporan kualitas data.")
    st.markdown("### Keterbatasan Data")
    st.warning("Dataset tidak memuat tanggal rilis atau tahun. Analisis tren waktu tidak ditampilkan karena informasi kalender tidak tersedia. ID lagu yang duplikat dipilih berdasarkan kemunculan dengan popularitas tertinggi pada setiap lagu, sehingga representasi genre dapat berubah apabila satu lagu muncul pada beberapa genre.")
