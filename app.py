import pandas as pd
import streamlit as st

st.set_page_config(page_title="Prorrateo de Facturas - Bodega", layout="wide")

st.title("🍷 Asistente de Prorrateo e Imputación a Centros de Costo")
st.markdown(
    "Herramienta interactiva de distribución de costos según reglas de la"
    " bodega."
)

# Diccionario Maestro de Centros de Costo
CC_DICT = {
    "1": "ADMINISTRACION",
    "4": "FINANCIACION",
    "5": "IMPUESTOS Y SERVICIOS",
    "101": "GENERAL AMBAS BODEGAS",
    "102": "INSTITUCIONAL COOPE",
    "103": "TALLER",
    "201": "GENERAL CORRALITOS",
    "202": "BLANCO GENERICO CORRALITOS",
    "203": "BLANCO VARIETAL CORRALITOS",
    "204": "TINTO GENERICO CORRALITOS",
    "205": "TINTO VARIETAL CORRALITOS",
    "206": "MOSTO CORRALITOS",
    "301": "GENERAL 3 DE MAYO",
    "302": "BLANCO GENERICO 3DE MAYO",
    "303": "BLANCO VARIETAL 3DE MAYO",
    "304": "TINTO GENERICO 3DE MAYO",
    "305": "TINTO VARIETAL 3DE MAYO",
    "306": "MOSTO 3DE MAYO",
}

col_ingreso, col_resultado = st.columns([1.3, 1])

