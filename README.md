# 🛡️ SafePlant AI - Sistema CCTV de Monitoreo de EPP con IA

> **Proyecto Final - Inteligencia Artificial Aplicada (560040)**  
> **Facultad de Ingeniería | Carrera de Ingeniería Industrial**  
> **Universidad de Lima (Ciclo 2026-2)**  
> **Docente:** Winston Lewis Fuentes  

---

## 📌 1. Descripción del Proyecto
**SafePlant AI** es una solución de Visión Artificial industrial diseñada bajo el marco de la **Ley 29783 (Seguridad y Salud en el Trabajo)** y alineada al **ODS 8 (Meta 8.8: Entornos laborales seguros)**. 

El sistema procesa flujos de video en tiempo real provenientes de cámaras CCTV, detecta la presencia o ausencia de Equipos de Protección Personal (Casco y Chaleco reflectante), calcula el **Índice de Cumplimiento Normativo SST**, archiva instantáneas fotográficas de las infracciones y genera auditorías exportables en formato CSV.

---

## 📄 2. Hojas Técnicas (Data Sheets)

### 2.1 Ficha Técnica del Modelo (YOLOv8n-EPP)
* **Arquitectura:** Red Neuronal Convolucional profunda de una sola etapa (*One-Stage Detector*).
* **Parámetros entrenables:** 3,012,018 (~3.01 Millones).
* **Tamaño del modelo binario:** 6.24 MB (`best.pt`).
* **Resolución de entrada:** 640×640 px (Entrenamiento) / 480×480 px (Inferencia en vivo).
* **Clases detectadas (6):** `boots` (0), `helmet` (1), `no helmet` (2), `no vest` (3), `person` (4), `vest` (5).
* **Algoritmo de supresión:** Non-Maximum Suppression (NMS) agnóstica con $IoU = 0.45$.
* **Velocidad de inferencia:** ~150 - 210 ms en CPU estándar / < 15 ms en GPU NVIDIA.

### 2.2 Ficha Técnica del Software & Dashboard
* **Framework Web:** Streamlit con renderizado reactivo y tema industrial.
* **Procesamiento de Video:** OpenCV (`cv2`) con reescalado dinámico y *frame skip* de 3 cuadros para maximizar FPS.
* **Control de Falsas Alarmas:** Algoritmo de enfriamiento (*cooldown*) temporal (3 s) para evitar saturación de la bitácora.
* **Zonas Industriales Configurables:**
  * *Zona A (Fundición y Hornos):* Exige Casco + Chaleco.
  * *Zona B (Almacén y Montacargas):* Exige Chaleco reflectante.
  * *Zona C (Taller de Mecanizado):* Exige Casco de seguridad.
  * *Zona D (Personalizado):* Supervisión libre.

### 2.3 Ficha Técnica del Dataset
* **Catálogo:** *PPE Computer Vision Model* (v1 2024-05-16).
* **Fuente:** Roboflow Universe (`constructionsite/ppe-fruwx/1`).
* **Enlace Público:** [https://universe.roboflow.com/constructionsite/ppe-fruwx/dataset/1](https://universe.roboflow.com/constructionsite/ppe-fruwx/dataset/1)
* **Volumen:** 2,591 imágenes anotadas en formato YOLOv8.
* **Licencia:** MIT License.

---

## 🧪 3. Simulaciones y Escenarios de Prueba

| Escenario Simulado | Entrada | Condición de Prueba | Resultado Esperado del Sistema |
| :--- | :--- | :--- | :--- |
| **Simulación 1: Acceso Seguro** | Cámara Web / Video | Operario portando casco y chaleco | Semáforo: `🟢 CONFORME (100% EPP)`, 0 infracciones en bitácora. |
| **Simulación 2: Omisión de Casco** | Cámara Web en vivo | Operario sin casco ingresando a Zona A | Semáforo: `🔴 ALERTA (Falta Casco)`, captura fotográfica automática en galería de evidencias. |
| **Simulación 3: Omisión de Chaleco** | Video de planta | Operario en almacén con ropa común | Semáforo: `🔴 ALERTA (Falta Chaleco)`, registro en bitácora con nivel de riesgo MEDIO. |
| **Simulación 4: Flujo Continuo** | Clip de CCTV (MP4) | Múltiples trabajadores en tránsito | Cálculo dinámico del % de cumplimiento global y exportación a reporte CSV. |

---

## 🤖 4. Registro de Prompts (Declaración de Uso de IA)
*Uso exclusivo de Inteligencia Artificial como copiloto de programación y optimización técnica:*

1. **Prompt Arquitectura:** *"Diseña un dashboard en Streamlit que cargue un modelo YOLOv8 ('best.pt') y procese video en vivo desde la webcam o archivos subidos, registrando en una tabla la hora y tipo de infracción cada vez que detecte 'no helmet' o 'no vest'."*
2. **Prompt Optimización de FPS:** *"El procesamiento frame a frame satura la CPU de la laptop. Optimiza app.py para reducir la resolución de inferencia a 480p y agrega un frame_skip configurable en la barra lateral para maximizar los FPS."*
3. **Prompt Mitigación de Spam (Cooldown):** *"Implementa un periodo de gracia (cooldown) de 3 a 5 segundos para que una misma persona parada frente a la cámara no genere 30 infracciones por segundo en la bitácora."*
4. **Prompt Métricas SST:** *"Crea una barra de progreso que calcule el % de Cumplimiento SST: (EPP Portados / EPP Requeridos) * 100 y clasifique el riesgo en Bajo, Moderado o Crítico."*

---

## 💻 5. Instrucciones de Instalación y Ejecución

```bash
# 1. Clonar el repositorio
git clone <URL_DE_ESTE_REPOSITORIO>
cd safeplant-ai-epp

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# 3. Instalar librerías
pip install -r requirements.txt

# 4. Iniciar el Dashboard
python -m streamlit run app.py
```

Acceder desde el navegador en: `http://localhost:8501`
