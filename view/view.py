from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QTextEdit, QFileDialog, QDialog, QFrame, QSizePolicy,
    QListWidgetItem, QStackedWidget, QSplitter, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QImage, QPixmap, QGuiApplication, QIcon, QPainter, QColor

try:
    import fitz
    PDF_PREVIEW_AVAILABLE = True
except Exception:
    fitz = None
    PDF_PREVIEW_AVAILABLE = False

# Paletas de colores (Solarized)
LIGHT_THEME = {
    "bg": "#fdf6e3",
    "surface": "#eee8d5",
    "surface_alt": "#f7f1dd",
    "text": "#586e75",
    "text_muted": "#93a1a1",
    "title": "#073642",
    "primary": "#268bd2",
    "primary_hover": "#2aa198",
    "border": "#d8d2bf",
    "scrollbar_bg": "#f3ecd8",
    "scrollbar_handle": "#c9c2b0"
}

DARK_THEME = {
    "bg": "#0d1117",
    "surface": "#161b22",
    "surface_alt": "#21262d",
    "text": "#c9d1d9",
    "text_muted": "#8b949e",
    "title": "#ffffff",
    "primary": "#58a6ff",
    "primary_hover": "#1f6feb",
    "border": "#30363d",
    "scrollbar_bg": "#0d1117",
    "scrollbar_handle": "#484f58"
}

def get_stylesheet(theme):
    return f"""
        QWidget {{
            background-color: {theme['bg']};
            color: {theme['text']};
            font-family: 'Source Sans 3', 'IBM Plex Sans', 'Segoe UI', sans-serif;
            font-size: 14px;
        }}

        /* Ventanas secundarias y paneles */
        QDialog, QMainWindow {{
            background-color: {theme['bg']};
        }}

        QFrame#header {{
            background-color: {theme['surface_alt']};
            border: 1px solid {theme['border']};
            border-radius: 10px;
        }}

        QFrame#card, QFrame#panel {{
            background-color: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 10px;
        }}

        QFrame#panel {{
            background-color: {theme['surface_alt']};
        }}

        /* Entradas de texto */
        QTextEdit, QListWidget {{
            background-color: {theme['surface']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
            padding: 12px;
            selection-background-color: {theme['primary']};
        }}
        
        QTextEdit:focus, QListWidget:focus {{
            border: 1px solid {theme['primary_hover']};
            box-shadow: 0 0 0 3px {theme['primary']}55;
        }}

        /* Etiquetas */
        QLabel {{
            color: {theme['text']};
            font-size: 15px;
            background-color: transparent;
        }}
        
        QLabel#title {{
            font-size: 24px;
            font-weight: 700;
            color: {theme['title']};
        }}

        QLabel#subtitle {{
            font-size: 14px;
            color: {theme['text_muted']};
        }}

        QLabel#section {{
            font-size: 16px;
            font-weight: 600;
            color: {theme['title']};
        }}

        QLabel#hint {{
            font-size: 13px;
            color: {theme['text_muted']};
        }}

        QLabel#note {{
            font-size: 12px;
            color: {theme['text_muted']};
        }}

        /* Botones */
        QPushButton {{
            background-color: {theme['surface_alt']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-bottom: 3px solid {theme['border']};
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: 500;
            transition: all 80ms ease-in-out;
        }}

        QPushButton:hover {{
            background-color: {theme['surface']};
        }}

        QPushButton:pressed {{
            background-color: {theme['primary']};
            color: #ffffff;
            border-bottom: 1px solid {theme['primary']};
            padding-top: 11px;
            padding-bottom: 9px;
        }}

        QPushButton#primary {{
            background-color: {theme['primary']};
            color: #ffffff;
            border: none;
        }}

        QPushButton#primary:hover {{
            background-color: {theme['primary_hover']};
        }}

        QPushButton#ghost {{
            background-color: transparent;
            border: 1px solid {theme['border']};
            color: {theme['text']};
        }}

        QPushButton#ghost:pressed {{
            background-color: {theme['border']};
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            border: none;
            background: {theme['scrollbar_bg']};
            width: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: {theme['scrollbar_handle']};
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        QScrollBar:horizontal {{
            border: none;
            background: {theme['scrollbar_bg']};
            height: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background: {theme['scrollbar_handle']};
            min-width: 20px;
            border-radius: 5px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
        }}

        /* Tooltips */
        QToolTip {{
            background-color: {theme['surface']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            padding: 6px 8px;
            border-radius: 6px;
            font-size: 12px;
        }}

        /* Barra de progreso */
        QProgressBar#headerProgress {{
            background: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 3px;
        }}
        QProgressBar#headerProgress::chunk {{
            background: {theme['primary']};
            border-radius: 3px;
        }}
    """

