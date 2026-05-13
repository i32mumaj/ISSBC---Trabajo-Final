# ISSBC – Diagnóstico Legal Asistido por IA

Aplicación de escritorio para análisis y diagnóstico de casos legales mediante un LLM local (Ollama). Arquitectura MVC con PyQt6.

---

## Características

### Análisis legal
- Genera hipótesis legales ordenadas por probabilidad a partir del resumen del caso
- Diagnóstico con título, nivel de gravedad, resumen, justificación estructurada y referencias legales aplicables
- Nivel de detalle seleccionable: **Rápido**, **Estándar** o **Exhaustivo**
- Modo revisión: resalta en el editor las frases clave del diagnóstico
- Referencias legales reales con acceso directo a búsqueda en el BOE

### Chat
- Conversación libre con el LLM en contexto del caso
- Streaming token a token con burbuja de escritura animada
- Soporte Markdown básico en las burbujas
- Timestamps y botón de copiar en cada mensaje
- Botón para regenerar el último análisis

### Editor del caso
- Corrector ortográfico en español con sugerencias en el menú contextual y diccionario personal
- Contador de tokens estimado en tiempo real
- Plantillas predefinidas (despido, arrendamiento, contrato mercantil, etc.)
- Autoguardado del borrador cada 30 segundos
- Título del caso editable con generación automática vía LLM

### Gestión de conversaciones
- Sidebar con lista de casos ordenados por fecha de modificación
- Cargar, eliminar y crear nuevos casos desde la barra lateral
- Persistencia completa: chat, hipótesis, diagnóstico, PDFs asociados

### Documentos PDF
- Visor integrado con paginación, zoom y overlay de página actual
- Extracción de texto por página para incluir en el contexto del LLM (hasta 4 documentos)
- Búsqueda de texto dentro del visor de PDFs
- Vista de miniaturas en cuadrícula
- Drag & drop de archivos en el panel
- Barra de progreso al cargar documentos grandes
- Estado vacío ilustrado cuando no hay documentos

### Exportación
- **PDF**: informe completo con hipótesis, justificación, citas y referencias legales
- **Word (.docx)**: documento editable con mismo contenido
- **CSV**: historial de conversación completo
- **Email**: abre cliente de correo con el diagnóstico prellenado
- **Imprimir**: diálogo de impresión del sistema (Ctrl+P)

### Archivos de caso `.issbc`
- Guarda y carga casos completos (chat, análisis, PDFs embebidos en base64) en un único archivo portátil

### Configuración
- Selector de modelo Ollama (descarga incluida desde la UI)
- Prompt extra personalizable que se añade a todas las peticiones
- Tamaño y familia de fuente globales (slider + selector)

### UX
- Tema Solarized claro/oscuro
- Animaciones de entrada en burbujas del chat
- Notificación de sistema al completar el análisis (si la ventana está minimizada)
- Tooltips con texto completo en campos truncados
- Popup de atajos de teclado (Ctrl+?)
- Gráfico de barras horizontal para hipótesis con indicador de confianza global

---

## Requisitos

- Python 3.11+
- [Ollama](https://ollama.com/) instalado y en ejecución con al menos un modelo descargado (por defecto `qwen2.5:7b`)

### Dependencias Python

```
PyQt6
PyMuPDF          # fitz — visor PDF y exportación
pyspellchecker   # corrector ortográfico
python-docx      # exportación Word
ollama           # cliente Python de Ollama
```

---

## Instalación

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install PyQt6 PyMuPDF pyspellchecker python-docx ollama
```

---

## Ejecución

```bash
python main.py
```

La ventana se abre maximizada. Asegúrate de que Ollama esté corriendo (`ollama serve`) antes de lanzar la app.

---

## Estructura del proyecto

```
Parcial1/
├── main.py                      # Punto de entrada (MVC wiring)
├── model/
│   └── model.py                 # Modelo de datos
├── view/
│   └── view.py                  # UI completa (PyQt6)
├── controller/
│   └── controller.py            # Lógica de la app, workers QThread
└── services/
    ├── llm_service.py           # Integración Ollama (hipótesis, diagnóstico, chat, título)
    ├── pdf_service.py           # Carga y extracción de texto de PDFs
    ├── export_service.py        # Exportación PDF / DOCX / CSV / email
    ├── conversation_service.py  # Persistencia de conversaciones (~/.issbc/convs/)
    └── settings_service.py      # Ajustes de usuario (~/.issbc/settings.json)
```

---

## Datos persistidos

Todos los datos se guardan en `~/.issbc/`:

| Ruta | Contenido |
|---|---|
| `~/.issbc/convs/*.json` | Conversaciones (chat, hipótesis, diagnóstico, rutas PDF) |
| `~/.issbc/settings.json` | Modelo, tamaño de fuente, prompt extra |
| `~/.issbc/pdf_cache/` | PDFs extraídos de archivos `.issbc` |

---

## Atajos de teclado

| Atajo | Acción |
|---|---|
| `Ctrl+Enter` | Analizar caso |
| `Ctrl+N` | Nuevo caso |
| `Ctrl+S` | Guardar caso como `.issbc` |
| `Ctrl+O` | Abrir caso `.issbc` |
| `Ctrl+P` | Imprimir diagnóstico |
| `Ctrl+,` | Abrir ajustes |
| `Ctrl+?` | Mostrar todos los atajos |
