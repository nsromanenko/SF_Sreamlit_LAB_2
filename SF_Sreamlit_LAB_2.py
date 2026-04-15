import streamlit as st
import pandas as pd

if "first_run" not in st.session_state:
    st.session_state["first_run"] = True
if "press_key" not in st.session_state:
    st.session_state["press_key"] = False
if "df_2" not in st.session_state:
    st.session_state["df_2"] = pd.DataFrame()
if "sel_grp" not in st.session_state:
    st.session_state["sel_grp"] = ''
if "sel_arg" not in st.session_state:
    st.session_state["sel_arg"] = ''
if "grafik_type" not in st.session_state:
    st.session_state["grafik_type"] = ''

st.session_state["arg_2"] = list()
st.session_state["arg_1"] = list()

@st.cache_data()
def safe_load_table(file, verbose=False):
    df = None
    try:
        if file.name.endswith(".csv"):
            encodings = ["utf-8", "cp1251"]
            for enc in encodings:
                try:
                    df = pd.read_csv(file, encoding=enc)
                    break
                except UnicodeDecodeError:
                    file.seek(0)
        elif file.name.endswith(".xls") or file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
    except pd.errors.EmptyDataError:
        if verbose:
            st.error("Ошибка: Файл пустой")
            st.stop()
    except Exception as e:
        if verbose:
            st.error(f"Неожиданная ошибка: {str(e)}")
            st.stop()
    return df

file = st.file_uploader("Загрузите файл с таблицей", type=["csv", "xls", "xlsx"])

if st.session_state["first_run"]:
    st.session_state["first_run"] = False
else:
    st.session_state["df_1"] = safe_load_table(file, True)
    st.dataframe(st.session_state["df_1"])
    df_columns = st.session_state["df_1"].columns.values.tolist()
    for i in df_columns:
        if st.session_state["df_1"][i].dtype == 'object':
            #-----------------------------------------------
            st.session_state["arg_1"].append(i)
        if st.session_state["df_1"][i].dtype in ('int8','int16','int32','int64',
                                                 'uint8','uint16','uint32','uint64',
                                                 'float32','float64'):
            st.session_state["arg_2"].append(i)

    col1, col2 = st.columns(2)
    with col1:
        sel_grp = st.selectbox("Выберите колонку для группировки", st.session_state["arg_1"])
    with col2:
        sel_arg = st.selectbox("Выберите колонку для агрегации", st.session_state["arg_2"])
    agr_type = st.radio(
        "Выберите тип агрегации", ["mean", "median", "std"], horizontal=True
    )

    grafik_type = st.radio(
        "Выберите тип Графика", ["Линейны график", "Диаграмма рассеивания"], horizontal=True
    )

    is_pressed = st.button("Создать график")

    if is_pressed:
        if agr_type == "mean":
            st.session_state["df_2"] = st.session_state["df_1"][[sel_grp, sel_arg]].groupby(sel_grp).mean()
        if agr_type == "median":
            st.session_state["df_2"] = st.session_state["df_1"][[sel_grp, sel_arg]].groupby(sel_grp).median()
        if agr_type == "std":
            st.session_state["df_2"] = st.session_state["df_1"][[sel_grp, sel_arg]].groupby(sel_grp).std()
        st.session_state["sel_grp"] = sel_grp
        st.session_state["sel_arg"] = sel_arg
        st.session_state["grafik_type"] = grafik_type
        if grafik_type == "Линейны график":
            st.line_chart(st.session_state["df_2"],
                          x_label=st.session_state["sel_grp"],
                          y_label=st.session_state["sel_arg"])
        if grafik_type == "Диаграмма рассеивания":
            st.scatter_chart(st.session_state["df_2"],
                             x_label=st.session_state["sel_grp"],
                             y_label=st.session_state["sel_arg"])
        st.session_state["press_key"] = True

    if st.session_state["press_key"] == False and not st.session_state["df_2"] is None:
        if st.session_state["grafik_type"] == "Линейны график":
            st.line_chart(st.session_state["df_2"],
                        x_label=st.session_state["sel_grp"],
                        y_label=st.session_state["sel_arg"])
        if st.session_state["grafik_type"] == "Диаграмма рассеивания":
            st.scatter_chart(st.session_state["df_2"],
                             x_label=st.session_state["sel_grp"],
                             y_label=st.session_state["sel_arg"])

st.session_state["press_key"] = False