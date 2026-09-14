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
    monto_sin_iva = st.number_input(
        "Monto sin IVA ($)", min_value=0.0, value=100000.0, step=1000.0
    )

  st.header("2. Árbol de Decisiones")
  tipo_gasto = st.radio(
      "¿Qué tipo de comprobante es?",
      ["Servicio", "Insumo Bodega"],
      horizontal=True,
  )

  imputaciones_finales = []
  cc_opciones = {}
  prefix_key = "serv"

  if tipo_gasto == "Servicio":
    prefix_key = "serv"
    afecta_prod = st.radio(
        "¿Afecta la producción?", ["Sí", "No"], horizontal=True
    )

    if afecta_prod == "No":
      st.subheader("Selecciona los Centros de Costo involucrados:")
      cc_opciones = {
          "102": "102 - INSTITUCIONAL COOPE",
          "103": "103 - TALLER",
          "1": "1 - ADMINISTRACION",
          "4": "4 - FINANCIACION",
          "5": "5 - IMPUESTOS Y SERVICIOS",
      }
    else:
      bodega_servicio = st.radio(
          "Selecciona la Bodega afectada:",
          ["Bodega Corralitos", "Bodega 3 de Mayo", "Ambas Bodegas"],
          horizontal=True,
      )

      cc_comunes = {
          "1": "1 - ADMINISTRACION",
          "4": "4 - FINANCIACION",
          "5": "5 - IMPUESTOS Y SERVICIOS",
          "103": "103 - TALLER",
      }

      cc_corralitos = {
          "201": "201 - GENERAL CORRALITOS",
          "202": "202 - BLANCO GENERICO CORRALITOS",
          "203": "203 - BLANCO VARIETAL CORRALITOS",
          "204": "204 - TINTO GENERICO CORRALITOS",
          "205": "205 - TINTO VARIETAL CORRALITOS",
          "206": "206 - MOSTO CORRALITOS",
      }

      cc_3demayo = {
          "301": "301 - GENERAL 3 DE MAYO",
          "302": "302 - BLANCO GENERICO 3DE MAYO",
          "303": "303 - BLANCO VARIETAL 3DE MAYO",
          "304": "304 - TINTO GENERICO 3DE MAYO",
          "305": "305 - TINTO VARIETAL 3DE MAYO",
          "306": "306 - MOSTO 3DE MAYO",
      }

      if bodega_servicio == "Bodega Corralitos":
        cc_opciones = {**cc_corralitos, **cc_comunes}
      elif bodega_servicio == "Bodega 3 de Mayo":
        cc_opciones = {**cc_3demayo, **cc_comunes}
      else:
        cc_opciones = {
            "101": "101 - GENERAL AMBAS BODEGAS",
            **cc_corralitos,
            **cc_3demayo,
            **cc_comunes,
        }

      st.subheader("Selecciona los Centros de Costo involucrados:")

  elif tipo_gasto == "Insumo Bodega":
    prefix_key = "ins"
    adiciona_vino = st.radio(
        "¿Adiciona a Vino / Mosto?", ["Sí", "No"], horizontal=True
    )

    if adiciona_vino == "No":
      st.subheader("Selecciona los Centros de Costo involucrados:")
      cc_opciones = {
          "101": "101 - GENERAL AMBAS BODEGAS",
          "102": "102 - INSTITUCIONAL COOPE",
          "103": "103 - TALLER",
          "1": "1 - ADMINISTRACION",
          "201": "201 - GENERAL CORRALITOS",
          "301": "301 - GENERAL 3 DE MAYO",
      }
    else:
      bodega_insumo = st.radio(
          "Selecciona Bodega de destino:",
          ["Corralitos", "3 de Mayo"],
          horizontal=True,
      )

      if bodega_insumo == "Corralitos":
        cc_opciones = {
            "202": "202 - BLANCO GENERICO CORRALITOS",
            "203": "203 - BLANCO VARIETAL CORRALITOS",
            "204": "204 - TINTO GENERICO CORRALITOS",
            "205": "205 - TINTO VARIETAL CORRALITOS",
            "206": "206 - MOSTO CORRALITOS",
        }
      else:
        cc_opciones = {
            "302": "302 - BLANCO GENERICO 3DE MAYO",
            "303": "303 - BLANCO VARIETAL 3DE MAYO",
            "304": "304 - TINTO GENERICO 3DE MAYO",
            "305": "305 - TINTO VARIETAL 3DE MAYO",
            "306": "306 - MOSTO 3DE MAYO",
        }

      st.subheader("Selecciona los productos de destino:")

  # Lógica común de despliegue, prorrateo y ajuste
  c1, c2 = st.columns(2)
  cc_seleccionados = []
  keys_cc = list(cc_opciones.keys())
  mitad = (len(keys_cc) + 1) // 2

  with c1:
    for k in keys_cc[:mitad]:
      if st.checkbox(cc_opciones[k], key=f"chk_{prefix_key}_{k}"):
        cc_seleccionados.append(k)
  with c2:
    for k in keys_cc[mitad:]:
      if st.checkbox(cc_opciones[k], key=f"chk_{prefix_key}_{k}"):
        cc_seleccionados.append(k)

  if len(cc_seleccionados) > 0:
    pct_defecto = round(100.0 / len(cc_seleccionados), 2)
    st.markdown("---")
    st.subheader("Ajuste de Porcentajes por Centro de Costo")
    st.caption(
        "Los % se dividen equitativamente. Si modificas los costos específicos,"
        " el sobrante ajusta automáticamente en el CC General."
    )

    generales_prioridad = ["101", "201", "301", "102"]
    cc_general_presente = None
    for g in generales_prioridad:
      if g in cc_seleccionados:
        cc_general_presente = g
        break

    pct_ingresados = {}
    for cc_code in cc_seleccionados:
      nombre_cc = CC_DICT[cc_code]
      pct_val = st.number_input(
          f"% para {cc_code} - {nombre_cc}",
          min_value=0.0,
          max_value=100.0,
          value=pct_defecto,
          step=1.0,
          key=f"pct_{prefix_key}_{cc_code}_{len(cc_seleccionados)}",
      )
      pct_ingresados[cc_code] = pct_val

    suma_otros = sum(
        v for k, v in pct_ingresados.items() if k != cc_general_presente
    )

    if cc_general_presente and len(cc_seleccionados) > 1:
      saldo_general = round(max(0.0, 100.0 - suma_otros), 2)
      pct_ingresados[cc_general_presente] = saldo_general
      st.info(
          f"ℹ️ El CC General **{cc_general_presente} -"
          f" {CC_DICT[cc_general_presente]}** se ajustó automáticamente a"
          f" **{saldo_general:.2f}%** para completar el 100%."
      )

    suma_total = round(sum(pct_ingresados.values()), 2)

    if suma_total > 100.0:
      st.error(
          f"⚠️ La suma de porcentajes excede el 100% (Actual: {suma_total:.2f}%)."
          " Por favor ajusta los valores."
      )
    else:
      for cc_code, val in pct_ingresados.items():
        imputaciones_finales.append((cc_code, val))
  else:
    st.warning("⚠️ Selecciona al menos un Centro de Costo.")

with col_resultado:
  st.header("3. Cuadro de Imputación Resultante")

  if imputaciones_finales:
    data_res = []
    for cc_code, pct in imputaciones_finales:
      monto_imputado = monto_sin_iva * (pct / 100.0)
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
