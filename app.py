import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="South Karnataka Nutrition Dashboard", layout="wide", page_icon="🥗")

# ── Custom CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Page background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    background-attachment: fixed;
}

/* Hide default streamlit header */
header[data-testid="stHeader"] { background: transparent; }

/* Hero banner */
.hero {
    background: linear-gradient(90deg, #f7971e, #ffd200, #21d397, #7450fe);
    background-size: 300% 300%;
    animation: gradientShift 6s ease infinite;
    border-radius: 20px;
    padding: 40px 48px;
    margin-bottom: 32px;
    color: white;
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.hero h1 { font-size: 2.6rem; font-weight: 800; margin: 0; color: white; }
.hero p  { font-size: 1.05rem; margin: 8px 0 0; opacity: 0.92; color: white; }

/* Metric cards */
.metric-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    backdrop-filter: blur(10px);
}
.metric-card .label { color: #aab4d4; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.metric-card .value { color: white; font-size: 2rem; font-weight: 800; margin-top: 4px; }
.metric-card .unit  { color: #7450fe; font-size: 0.85rem; font-weight: 600; }

/* Section headers */
.section-title {
    color: white;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 24px 0 12px;
    padding-left: 12px;
    border-left: 4px solid #ffd200;
}

/* Tabs styling */
[data-testid="stTabs"] button {
    color: #aab4d4 !important;
    font-weight: 600;
    font-size: 0.95rem;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ffd200 !important;
    border-bottom: 3px solid #ffd200 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stRadio label { color: #ccd6f6 !important; }

/* Selectbox & widgets */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    color: white !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* Divider */
hr { border-color: rgba(255,255,255,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ── Load & clean data ──────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    # Per 100g: nutrients start at column index 4; CWYE Per Serving: nutrients start at 6
    sheet_config = {"Per 100g": ("100g", 4), "CWYE Per Serving": ("serving", 6)}
    all_data = {}
    for sheet_name, (label, nutrient_start) in sheet_config.items():
        df = pd.read_excel("Nutrition Final excel sheet.xlsx", sheet_name=sheet_name)
        nutrient_cols = df.columns[nutrient_start:]
        df = df[df[nutrient_cols].notnull().any(axis=1)].copy()
        df = df.rename(columns={"Survey Food Item": "Food"})
        df = df.reset_index(drop=True)
        all_data[label] = df
    return all_data

data = load_data()

NUTRIENTS = [
    "Energy kcal", "Protein g", "Fat g", "Carbohydrate g", "Fiber g",
    "Calcium mg", "Iron mg", "VitaminC mg", "VitaminA ug", "Sodium mg",
    "Phosphorus mg", "Magnesium mg", "Potassium mg", "Zinc mg",
    "B1 Thiamine mg", "B2 Riboflavin mg", "B3 Niacin mg", "B9 Folate ug",
    "VitaminD ug", "VitaminE mg", "VitaminK ug"
]

COLORS = ["#7450fe", "#21d397", "#ffd200", "#f7971e", "#ff6b6b", "#4ecdc4", "#a8edea"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white", family="Inter"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.1)"),
    margin=dict(t=20, b=80, l=10, r=10),
)

# ── Sidebar ────────────────────────────────────────────────────────────────────

st.sidebar.markdown("## ⚙️ Settings")
serving = st.sidebar.radio("View", ["100g", "serving"], format_func=lambda x: "Per 100g" if x == "100g" else "CWYE Per Serving")
df = data[serving]
food_list = sorted(df["Food"].dropna().unique().tolist())

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dataset Overview")
st.sidebar.markdown(f"- **{len(food_list)} foods** tracked")
st.sidebar.markdown(f"- **{len(NUTRIENTS)} nutrients** per food")
st.sidebar.markdown("- Source: INDB · CWYE · IFCT")
st.sidebar.markdown("- Region: South Karnataka")

# ── Hero Banner ────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <h1>🥗 South Karnataka Nutrition Dashboard</h1>
    <p>Explore, compare, and discover the nutritional profiles of traditional South Karnataka foods</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["🔍  Explore a Food", "⚖️  Compare Two Foods", "🏆  Top Foods by Nutrient"])

# ── Tab 1 ──────────────────────────────────────────────────────────────────────

with tab1:
    selected_food = st.selectbox("Search or select a food", food_list, key="single")
    row = df[df["Food"] == selected_food].iloc[0]
    available = [n for n in NUTRIENTS if pd.notnull(row.get(n))]

    if not available:
        st.warning("No nutrient data available for this food.")
    else:
        # Key metric cards
        metrics = [
            ("Energy", row.get("Energy kcal", 0), "kcal"),
            ("Protein", row.get("Protein g", 0), "g"),
            ("Carbs", row.get("Carbohydrate g", 0), "g"),
            ("Fat", row.get("Fat g", 0), "g"),
        ]
        cols = st.columns(4)
        for col, (label, val, unit) in zip(cols, metrics):
            col.markdown(f"""
            <div class="metric-card">
                <div class="label">{label}</div>
                <div class="value">{val:.1f}</div>
                <div class="unit">{unit}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        left, right = st.columns([1, 2])

        with left:
            st.markdown('<div class="section-title">Macronutrient Split</div>', unsafe_allow_html=True)
            macros = {k: v for k, v in {
                "Protein": row.get("Protein g", 0),
                "Fat": row.get("Fat g", 0),
                "Carbohydrate": row.get("Carbohydrate g", 0),
                "Fiber": row.get("Fiber g", 0)
            }.items() if pd.notnull(v) and v > 0}

            fig_pie = go.Figure(go.Pie(
                labels=list(macros.keys()),
                values=list(macros.values()),
                hole=0.5,
                marker=dict(colors=COLORS),
                textinfo="percent+label",
                textfont=dict(size=13, color="white"),
            ))
            fig_pie.update_layout(**{**PLOTLY_LAYOUT, "margin": dict(t=10, b=10, l=10, r=10), "height": 300})
            st.plotly_chart(fig_pie, use_container_width=True)

        with right:
            st.markdown('<div class="section-title">All Nutrients</div>', unsafe_allow_html=True)
            vals = [row.get(n, 0) for n in available]
            labels = [n.replace(" mg","").replace(" ug","").replace(" g","").replace(" kcal","") for n in available]

            fig_bar = go.Figure(go.Bar(
                x=labels, y=vals,
                marker=dict(
                    color=vals,
                    colorscale=[[0, "#7450fe"], [0.5, "#21d397"], [1, "#ffd200"]],
                    showscale=False
                ),
                text=[f"{v:.1f}" for v in vals],
                textposition="outside",
                textfont=dict(color="white", size=11),
            ))
            fig_bar.update_layout(**{**PLOTLY_LAYOUT, "height": 360, "xaxis": dict(tickangle=-40, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="white"))})
            st.plotly_chart(fig_bar, use_container_width=True)

# ── Tab 2 ──────────────────────────────────────────────────────────────────────

with tab2:
    st.markdown('<div class="section-title">Pick two foods to compare</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    food_a = c1.selectbox("🟣 Food A", food_list, index=0, key="cmp_a")
    food_b = c2.selectbox("🟡 Food B", food_list, index=1, key="cmp_b")

    row_a = df[df["Food"] == food_a].iloc[0]
    row_b = df[df["Food"] == food_b].iloc[0]
    common = [n for n in NUTRIENTS if pd.notnull(row_a.get(n)) and pd.notnull(row_b.get(n))]

    if not common:
        st.warning("Not enough shared nutrient data to compare.")
    else:
        labels = [n.replace(" mg","").replace(" ug","").replace(" g","").replace(" kcal","") for n in common]

        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Bar(name=food_a, x=labels, y=[row_a[n] for n in common],
                                  marker_color="#7450fe", opacity=0.9))
        fig_cmp.add_trace(go.Bar(name=food_b, x=labels, y=[row_b[n] for n in common],
                                  marker_color="#ffd200", opacity=0.9))
        fig_cmp.update_layout(**{
            **PLOTLY_LAYOUT,
            "barmode": "group",
            "height": 420,
            "legend": dict(orientation="h", y=1.12, font=dict(color="white", size=13)),
            "xaxis": dict(tickangle=-40, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="white")),
            "yaxis": dict(gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
        })
        st.plotly_chart(fig_cmp, use_container_width=True)

        st.markdown('<div class="section-title">Nutrient Table</div>', unsafe_allow_html=True)
        table = pd.DataFrame({
            "Nutrient": labels,
            food_a: [round(row_a[n], 2) for n in common],
            food_b: [round(row_b[n], 2) for n in common],
        })
        st.dataframe(table, use_container_width=True, hide_index=True)

# ── Tab 3 ──────────────────────────────────────────────────────────────────────

with tab3:
    st.markdown('<div class="section-title">Find the richest sources of any nutrient</div>', unsafe_allow_html=True)

    col_sel, col_slider = st.columns([2, 1])
    nutrient_choice = col_sel.selectbox(
        "Choose a nutrient",
        NUTRIENTS,
        format_func=lambda n: n.replace(" mg","").replace(" ug","").replace(" g","").replace(" kcal","")
    )
    top_n = col_slider.slider("Show top N foods", 5, 20, 10)

    top_df = df[["Food", nutrient_choice]].dropna().sort_values(nutrient_choice, ascending=False).head(top_n)

    if top_df.empty:
        st.warning("No data available for this nutrient.")
    else:
        fig_top = go.Figure(go.Bar(
            x=top_df[nutrient_choice],
            y=top_df["Food"],
            orientation="h",
            marker=dict(
                color=top_df[nutrient_choice],
                colorscale=[[0, "#7450fe"], [0.5, "#21d397"], [1, "#ffd200"]],
                showscale=False,
            ),
            text=[f"{v:.1f}" for v in top_df[nutrient_choice]],
            textposition="outside",
            textfont=dict(color="white"),
        ))
        fig_top.update_layout(**{
            **PLOTLY_LAYOUT,
            "height": 440,
            "margin": dict(t=10, b=30, l=220, r=60),
            "yaxis": dict(autorange="reversed", tickfont=dict(color="white", size=13), gridcolor="rgba(255,255,255,0.06)"),
            "xaxis": dict(title=nutrient_choice, tickfont=dict(color="white"), gridcolor="rgba(255,255,255,0.06)"),
        })
        st.plotly_chart(fig_top, use_container_width=True)