def build_pdf_icon():
    pix = QPixmap(24, 32)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.fillRect(2, 2, 20, 28, QColor("#d32f2f"))
    painter.setPen(Qt.GlobalColor.white)
    painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "PDF")
    painter.end()
    return QIcon(pix)

class BaseDialog(QDialog):
    def __init__(self, title, is_dark_mode=False):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self.is_dark_mode = is_dark_mode
        self.setStyleSheet(get_stylesheet(DARK_THEME if is_dark_mode else LIGHT_THEME))
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Titulo interno
        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("title")
        self.main_layout.addWidget(self.lbl_title)

    def update_theme(self, is_dark):
        self.is_dark_mode = is_dark
        self.setStyleSheet(get_stylesheet(DARK_THEME if is_dark else LIGHT_THEME))

class HypothesisWindow(BaseDialog):
    def __init__(self, is_dark_mode=False):
        super().__init__("Hipótesis evaluadas", is_dark_mode)
        
        self.list_widget = QListWidget()
        self.main_layout.addWidget(self.list_widget)
        
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.accept)
        self.main_layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def update_data(self, hypotheses):
        self.list_widget.clear()
        for h in hypotheses:
            self.list_widget.addItem(f"{h['name']} - Relevancia: {h['score']}")

class DiagnosisWindow(BaseDialog):
    def __init__(self, is_dark_mode=False):
        super().__init__("Diagnóstico final", is_dark_mode)
        
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card_layout = QVBoxLayout(self.card)

        self.badge_layout = QHBoxLayout()
        self.badge = QLabel()
        self.badge.setFixedSize(16, 16)
        self.badge.setStyleSheet("border-radius: 8px; background-color: #fbbf24;")
        self.badge_label = QLabel("Riesgo medio")
        self.badge_label.setObjectName("hint")
        self.badge_layout.addWidget(self.badge)
        self.badge_layout.addWidget(self.badge_label)
        self.badge_layout.addStretch()

        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.label.setText("🩺 Aún no hay diagnóstico.\nEjecuta 'Diagnosticar' para ver resultados.")

        self.card_layout.addLayout(self.badge_layout)
        self.card_layout.addWidget(self.label)
        self.main_layout.addWidget(self.card)
        
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.accept)
        self.main_layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def update_data(self, diagnosis):
        if diagnosis:
            self.label.setText(diagnosis)
            self.badge.setStyleSheet("border-radius: 8px; background-color: #fbbf24;")
            self.badge_label.setText("Riesgo medio")
        else:
            self.label.setText("🩺 Aún no hay diagnóstico.\nEjecuta 'Diagnosticar' para ver resultados.")
            self.badge.setStyleSheet("border-radius: 8px; background-color: #9ca3af;")
            self.badge_label.setText("En espera")

class JustificationWindow(BaseDialog):
    def __init__(self, is_dark_mode=False):
        super().__init__("Justificación del diagnóstico", is_dark_mode)
        
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.main_layout.addWidget(self.text)
        
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.accept)
        self.main_layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def update_data(self, justification):
        self.text.setText(justification)

