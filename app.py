import streamlit as st
import dns.resolver
import pandas as pd
from io import StringIO
import time

st.set_page_config(page_title="Exportador DNS", page_icon="🌐", layout="wide")

st.title("🌐 Exportador de registros DNS y subdominios")
st.write("Sube tu archivo `.txt` con la lista de dominios (uno por línea).")

uploaded_file = st.file_uploader("Selecciona tu archivo TXT", type=["txt"])

COMMON_SUBS = ["www", "mail", "api", "smtp", "ftp", "autodiscover", "webmail", "portal", "app", "dev"]

TIPOS = ["A", "AAAA", "MX", "CNAME", "TXT", "NS", "SRV"]

def obtener_registros(dominio):
    data = []
    for tipo in TIPOS:
        try:
            respuestas = dns.resolver.resolve(dominio, tipo)
            for r in respuestas:
                data.append((dominio, "", tipo, r.to_text()))
        except Exception:
            pass
    for sub in COMMON_SUBS:
        subdominio = f"{sub}.{dominio}"
        for tipo in TIPOS:
            try:
                respuestas = dns.resolver.resolve(subdominio, tipo)
                for r in respuestas:
                    data.append((dominio, sub, tipo, r.to_text()))
            except Exception:
                pass
    return data

if uploaded_file:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    dominios = [d.strip() for d in stringio.readlines() if d.strip()]

    st.write(f"📄 Se cargaron **{len(dominios)} dominios**.")
    start = st.button("🔍 Iniciar consulta DNS")

    if start:
        resultados = []
        progress = st.progress(0)
        status = st.empty()
        total = len(dominios)
        batch = 0

        for i, dominio in enumerate(dominios, start=1):
            status.text(f"Procesando {dominio} ({i}/{total})...")
            registros = obtener_registros(dominio)
            for r in registros:
                resultados.append(r)

            if i % 50 == 0:
                batch += 1
                st.info(f"Lote {batch} procesado ({i}/{total})")

            progress.progress(i / total)
            time.sleep(0.1)

        df = pd.DataFrame(resultados, columns=["Dominio", "Subdominio", "Tipo", "Valor"])

        st.success(f"✅ Consulta completada ({len(df)} registros encontrados).")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Descargar resultados en CSV",
            data=csv,
            file_name="registros_dns.csv",
            mime="text/csv"
        )
