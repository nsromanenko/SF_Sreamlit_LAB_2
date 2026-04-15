import streamlit as st
import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="CSV Analyzer (Polars)", layout="wide")

@st.cache_data
def load_data(file):
    try:
        df = pl.read_csv(file)
    except:
        file.seek(0)
        df = pl.read_csv(file, encoding="cp1251")
    return df

st.title("Анализ CSV (Polars)")

file = st.file_uploader("Загрузите CSV файл", type=["csv"])

if file:
    df = load_data(file)

    st.subheader("Данные")
    st.dataframe(df.head(100).to_pandas())

    numeric_cols = df.select(pl.NUMERIC_DTYPES).columns
    text_cols = df.select(pl.Utf8).columns

    st.subheader("Анализ")

    col1, col2 = st.columns(2)

    with col1:
        group_col = st.selectbox("Группировка", text_cols)

    with col2:
        value_col = st.selectbox("Значение", numeric_cols)

    agg_func = st.radio("Агрегация", ["mean", "median", "std"], horizontal=True)

    chart_type = st.radio("Тип графика", ["Линия", "Scatter"], horizontal=True)

    if st.button("Построить"):
        if agg_func == "mean":
            result = df.groupby(group_col).agg(pl.col(value_col).mean())
        elif agg_func == "median":
            result = df.groupby(group_col).agg(pl.col(value_col).median())
        else:
            result = df.groupby(group_col).agg(pl.col(value_col).std())

        result_pd = result.to_pandas()

        st.subheader("Результат")
        st.dataframe(result_pd)

        fig, ax = plt.subplots()

        if chart_type == "Линия":
            ax.plot(result_pd[group_col], result_pd[value_col])
        else:
            ax.scatter(result_pd[group_col], result_pd[value_col])

        ax.set_xlabel(group_col)
        ax.set_ylabel(value_col)

        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.download_button(
            "Скачать график",
            buf.getvalue(),
            "chart.png",
            "image/png"
        )

    st.subheader("Распределение")

    hist_col = st.selectbox("Столбец", numeric_cols)

    fig, ax = plt.subplots()
    ax.hist(df[hist_col].to_pandas().dropna(), bins=30)

    st.pyplot(fig)
