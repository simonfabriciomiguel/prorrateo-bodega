import pandas as pd
import streamlit as st

st.set_page_config(page_title="Prorrateo de Facturas - Bodega", layout="wide")

st.title("🍷 Asistente de Prorrateo e Imputación a Centros de Costo")
st.markdown("Herramienta interactiva de distribución de costos según reglas de la bodega.")

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
        monto_sin_iva = st.number_input("Monto sin IVA ($)", min_value=0.0, value=100000.0, step=1000.0)

    st.header("2. Árbol de Decisiones")
    tipo_gasto = st.radio("¿Qué tipo de comprobante es?", ["Servicio", "Insumo Bodega"], horizontal=True)

    imputaciones_finales = []

    if tipo_gasto == "Servicio":
        afecta_prod = st.radio("¿Afecta la producción?", ["Sí", "No"], horizontal=True)

        if afecta_prod == "No":
            imputaciones_finales.append(("102", 100.0))
            st.info("Imputación directa a: **102 - INSTITUCIONAL COOPE** (100%)")
        else:
            st.subheader("Selecciona los Centros de Costo involucrados:")
            
            # Filtramos los CC disponibles para Servicios que afectan producción
            cc_opciones_servicios = {
                "1": "1 - ADMINISTRACION",
                "4": "4 - FINANCIACION",
                "5": "5 - IMPUESTOS Y SERVICIOS",
                "101": "101 - GENERAL AMBAS BODEGAS",
                "103": "103 - TALLER",
                "201": "201 - GENERAL CORRALITOS",
                "301": "301 - GENERAL 3 DE MAYO"
            }
            
            # Desplegamos casillas de verificación directas para cada CC
            c1, c2 = st.columns(2)
            cc_seleccionados = []
            
            keys_cc = list(cc_opciones_servicios.keys())
            mitad = (len(keys_cc) + 1) // 2
            
            with c1:
                for k in keys_cc[:mitad]:
                    if st.checkbox(cc_opciones_servicios[k], key=f"chk_{k}"):
                        cc_seleccionados.append(k)
            with c2:
                for k in keys_cc[mitad:]:
                    if st.checkbox(cc_opciones_servicios[k], key=f"chk_{k}"):
                        cc_seleccionados.append(k)

            if len(cc_seleccionados) > 0:
                pct_defecto = round(100.0 / len(cc_seleccionados), 2)
                st.markdown("---")
                st.subheader("Ajuste de Porcentajes por Centro de Costo")
                st.caption("Los porcentajes se dividen equitativamente. Puedes modificarlos manualmente si lo deseas.")

                pct_ingresados = {}
                for cc_code in cc_seleccionados:
                    nombre_cc = CC_DICT[cc_code]
                    # Clave dinámica dependiente de la cantidad de seleccionados para forzar el recálculo equitativo
                    pct_val = st.number_input(
                        f"% para {cc_code} - {nombre_cc}",
                        min_value=0.0,
                        max_value=100.0,
                        value=pct_defecto,
                        step=1.0,
                        key=f"pct_{cc_code}_{len(cc_seleccionados)}"
                    )
                    pct_ingresados[cc_code] = pct_val

                suma_pct = sum(pct_ingresados.values())

                if suma_pct > 100.001:
                    st.error(f"⚠️ La suma de porcentajes excede el 100% (Actual: {suma_pct:.2f}%). Por favor ajusta los valores.")
                else:
                    diferencia = round(100.0 - suma_pct, 2)
                    if diferencia > 0.001:
                        # Asignar resto al CC General adecuado si existe
                        if "101" in cc_seleccionados:
                            cc_ajuste = "101"
                        elif "201" in cc_seleccionados:
                            cc_ajuste = "201"
                        elif "301" in cc_seleccionados:
                            cc_ajuste = "301"
                        else:
                            cc_ajuste = cc_seleccionados[0]

                        pct_ingresados[cc_ajuste] = round(pct_ingresados.get(cc_ajuste, 0.0) + diferencia, 2)
                        st.warning(f"ℹ️ Se ajustó un **{diferencia:.2f}%** sobrante a **{cc_ajuste} - {CC_DICT[cc_ajuste]}** para completar el 100%.")

                    for cc_code, val in pct_ingresados.items():
                        imputaciones_finales.append((cc_code, val))
            else:
                st.warning("⚠️ Selecciona al menos un Centro de Costo.")

    elif tipo_gasto == "Insumo Bodega":
        adiciona_vino = st.radio("¿Adiciona a Vino / Mosto?", ["Sí", "No"], horizontal=True)

        if adiciona_vino == "No":
            destino_insumo = st.radio("Selecciona destino del insumo:", ["Bodega Corralitos", "Bodega 3 de Mayo", "Ambas Bodegas"], horizontal=True)
            if destino_insumo == "Bodega Corralitos":
                imputaciones_finales.append(("201", 100.0))
            elif destino_insumo == "Bodega 3 de Mayo":
                imputaciones_finales.append(("301", 100.0))
            else:
                imputaciones_finales.append(("101", 100.0))
        else:
            bodega_vino = st.radio("Selecciona Bodega de destino:", ["Corralitos", "3 de Mayo"], horizontal=True)
            
            if bodega_vino == "Corralitos":
                opciones_vino = {
                    "202": "202 - BLANCO GENERICO CORRALITOS",
                    "203": "203 - BLANCO VARIETAL CORRALITOS",
                    "204": "204 - TINTO GENERICO CORRALITOS",
                    "205": "205 - TINTO VARIETAL CORRALITOS",
                    "206": "206 - MOSTO CORRALITOS"
                }
            else:
                opciones_vino = {
                    "302": "302 - BLANCO GENERICO 3DE MAYO",
                    "303": "303 - BLANCO VARIETAL 3DE MAYO",
                    "304": "304 - TINTO GENERICO 3DE MAYO",
                    "305": "305 - TINTO VARIETAL 3DE MAYO",
                    "306": "306 - MOSTO 3DE MAYO"
                }

            cc_vino = st.selectbox("Selecciona el producto específico:", list(opciones_vino.keys()), format_func=lambda x: opciones_vino[x])
            imputaciones_finales.append((cc_vino, 100.0))

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
                "Monto Imputado ($)": f"${monto_imputado:,.2f}"
            })

        df_res = pd.DataFrame(data_res)
        st.table(df_res)
        
        st.success(f"✓ Factura **{nro_factura}** procesada correctamente.")
        
        st.download_button(
            label="📥 Descargar Imputación en CSV",
            data=df_res.to_csv(index=False).encode('utf-8'),
            file_name=f"imputacion_{nro_factura}.csv",
            mime="text/csv"
        )
