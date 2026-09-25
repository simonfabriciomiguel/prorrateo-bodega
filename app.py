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
    nro_factura = st.text_input("N° Referencia / Proveedor / Empleado", "F-0001-00001234")
  with col_f2:
    monto_ingresado = st.number_input(
        "Monto Total ($)", min_value=0.0, value=121000.0, step=1000.0
    )

  st.subheader("Descuento de IVA (Opcional):")
  c_iva1, c_iva2 = st.columns(2)
  with c_iva1:
    iva_21 = st.checkbox("IVA 21%", value=False, key="chk_iva_21")
  with c_iva2:
    iva_105 = st.checkbox("IVA 10.5%", value=False, key="chk_iva_105")

  # Cálculo del monto Neto sin IVA
  monto_sin_iva = monto_ingresado
  tasa_aplicada = 0.0

  if iva_21 and not iva_105:
    monto_sin_iva = round(monto_ingresado / 1.21, 2)
    tasa_aplicada = 21.0
  elif iva_105 and not iva_21:
    monto_sin_iva = round(monto_ingresado / 1.105, 2)
    tasa_aplicada = 10.5
  elif iva_21 and iva_105:
    st.warning("⚠️ Selecciona solo un tipo de IVA. Se mantendrá el monto total.")

  if tasa_aplicada > 0:
    st.info(
        f"💡 **Monto Neto sin IVA ({tasa_aplicada}%):**"
        f" **${monto_sin_iva:,.2f}**"
    )

  st.header("2. Clasificación y Árbol de Decisiones")
  tipo_gasto = st.radio(
      "¿Qué tipo de comprobante es?",
      [
          "Servicio", 
          "Herramienta / Maquinaria", 
          "Insumo Bodega", 
          "Energía Eléctrica", 
          "Personal / Mano de Obra"
      ],
      horizontal=True,
  )

  imputaciones_finales = []

  # ==========================================
  # RAMA 1: SERVICIO / HERRAMIENTA / INSUMO
  # ==========================================
  if tipo_gasto in ["Servicio", "Herramienta / Maquinaria", "Insumo Bodega"]:
    cc_opciones = {}
    prefix_key = "std"

    if tipo_gasto in ["Servicio", "Herramienta / Maquinaria"]:
      afecta_prod = st.radio("¿Afecta la producción?", ["Sí", "No"], horizontal=True)

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
        bodega_servicio = st.radio("Selecciona la Bodega afectada:", ["Bodega Corralitos", "Bodega 3 de Mayo", "Ambas Bodegas"], horizontal=True)
        cc_comunes = {"1": "1 - ADMINISTRACION", "4": "4 - FINANCIACION", "5": "5 - IMPUESTOS Y SERVICIOS", "103": "103 - TALLER"}
        cc_corralitos = {"201": "201 - GENERAL CORRALITOS", "202": "202 - BLANCO GENERICO CORRALITOS", "203": "203 - BLANCO VARIETAL CORRALITOS", "204": "204 - TINTO GENERICO CORRALITOS", "205": "205 - TINTO VARIETAL CORRALITOS", "206": "206 - MOSTO CORRALITOS"}
        cc_3demayo = {"301": "301 - GENERAL 3 DE MAYO", "302": "302 - BLANCO GENERICO 3DE MAYO", "303": "303 - BLANCO VARIETAL 3DE MAYO", "304": "304 - TINTO GENERICO 3DE MAYO", "305": "305 - TINTO VARIETAL 3DE MAYO", "306": "306 - MOSTO 3DE MAYO"}

        if bodega_servicio == "Bodega Corralitos":
          cc_opciones = {**cc_corralitos, **cc_comunes}
        elif bodega_servicio == "Bodega 3 de Mayo":
          cc_opciones = {**cc_3demayo, **cc_comunes}
        else:
          cc_opciones = {"101": "101 - GENERAL AMBAS BODEGAS", **cc_corralitos, **cc_3demayo, **cc_comunes}
        st.subheader("Selecciona los Centros de Costo involucrados:")

    elif tipo_gasto == "Insumo Bodega":
      adiciona_vino = st.radio("¿Adiciona a Vino / Mosto?", ["Sí", "No"], horizontal=True)

      if adiciona_vino == "No":
        st.subheader("Selecciona centro de costo de destino:")
        cc_opciones = {"101": "101 - GENERAL AMBAS BODEGAS", "102": "102 - INSTITUCIONAL COOPE", "103": "103 - TALLER", "1": "1 - ADMINISTRACION", "201": "201 - GENERAL CORRALITOS", "301": "301 - GENERAL 3 DE MAYO"}
      else:
        bodega_insumo = st.radio("Selecciona Bodega de destino:", ["Corralitos", "3 de Mayo"], horizontal=True)
        if bodega_insumo == "Corralitos":
          cc_opciones = {"201": "201 - GENERAL CORRALITOS", "202": "202 - BLANCO GENERICO CORRALITOS", "203": "203 - BLANCO VARIETAL CORRALITOS", "204": "204 - TINTO GENERICO CORRALITOS", "205": "205 - TINTO VARIETAL CORRALITOS", "206": "206 - MOSTO CORRALITOS"}
        else:
          cc_opciones = {"301": "301 - GENERAL 3 DE MAYO", "302": "302 - BLANCO GENERICO 3DE MAYO", "303": "303 - BLANCO VARIETAL 3DE MAYO", "304": "304 - TINTO GENERICO 3DE MAYO", "305": "305 - TINTO VARIETAL 3DE MAYO", "306": "306 - MOSTO 3DE MAYO"}
        st.subheader("Selecciona centro de costo de destino:")

    # Despliegue de casilleros
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
      
      generales_prioridad = ["101", "201", "301", "102"]
      cc_general_presente = next((g for g in generales_prioridad if g in cc_seleccionados), None)

      pct_ingresados = {}
      for cc_code in cc_seleccionados:
        pct_val = st.number_input(f"% para {cc_code} - {CC_DICT[cc_code]}", min_value=0.0, max_value=100.0, value=pct_defecto, step=1.0, key=f"pct_{prefix_key}_{cc_code}")
        pct_ingresados[cc_code] = pct_val

      suma_otros = sum(v for k, v in pct_ingresados.items() if k != cc_general_presente)

      if cc_general_presente and len(cc_seleccionados) > 1:
        saldo_general = round(max(0.0, 100.0 - suma_otros), 2)
        pct_ingresados[cc_general_presente] = saldo_general
        st.info(f"ℹ️ El saldo restante ({saldo_general:.2f}%) ajustó automáticamente en **{cc_general_presente} - {CC_DICT[cc_general_presente]}**.")

      suma_total = round(sum(pct_ingresados.values()), 2)
      if suma_total > 100.0:
        st.error(f"⚠️ La suma excede el 100% (Actual: {suma_total:.2f}%).")
      else:
        for cc_code, val in pct_ingresados.items():
          imputaciones_finales.append((cc_code, val))
    else:
      st.warning("⚠️ Selecciona al menos un Centro de Costo.")

  # ==========================================
  # RAMA 2: ENERGÍA ELÉCTRICA
  # ==========================================
  elif tipo_gasto == "Energía Eléctrica":
    st.subheader("Prorrateo de Energía Eléctrica (Fijo + Variable)")
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_seleccionado = st.selectbox("Mes de facturación:", meses)

    es_invierno = mes_seleccionado in ["Mayo", "Junio", "Julio", "Agosto"]
    if es_invierno:
      st.info("❄️ **Factor Estacional (Invierno):** Se sugiere asignar un porcentaje mayor (ej. 30%) a Gastos Generales por mayor uso de iluminación y calefacción.")
      def_fijo = 30.0
    else:
      st.success("☀️ **Factor Estacional (Resto del año):** Se sugiere el porcentaje estándar de Gastos Generales (ej. 15%).")
      def_fijo = 15.0

    col_e1, col_e2 = st.columns(2)
    with col_e1:
      pct_fijo = st.number_input("% Fijo Estructural", value=def_fijo, min_value=0.0, max_value=100.0, step=1.0)
    with col_e2:
      cc_fijo_opcion = st.selectbox("Imputar Cargo Fijo a:", ["101 - GENERAL AMBAS BODEGAS", "1 - ADMINISTRACION", "201 - GENERAL CORRALITOS", "301 - GENERAL 3 DE MAYO"])
      cc_fijo = cc_fijo_opcion.split(" - ")[0]

    imputaciones_finales.append((cc_fijo, pct_fijo))
    saldo_variable = round(100.0 - pct_fijo, 2)
    st.markdown(f"**Saldo Variable a distribuir en procesos:** {saldo_variable}%")

    if saldo_variable > 0:
      st.subheader("Selecciona las bodegas operativas que consumieron energía:")
      c1, c2 = st.columns(2)
      b_corr = c1.checkbox("Bodega Corralitos (201)", value=True)
      b_3dm = c2.checkbox("Bodega 3 de Mayo (301)")

      cc_energia = []
      if b_corr: cc_energia.append("201")
      if b_3dm: cc_energia.append("301")

      if cc_energia:
        pct_var_defecto = round(saldo_variable / len(cc_energia), 2)
        pct_ingresados_e = {}
        for cc in cc_energia:
          val = st.number_input(f"% para {cc} - {CC_DICT[cc]}", min_value=0.0, max_value=saldo_variable, value=pct_var_defecto, step=1.0)
          pct_ingresados_e[cc] = val

        suma_var = sum(pct_ingresados_e.values())
        if suma_var > saldo_variable:
          st.error(f"⚠️ La suma de las bodegas supera el saldo variable de {saldo_variable}%.")
        else:
          dif_e = round(saldo_variable - suma_var, 2)
          if dif_e > 0.001:
             st.warning(f"ℹ️ El remanente de energía ({dif_e:.2f}%) ajustó automáticamente en **{cc_energia[0]}**.")
             pct_ingresados_e[cc_energia[0]] += dif_e

          for k, v in pct_ingresados_e.items():
            # Si el CC fijo es igual a una de las bodegas, sumamos los porcentajes
            imputaciones_finales.append((k, v))
      else:
        st.warning("⚠️ Selecciona al menos una bodega para distribuir el consumo.")

  # ==========================================
  # RAMA 3: PERSONAL / MANO DE OBRA
  # ==========================================
  elif tipo_gasto == "Personal / Mano de Obra":
    st.subheader("Prorrateo de Mano de Obra por Tareas")
    total_horas = st.number_input("Total de horas trabajadas en el periodo:", min_value=1.0, value=160.0, step=1.0)

    st.markdown("Selecciona las áreas donde el personal prestó servicio:")
    c1, c2 = st.columns(2)
    with c1:
      chk_admin = st.checkbox("Administración (1)")
      chk_taller = st.checkbox("Mantenimiento / Taller (103)", value=True)
      chk_corr = st.checkbox("Bodega Corralitos (201)", value=True)
    with c2:
      chk_3dm = st.checkbox("Bodega 3 de Mayo (301)")
      chk_ambas = st.checkbox("General Ambas Bodegas (101)")

    cc_horas = []
    if chk_admin: cc_horas.append("1")
    if chk_taller: cc_horas.append("103")
    if chk_corr: cc_horas.append("201")
    if chk_3dm: cc_horas.append("301")
    if chk_ambas: cc_horas.append("101")

    if cc_horas:
      horas_defecto = float(total_horas) / len(cc_horas)
      st.markdown("---")
      st.markdown("**Distribuye las horas dedicadas a cada área:**")

      horas_ingresadas = {}
      for cc in cc_horas:
        val_h = st.number_input(f"Horas en {cc} - {CC_DICT[cc]}", min_value=0.0, max_value=float(total_horas), value=horas_defecto, step=0.5)
        horas_ingresadas[cc] = val_h

      suma_h = sum(horas_ingresadas.values())
      if suma_h > total_horas:
        st.error(f"⚠️ La suma de horas ({suma_h}) supera el total ingresado ({total_horas}).")
      else:
        dif_h = total_horas - suma_h
        if dif_h > 0.001:
          st.warning(f"ℹ️ Quedan {dif_h:.1f} horas sin asignar. Se sumarán a **{cc_horas[0]}** para cuadrar el 100%.")
          horas_ingresadas[cc_horas[0]] += dif_h

        # Calculamos el % que representa cada bloque de horas y lo agregamos a las imputaciones
        for k, v in horas_ingresadas.items():
          pct_calculado = (v / total_horas) * 100.0
          imputaciones_finales.append((k, pct_calculado))
    else:
      st.warning("⚠️ Selecciona al menos un área o tarea.")

