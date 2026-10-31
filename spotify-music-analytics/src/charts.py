import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.analytics import AUDIO_FEATURES

COLORS = {"green": "#1ED760", "muted": "#A7A7A7", "panel": "#181818"}
LAYOUT = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, Arial", color="#F4F4F4"), margin=dict(l=45, r=20, t=55, b=45))
FEATURE_LABELS = {
    "popularity": "Popularitas", "energy": "Energi", "danceability": "Kemudahan untuk Menari",
    "valence": "Nuansa Positif Musik", "acousticness": "Karakteristik Akustik", "loudness": "Tingkat Kekerasan Suara",
    "speechiness": "Unsur Dialog", "instrumentalness": "Karakteristik Instrumental", "liveness": "Suasana Pertunjukan Langsung",
    "tempo": "Tempo Musik", "track_name": "Nama Lagu", "artists": "Artis", "track_genre": "Genre Musik", "explicit": "Konten Eksplisit"
}


def style(fig, title, height=360):
    fig.update_layout(**LAYOUT, title=dict(text=title, x=0.02, xanchor="left"), height=height, hoverlabel=dict(bgcolor="#252525"))
    return fig


def genre_bar(summary: pd.DataFrame, by="avg_popularity", top_n=15, title="Genre dengan Popularitas Tertinggi"):
    data = summary.sort_values(by, ascending=False).head(top_n).sort_values(by)
    labels = "Rata-rata Popularitas" if by == "avg_popularity" else "Jumlah Lagu"
    fig = px.bar(data, x=by, y="track_genre", orientation="h", color=by, color_continuous_scale=["#14532D", COLORS["green"]], custom_data=["track_count"], labels=FEATURE_LABELS)
    fig.update_traces(hovertemplate="Genre Musik: %{y}<br>%{x:.2f}<br>Jumlah Lagu: %{customdata[0]:,}<extra></extra>")
    fig.update_layout(coloraxis_showscale=False, xaxis_title=labels, yaxis_title="")
    return style(fig, title)


def popularity_histogram(df: pd.DataFrame):
    fig = px.histogram(df, x="popularity", nbins=21, color_discrete_sequence=[COLORS["green"]])
    fig.update_traces(hovertemplate="Popularitas: %{x}<br>Jumlah Lagu: %{y:,}<extra></extra>")
    fig.update_layout(xaxis_title="Skor Popularitas", yaxis_title="Jumlah Lagu")
    return style(fig, "Distribusi Popularitas", 320)


def scatter(df: pd.DataFrame, color_feature="popularity", max_points=5000):
    plot_df = df.sample(min(max_points, len(df)), random_state=42) if len(df) > max_points else df.copy()
    hover = ["track_name", "artists", "track_genre", "popularity", "energy", "danceability"]
    fig = px.scatter(plot_df, x="danceability", y="energy", color=color_feature, size="popularity", size_max=10,
                     color_continuous_scale="Viridis", hover_data=hover, labels=FEATURE_LABELS, opacity=0.72)
    fig.update_layout(xaxis_title="Kemudahan untuk Menari", yaxis_title="Energi", coloraxis_showscale=True,
                      coloraxis_colorbar_title_text=FEATURE_LABELS.get(color_feature, "Popularitas"))
    return style(fig, f"Kemudahan untuk Menari dan Energi — sampel {len(plot_df):,} lagu", 420)


def correlation_heatmap(df: pd.DataFrame):
    corr = df[AUDIO_FEATURES].corr(numeric_only=True)
    label_columns = [FEATURE_LABELS.get(column, column) for column in corr.columns]
    fig = go.Figure(go.Heatmap(z=corr.values, x=label_columns, y=label_columns, colorscale="Viridis", zmin=-1, zmax=1,
                               text=np.round(corr.values, 2), texttemplate="%{text:.2f}", hovertemplate="%{y} dengan %{x}<br>r=%{z:.2f}<extra></extra>"))
    fig.update_layout(xaxis_tickangle=-35, yaxis_autorange="reversed")
    fig.update_traces(hovertemplate="%{y} dengan %{x}<br>r=%{z:.2f}<extra></extra>")
    return style(fig, "Korelasi Karakteristik Audio", 440)


def feature_distribution(df: pd.DataFrame, feature="energy"):
    fig = px.histogram(df, x=feature, nbins=30, color_discrete_sequence=["#30C48D"])
    feature_label = FEATURE_LABELS.get(feature, feature.title())
    fig.update_traces(hovertemplate=f"{feature_label}: %{{x:.2f}}<br>Jumlah Lagu: %{{y:,}}<extra></extra>")
    fig.update_layout(xaxis_title=feature_label, yaxis_title="Jumlah Lagu")
    return style(fig, f"Distribusi {feature_label}", 340)


def explicit_donut(df: pd.DataFrame):
    counts = df["explicit"].map({True: "Eksplisit", False: "Tidak Eksplisit"}).value_counts().rename_axis("Jenis Konten").reset_index(name="Jumlah Lagu")
    fig = px.pie(counts, names="Jenis Konten", values="Jumlah Lagu", hole=0.68, color="Jenis Konten", color_discrete_map={"Eksplisit": "#1ED760", "Tidak Eksplisit": "#4E4E4E"})
    fig.update_traces(textposition="inside", textinfo="percent+label", hovertemplate="%{label}<br>Jumlah Lagu: %{value:,}<br>%{percent}<extra></extra>")
    return style(fig, "Distribusi Konten Eksplisit", 340)
