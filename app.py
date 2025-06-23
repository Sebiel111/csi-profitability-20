
import streamlit as st
import pandas as pd

# --- CSS Styling ---
st.markdown("""<style>
  body, html { background-color: #f9f9f9; }
  .block-container { padding: 2rem; }
  h1 { font-size: 2.5rem !important; margin-bottom: 1rem; }
  /* Slider label font-size */
  .stSlider label, .stSlider .css-1ptx2ea { font-size: 22px !important; }
  /* Hide default slider ticks */
  .stSlider .rc-slider-mark-text { visibility: hidden; }
  .input-col { display: flex; flex-direction: column; align-items: center; margin: 0 0.5rem; }
  .input-col label { font-size: 22px !important; font-weight: bold; margin-bottom: 0.5rem; text-align: center; }
  .input-col input { font-size: 22px !important; height: 2.5rem !important; line-height: 2.5rem !important; 
                     text-align: center !important; width: 100% !important; max-width: 160px !important; }
  .stButton button { background-color: #4F46E5; color: white; font-weight: bold;
                     border-radius: 0.5rem; padding: 1rem 2rem; font-size: 22px !important; margin-top: 1rem; }
  table.custom { width:100%; border-collapse: collapse; font-size:22px; margin-top: 1rem; }
  table.custom th { text-align:center; font-weight:bold; border-bottom:1px solid #ccc; padding:10px; }
  table.custom td { text-align:right; padding:10px; border-bottom:1px solid #eee; }
  table.custom td.left { text-align:left; }
  table.custom tr.total-row { font-weight:bold; background-color: #eeeeee; }
</style>""", unsafe_allow_html=True)

# --- Labels and Locales ---
labels = {
    "English": {"code":"en_US","language":"English","title":"CSI Profitability Simulator",
                "csi":"CSI score (out of {max})","sample":"Sample size (Volvo Selekt sales)",
                "ownership":"Ownership duration (years)","vehicle":"Vehicle sale profit",
                "warranty":"Volvo Selekt warranty (years)","service":"Service profit per year per customer",
                "run":"Run simulation","results":"Results","year":"Year",
                "service_cust":"Service customers","repeat":"Repeat purchases","total_profit":"Total profit",
                "total":"Total","download":"Download CSV"},
    "Español": {"code":"es_ES","language":"Español","title":"Simulador de rentabilidad CSI",
                "csi":"Puntuación CSI (de {max})","sample":"Volumen de ventas Volvo Selekt",
                "ownership":"Duración de propiedad (años)","vehicle":"Beneficio por venta de vehículo",
                "warranty":"Garantía Volvo Selekt (años)","service":"Beneficio de servicio por cliente y año",
                "run":"Ejecutar simulación","results":"Resultados","year":"Año",
                "service_cust":"Clientes de servicio","repeat":"Recompras","total_profit":"Beneficio total",
                "total":"Total","download":"Descargar CSV"},
    "Português": {"code":"pt_PT","language":"Português","title":"Simulador de rentabilidade CSI",
                  "csi":"Pontuação CSI (de {max})","sample":"Vendas Volvo Selekt",
                  "ownership":"Duração de propriedade (anos)","vehicle":"Lucro por venda de veículo",
                  "warranty":"Garantia Volvo Selekt (anos)","service":"Lucro de serviço por cliente por ano",
                  "run":"Executar simulação","results":"Resultados","year":"Ano",
                  "service_cust":"Clientes de serviço","repeat":"Recompras","total_profit":"Lucro total",
                  "total":"Total","download":"Baixar CSV"},
    "Français": {"code":"fr_FR","language":"Français","title":"Simulateur de rentabilité CSI",
                 "csi":"Score CSI (sur {max})","sample":"Nombre de ventes Volvo Selekt",
                 "ownership":"Durée de possession (ans)","vehicle":"Profit par vente de véhicule",
                 "warranty":"Garantie Volvo Selekt (ans)","service":"Profit service par client et par an",
                 "run":"Lancer la simulation","results":"Résultats","year":"Année",
                 "service_cust":"Clients service","repeat":"Achats répétés","total_profit":"Profit total",
                 "total":"Total","download":"Télécharger CSV"},
    "Deutsch": {"code":"de_DE","language":"Deutsch","title":"CSI-Ertragsimulator",
                "csi":"CSI-Wert (von {max})","sample":"Volvo Selekt-Verkäufe",
                "ownership":"Besitzdauer (Jahre)","vehicle":"Gewinn pro Fahrzeugverkauf",
                "warranty":"Volvo Selekt-Garantie (Jahre)","service":"Servicegewinn pro Kunde und Jahr",
                "run":"Simulation starten","results":"Ergebnisse","year":"Jahr",
                "service_cust":"Servicekunden","repeat":"Wiederholungskäufe","total_profit":"Gesamtgewinn",
                "total":"Gesamt","download":"CSV herunterladen"},
    "Italiano": {"code":"it_IT","language":"Italiano","title":"Simulatore di redditività CSI",
                 "csi":"Punteggio CSI (su {max})","sample":"Vendite Volvo Selekt",
                 "ownership":"Durata proprietà (anni)","vehicle":"Profitto per vendita veicolo",
                 "warranty":"Garanzia Volvo Selekt (anni)","service":"Profitto assistenza per cliente all'anno",
                 "run":"Esegui simulazione","results":"Risultati","year":"Anno",
                 "service_cust":"Clienti assistenza","repeat":"Riacquisti","total_profit":"Profitto totale",
                 "total":"Totale","download":"Scarica CSV"},
    "Svenska": {"code":"sv_SE","language":"Svenska","title":"CSI Lönsamhetssimulator",
                "csi":"CSI-poäng (av {max})","sample":"Volvo Selekt-försäljning",
                "ownership":"Ägarperiod (år)","vehicle":"Vinst per bilförsäljning",
                "warranty":"Volvo Selekt-garanti (år)","service":"Servicevinst per kund och år",
                "run":"Kör simulering","results":"Resultat","year":"År",
                "service_cust":"Servicekunder","repeat":"Återköp","total_profit":"Total vinst",
                "total":"Totalt","download":"Ladda ner CSV"}
}

