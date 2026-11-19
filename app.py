import streamlit as st
import pandas as pd
import numpy as np
import cv2
import tempfile
import time
import base64
from datetime import datetime
from PIL import Image
from ultralytics import YOLO

# Configuración de la página
st.set_page_config(
    page_title="SafePlant AI - Monitoreo de EPP",
    layout="wide",
    page_icon="🛡️"
)

# Inicializar Base de Datos Temporal (Session State)
if 'infracciones' not in st.session_state:
    st.session_state.infracciones = []
if 'evidencias' not in st.session_state:
    st.session_state.evidencias = []
if 'ultimo_registro' not in st.session_state:
    st.session_state.ultimo_registro = {}
if 'personas_en_cuadro_actual' not in st.session_state:
    st.session_state.personas_en_cuadro_actual = 0
if 'cumplimiento_actual' not in st.session_state:
    st.session_state.cumplimiento_actual = 100

# Título y Encabezado
st.title("🛡️ SafePlant AI - Sistema CCTV de Seguridad y Salud en el Trabajo")
st.caption("Supervisión inteligente de EPP en tiempo real con YOLOv8 | Ingeniería Industrial (Ciclo 2026-2)")
st.markdown("---")

# Cargar el modelo YOLO
@st.cache_resource
def load_model():
    return YOLO('best.pt')

model = load_model()
clases_infraccion = [2, 3] # 2: 'no helmet', 3: 'no vest'
clase_persona = 4 # 4: 'person'

# BARRA LATERAL (CONTROLES INDUSTRIALES)
st.sidebar.header("🏭 Configuración de Planta")

# Selector de Zona Industrial
zonas_planta = {
    "Zona A: Nave de Fundición y Hornos (EPP Crítico)": {"casco": True, "chaleco": True, "riesgo": "ALTO"},
    "Zona B: Almacén y Tránsito de Montacargas": {"casco": False, "chaleco": True, "riesgo": "MEDIO"},
    "Zona C: Taller de Mecanizado y Línea de Ensamble": {"casco": True, "chaleco": False, "riesgo": "MEDIO"},
    "Zona D: Personalizada": {"casco": True, "chaleco": True, "riesgo": "CONFIGURABLE"}
}

zona_seleccionada = st.sidebar.selectbox("Sector / Área de Supervisión:", list(zonas_planta.keys()))
config_zona = zonas_planta[zona_seleccionada]

st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ EPP Requerido en Sector")

if zona_seleccionada == "Zona D: Personalizada":
    check_casco = st.sidebar.checkbox("Supervisar Casco de Seguridad", value=True)
    check_chaleco = st.sidebar.checkbox("Supervisar Chaleco Reflectante", value=True)
else:
    check_casco = st.sidebar.checkbox("Supervisar Casco de Seguridad", value=config_zona["casco"])
    check_chaleco = st.sidebar.checkbox("Supervisar Chaleco Reflectante", value=config_zona["chaleco"])