with col_resultado:
  st.header("3. Cuadro de Imputación Resultante")

  if imputaciones_finales:
    # Agrupamos por CC en caso de que (por ej en Energía) el CC fijo y el variable sean el mismo
    df_temp = pd.DataFrame(imputaciones_finales, columns=["Código CC", "Porcentaje"])
    df_agrupado = df_temp.groupby("Código CC", as_index=False)["Porcentaje"].sum()

    data_res = []
    for _, row in df_agrupado.iterrows():
      cc_code = row["Código CC"]
      pct = row["Porcentaje"]
      monto_imputado = round(monto_sin_iva * (pct / 100.0), 2)
      nombre_cc = CC_DICT.get(cc_code, "DESCONOCIDO")
      
      data_res.append({
          "Código CC": cc_code,
          "Centro de Costo": nombre_cc,
          "% Asignado": f"{pct:.2f}%",
          "Monto Imputado ($)": f"${monto_imputado:,.2f}",
      })

    df_res = pd.DataFrame(data_res)
    st.table(df_res)

    st.success(f"✓ Operación **{nro_factura}** procesada correctamente.")

    st.download_button(
        label="📥 Descargar Imputación en CSV",
        data=df_res.to_csv(index=False).encode("utf-8"),
        file_name=f"imputacion_{nro_factura.replace(' ', '_')}.csv",
        mime="text/csv",
    )
