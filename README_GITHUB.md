## 1. Hojas Tecnicas

### Modelo (YOLOv8n)
- Arquitectura: YOLOv8 nano de Ultralytics. Usamos la version nano porque es bastante ligera y corre fluido en la CPU de una laptop sin necesidad de tener una tarjeta grafica dedicada.
- Archivo de pesos: `best.pt` (pesa 6.24 MB).
- Cantidad de parametros: 3.01 millones.
- Resolucion de entrada: 480x480 px en la app para ganar velocidad de procesamiento (FPS) en vivo.
- Clases del modelo: boots, helmet, no helmet, no vest, person, vest.
- Parametros de deteccion: Confianza minima en 0.30, IoU en 0.45 y NMS agnostico activado para evitar que dibuje varios cuadros sobre la misma persona.

### Dataset
- Nombre: PPE Computer Vision Model
- Plataforma: Roboflow Universe (proyecto: constructionsite/ppe-fruwx/1)
- Link publico: https://universe.roboflow.com/constructionsite/ppe-fruwx/dataset/1
- Licencia: MIT (uso libre)
- Cantidad de imagenes: 2591 fotos etiquetadas en obras y plantas industriales.
- Entrenamiento: Se entreno durante 50 epocas en Google Colab usando una GPU Tesla T4.

### Librerias utilizadas
- Python 3.10 o superior
- ultralytics (para cargar y correr el modelo YOLO)
- streamlit (para la interfaz visual del dashboard)
- opencv-python (para la lectura y dibujado de cuadros en el video)
- pandas y numpy (para la tabla de infracciones y exportar el reporte)

---

## 2. Pruebas y Simulaciones Realizadas

Probamos el funcionamiento de la aplicacion en diferentes situaciones de planta:

1. Operario con equipo completo: Si la persona tiene puesto su casco y chaleco, el modelo los detecta con mas del 85% de confianza, marca 100% de cumplimiento y no agrega ninguna infraccion a la bitacora.
2. Operario sin casco: Si entra alguien sin casco, el sistema detecta la falta, pinta el cuadro en rojo, emite una advertencia visual en pantalla y guarda la foto de la infraccion con la hora exacta.
3. Operario sin chaleco: Como en tomas de perfil o de lejos el modelo a veces no detecta directo la etiqueta "no vest", agregamos una validacion en codigo: si reconoce a una persona y no encuentra chaleco en su cuerpo, lo registra automaticamente como falta de chaleco.
4. Tiempo de enfriamiento (cooldown): Para que no se generen 30 filas repetidas por segundo si alguien se queda parado frente a la camara, pusimos un freno de 3 segundos entre registros de una misma falta.
5. Filtro por zonas de trabajo: Probamos cambiando de zona en el menu lateral. Por ejemplo, en Zona Almacen solo pide chaleco obligatorio, mientras que en Zona Produccion exige casco y chaleco juntos.

---

## 3. Prompts Utilizados (Uso de Inteligencia Artificial)

Siguiendo las normas del curso, la inteligencia artificial se uso como asistente de programacion para resolver dudas de codigo, optimizar funciones en Python y armar la interfaz:

- Prompt 1 (Base de la aplicacion): Como estructuro una aplicacion en Streamlit que cargue mi modelo best.pt de YOLOv8 y procese video en vivo desde la camara o subiendo un archivo mp4?
- Prompt 2 (Mejora de velocidad): La camara web se me cuelga en la laptop cuando corre YOLO. Que puedo hacer en OpenCV o Streamlit para bajar la resolucion a 480p y procesar menos frames por segundo para que no consuma tanta CPU?
- Prompt 3 (Control de registros repetidos): Cuando detecta a alguien sin casco me llena la tabla con cientos de filas iguales en pocos segundos. Como hago una logica de cooldown en Python que espere 3 segundos antes de registrar otra infraccion?
- Prompt 4 (Validacion de chaleco): Mi modelo a veces no detecta bien la clase no vest cuando la persona se mueve. Como programo una regla para que si detecta person y no detecta vest, cuente como infraccion de chaleco?
- Prompt 5 (Descarga de reportes): Como agrego un boton en Streamlit para que el usuario pueda descargar la tabla de infracciones en un archivo CSV ordenado con fecha, hora y tipo de falta?

---

## 4. Como Ejecutar el Proyecto en Local

Pasos para levantarlo en cualquier computadora con Windows o Mac:

### 1. Tener los archivos listos
Descargar o clonar este repositorio y verificar que esten en la misma carpeta:
- `app.py`
- `best.pt`
- `requirements.txt`

### 2. Instalar las dependencias
Abrir la terminal o PowerShell dentro de la carpeta y correr:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicacion
Lanzar Streamlit con este comando:
```bash
python -m streamlit run app.py
```

Si estas en Windows y la consola muestra algun aviso por emojis o caracteres raros, usar este comando alternativo:
```powershell
$env:PYTHONIOENCODING="utf-8"; python -m streamlit run app.py
```

### 4. Abrir el panel
Entrar desde el navegador a:
```
http://localhost:8501
```

En la barra lateral se puede cambiar entre camara en vivo, subir un video de prueba o usar una imagen fija, ademas de elegir la zona de planta a supervisar.