st.sidebar.markdown("---")
st.sidebar.subheader("📹 Origen del Flujo de Video")
fuente = st.sidebar.radio("Fuente de Entrada:", ["Cámara Web en Vivo", "Subir Archivo (Foto/Video)"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Calibración del Algoritmo")
conf_threshold = st.sidebar.slider("Confianza mínima de la IA:", min_value=0.15, max_value=0.85, value=0.30, step=0.05,
                                   help="30% equilibra sensibilidad y eliminación de falsas alarmas.")
analysis_res = st.sidebar.select_slider("Resolución de Inferencia:", options=[320, 480, 640], value=480,
                                        help="480p ofrece excelente nitidez para detección de cascos y chalecos.")
frame_skip = st.sidebar.slider("Salto de Cuadros (Frame Skip):", min_value=1, max_value=8, value=3,
                               help="Analiza 1 de cada N cuadros para mantener alta tasa de FPS.")
cooldown_segundos = st.sidebar.slider("Periodo de Gracia Infracciones (segundos):", min_value=2, max_value=10, value=3,
                                      help="Evita registrar la misma falta múltiples veces por segundo.")

# Métricas Superiores Dinámicas (KPIs SST)
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
placeholder_m1 = metric_col1.empty()
placeholder_m2 = metric_col2.empty()
placeholder_m3 = metric_col3.empty()
placeholder_m4 = metric_col4.empty()

# Barra de Cumplimiento SST
placeholder_progreso = st.empty()

def actualizar_metricas(personas_actuales=0, cascos_actuales=0, chalecos_actuales=0, falta_casco=False, falta_chaleco=False):
    total_infracciones = len(st.session_state.infracciones)
    
    # Cálculo del % de Cumplimiento EPP
    epp_exigidos = 0
    if check_casco: epp_exigidos += 1
    if check_chaleco: epp_exigidos += 1
    
    if personas_actuales == 0 or epp_exigidos == 0:
        cumplimiento = 100
        estado_vivo = "⚪ Área Despejada"
    else:
        epp_portados = 0
        if check_casco: epp_portados += min(cascos_actuales, personas_actuales)
        if check_chaleco: epp_portados += min(chalecos_actuales, personas_actuales)
        
        total_posible = personas_actuales * epp_exigidos
        cumplimiento = int((epp_portados / total_posible) * 100)
        
        falta_c = falta_casco if check_casco else False
        falta_v = falta_chaleco if check_chaleco else False
        
        if not falta_c and not falta_v:
            estado_vivo = f"🟢 CONFORME ({cumplimiento}% EPP)"
        elif falta_c and falta_v:
            estado_vivo = "🔴 CRÍTICO (Sin Casco ni Chaleco)"
        elif falta_c:
            estado_vivo = "🔴 ALERTA (Falta Casco)"
        else:
            estado_vivo = "🔴 ALERTA (Falta Chaleco)"

    st.session_state.cumplimiento_actual = cumplimiento

    placeholder_m1.metric("👷 Trabajadores en Cuadro", personas_actuales)
    placeholder_m2.metric("🛡️ Cascos Detectados", cascos_actuales)
    placeholder_m3.metric("🦺 Chalecos Detectados", chalecos_actuales)
    placeholder_m4.metric("🚦 Estado de Seguridad", estado_vivo)
    
    # Barra visual de cumplimiento SST
    placeholder_progreso.progress(
        cumplimiento / 100.0,
        text=f"📊 Índice de Cumplimiento Normativo SST (Ley 29783): {cumplimiento}% | Nivel de Riesgo: {'BAJO' if cumplimiento >= 90 else ('MODERADO' if cumplimiento >= 60 else 'CRÍTICO')}"
    )

actualizar_metricas(st.session_state.personas_en_cuadro_actual)
st.markdown("---")

# Layout Principal: Video (Izquierda) / Módulos de Analítica (Derecha)
col_video, col_datos = st.columns([1.8, 1.2])

def procesar_detecciones(results, frame_raw=None):
    ahora = time.time()
    hora_str = datetime.now().strftime("%H:%M:%S")
    personas_detectadas = 0
    cascos_detectados = 0
    chalecos_detectados = 0
    sin_casco_detectados = 0
    sin_chaleco_detectados = 0
    detecciones_en_cuadro = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            nombre_clase = model.names[cls_id]
            detecciones_en_cuadro.append(f"{nombre_clase} ({conf:.0%})")
            
            if cls_id == clase_persona: # 4: person
                personas_detectadas += 1
            elif cls_id == 1: # 1: helmet
                cascos_detectados += 1
            elif cls_id == 5: # 5: vest
                chalecos_detectados += 1
            elif cls_id == 2: # 2: no helmet
                sin_casco_detectados += 1
            elif cls_id == 3: # 3: no vest
                sin_chaleco_detectados += 1

    falta_casco = False
    falta_chaleco = False

    # Lógica de Seguridad Industrial Deductiva:
    if personas_detectadas > 0:
        # Miniatura para evidencia si hay infracción
        thumb = None
        if frame_raw is not None:
            thumb = cv2.resize(frame_raw, (280, 180))
            thumb = cv2.cvtColor(thumb, cv2.COLOR_BGR2RGB)
            thumb = Image.fromarray(thumb)

        # 1. Verificación de Casco
        if check_casco:
            if sin_casco_detectados > 0 or cascos_detectados == 0:
                falta_casco = True
                ultimo = st.session_state.ultimo_registro.get("NO HELMET", 0)
                if ahora - ultimo >= cooldown_segundos:
                    st.session_state.infracciones.append({
                        "Hora": hora_str,
                        "Sector": zona_seleccionada.split(":")[0],
                        "Falta": "NO HELMET",
                        "Confianza": "92%" if sin_casco_detectados > 0 else "DETECCIÓN CCTV",
                        "Riesgo": "ALTO",
                        "Acción": "Notificar a Supervisor de Planta"
                    })
                    st.session_state.ultimo_registro["NO HELMET"] = ahora
                    if thumb is not None:
                        st.session_state.evidencias.insert(0, {
                            "Hora": hora_str,
                            "Falta": "FALTA DE CASCO",
                            "Sector": zona_seleccionada.split(":")[0],
                            "Img": thumb
                        })
                        if len(st.session_state.evidencias) > 10:
                            st.session_state.evidencias.pop()

        # 2. Verificación de Chaleco
        if check_chaleco:
            if sin_chaleco_detectados > 0 or chalecos_detectados == 0:
                falta_chaleco = True
                ultimo = st.session_state.ultimo_registro.get("NO VEST", 0)
                if ahora - ultimo >= cooldown_segundos:
                    st.session_state.infracciones.append({
                        "Hora": hora_str,
                        "Sector": zona_seleccionada.split(":")[0],
                        "Falta": "NO VEST",
                        "Confianza": "90%" if sin_chaleco_detectados > 0 else "DETECCIÓN CCTV",
                        "Riesgo": "MEDIO",
                        "Acción": "Advertencia por Altavoz / Bitácora"
                    })
                    st.session_state.ultimo_registro["NO VEST"] = ahora
                    if thumb is not None:
                        st.session_state.evidencias.insert(0, {
                            "Hora": hora_str,
                            "Falta": "FALTA DE CHALECO",
                            "Sector": zona_seleccionada.split(":")[0],
                            "Img": thumb
                        })
                        if len(st.session_state.evidencias) > 10:
                            st.session_state.evidencias.pop()

    return personas_detectadas, cascos_detectados, chalecos_detectados, falta_casco, falta_chaleco, detecciones_en_cuadro

with col_video:
    st.subheader(f"📡 Feed de Monitoreo - {zona_seleccionada.split(':')[0]}")
    
    if fuente == "Cámara Web en Vivo":
        run_webcam = st.sidebar.checkbox("Encender Cámara", key="webcam_toggle")
        st_frame = st.empty()
        st_info_det = st.empty()
        
        if run_webcam:
            camera = cv2.VideoCapture(0)
            frame_count = 0
            
            while run_webcam:
                ret, frame = camera.read()
                if not ret:
                    st.error("No se pudo obtener señal de la cámara web.")
                    break
                    
                frame_count += 1
                if frame_count % frame_skip != 0:
                    continue
                
                h, w = frame.shape[:2]
                frame_disp = cv2.resize(frame, (640, int(640 * h / w)))
                
                # Inferencia con YOLOv8
                results = model(frame_disp, imgsz=analysis_res, conf=conf_threshold, iou=0.45, agnostic_nms=True, verbose=False)
                personas, cascos, chalecos, f_c, f_v, dets = procesar_detecciones(results, frame_raw=frame_disp)
                
                # Actualizar métricas periódicamente para mantener altos FPS
                if frame_count % (frame_skip * 2) == 0:
                    st.session_state.personas_en_cuadro_actual = personas
                    actualizar_metricas(personas, cascos, chalecos, f_c, f_v)
                
                res_plotted = results[0].plot()
                res_plotted = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)
                st_frame.image(res_plotted, channels="RGB", use_container_width=True)
                
                if dets:
                    st_info_det.caption(f"🎯 **Detectando ahora:** {' | '.join(dets)}")
                else:
                    st_info_det.caption("🎯 *Sin detecciones sobre el umbral configurado.*")
            
            camera.release()
        else:
            st.info("💡 **Consejo:** Para una inspección óptima, sitúate a 1.5 - 2 metros de la cámara mostrando cabeza y torso (ángulo CCTV).")
            st_frame.image("https://via.placeholder.com/800x450.png?text=Camara+Apagada+-+Activar+en+Barra+Lateral", use_container_width=True)
            
    else:
        uploaded_file = st.sidebar.file_uploader("Subir Archivo de Video o Imagen", type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'])
        
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # --- IMAGEN ---
            if file_extension in ['jpg', 'jpeg', 'png']:
                image = Image.open(uploaded_file)
                img_array = np.array(image)
                
                with st.spinner('Analizando imagen...'):
                    results = model(img_array, imgsz=analysis_res, conf=conf_threshold, iou=0.45, agnostic_nms=True, verbose=False)
                    personas, cascos, chalecos, f_c, f_v, dets = procesar_detecciones(results, frame_raw=img_array)
                    actualizar_metricas(personas, cascos, chalecos, f_c, f_v)
                    
                    res_plotted = results[0].plot()
                    st.image(res_plotted, caption='Análisis Completado', use_container_width=True)
                    if dets:
                        st.caption(f"🎯 **Detectando:** {' | '.join(dets)}")
                                
            # --- VIDEO ---
            elif file_extension in ['mp4', 'avi', 'mov']:
                tfile = tempfile.NamedTemporaryFile(delete=False) 
                tfile.write(uploaded_file.read())
                
                video_cap = cv2.VideoCapture(tfile.name)
                st_frame = st.empty() 
                st_video_dets = st.empty()
                st.sidebar.warning("⚠️ Para detener la reproducción, desmarca el archivo o refresca la página (F5).")
                
                frame_count = 0
                
                while video_cap.isOpened():
                    ret, frame = video_cap.read()
                    if not ret:
                        break
                    
                    frame_count += 1
                    if frame_count % frame_skip != 0:
                        continue
                    
                    h, w = frame.shape[:2]
                    frame_disp = cv2.resize(frame, (640, int(640 * h / w)))
                    
                    results = model(frame_disp, imgsz=analysis_res, conf=conf_threshold, iou=0.45, agnostic_nms=True, verbose=False)
                    personas, cascos, chalecos, f_c, f_v, dets = procesar_detecciones(results, frame_raw=frame_disp)
                    actualizar_metricas(personas, cascos, chalecos, f_c, f_v)
                    
                    res_plotted = results[0].plot()
                    res_plotted = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)
                    st_frame.image(res_plotted, channels="RGB", use_container_width=True)
                    if dets:
                        st_video_dets.caption(f"🎯 **Detectando ahora:** {' | '.join(dets)}")
                                
                video_cap.release()
                st.success("Análisis de video finalizado.")
        else:
            st.image("https://via.placeholder.com/800x450.png?text=Esperando+Archivo+de+Video+o+Foto...", use_container_width=True)

with col_datos:
    st.subheader("📋 Gestión de Seguridad Operativa")
    
    tab_bitacora, tab_evidencias, tab_graficos = st.tabs([
        "📝 Bitácora SST",
        "📸 Evidencias Capturadas",
        "📊 Distribución de Riesgos"
    ])
    
    with tab_bitacora:
        st.metric("⚠️ Total Infracciones Acumuladas", len(st.session_state.infracciones))
        
        if len(st.session_state.infracciones) > 0:
            df = pd.DataFrame(st.session_state.infracciones)
            st.dataframe(df.iloc[::-1], use_container_width=True, height=280)
            
            # Exportar Reporte Industrial Completo
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Exportar Auditoría SST (CSV)",
                data=csv,
                file_name=f'auditoria_sst_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
                use_container_width=True
            )
            
            if st.button("🧹 Reiniciar Auditoría y Bitácora", use_container_width=True):
                st.session_state.infracciones = []
                st.session_state.evidencias = []
                st.session_state.ultimo_registro = {}
                st.session_state.personas_en_cuadro_actual = 0
                st.session_state.cumplimiento_actual = 100
                st.rerun()
        else:
            st.success("✅ No se registran incidentes activos. Planta operando bajo normativa.")

    with tab_evidencias:
        st.write("**Instantáneas de Infracciones Detectadas (Auditoría Visual)**")
        if len(st.session_state.evidencias) > 0:
            for ev in st.session_state.evidencias[:4]:
                st.image(ev["Img"], caption=f"🚨 {ev['Falta']} - {ev['Hora']} ({ev['Sector']})", use_container_width=True)
                st.markdown("---")
        else:
            st.info("Sin registros fotográficos. Al detectarse una infracción, la imagen se archivará automáticamente aquí.")

    with tab_graficos:
        st.write("**Frecuencia de Infracciones por Tipo**")
        if len(st.session_state.infracciones) > 0:
            df = pd.DataFrame(st.session_state.infracciones)
            conteo_faltas = df['Falta'].value_counts()
            st.bar_chart(conteo_faltas)
            
            st.write("**Infracciones por Sector de Planta**")
            conteo_sector = df['Sector'].value_counts()
            st.bar_chart(conteo_sector)
        else:
            st.info("El gráfico de riesgos se generará conforme se acumulen datos de inspección.")

st.markdown("---")
st.caption("Proyecto de Inteligencia Artificial Aplicada (560040) - Universidad de Lima | YOLOv8 + Streamlit")
