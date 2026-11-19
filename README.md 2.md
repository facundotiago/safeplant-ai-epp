# SafePlant AI - Detector de EPP para Planta Industrial

Proyecto desarrollado para el curso de Inteligencia Artificial Aplicada (Sección 359), carrera de Ingeniería Industrial en la Universidad de Lima.

El objetivo del proyecto es monitorear en tiempo real mediante visión computacional el uso correcto de Equipos de Protección Personal (casco y chaleco) en áreas operativas, registrando infracciones y calculando el nivel de cumplimiento de seguridad en planta.

---

## 1. Hojas Técnicas

### Modelo (YOLOv8n)
* **Arquitectura:** YOLOv8 nano (Ultralytics). Se eligió la versión nano por su bajo consumo de recursos, permitiendo correr la inferencia en tiempo real directamente en la CPU de una laptop estándar.
* **Archivo de pesos:** `best.pt` (6.24 MB).
* **Parámetros:** 3.01 millones.
* **Resolución de trabajo:** 480x480 px (escalado para optimizar FPS en video en vivo).
* **Clases configuradas:** `boots`, `helmet`, `no helmet`, `no vest`, `person`, `vest`.
* **Ajustes de inferencia:** Umbral de confianza mínimo en 0.30, IoU en 0.45 y NMS agnóstico activado para evitar cuadros duplicados sobre el mismo operario.

### Dataset de Entrenamiento
* **Nombre:** PPE Computer Vision Model
* **Plataforma:** Roboflow Universe (`constructionsite/ppe-fruwx/1`)
* **Enlace:** https://universe.roboflow.com/constructionsite/ppe-fruwx/dataset/1
* **Licencia:** MIT (acceso abierto)
* **Contenido:** 2,591 imágenes anotadas con bounding boxes en escenarios de construcción y talleres.
* **Entrenamiento:** 50 épocas en Google Colab con aceleración GPU (Tesla T4).

### Requisitos y Librerías
* Python 3.10 o superior
* `ultralytics` (inferencia de YOLOv8)
* `streamlit` (interfaz web del panel de control)
* `opencv-python` (captura y manipulación de frames de video)
* `pandas` y `numpy` (gestión de la bitácora y cálculo de métricas)

---

## 2. Simulaciones y Pruebas Realizadas

El sistema fue probado bajo distintas condiciones para validar la respuesta del algoritmo y la interfaz:

1. **Prueba con casco y chaleco colocados:** El modelo identifica ambas prendas con confianza superior al 85%. El índice de cumplimiento se mantiene en 100% y no se generan registros en la bitácora.
2. **Prueba de omisión de casco:** Al ingresar una persona sin casco, se detecta la clase `no helmet` o la ausencia del mismo sobre el área de la cabeza, marcando el cuadro en rojo, emitiendo alerta visual y guardando la captura con marca de tiempo.
3. **Prueba de omisión de chaleco (lógica deductiva):** Dado que en tomas frontales o casuales a veces la etiqueta directa de "no vest" tiene menor muestra en el dataset, el script valida: si detecta `person` y no detecta `vest`, marca la infracción por falta de chaleco.
4. **Prueba de enfriamiento (cooldown):** Se configuró una ventana de 3 segundos para que si una misma persona permanece frente a la cámara, el sistema no colapse la bitácora ni el archivo CSV con decenas de alertas idénticas por segundo.
5. **Prueba por zonas industriales:** Se validó el cambio de requerimientos según la zona seleccionada (por ejemplo, en Almacén solo se exige chaleco, mientras que en Producción se exige casco y chaleco obligatorios).

---

## 3. Prompts Utilizados (Declaración de Uso de IA)

Siguiendo las pautas del curso, la inteligencia artificial generativa se utilizó únicamente como soporte para la programación, depuración de código en Python y optimización de rendimiento:

* **Prompt 1 (Estructura base de Streamlit):** *"Ayúdame a armar una app en Streamlit que cargue un modelo YOLOv8 local (best.pt) y procese video frame por frame desde la webcam o subiendo un archivo mp4."*
* **Prompt 2 (Optimización de FPS):** *"El video va muy lento cuando corre en la laptop. ¿Cómo puedo bajar la resolución a 480p y saltar frames para que la inferencia no consuma toda la CPU?"*
* **Prompt 3 (Evitar duplicados en la bitácora):** *"Si la cámara se queda apuntando a alguien sin casco se crean cientos de filas en segundos. Escribe una función de cooldown en Python que guarde la infracción solo si pasaron al menos 3 segundos desde la última."*
* **Prompt 4 (Lógica para chaleco):** *"El modelo a veces no reconoce la clase 'no vest'. ¿Cómo puedo hacer una lógica en Python para que si detecta 'person' y no hay 'vest', lo cuente como falta de chaleco?"*
* **Prompt 5 (Exportación a CSV):** *"Agrega una opción en Streamlit para descargar los datos de la tabla de infracciones en un archivo CSV formateado con fecha, hora y tipo de falta."*

---

## 4. Instrucciones de Instalación y Ejecución

Para correr el proyecto en una computadora local:

### 1. Descargar o clonar los archivos
Guardar en una misma carpeta los archivos del proyecto (`app.py`, `best.pt`, `requirements.txt`).

### 2. Instalar las dependencias
Abrir la terminal o PowerShell en la carpeta del proyecto y ejecutar:
```bash
pip install -r requirements.txt
```

### 3. Iniciar la aplicación
Ejecutar el comando de Streamlit:
```bash
python -m streamlit run app.py
```

*(En Windows, si la consola muestra advertencias por caracteres especiales o emojis, iniciar con:)*
```powershell
$env:PYTHONIOENCODING="utf-8"; python -m streamlit run app.py
```

### 4. Abrir en el navegador
Ingresar a la dirección local:
```
http://localhost:8501
```

Desde el panel lateral se puede seleccionar la fuente de video (cámara web, imagen de prueba o archivo de video), cambiar la zona de planta y ajustar la sensibilidad del modelo.