class PDFWindow(BaseDialog):
    def __init__(self, is_dark_mode=False):
        super().__init__("Documentos anexos", is_dark_mode)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(240)
        self.list_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)

        self.preview_stack = QStackedWidget()
        self.preview_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_placeholder = QLabel("Selecciona un PDF para vista previa.")
        self.preview_placeholder.setObjectName("hint")
        self.preview_placeholder.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.preview_stack.addWidget(self.preview_placeholder)
        self.preview_placeholder.setText("👋 Bienvenido.\nAñade PDFs y selecciónalos para ver la vista previa aquí.")

        self.preview_container = QFrame()
        self.preview_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_container_layout = QVBoxLayout(self.preview_container)
        self.preview_container_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_container_layout.setSpacing(0)

        self.preview_image = QLabel()
        self.preview_image.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.preview_image.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.preview_image.setScaledContents(False)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.preview_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_scroll.setWidget(self.preview_image)

        # Overlay info y zoom flotante
        self.overlay_bar = QHBoxLayout()
        self.overlay_bar.setContentsMargins(12, 12, 12, 0)
        self.overlay_bar.setSpacing(8)
        self.overlay_label = QLabel("")
        self.overlay_label.setObjectName("hint")
        self.overlay_label.setStyleSheet("background: rgba(0,0,0,0.35); padding: 6px 10px; border-radius: 8px; color: white;")
        self.overlay_bar.addStretch()
        self.overlay_bar.addWidget(self.overlay_label)

        self.overlay_zoom = QHBoxLayout()
        self.overlay_zoom.setContentsMargins(12, 8, 12, 12)
        self.overlay_zoom.setSpacing(6)
        self.float_zoom_out = QPushButton("-")
        self.float_zoom_in = QPushButton("+")
        for btn in (self.float_zoom_out, self.float_zoom_in):
            btn.setFixedSize(40, 40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("ghost")
        self.overlay_zoom.addStretch()
        self.overlay_zoom.addWidget(self.float_zoom_out)
        self.overlay_zoom.addWidget(self.float_zoom_in)

        self.preview_container_layout.addLayout(self.overlay_bar)
        self.preview_container_layout.addWidget(self.preview_scroll)
        self.preview_container_layout.addLayout(self.overlay_zoom)

        if PDF_PREVIEW_AVAILABLE:
            self.preview_stack.addWidget(self.preview_container)

        self.splitter.addWidget(self.list_widget)
        self.splitter.addWidget(self.preview_stack)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([240, 1080])
        self.main_layout.addWidget(self.splitter)

        # Navegación de páginas
        self.nav_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton("◀")
        self.next_page_btn = QPushButton("▶")
        for btn in (self.prev_page_btn, self.next_page_btn):
            btn.setFixedWidth(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.page_label = QLabel("Página - / -")
        self.page_label.setObjectName("note")

        self.zoom_out_btn = QPushButton("–")
        self.zoom_in_btn = QPushButton("+")
        for btn in (self.zoom_out_btn, self.zoom_in_btn):
            btn.setFixedWidth(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_label = QLabel("100%")
        self.zoom_label.setObjectName("note")

        self.nav_layout.addWidget(self.prev_page_btn)
        self.nav_layout.addWidget(self.page_label)
        self.nav_layout.addWidget(self.next_page_btn)
        self.nav_layout.addSpacing(12)
        self.nav_layout.addWidget(self.zoom_out_btn)
        self.nav_layout.addWidget(self.zoom_label)
        self.nav_layout.addWidget(self.zoom_in_btn)
        self.nav_layout.addStretch()
        self.main_layout.addLayout(self.nav_layout)
        
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Añadir PDFs")
        self.add_btn.setObjectName("primary")
        
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.accept)
        
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.close_btn)
        
        self.main_layout.addLayout(self.btn_layout)
        # Title minimal, splitter takes the rest, buttons stick to bottom
        self.main_layout.setStretch(0, 0)  # title
        self.main_layout.setStretch(1, 1)  # splitter
        self.main_layout.setStretch(2, 0)  # nav
        self.main_layout.setStretch(3, 0)  # buttons

        self.current_pdf_path = None
        self.current_page = 0
        self.current_page_count = 0
        self.zoom_factor = 1.0
        self.current_file_name = None

        self.prev_page_btn.clicked.connect(lambda: self.change_page(-1))
        self.next_page_btn.clicked.connect(lambda: self.change_page(1))
        self.zoom_out_btn.clicked.connect(lambda: self.change_zoom(-0.1))
        self.zoom_in_btn.clicked.connect(lambda: self.change_zoom(0.1))
        self.float_zoom_out.clicked.connect(lambda: self.change_zoom(-0.1))
        self.float_zoom_in.clicked.connect(lambda: self.change_zoom(0.1))

    def update_data(self, pdfs):
        self.list_widget.clear()
        if not pdfs:
            placeholder = QListWidgetItem("No hay PDFs aún. Usa Añadir.")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            placeholder.setData(Qt.ItemDataRole.UserRole, "")
            self.list_widget.addItem(placeholder)
            self.preview_placeholder.setText("👋 Bienvenido.\nAñade PDFs para comenzar y selecciónalos para previsualizarlos.")
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            self.update_nav_state(disable=True)
            return

        icon = build_pdf_icon()
        for pdf in pdfs:
            item = QListWidgetItem(icon, pdf["name"])
            item.setData(Qt.ItemDataRole.UserRole, pdf["path"])
            self.list_widget.addItem(item)

        # Seleccionar y forzar carga inicial
        self.list_widget.setCurrentRow(0)
        self.on_selection_changed()

    def on_selection_changed(self):
        selected = self.list_widget.selectedItems()
        if not selected:
            self.preview_placeholder.setText("Selecciona un PDF para vista previa.")
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            self.update_nav_state(disable=True)
            return

        path = selected[0].data(Qt.ItemDataRole.UserRole)
        if not path:
            self.preview_placeholder.setText("Selecciona un PDF para vista previa.")
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            self.update_nav_state(disable=True)
            return

        if not PDF_PREVIEW_AVAILABLE:
            self.preview_placeholder.setText(
                "Vista previa no disponible en este entorno.\n"
                f"Archivo seleccionado: {path}"
            )
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            self.update_nav_state(disable=True)
            return

        try:
            doc = fitz.open(path)
            if doc.page_count == 0:
                raise ValueError("PDF vacío.")
            page_count = doc.page_count
            doc.close()
        except Exception:
            self.preview_placeholder.setText("No se pudo cargar la vista previa del PDF.")
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            self.update_nav_state(disable=True)
            return

        self.current_pdf_path = path
        self.current_page_count = page_count
        self.current_page = 0
        self.current_file_name = path.split("/")[-1] if "/" in path else path.split("\\")[-1]
        self.zoom_factor = 1.0
        self.render_page(self.current_page)
        self.update_nav_state()

    def render_page(self, page_index):
        if not self.current_pdf_path:
            return
        try:
            doc = fitz.open(self.current_pdf_path)
            if page_index < 0 or page_index >= doc.page_count:
                doc.close()
                raise ValueError("Página fuera de rango")
            page = doc.load_page(page_index)
            rect = page.rect
            target_width = 1100
            base_scale = min(2.5, max(1.0, target_width / rect.width))
            scale = min(3.0, max(0.5, base_scale * self.zoom_factor))
            matrix = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888).copy()
            doc.close()
        except Exception:
            self.preview_placeholder.setText("No se pudo cargar la vista previa del PDF.")
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            self.update_nav_state(disable=True)
            return

        self.preview_image.setPixmap(QPixmap.fromImage(image))
        self.preview_image.adjustSize()
        self.preview_scroll.verticalScrollBar().setValue(0)
        self.preview_scroll.horizontalScrollBar().setValue(0)
        self.page_label.setText(f"Página {page_index + 1} / {self.current_page_count}")
        self.zoom_label.setText(f"{int(self.zoom_factor*100)}%")
        self.overlay_label.setText(f"{self.current_file_name} • {page_index + 1}/{self.current_page_count}")
        self.preview_stack.setCurrentWidget(self.preview_container)

    def change_page(self, delta):
        if self.current_pdf_path is None:
            return
        new_page = self.current_page + delta
        if new_page < 0 or new_page >= self.current_page_count:
            return
        self.current_page = new_page
        self.render_page(self.current_page)
        self.update_nav_state()

    def change_zoom(self, delta):
        if self.current_pdf_path is None:
            return
        self.zoom_factor = min(3.0, max(0.5, self.zoom_factor + delta))
        self.render_page(self.current_page)
        self.update_nav_state()

    def update_nav_state(self, disable=False):
        if disable or self.current_pdf_path is None:
            self.prev_page_btn.setEnabled(False)
            self.next_page_btn.setEnabled(False)
            self.page_label.setText("Página - / -")
            self.zoom_out_btn.setEnabled(False)
            self.zoom_in_btn.setEnabled(False)
            self.float_zoom_out.setEnabled(False)
            self.float_zoom_in.setEnabled(False)
            self.zoom_label.setText("100%")
            self.overlay_label.setText("")
            return

        self.prev_page_btn.setEnabled(self.current_page > 0)
        self.next_page_btn.setEnabled(self.current_page < self.current_page_count - 1)
        self.page_label.setText(f"Página {self.current_page + 1} / {self.current_page_count}")

        self.zoom_out_btn.setEnabled(True)
        self.zoom_in_btn.setEnabled(True)
        self.float_zoom_out.setEnabled(True)
        self.float_zoom_in.setEnabled(True)
        self.zoom_label.setText(f"{int(self.zoom_factor*100)}%")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de diagnóstico legal")
        self.setMinimumSize(900, 620)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.status = self.statusBar()
        self.status.showMessage("Modo Local activo")

        self.is_dark_mode = False  # Por defecto claro

        # Referencias a ventanas secundarias
        self.hw = None
        self.dw = None
        self.jw = None
        self.pw = None
        self.pdf_callback = None
        self.pdf_add_callback = None

        # Widget central y layout
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(18)

        # Barra superior con título y botón de tema
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header")
        self.top_bar = QHBoxLayout(self.header_frame)
        self.top_bar.setContentsMargins(16, 14, 16, 14)

        self.header_left = QHBoxLayout()
        self.header_left.setSpacing(12)

        self.header_layout = QVBoxLayout()
        self.header_layout.setSpacing(4)
        self.title_label = QLabel("Sistema de diagnóstico legal")
        self.title_label.setObjectName("title")
        self.subtitle_label = QLabel("Introduce los hechos, síntomas o cláusulas para evaluar.")
        self.subtitle_label.setObjectName("subtitle")
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addWidget(self.subtitle_label)

        self.header_left.addLayout(self.header_layout)

        self.theme_btn = QPushButton("Modo oscuro")
        self.theme_btn.setObjectName("ghost")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)

        self.top_bar.addLayout(self.header_left)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.theme_btn)

        self.main_layout.addWidget(self.header_frame)
        # Barra de progreso ficticia
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("headerProgress")
        self.main_layout.addWidget(self.progress_bar)

        # Contenido principal con columna de entrada y panel de acciones
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(20)
        self.main_layout.addLayout(self.content_layout)

        # Card central para entrada de texto
        self.card_frame = QFrame()
        self.card_frame.setObjectName("card")
        self.card_layout = QVBoxLayout(self.card_frame)
        self.card_layout.setContentsMargins(20, 20, 20, 20)
        self.card_layout.setSpacing(12)

        # Barra rápida sobre el editor
        self.tools_layout = QHBoxLayout()
        self.tools_layout.setSpacing(8)
        self.clear_btn = QPushButton("Limpiar")
        self.clear_btn.setObjectName("ghost")
        self.clear_btn.setToolTip("Vaciar el texto")
        self.paste_btn = QPushButton("Pegar")
        self.paste_btn.setObjectName("ghost")
        self.paste_btn.setToolTip("Pegar desde portapapeles")
        for btn in (self.clear_btn, self.paste_btn):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tools_layout.addWidget(self.clear_btn)
        self.tools_layout.addWidget(self.paste_btn)
        self.tools_layout.addStretch()
        self.card_layout.addLayout(self.tools_layout)

        self.input_title = QLabel("Resumen del caso")
        self.input_title.setObjectName("section")
        self.input_hint = QLabel("Describe el contexto legal, fechas, actores y cláusulas relevantes.")
        self.input_hint.setObjectName("hint")
        self.input_hint.setWordWrap(True)

        self.symptoms_input = QTextEdit()
        self.symptoms_input.setPlaceholderText("Ej. El cliente firmó un contrato de arrendamiento en 2020 y...")
        self.symptoms_input.setMinimumHeight(260)
        self.symptoms_input.textChanged.connect(self.update_counter)

        self.card_layout.addWidget(self.input_title)
        self.card_layout.addWidget(self.input_hint)
        self.card_layout.addWidget(self.symptoms_input)

        # Contador de texto
        self.counter_label = QLabel("0 palabras | 0 caracteres")
        self.counter_label.setObjectName("note")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.card_layout.addWidget(self.counter_label)

        self.content_layout.addWidget(self.card_frame, 3)

        # Panel lateral de acciones
        self.side_panel = QFrame()
        self.side_panel.setObjectName("panel")
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_layout.setContentsMargins(16, 16, 16, 16)
        self.side_layout.setSpacing(12)

        self.actions_title = QLabel("Acciones")
        self.actions_title.setObjectName("section")
        self.actions_hint = QLabel("Flujo recomendado: adjuntar PDFs, evaluar hipótesis y diagnosticar.")
        self.actions_hint.setObjectName("hint")
        self.actions_hint.setWordWrap(True)

        self.pdf_btn = QPushButton("Gestionar PDFs")
        self.evaluate_btn = QPushButton("Evaluar hipótesis")
        self.justify_btn = QPushButton("Ver justificación")
        self.diagnose_btn = QPushButton("Diagnosticar")
        self.diagnose_btn.setObjectName("primary")

        for btn in [self.pdf_btn, self.evaluate_btn, self.justify_btn, self.diagnose_btn]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(36)

        self.actions_note = QLabel("Los resultados se muestran en ventanas separadas.")
        self.actions_note.setObjectName("note")
        self.actions_note.setWordWrap(True)

        self.side_layout.addWidget(self.actions_title)
        self.side_layout.addWidget(self.actions_hint)
        self.side_layout.addWidget(self.pdf_btn)
        self.side_layout.addWidget(self.evaluate_btn)
        self.side_layout.addWidget(self.justify_btn)
        self.side_layout.addWidget(self.diagnose_btn)
        self.side_layout.addStretch()
        self.side_layout.addWidget(self.actions_note)

        self.content_layout.addWidget(self.side_panel, 1)

        # Aplicar el tema inicial
        self.apply_theme()

        # Conexiones micro-UX
        self.clear_btn.clicked.connect(self.symptoms_input.clear)
        self.paste_btn.clicked.connect(self.paste_text)
        self.update_counter()

    def apply_theme(self):
        theme = DARK_THEME if self.is_dark_mode else LIGHT_THEME
        self.setStyleSheet(get_stylesheet(theme))
        
        if self.is_dark_mode:
            self.theme_btn.setText("Modo claro")
        else:
            self.theme_btn.setText("Modo oscuro")
            
        # Actualizar ventanas secundarias si existen
        for win in [self.hw, self.dw, self.jw, self.pw]:
            if win:
                win.update_theme(self.is_dark_mode)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    # conexiones (Mantenidas exactas para el controlador)
    def on_evaluate_clicked(self, callback):
        self.evaluate_btn.clicked.connect(callback)

    def on_diagnose_clicked(self, callback):
        self.diagnose_btn.clicked.connect(callback)

    def on_justify_clicked(self, callback):
        self.justify_btn.clicked.connect(callback)

    def on_pdf_clicked(self, callback):
        self.pdf_callback = callback
        self.pdf_btn.clicked.connect(callback)

    def on_pdf_add_clicked(self, callback):
        self.pdf_add_callback = callback

    # getters
    def get_symptoms(self):
        return [line for line in self.symptoms_input.toPlainText().split("\n") if line.strip()]

    # utilidades de entrada
    def update_counter(self):
        text = self.symptoms_input.toPlainText()
        words = len([w for w in text.split() if w.strip()])
        chars = len(text)
        self.counter_label.setText(f"{words} palabras | {chars} caracteres")
        if self.status:
            self.status.showMessage("Listo" if chars == 0 else "Editando resumen...")

    def paste_text(self):
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            self.symptoms_input.insertPlainText(clipboard.text())

    # ventanas auxiliares
    def show_hypotheses(self, hypotheses):
        if not self.hw:
            self.hw = HypothesisWindow(self.is_dark_mode)
        self.hw.update_data(hypotheses)
        self.hw.show()
        self.hw.raise_()
        self.hw.activateWindow()

    def show_diagnosis(self, diagnosis):
        if not self.dw:
            self.dw = DiagnosisWindow(self.is_dark_mode)
        self.dw.update_data(diagnosis)
        self.dw.show()
        self.dw.raise_()
        self.dw.activateWindow()

    def show_justification(self, justification):
        if not self.jw:
            self.jw = JustificationWindow(self.is_dark_mode)
        self.jw.update_data(justification)
        self.jw.show()
        self.jw.raise_()
        self.jw.activateWindow()

    def show_pdf_window(self, pdfs):
        if not self.pw:
            self.pw = PDFWindow(self.is_dark_mode)
        if self.pdf_add_callback:
            try:
                self.pw.add_btn.clicked.disconnect()
            except Exception:
                pass
            self.pw.add_btn.clicked.connect(self.pdf_add_callback)
        self.pw.update_data(pdfs)
        self.pw.show()
        self.pw.raise_()
        self.pw.activateWindow()
