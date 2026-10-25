"""AgriSwitch-MASI: four-page historical research dashboard.
Run with: streamlit run app.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT
GREEN = "#286847"
PALETTE = ["#286847", "#70ad85", "#e1a344", "#417b9e", "#8e70b3", "#c06b54"]
YEARS_MASI = ["2021-22", "2022-23", "2023-24", "2024-25"]

st.set_page_config(page_title="AgriSwitch-MASI | Agricultural Insights", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")
st.html("""<style>
:root { --forest:#184d37; --mint:#eff7f0; }
.block-container { max-width: 1390px; padding-top: 1.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #f3f8f2; border-right:1px solid #dbe7dc; }
[data-testid="stMetric"] { background:#f1f7f0; border:1px solid #dce9dd; border-radius:14px; padding:14px 17px; }
[data-testid="stMetricLabel"] { font-weight:600; }
h1,h2,h3 { letter-spacing:-.025em; }
.hero { background:linear-gradient(115deg,#194c38 0%,#276e4f 62%,#39865d 100%);
        padding:27px 32px;border-radius:18px;color:#fff;margin:6px 0 20px; }
.hero h1 { color:white; font-size:2.05rem;margin:0 0 8px; }
.hero p { color:#e4f3e7; font-size:1rem;margin:0; }
.eyebrow { font-size:.78rem;letter-spacing:.12em;font-weight:700;color:#39805a;text-transform:uppercase; }
.note { background:#f1f7f1; border-left:4px solid #54966b; border-radius:8px;
        padding:12px 15px; font-size:.91rem; color:#315642; margin:12px 0; }
[data-testid="stRadio"] label { padding-top:4px;padding-bottom:4px; }
</style>""")

@st.cache_data(show_spinner=False)
def load_csv(name):
    filename = DATA / name
    if not filename.exists():
        return pd.DataFrame()
    return pd.read_csv(filename)

crop = load_csv("agriswitch_with_target.csv")
climate = load_csv("climate_annual_complete.csv")
market = load_csv("AgriSwitch_Market_Arrivals_Cleaned.csv")
masi = load_csv("AgriSwitch_MASI_Results.csv")

# Drop empty, incomplete labels from class summaries (but not from area trends).
if not crop.empty:
    crop["Year"] = crop["Year"].astype(str)
if not climate.empty:
    climate["Year"] = climate["Year"].astype(str)
if not market.empty:
    market["Year"] = market["Year"].astype(str)
    market["Commodity"] = market["Commodity"].astype(str).str.strip()
if not masi.empty:
    masi["Commodity"] = masi["Commodity"].astype(str).str.strip()

PAGES = [
    "Overview Dashboard",
    "Crop Pattern Analysis",
    "Climate Analysis",
    "Market Arrivals & MASI",
]

with st.sidebar:
    st.markdown("## 🌾 AgriSwitch-MASI")
    st.caption("Agricultural research explorer")
    st.divider()
    page = st.radio("Navigation", PAGES, label_visibility="collapsed")
    st.divider()
    st.markdown("**Research coverage**")
    st.caption("5 districts · Maharashtra")
    st.caption("6 crops · 2017–18 to 2022–23")
    st.caption("Climate: through 2024–25")
    st.caption("Market-arrival stability: 2021–22 to 2024–25")
    with st.expander("Dataset status"):
        for title, df in [("Crop & area",crop),("Climate",climate),("Market arrivals",market),("MASI",masi)]:
            st.write(f"{'✅' if not df.empty else '⚠️'} {title}: {len(df)} rows")
    st.caption("Research demonstration · historical records, not live forecasts")

st.html('''<div class="hero"><h1>🌾 AgriSwitch–MASI</h1>
<p>Climate-related crop patterns and market-arrival stability in selected Maharashtra districts</p></div>''')


def chart(fig):
    fig.update_layout(
        margin=dict(l=12,r=12,t=55,b=12),
        font=dict(family="Arial",size=12),
        legend_title_text="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified" if fig.data and fig.data[0].type in ("scatter", "bar") else "closest",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(70,115,79,.12)")
    st.plotly_chart(fig, use_container_width=True)


def empty(df):
    if df.empty:
        st.warning("No observations match the selected filters.")
        return True
    return False


def selection(df, key, include_crop=True, include_year=True):
    cols = st.columns(3 if include_crop and include_year else 2)
    districts = sorted(df["District"].dropna().unique())
    district = cols[0].selectbox("District", ["All districts"] + districts, key=f"{key}_district")
    chosen_crop = "All crops"
    year = "All years"
    if include_crop:
        crops = sorted(df["Crop"].dropna().unique())
        chosen_crop = cols[1].selectbox("Crop", ["All crops"] + crops, key=f"{key}_crop")
    if include_year:
        years = sorted(df["Year"].dropna().unique())
        year = cols[2 if include_crop else 1].selectbox("Agricultural year", ["All years"] + years, key=f"{key}_year")
    f = df.copy()
    if district != "All districts":
        f = f[f["District"] == district]
    if chosen_crop != "All crops":
        f = f[f["Crop"] == chosen_crop]
    if year != "All years":
        f = f[f["Year"] == year]
    return f, district, chosen_crop, year


def area_fig(df, title="Cultivated area by agricultural year"):
    ag = df.groupby("Year", as_index=False)["Area_ha"].sum().sort_values("Year")
    fig = px.bar(ag, x="Year", y="Area_ha", color_discrete_sequence=[GREEN], title=title,
                 labels={"Area_ha":"Cultivated area (ha)","Year":"Agricultural year"})
    fig.update_traces(hovertemplate="%{x}<br>%{y:,.0f} hectares<extra></extra>")
    return fig


if page == "Overview Dashboard":
    st.markdown('<div class="eyebrow">Research at a glance</div>', unsafe_allow_html=True)
    st.header("Overview Dashboard")
    if empty(crop):
        st.stop()
    total_labels = int(crop["AgriSwitch_Target"].notna().sum())
    metrics = st.columns(4)
    metrics[0].metric("Districts studied", f"{crop['District'].nunique()}")
    metrics[1].metric("Crops analysed", f"{crop['Crop'].nunique()}")
    metrics[2].metric("Crop-area records", f"{len(crop)}")
    metrics[3].metric("Valid area-change labels", f"{total_labels}")
    st.html('<div class="note">Explore observed agricultural and climate patterns. District-level cultivated-area changes do not demonstrate individual farmers switching crops.</div>')
    st.subheader("Explore the data")
    f, district, chosen_crop, year = selection(crop, "overview")
    if not empty(f):
        left, right = st.columns([1.25, 1])
        with left:
            chart(area_fig(f))
        with right:
            counts = f["AgriSwitch_Target"].dropna().map({0.0:"Below 10%",1.0:"At least 10%"}).value_counts()
            if not counts.empty:
                fig = px.pie(names=counts.index, values=counts.values, hole=.62,
                    color_discrete_sequence=["#286847", "#98cdb0"],
                    title="Historical crop-area change categories")
                fig.update_traces(textinfo="percent+label")
                chart(fig)
            else:
                st.info("Change labels are unavailable for these records.")
        st.markdown("#### Quick statistics for selected records")
        m1,m2,m3 = st.columns(3)
        m1.metric("Total area across selected records",f"{f['Area_ha'].sum():,.0f} ha")
        m2.metric("Significant-change labels",f"{int(f['AgriSwitch_Target'].eq(1).sum())}")
        m3.metric("Reporting years",str(f["Year"].nunique()))
    st.caption("Crop records: 2017–18 to 2022–23. Climate: 2017–18 to 2024–25. MASI: 2021–22 to 2024–25.")

elif page == "Crop Pattern Analysis":
    st.markdown('<div class="eyebrow">Cultivation trends</div>', unsafe_allow_html=True)
    st.header("🌱 Crop Pattern Analysis")
    st.write("Compare cultivated area, recorded production, and yield by district, crop, and agricultural year.")
    if empty(crop): st.stop()
    f, district, chosen_crop, year = selection(crop, "crop")
    if not empty(f):
        a,b,c = st.columns(3)
        a.metric("Selected records",f"{len(f)}")
        b.metric("Total area in selected records",f"{f['Area_ha'].sum():,.0f} ha")
        c.metric("Significant year-on-year changes",f"{int(f['AgriSwitch_Target'].eq(1).sum())}")
        st.subheader("Cultivated-area trends")
        trend = f.groupby(["Year","Crop"],as_index=False)["Area_ha"].sum().sort_values("Year")
        if chosen_crop == "All crops":
            fig = px.line(trend,x="Year",y="Area_ha",color="Crop",markers=True,
                color_discrete_sequence=PALETTE,title="Cultivated area by crop",
                labels={"Area_ha":"Area (hectares)","Year":"Agricultural year"})
        else:
            fig = px.line(trend,x="Year",y="Area_ha",markers=True,title=f"{chosen_crop} cultivated area",
                color_discrete_sequence=[GREEN],labels={"Area_ha":"Area (hectares)","Year":"Agricultural year"})
        chart(fig)
        left,right=st.columns(2)
        with left:
            vals=f.dropna(subset=["Area_Change_Pct"])
            if not vals.empty:
                fig=px.bar(vals,x="Year",y="Area_Change_Pct",color="Crop" if chosen_crop=="All crops" else None,
                    barmode="group",color_discrete_sequence=PALETTE,title="Year-on-year area change (%)")
                fig.add_hline(y=10,line_dash="dot",line_color="#9c6a22")
                fig.add_hline(y=-10,line_dash="dot",line_color="#9c6a22")
                chart(fig)
            else:st.info("Previous-year area comparison is unavailable for these records.")
        with right:
            tab=f.groupby("Crop",as_index=False)["Area_ha"].sum().sort_values("Area_ha",ascending=False)
            fig=px.bar(tab,x="Crop",y="Area_ha",title="Area distribution by crop",
                color_discrete_sequence=["#70ad85"])
            chart(fig)
        st.subheader("Underlying crop records")
        fields=["District","Crop","Year","Area_ha","Previous_Area_ha","Area_Change_Pct","Production","Production_Unit","Yield","Yield_Unit"]
        st.dataframe(f[fields].sort_values(["District","Crop","Year"]),use_container_width=True,hide_index=True)
        st.caption("Production and yield units vary across crops. Do not add together unlike production units.")

elif page == "Climate Analysis":
    st.markdown('<div class="eyebrow">Observed climate</div>', unsafe_allow_html=True)
    st.header("🌦️ Climate Analysis")
    st.write("Explore rainfall, temperatures, and within-study-period climate anomalies across the selected districts.")
    if empty(climate): st.stop()
    f,district,_,year=selection(climate,"climate",include_crop=False)
    climate_metrics={
        "Annual rainfall":"Annual_Rainfall",
        "Mean minimum temperature":"Mean_Min_Temp",
        "Mean maximum temperature":"Mean_Max_Temp",
        "Maximum daily rainfall":"Max_Daily_Rainfall"
    }
    metric=st.selectbox("Climate indicator",list(climate_metrics))
    col=climate_metrics[metric]
    if not empty(f):
        one,two,three=st.columns(3)
        one.metric("Districts selected",str(f["District"].nunique()))
        two.metric("Annual observations",str(len(f)))
        three.metric("Mean selected indicator",f"{f[col].mean():,.1f}")
        fig=px.line(f.sort_values("Year"),x="Year",y=col,color="District",markers=True,
            color_discrete_sequence=PALETTE,title=f"{metric} by district and year",
            labels={col:metric,"Year":"Agricultural year"})
        chart(fig)
    st.subheader("Climate anomaly heatmap")
    # Always compute baselines from the full 8-year dataset, not the year-filtered slice.
    reference=climate.copy()
    reference["Rainfall anomaly (%)"]=100*(reference["Annual_Rainfall"] / reference.groupby("District")["Annual_Rainfall"].transform("mean")-1)
    reference["Minimum temperature anomaly (°C)"]=reference["Mean_Min_Temp"]-reference.groupby("District")["Mean_Min_Temp"].transform("mean")
    reference["Maximum temperature anomaly (°C)"]=reference["Mean_Max_Temp"]-reference.groupby("District")["Mean_Max_Temp"].transform("mean")
    anomaly=st.selectbox("Anomaly type",["Rainfall anomaly (%)","Minimum temperature anomaly (°C)","Maximum temperature anomaly (°C)"])
    if district!="All districts": reference=reference[reference["District"]==district]
    if year!="All years": reference=reference[reference["Year"]==year]
    pivot=reference.pivot(index="District",columns="Year",values=anomaly)
    if not pivot.empty:
        fig=px.imshow(pivot,aspect="auto",text_auto=".1f",color_continuous_scale="RdBu_r",
             color_continuous_midpoint=0, title=f"{anomaly}: difference from district-specific study mean")
        fig.update_layout(xaxis_title="Agricultural year",yaxis_title="District")
        chart(fig)
    st.html('<div class="note">Anomalies use each district’s 2017–18 to 2024–25 average, not a long-term climatological normal. Verify rainfall units against the original source metadata.</div>')

elif page == "Market Arrivals & MASI":
    st.markdown('<div class="eyebrow">Agricultural market insights</div>', unsafe_allow_html=True)
    st.header("📦 Market Arrivals & MASI")
    st.write("MASI is a project-defined **Market Arrival Stability Index**. A higher score means less relative year-to-year variability in the historical reported arrivals.")
    st.latex(r"CV = \frac{\mathrm{sample\ standard\ deviation}}{\mathrm{mean\ arrival}},\qquad MASI = \frac{100}{1+CV}")
    if not masi.empty:
        best=masi.sort_values("MASI",ascending=False)
        m1,m2,m3=st.columns(3)
        m1.metric("Commodities in MASI",len(best))
        m2.metric("Highest historical stability",str(best.iloc[0]["Commodity"]))
        m3.metric("Highest MASI score",f"{best.iloc[0]['MASI']:.2f}")
        fig=px.bar(best,x="Commodity",y="MASI",text="MASI",range_y=[0,100],
            color_discrete_sequence=[GREEN],title="Historical MASI scores (2021–22 to 2024–25)")
        fig.update_traces(texttemplate="%{text:.2f}",textposition="outside")
        chart(fig)
        st.dataframe(best[["Commodity","Observations","Mean_Arrival","Std_Arrival","CV","MASI"]].style.format(
            {"Mean_Arrival":"{:,.1f}","Std_Arrival":"{:,.1f}","CV":"{:.4f}","MASI":"{:.2f}"}),hide_index=True,use_container_width=True)
    else:st.warning("MASI results file is missing.")
    if not market.empty:
        st.subheader("Reported market-arrival trends")
        available=market[market["Year"].isin(YEARS_MASI)].copy()
        commodities=sorted(available["Commodity"].dropna().unique())
        selected=st.multiselect("Commodities",commodities,default=[x for x in ["Wheat","Maize","Soyabean"] if x in commodities])
        subset=available[available["Commodity"].isin(selected)]
        if not empty(subset):
            trend=subset.groupby(["Year","Commodity"],as_index=False)["Total_Reported_Arrival"].sum().sort_values("Year")
            fig=px.line(trend,x="Year",y="Total_Reported_Arrival",color="Commodity",markers=True,
                color_discrete_sequence=PALETTE,title="Reported arrivals by commodity and marketing year",
                labels={"Year":"Marketing year","Total_Reported_Arrival":"Reported arrival quantity"})
            chart(fig)
            st.dataframe(subset[["Commodity","Year","Total_Reported_Arrival","MSP","Kharif_Price","Rabi_Price"]].sort_values(["Commodity","Year"]),hide_index=True,use_container_width=True)
        st.html('<div class="note">MASI covers four years only (2021–22 through 2024–25). Market/APMC identifiers and reporting completeness are unverified. These are descriptive stability scores, not predicted shocks or market-risk probabilities.</div>')