# Helpers
def format_number(val, sep):
    s = f"{int(val):,}"
    if sep == ",":
        return s
    return s.replace(",", sep)

def parse_int(s):
    digits = "".join(ch for ch in s if ch.isdigit())
    return int(digits) if digits else 0

# Simulation
def get_pct(score):
    if score>=901: return 0.74,0.35
    if score>=801: return 0.51,0.24
    if score>=701: return 0.32,0.19
    return 0.14,0.16

def simulate(csi, count, s_profit, own, warr, v_profit):
    years=list(range(2026,2041))
    service={y:0 for y in years}; repeat={y:0 for y in years}; total={y:0 for y in years}
    waves=[{"year":2025,"count":count,"rep":False}]
    spct,rpct = get_pct(csi)
    for y in years:
        new=[]
        for w in waves:
            age=y-w["year"]
            if 1<=age<=warr: service[y]+=w["count"]*spct
            if not w["rep"] and age>=own:
                r=w["count"]*rpct; repeat[y]+=r; w["rep"]=True
                new.append({"year":y,"count":r,"rep":False})
        waves.extend(new)
        total[y]=round(service[y])*s_profit+round(repeat[y])*v_profit
    df=pd.DataFrame({
        L["year"]:years,
        L["service_cust"]:[round(service[y]) for y in years],
        L["repeat"]:[round(repeat[y]) for y in years],
        L["total_profit"]:[round(total[y]) for y in years]
    })
    totals={L["year"]:L["total"],L["service_cust"]:df[L["service_cust"]].sum(),
            L["repeat"]:df[L["repeat"]].sum(),L["total_profit"]:df[L["total_profit"]].sum()}
    return pd.concat([pd.DataFrame([totals]),df],ignore_index=True)

# UI
language = st.selectbox("Language", list(labels.keys()), format_func=lambda x: labels[x]["language"])
L = labels[language]
sep = "," if language=="English" else " " if language=="Svenska" else "."

st.title(L["title"])

# Localized CSI label and slider
max_val = 1000
csi_label = L["csi"].format(max=format_number(max_val, sep))
st.markdown(f"**{csi_label}**")
csi = st.slider("", 0, max_val, 870)

# Custom slider endpoints
col_min, col_max = st.columns([1,9,1])[0], st.columns([1,9,1])[2]
col_min.markdown(format_number(0, sep))
col_max.markdown(format_number(max_val, sep))

# Inputs aligned and formatted on_change
cols = st.columns(5)
keys = ["sample","ownership","vehicle","warranty","service"]
labels_input = [L["sample"], L["ownership"], L["vehicle"], L["warranty"], L["service"]]
for col, key, lbl in zip(cols, keys, labels_input):
    with col:
        st.markdown(f'<div class="input-col"><label>{lbl}</label></div>', unsafe_allow_html=True)
        st.text_input("", key=key, on_change=lambda k=key: st.session_state.update({k: format_number(parse_int(st.session_state[k]), sep)}))

# Run simulation button
if st.button(L["run"]):
    count=parse_int(st.session_state.get("sample",""))
    own=parse_int(st.session_state.get("ownership",""))
    vprofit=parse_int(st.session_state.get("vehicle",""))
    warr=parse_int(st.session_state.get("warranty",""))
    sprofit=parse_int(st.session_state.get("service",""))
    df=simulate(csi,count,sprofit,own,warr,vprofit)
    html="<table class='custom'><thead><tr>"
    for col in df.columns: html+=f"<th>{col}</th>"
    html+="</tr></thead><tbody>"
    for _,row in df.iterrows():
        cls=" class='total-row'" if row[0]==L["total"] else ""
        html+=f"<tr{cls}><td class='left'>{row[0]}</td>"
        for val in row.iloc[1:]: html+=f"<td>{format_number(val,sep)}</td>"
        html+="</tr>"
    html+="</tbody></table>"
    st.subheader(L["results"])
    st.markdown(html, unsafe_allow_html=True)
    st.download_button(L["download"], df.to_csv(index=False).encode(), "csi_profitability.csv", "text/csv")