with col_ingreso:
  st.header("1. Datos del Comprobante")
  col_f1, col_f2 = st.columns(2)
  with col_f1:
    nro_factura = st.text_input("N° Factura / Proveedor", "F-0001-00001234")
  with col_f2:
    monto_total = st.number_input(
        "Monto Total de Factura ($)", min_value=0.0, value=100000.0, step=1000.0
    )

  st.header("2. Árbol de Decisiones")
  tipo_gasto = st.radio(
      "¿Qué tipo de comprobante es?",
      ["Servicio", "Insumo Bodega"],
      horizontal=True,
  )

  imputaciones_finales = []

  if tipo_gasto == "Servicio":
    afecta_prod = st.radio(
        "¿Afecta la producción?", ["Sí", "No"], horizontal=True
    )

    if afecta_prod == "No":
      imputaciones_finales.append(("102", 100.0))
      st.info("Imputación directa a: **102 - INSTITUCIONAL COOPE** (100%)")
    else:
      st.subheader("Selecciona las áreas y/o bodegas involucradas:")

      c1, c2 = st.columns(2)
      with c1:
        b_corralitos = st.checkbox("Bodega Corralitos (201)")
        b_3dm = st.checkbox("Bodega 3 de Mayo (301)")
        b_ambas = st.checkbox("General Ambas Bodegas (101)")
      with c2:
        b_taller = st.checkbox("Taller (103)")
        b_admin = st.checkbox("Administración (1)")
        b_fin = st.checkbox("Financiación (4)")
        b_imp = st.checkbox("Impuestos y Servicios (5)")

      cc_seleccionados = []
      if b_corralitos:
        cc_seleccionados.append("201")
      if b_3dm:
        cc_seleccionados.append("301")
      if b_ambas:
        cc_seleccionados.append("101")
      if b_taller:
        cc_seleccionados.append("103")
      if b_admin:
        cc_seleccionados.append("1")
      if b_fin:
        cc_seleccionados.append("4")
      if b_imp:
        cc_seleccionados.append("5")

      if len(cc_seleccionados) > 0:
        pct_defecto = round(100.0 / len(cc_seleccionados), 2)
        st.markdown("---")
        st.subheader("Ajuste de Porcentajes por Centro de Costo")
        st.caption(
            "Puedes modificar los % manualmente. Si la suma no llega a 100%,"
            " el sobrante se asignará automáticamente al CC General."
        )

        pct_ingresados = {}
        for cc_code in cc_seleccionados:
          nombre_cc = CC_DICT[cc_code]
          pct_val = st.number_input(
              f"% para {cc_code} - {nombre_cc}",
              min_value=0.0,
              max_value=100.0,
              value=pct_defecto,
              step=1.0,
              key=f"pct_{cc_code}",
          )
          pct_ingresados[cc_code] = pct_val

        suma_pct = sum(pct_ingresados.values())

        if suma_pct > 100.0:
          st.error(
              f"⚠️ La suma de porcentajes excede el 100% (Actual: {suma_pct:.2f}%)."
              " Por favor ajusta los valores."
          )
        else:
          diferencia = 100.0 - suma_pct
          if diferencia > 0.001:
            if "101" in cc_seleccionados:
              cc_ajuste = "101"
            elif "201" in cc_seleccionados:
              cc_ajuste = "201"
            elif "301" in cc_seleccionados:
              cc_ajuste = "301"
            else:
              cc_ajuste = cc_seleccionados[0]

            pct_ingresados[cc_ajuste] = (
                pct_ingresados.get(cc_ajuste, 0.0) + diferencia
            )
            st.warning(
                f"ℹ️ La suma fue {suma_pct:.2f}%. Se asignaron **{diferencia:.2f}%**"
                f" sobrantes a **{cc_ajuste} - {CC_DICT[cc_ajuste]}**."
            )

          for cc_code, val in pct_ingresados.items():
            imputaciones_finales.append((cc_code, val))
      else:
        st.warning("⚠️ Selecciona al menos un área o bodega.")

  elif tipo_gasto == "Insumo Bodega":
    adiciona_vino = st.radio(
        "¿Adiciona a Vino / Mosto?", ["Sí", "No"], horizontal=True
    )

    if adiciona_vino == "No":
      destino_insumo = st.radio(
          "Selecciona destino del insumo:",
          ["Bodega Corralitos", "Bodega 3 de Mayo", "Ambas Bodegas"],
          horizontal=True,
      )
      if destino_insumo == "Bodega Corralitos":
        imputaciones_finales.append(("201", 100.0))
      elif destino_insumo == "Bodega 3 de Mayo":
        imputaciones_finales.append(("301", 100.0))
      else:
        imputaciones_finales.append(("101", 100.0))
    else:
      bodega_vino = st.radio(
          "Selecciona Bodega de destino:",
          ["Corralitos", "3 de Mayo"],
          horizontal=True,
      )

      if bodega_vino == "Corralitos":
        opciones_vino = {
            "202": "202 - BLANCO GENERICO CORRALITOS",
            "203": "203 - BLANCO VARIETAL CORRALITOS",
            "204": "204 - TINTO GENERICO CORRALITOS",
            "205": "205 - TINTO VARIETAL CORRALITOS",
            "206": "206 - MOSTO CORRALITOS",
        }
      else:
        opciones_vino = {
            "302": "302 - BLANCO GENERICO 3DE MAYO",
            "303": "303 - BLANCO VARIETAL 3DE MAYO",
            "304": "304 - TINTO GENERICO 3DE MAYO",
            "305": "305 - TINTO VARIETAL 3DE MAYO",
            "306": "306 - MOSTO 3DE MAYO",
        }

      cc_vino = st.selectbox(
          "Selecciona el producto específico:",
          list(opciones_vino.keys()),
          format_func=lambda x: opciones_vino[x],
      )
      imputaciones_finales.append((cc_vino, 100.0))

with col_resultado:
  st.header("3. Cuadro de Imputación Resultante")

  if imputaciones_finales:
    data_res = []
    for cc_code, pct in imputaciones_finales:
      monto_imputado = monto_total * (pct / 100.0)
      nombre_cc = CC_DICT.get(cc_code, "DESCONOCIDO")
      data_res.append({
          "Código CC": cc_code,
          "Centro de Costo": nombre_cc,
          "% Asignado": f"{pct:.2f}%",
          "Monto Imputado ($)": f"${monto_imputado:,.2f}",
      })

    df_res = pd.DataFrame(data_res)
    st.table(df_res)

    st.success(f"✓ Factura **{nro_factura}** procesada correctamente.")

    st.download_button(
        label="📥 Descargar Imputación en CSV",
        data=df_res.to_csv(index=False).encode("utf-8"),
        file_name=f"imputacion_{nro_factura}.csv",
        mime="text/csv",
    )
