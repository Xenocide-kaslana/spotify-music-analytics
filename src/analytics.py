import pandas as pd

AUDIO_FEATURES = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]


def filter_tracks(df: pd.DataFrame, genres=None, popularity_range=(0, 100), explicit="All", duration_range=None) -> pd.DataFrame:
    result = df.copy()
    if genres:
        result = result[result["track_genre"].isin(genres)]
    result = result[result["popularity"].between(popularity_range[0], popularity_range[1])]
    if explicit in ("Explicit", "Eksplisit"):
        result = result[result["explicit"] == True]
    elif explicit in ("Non-explicit", "Tidak Eksplisit"):
        result = result[result["explicit"] == False]
    if duration_range is not None:
        result = result[result["duration_min"].between(duration_range[0], duration_range[1])]
    return result


def genre_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("track_genre", as_index=False)
            .agg(track_count=("track_id", "size"), avg_popularity=("popularity", "mean"),
                 avg_energy=("energy", "mean"), avg_danceability=("danceability", "mean"))
            .sort_values("track_count", ascending=False))


def key_insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["Tidak ada lagu yang sesuai dengan filter saat ini."]
    summary = genre_summary(df)
    insights = []
    if len(summary) >= 1:
        best = summary.loc[summary["avg_popularity"].idxmax()]
        insights.append(f"Genre dengan rata-rata popularitas tertinggi adalah {best['track_genre']} ({best['avg_popularity']:.1f}; jumlah lagu {int(best['track_count'])}).")
        biggest = summary.iloc[0]
        insights.append(f"Genre dengan jumlah lagu terbanyak adalah {biggest['track_genre']} ({int(biggest['track_count'])} lagu).")
    explicit_share = 100 * df["explicit"].mean()
    insights.append(f"Sebanyak {explicit_share:.1f}% lagu memiliki konten eksplisit.")
    corr = df[AUDIO_FEATURES].corr(numeric_only=True)
    pairs = [(corr.columns[i], corr.columns[j], corr.iloc[i, j])
             for i in range(len(corr)) for j in range(i + 1, len(corr))]
    if pairs:
        feature_a, feature_b, value = max(pairs, key=lambda x: abs(x[2]))
        nama_fitur = {
            "danceability": "kemudahan untuk menari", "energy": "energi", "loudness": "tingkat kekerasan suara",
            "speechiness": "unsur dialog", "acousticness": "karakteristik akustik", "instrumentalness": "karakteristik instrumental",
            "liveness": "suasana pertunjukan langsung", "valence": "nuansa positif musik", "tempo": "tempo musik"
        }
        insights.append(f"Hubungan korelasi terkuat ditemukan antara {nama_fitur.get(feature_a, feature_a)} dan {nama_fitur.get(feature_b, feature_b)} (r={value:.2f}). Korelasi ini tidak menunjukkan hubungan sebab-akibat.")
    return insights
