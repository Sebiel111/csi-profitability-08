
import streamlit as st
import pandas as pd

# CSS for styling inputs and table
st.markdown(
    '''
    <style>
        body, html { background-color: #f9f9f9; }
        .block-container { padding: 2rem; font-size: 20px; }
        h1 { color: #1c1c1e; }
        .stButton button {
            background-color: #4F46E5;
            color: white;
            font-weight: bold;
            border-radius: 0.5rem;
            padding: 1rem 2rem;
            font-size: 1.5rem;
        }
        label, .stSlider, .stTextInput label, .stTextInput input {
            font-size: 1.5rem !important;
        }
        .stTextInput input {
            text-align: right;
        }
        .stSlider { padding: 1rem 0; }
        table.custom {
            width: 100%;
            border-collapse: collapse;
            font-size: 22px;
        }
        table.custom th {
            text-align: center;
            font-weight: bold;
            border-bottom: 1px solid #ccc;
            padding: 10px;
        }
        table.custom td {
            text-align: right;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        table.custom td.left { text-align: left; }
        table.custom tr.total-row {
            font-weight: bold;
            background-color: #eeeeee;
        }
    </style>
    ''',
    unsafe_allow_html=True
)

# Translation dictionary for English and Swedish
labels = {
    "English": {
        "language": "Language",
        "title": "CSI Profitability Simulator",
        "csi_score": "CSI score (out of 1,000)",
        "sample_size": "Sample size (Volvo Selekt sales)",
        "ownership_duration": "Ownership duration (years)",
        "warranty_duration": "Volvo Selekt warranty (years)",
        "vehicle_profit": "Vehicle sale profit",
        "service_profit": "Service profit per year per customer",
        "run": "Run simulation",
        "results": "Results",
        "year": "Year",
        "service_customers": "Service customers",
        "repeat_purchases": "Repeat purchases",
        "total_profit": "Total profit",
        "total": "Total",
        "download": "Download CSV"
    },
    "Svenska": {
        "language": "Språk",
        "title": "CSI Lönsamhetssimulator",
        "csi_score": "CSI-poäng (av 1 000)",
        "sample_size": "Volvo Selekt-försäljning",
        "ownership_duration": "Ägarperiod (år)",
        "warranty_duration": "Volvo Selekt-garanti (år)",
        "vehicle_profit": "Vinst per bilförsäljning",
        "service_profit": "Servicevinst per kund och år",
        "run": "Kör simulering",
        "results": "Resultat",
        "year": "År",
        "service_customers": "Servicekunder",
        "repeat_purchases": "Återköp",
        "total_profit": "Total vinst",
        "total": "Totalt",
        "download": "Ladda ner CSV"
    }
}

# Language selector
language = st.selectbox(labels["English"]["language"], list(labels.keys()))
L = labels[language]

st.title(L["title"])

# Number formatting and parsing
def format_number(n):
    return f"{n:,}" if language == "English" else f"{n:,}".replace(","," ")

def parse_number(s):
    # Remove spaces and non-breaking spaces
    return int(str(s).replace(" ","").replace(" ","").replace(",","").replace(".",""))

def get_csi_percentages(score):
    if score >= 901: return 0.74, 0.35
    if score >= 801: return 0.51, 0.24
    if score >= 701: return 0.32, 0.19
    return 0.14, 0.16

def simulate(csi, count, s_profit, own_years, warranty, v_profit):
    years = list(range(2026, 2041))
    service = {y:0 for y in years}
    repeat = {y:0 for y in years}
    total = {y:0 for y in years}
    waves = [{"year":2025, "count":count}]
    s_pct, r_pct = get_csi_percentages(csi)
    for y in years:
        new = []
        for w in waves:
            age = y - w["year"]
            if 1 <= age <= warranty:
                service[y] += w["count"] * s_pct
            if age == own_years:
                r = w["count"] * r_pct
                repeat[y] += r
                new.append({"year": y, "count": r})
        waves.extend(new)
        total[y] = round(service[y])*s_profit + round(repeat[y])*v_profit
    df = pd.DataFrame({
        L["year"]: years,
        L["service_customers"]: [round(service[y]) for y in years],
        L["repeat_purchases"]: [round(repeat[y]) for y in years],
        L["total_profit"]: [round(total[y]) for y in years]
    })
    tot = {
        L["year"]: L["total"],
        L["service_customers"]: int(df[L["service_customers"]].sum()),
        L["repeat_purchases"]: int(df[L["repeat_purchases"]].sum()),
        L["total_profit"]: int(df[L["total_profit"]].sum())
    }
    return pd.concat([pd.DataFrame([tot]), df], ignore_index=True)

def render_table(df):
    html = f"<table class='custom'><thead><tr>"
    for col in df.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        cls = " class='total-row'" if row[df.columns[0]]==L["total"] else ""
        html += f"<tr{cls}>"
        html += f"<td class='left'>{row[df.columns[0]]}</td>"
        for val in row[1:]:
            html += f"<td>{format_number(val)}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html

# Inputs as text_input for full control
with st.form("form"):
    csi_score = st.text_input(L["csi_score"], format_number(870))
    sample = st.text_input(L["sample_size"], format_number(100))
    own = st.text_input(L["ownership_duration"], format_number(2))
    vp = st.text_input(L["vehicle_profit"], format_number(1225))
    sp = st.text_input(L["service_profit"], format_number(350))
    warranty = st.text_input(L["warranty_duration"], format_number(3))
    go = st.form_submit_button(L["run"])

if go:
    # parse inputs
    csi = int(csi_score)
    count = parse_number(sample)
    own_years = parse_number(own)
    vprofit = parse_number(vp)
    sprofit = parse_number(sp)
    warranty_years = parse_number(warranty)
    # simulate and render
    df = simulate(csi, count, sprofit, own_years, warranty_years, vprofit)
    st.subheader(L["results"])
    st.markdown(render_table(df), unsafe_allow_html=True)
    st.download_button(L["download"], df.to_csv(index=False).encode('utf-8'), "csi_profitability.csv", "text/csv")
