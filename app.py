
import streamlit as st
import pandas as pd

st.markdown(
    '''
    <style>
        html, body {
            background-color: #f9f9f9;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            font-size: 20px;
        }
        .stButton button {
            background-color: #4F46E5;
            color: white;
            font-weight: bold;
            border-radius: 0.5rem;
            padding: 1rem 2rem;
            font-size: 1.5rem;
        }
        .stNumberInput input[type=number]::-webkit-inner-spin-button, 
        .stNumberInput input[type=number]::-webkit-outer-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }
        .stNumberInput input[type=number] {
            -moz-appearance: textfield;
        }
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
        table.custom td.left {
            text-align: left;
        }
        table.custom tr.total-row {
            font-weight: bold;
            background-color: #eeeeee;
        }
    </style>
    ''', unsafe_allow_html=True
)

st.title("CSI Profitability Simulator")

language = st.selectbox("Language", ["English", "Español", "Français", "Deutsch", "Português", "Italiano", "Svenska"])

def format_number(n, lang):
    if lang in ["English", "Svenska"]:
        return f"{n:,}"
    else:
        return f"{n:,}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_csi_percentages(csi_score):
    if csi_score >= 901:
        return 0.74, 0.35
    elif 801 <= csi_score <= 900:
        return 0.51, 0.24
    elif 701 <= csi_score <= 800:
        return 0.32, 0.19
    else:
        return 0.14, 0.16

def simulate_profitability(csi_score, initial_customers, service_profit_per_year,
                           ownership_years, warranty_years, vehicle_sale_profit,
                           start_year=2026, end_year=2040):
    years = list(range(start_year, end_year + 1))
    service_customers = {year: 0 for year in years}
    repeat_customers = {year: 0 for year in years}
    total_profit = {year: 0 for year in years}

    customer_waves = [{"year": 2025, "count": initial_customers}]
    service_return_pct, repeat_purchase_pct = get_csi_percentages(csi_score)

    for year in years:
        new_waves = []
        for wave in customer_waves:
            age = year - wave["year"]
            if 1 <= age <= warranty_years:
                service = wave["count"] * service_return_pct
                service_customers[year] += service
            if age == ownership_years:
                repeats = wave["count"] * repeat_purchase_pct
                repeat_customers[year] += repeats
                new_waves.append({"year": year, "count": repeats})
        customer_waves.extend(new_waves)
        total_profit[year] = (
            round(service_customers[year]) * service_profit_per_year +
            round(repeat_customers[year]) * vehicle_sale_profit
        )

    df = pd.DataFrame({
        "Year": years,
        "Service customers": [round(service_customers[y]) for y in years],
        "Repeat purchases": [round(repeat_customers[y]) for y in years],
        "Total profit": [round(total_profit[y]) for y in years]
    })

    totals = {
        "Year": "Total",
        "Service customers": int(df["Service customers"].sum()),
        "Repeat purchases": int(df["Repeat purchases"].sum()),
        "Total profit": int(df["Total profit"].sum())
    }
    df = pd.concat([pd.DataFrame([totals]), df], ignore_index=True)
    return df

def render_table_html(df, lang):
    rows = ""
    for _, row in df.iterrows():
        row_class = ' class="total-row"' if row["Year"] == "Total" else ""
        rows += f'<tr{row_class}>'
        rows += f'<td class="left">{row["Year"]}</td>'
        rows += f'<td>{format_number(row["Service customers"], lang)}</td>'
        rows += f'<td>{format_number(row["Repeat purchases"], lang)}</td>'
        rows += f'<td>{format_number(row["Total profit"], lang)}</td>'
        rows += '</tr>'
    return f'''
    <table class="custom">
        <thead>
            <tr><th>Year</th><th>Service customers</th><th>Repeat purchases</th><th>Total profit</th></tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    '''

with st.form("form"):
    csi_score = st.slider("CSI score (out of 1,000)", 0, 1000, 870)
    col1, col2 = st.columns(2)
    with col1:
        initial_customers = st.number_input("Sample size (Volvo Selekt sales)", min_value=1, value=100)
        ownership_duration = st.number_input("Ownership duration (years)", min_value=1, value=2)
        vehicle_profit = st.number_input("Vehicle sale profit", min_value=0, value=1225)
    with col2:
        service_profit = st.number_input("Service profit per year per customer", min_value=0, value=350)
        warranty_duration = st.number_input("Volvo Selekt warranty (years)", min_value=1, value=3)
    submitted = st.form_submit_button("Run simulation")

if submitted:
    df = simulate_profitability(
        csi_score,
        initial_customers,
        service_profit,
        ownership_duration,
        warranty_duration,
        vehicle_profit
    )
    st.subheader("Results")
    st.markdown(render_table_html(df, language), unsafe_allow_html=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "csi_profitability_results.csv", "text/csv")
