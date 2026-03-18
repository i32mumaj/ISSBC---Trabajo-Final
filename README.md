Aquí tienes el README actualizado con la sección de instalación añadida al final:

```markdown
# Sistema de Diagnóstico Legal (ISSBC – Parcial)

> Nota: Esta entrega se centra en la **vista (UI)** como parte del examen de la asignatura ISSBC. La lógica de negocio está simulada y pendiente de completar.

## Cómo usar la app

1) Arranque  
   - Activa la venv (`.venv`) y ejecuta `python main.py`. La ventana se abre maximizada.

2) Tema y estado  
   - Puedes alternar entre modo claro/oscuro. La barra de estado indica "Modo Local activo".

3) Resumen del caso  
   - Escribe el contexto legal en el cuadro principal.  
   - Usa la barra rápida: **Limpiar** (vacía el texto) y **Pegar** (desde portapapeles).  
   - El contador muestra palabras y caracteres; el focus resalta el borde.

4) Gestión de PDFs  
   - Haz clic en **Gestionar PDFs**. Se abre la vista de documentos anexos (maximizada).  
   - **Añadir PDFs**: selecciona archivos; se muestran en la lista con icono.  
   - Selecciona un PDF para ver la preview con scroll.  
   - Navegación: botones ◀/▶ para páginas; overlay muestra "archivo • página X/Y".  
   - Zoom: botones +/– (barra y flotantes) escalan la preview.  
   - Si no hay PDFs, verás un estado de bienvenida con instrucciones.

5) Hipótesis, justificación y diagnóstico  
   - Botones dedicados para mostrar resultados simulados en ventanas modales.  
   - La ventana de diagnóstico incluye un badge de severidad (placeholder).

## Características de la UI

- Tema Solarized claro/oscuro, tipografía moderna, botones con hover/pressed/elevación.  
- Estilos de focus mejorados, tooltips tematizados y barra de progreso decorativa bajo el header.  
- Barra de estado informativa.  
- Preview de PDFs con paginación, zoom, overlay informativo y estados vacíos amigables.  
- Layout maximizado en todas las ventanas para aprovechar espacio.

## Limitaciones actuales

- La lógica (LLM, evaluación real, diagnóstico) no está implementada; esta versión es principalmente la interfaz gráfica del parcial.

## Ejecución rápida

```bash
python -m venv .venv
./.venv/Scripts/activate  # Windows
pip install PyQt6
python main.py
```

## Instalación paso a paso

### 1. Crear el entorno virtual

Abre la terminal en la carpeta raíz del proyecto y ejecuta:

```bash
python -m venv .venv
```

### 2. Activar el entorno virtual

Ejecuta el comando correspondiente a tu sistema operativo:

- **Windows (CMD):** `.venv\Scripts\activate`
- **Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`
- **macOS / Linux:** `source .venv/bin/activate`

### 3. Instalar las dependencias

Instala la librería de la interfaz gráfica y el motor para leer los PDFs:

```bash
pip install PyQt6 PyMuPDF
```

### 4. Ejecutar el programa

Lanza el archivo principal de la aplicación:

```bash
python main.py
```
```