#!/usr/bin/env python3
"""
Kernel Chunker - Retro Industrial Desktop Tool
Splits large PRISM kernel decks into digestible chunks for Mika.

Design Philosophy: Same retro-industrial aesthetic as PyPulse.
"Beauty first, utility later."

Author: Black Orchard Labs
Date: January 2026
"""

import sys
import json
import os
import webbrowser
from pathlib import Path
from datetime import datetime

KOFI_URL = "https://ko-fi.com/blackorchardlabs"

try:
    from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                                  QHBoxLayout, QTextEdit, QPushButton, QScrollArea,
                                  QFrame, QMessageBox, QFileDialog)
    from PyQt6.QtCore import Qt, QPoint, QRectF, QMimeData
    from PyQt6.QtGui import (QPainter, QBrush, QPen, QColor, QFont, QPixmap,
                              QLinearGradient, QPainterPath, QClipboard, QDragEnterEvent,
                              QDropEvent)
except ImportError:
    print("PyQt6 not found. Please install with: pip install PyQt6")
    sys.exit(1)


class DropTextEdit(QTextEdit):
    """Text edit that passes drops to parent window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)  # Let parent handle drops


class ChunkCard(QFrame):
    """A card displaying a single kernel chunk"""

    def __init__(self, chunk_num, kernel_data, parent=None):
        super().__init__(parent)
        self.chunk_num = chunk_num
        self.kernel_data = kernel_data
        self.is_copied = False
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 2px solid #444;
                border-radius: 5px;
            }
            QFrame:hover {
                border: 2px solid #FF9500;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Chunk info
        info_layout = QVBoxLayout()

        # Title
        title = self.kernel_data.get('title', f'Kernel {self.chunk_num}')
        if len(title) > 50:
            title = title[:47] + "..."
        title_label = QLabel(f"<b style='color: #FF9500;'>#{self.chunk_num}</b> {title}")
        title_label.setStyleSheet("color: #ddd; font-size: 11px;")
        info_layout.addWidget(title_label)

        # Metadata - show section type or kernel ID
        section_type = self.kernel_data.get('section', None)
        if section_type:
            section_names = {
                'header': 'Identity & Metadata',
                'emotional_arc': 'Emotional Arc',
                'heat_signature': 'Heat Signature',
                'language_motifs': 'Language & Motifs',
                'physical_anchors': 'Physical Anchors',
                'visual_description': 'Visual Description',
                'dynamics': 'Relationship Dynamics',
                'core_truth': 'Core Truth & Boundaries',
                'cubic_attractor': 'Cubic Attractor',
                'export': 'Export Notes'
            }
            display_section = section_names.get(section_type, section_type)
            meta_label = QLabel(f"Section: {display_section}")
            meta_label.setStyleSheet("color: #9B59B6; font-size: 9px; font-weight: bold;")
        else:
            kernel_id = self.kernel_data.get('id', 'unknown')
            if len(kernel_id) > 40:
                kernel_id = "..." + kernel_id[-37:]
            meta_label = QLabel(f"ID: {kernel_id}")
            meta_label.setStyleSheet("color: #888; font-size: 9px;")
        info_layout.addWidget(meta_label)

        # Heat signature preview
        heat = self.kernel_data.get('heat_signature', {})
        if heat:
            tenderness = heat.get('tenderness', 0)
            trust = heat.get('trust', 0)
            erotic = heat.get('erotic_charge', 0)
            heat_text = f"Heat: T:{tenderness:.1f} Tr:{trust:.1f} E:{erotic:.1f}"
            heat_label = QLabel(heat_text)
            heat_label.setStyleSheet("color: #FF6B6B; font-size: 9px;")
            info_layout.addWidget(heat_label)

        layout.addLayout(info_layout, 1)

        # Copy button
        copy_btn = QPushButton("COPY")
        copy_btn.setFixedSize(60, 50)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #FF9500;
                border: 2px solid #555;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #FF9500;
            }
            QPushButton:pressed {
                background-color: #FF9500;
                color: #000;
            }
        """)
        copy_btn.clicked.connect(self.copy_kernel)
        layout.addWidget(copy_btn)

    def copy_kernel(self):
        """Copy this kernel to clipboard"""
        clipboard = QApplication.clipboard()
        # Wrap single kernel in a minimal deck format
        kernel_json = json.dumps(self.kernel_data, indent=2)
        clipboard.setText(kernel_json)

        # Mark as copied
        self.is_copied = True

        # Visual feedback - flash green then grey out
        self.setStyleSheet("""
            QFrame {
                background-color: #3a4a3a;
                border: 2px solid #00FF64;
                border-radius: 5px;
            }
        """)
        # Grey out after delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.set_copied_style)

    def set_copied_style(self):
        """Grey out the card after copying"""
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 5px;
            }
        """)
        # Dim the labels too
        for child in self.findChildren(QLabel):
            child.setStyleSheet(child.styleSheet().replace("#ddd", "#555").replace("#888", "#444").replace("#FF6B6B", "#663333"))
        for child in self.findChildren(QPushButton):
            child.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a2a;
                    color: #555;
                    border: 2px solid #333;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10px;
                }
            """)

    def reset_style(self):
        """Reset to default uncopied style"""
        self.is_copied = False
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 2px solid #444;
                border-radius: 5px;
            }
            QFrame:hover {
                border: 2px solid #FF9500;
            }
        """)
        # Restore label colors
        labels = self.findChildren(QLabel)
        if len(labels) >= 1:
            labels[0].setStyleSheet("color: #ddd; font-size: 11px;")  # Title
        if len(labels) >= 2:
            labels[1].setStyleSheet("color: #888; font-size: 9px;")   # Meta
        if len(labels) >= 3:
            labels[2].setStyleSheet("color: #FF6B6B; font-size: 9px;")  # Heat
        # Restore button
        for btn in self.findChildren(QPushButton):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: #FF9500;
                    border: 2px solid #555;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                    border-color: #FF9500;
                }
                QPushButton:pressed {
                    background-color: #FF9500;
                    color: #000;
                }
            """)


class KernelChunker(QWidget):
    """Main Kernel Chunker Widget"""

    def __init__(self):
        super().__init__()
        self.chunks = []
        self.current_chunk_index = 0
        self.is_dragging = False
        self.drag_position = QPoint()
        self.background_pixmap = None

        self.init_ui()
        self.load_assets()

    def init_ui(self):
        self.setFixedSize(400, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("Kernel Chunker")
        self.setAcceptDrops(True)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 45, 15, 15)
        main_layout.setSpacing(10)

        # Close button (top right)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FF4444;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        # Position it absolutely in top-right
        self.close_btn.setParent(self)
        self.close_btn.move(370, 8)

        # Ko-fi support button (heart)
        self.kofi_btn = QPushButton("♥")
        self.kofi_btn.setFixedSize(24, 24)
        self.kofi_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: none;
                font-size: 20px;
            }
            QPushButton:hover {
                color: #FF5E5B;
            }
        """)
        self.kofi_btn.setToolTip("Support us on Ko-fi!")
        self.kofi_btn.clicked.connect(self.open_kofi)
        self.kofi_btn.setParent(self)
        self.kofi_btn.move(340, 8)

        # Drop zone / input area
        self.drop_zone = DropTextEdit(self)
        self.drop_zone.setPlaceholderText("Drop kernel deck JSON here\nor paste and click CHUNK...")
        self.drop_zone.setFixedHeight(120)
        self.drop_zone.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #aaa;
                border: 2px dashed #555;
                border-radius: 5px;
                font-family: Consolas, monospace;
                font-size: 10px;
                padding: 8px;
            }
            QTextEdit:focus {
                border-color: #FF9500;
            }
        """)
        main_layout.addWidget(self.drop_zone)

        # Button row
        btn_layout = QHBoxLayout()

        self.load_btn = QPushButton("LOAD")
        self.load_btn.setFixedHeight(35)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #aaa;
                border: 2px solid #555;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: #FF9500;
                border-color: #FF9500;
            }
        """)
        self.load_btn.clicked.connect(self.load_file)
        btn_layout.addWidget(self.load_btn)

        self.chunk_btn = QPushButton("CHUNK")
        self.chunk_btn.setFixedHeight(35)
        self.chunk_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9500;
                color: #000;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #FFa520;
            }
            QPushButton:pressed {
                background-color: #cc7700;
            }
        """)
        self.chunk_btn.clicked.connect(self.process_chunks)
        btn_layout.addWidget(self.chunk_btn)

        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setFixedHeight(35)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #888;
                border: 2px solid #555;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: #aaa;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)

        main_layout.addLayout(btn_layout)

        # Status label
        self.status_label = QLabel("Ready - Drop or paste a kernel deck")
        self.status_label.setStyleSheet("color: #888; font-size: 10px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Chunks scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #FF9500;
            }
        """)

        self.chunks_container = QWidget()
        self.chunks_layout = QVBoxLayout(self.chunks_container)
        self.chunks_layout.setContentsMargins(0, 0, 0, 0)
        self.chunks_layout.setSpacing(8)
        self.chunks_layout.addStretch()

        scroll.setWidget(self.chunks_container)
        main_layout.addWidget(scroll, 1)

        # Copy All button
        self.copy_all_btn = QPushButton("COPY ALL (Sequentially)")
        self.copy_all_btn.setFixedHeight(35)
        self.copy_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a4a2a;
                color: #00FF64;
                border: 2px solid #00AA44;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3a5a3a;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #555;
                border-color: #444;
            }
        """)
        self.copy_all_btn.clicked.connect(self.copy_next_chunk)
        self.copy_all_btn.setEnabled(False)
        main_layout.addWidget(self.copy_all_btn)

    def load_assets(self):
        assets_dir = Path(__file__).parent / "assets"
        yellow_path = assets_dir / "body_yellow.png"
        if yellow_path.exists():
            self.background_pixmap = QPixmap(str(yellow_path))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        self.draw_background(painter)
        self.draw_title(painter)
        self.draw_rivets(painter)
        self.draw_close_button(painter)
        self.draw_manufacturer_plate(painter)

    def draw_background(self, painter):
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), 8, 8)

        if self.background_pixmap and not self.background_pixmap.isNull():
            painter.setClipPath(path)
            scaled = self.background_pixmap.scaled(
                self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled)
        else:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(212, 160, 23))
            gradient.setColorAt(0.5, QColor(180, 136, 20))
            gradient.setColorAt(1, QColor(150, 113, 16))
            painter.fillPath(path, QBrush(gradient))

    def draw_title(self, painter):
        font = QFont("Arial Black", 12, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font)

        # Position next to top-left rivet (shifted right)
        rect = self.rect().adjusted(48, 22, -40, -self.height() + 49)

        # Shadow
        painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
        painter.drawText(rect.translated(1, 1), Qt.AlignmentFlag.AlignLeft, "KERNEL CHUNKER")

        # Highlight
        painter.setPen(QPen(QColor(255, 255, 255, 150), 1))
        painter.drawText(rect.translated(-1, -1), Qt.AlignmentFlag.AlignLeft, "KERNEL CHUNKER")

        # Main
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft, "KERNEL CHUNKER")

    def draw_rivets(self, painter):
        rivet_size = 4
        rivet_color = QColor(80, 80, 80)

        corners = [
            (5, 5), (self.width() - 9, 5),
            (5, self.height() - 9), (self.width() - 9, self.height() - 9)
        ]

        for x, y in corners:
            painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
            painter.drawEllipse(x + 1, y + 1, rivet_size, rivet_size)
            painter.setPen(QPen(rivet_color, 1))
            painter.setBrush(QBrush(rivet_color))
            painter.drawEllipse(x, y, rivet_size, rivet_size)

    def draw_close_button(self, painter):
        # Draw X button in top right
        x, y = self.width() - 25, 10
        size = 15

        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawLine(x, y, x + size, y + size)
        painter.drawLine(x + size, y, x, y + size)

    def draw_manufacturer_plate(self, painter):
        font = QFont("Arial", 6)
        painter.setFont(font)

        plate_rect = self.rect().adjusted(self.width() - 105, self.height() - 18, -5, -3)
        painter.fillRect(plate_rect, QBrush(QColor(40, 40, 40, 200)))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawRect(plate_rect)
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawText(plate_rect, Qt.AlignmentFlag.AlignCenter, "BLACK ORCHARD LABS")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking close button
            x, y = self.width() - 25, 10
            if x <= event.pos().x() <= x + 15 and y <= event.pos().y() <= y + 15:
                self.close()
                return

            # Start dragging
            if event.pos().y() < 40:
                self.is_dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def dragEnterEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls() or mime.hasText():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls() or mime.hasText():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                file_path = url.toLocalFile()
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            self.drop_zone.setText(content)
                            self.status_label.setText(f"Loaded: {Path(file_path).name}")
                        event.accept()
                        return
                    except Exception as e:
                        self.status_label.setText(f"Error: {e}")
        elif mime.hasText():
            self.drop_zone.setText(mime.text())
            event.accept()
            return
        event.ignore()

    def load_file(self):
        """Open file browser to load a kernel JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Kernel Deck",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.drop_zone.setText(content)
                    self.status_label.setText(f"Loaded: {Path(file_path).name}")
            except Exception as e:
                self.status_label.setText(f"Error: {e}")

    def chunk_single_kernel(self, kernel):
        """Split a single ETA/PRISM kernel into logical sections for sequential loading"""
        sections = []

        # 1. Header - identity info
        header = {}
        for key in ['id', 'title', 'version', 'extraction_date', 'source', 'deck_id', 'kernel_count', 'compression_ratio']:
            if key in kernel:
                header[key] = kernel[key]
        if header:
            sections.append({
                'section': 'header',
                'title': kernel.get('title', 'Header'),
                'id': kernel.get('id', 'unknown'),
                'data': header
            })

        # 2. Emotional Arc
        if 'emotional_arc' in kernel:
            sections.append({
                'section': 'emotional_arc',
                'title': 'Emotional Arc',
                'id': kernel.get('id', 'unknown'),
                'emotional_arc': kernel['emotional_arc']
            })

        # 3. Heat Signature
        if 'heat_signature' in kernel:
            sections.append({
                'section': 'heat_signature',
                'title': 'Heat Signature',
                'id': kernel.get('id', 'unknown'),
                'heat_signature': kernel['heat_signature']
            })

        # 4. Language & Motifs
        lang_motifs = {}
        if 'language_patterns' in kernel:
            lang_motifs['language_patterns'] = kernel['language_patterns']
        if 'motifs' in kernel:
            lang_motifs['motifs'] = kernel['motifs']
        if lang_motifs:
            sections.append({
                'section': 'language_motifs',
                'title': 'Language & Motifs',
                'id': kernel.get('id', 'unknown'),
                **lang_motifs
            })

        # 5. Physical Anchors
        if 'physical_anchors' in kernel:
            sections.append({
                'section': 'physical_anchors',
                'title': 'Physical Anchors',
                'id': kernel.get('id', 'unknown'),
                'physical_anchors': kernel['physical_anchors']
            })

        # 6. Visual Description (for visual ETA kernels)
        if 'visual_description' in kernel:
            sections.append({
                'section': 'visual_description',
                'title': 'Visual Description',
                'id': kernel.get('id', 'unknown'),
                'visual_description': kernel['visual_description']
            })

        # 7. Dynamics - consent, power, aftercare
        dynamics = {}
        for key in ['consent_pattern', 'power_dynamic', 'aftercare']:
            if key in kernel:
                dynamics[key] = kernel[key]
        if dynamics:
            sections.append({
                'section': 'dynamics',
                'title': 'Relationship Dynamics',
                'id': kernel.get('id', 'unknown'),
                **dynamics
            })

        # 8. Boundaries & Core Truth
        core = {}
        for key in ['pattern_boundaries', 'what_makes_it_work', 'core_truth', 'why_it_matters']:
            if key in kernel:
                core[key] = kernel[key]
        if core:
            sections.append({
                'section': 'core_truth',
                'title': 'Core Truth & Boundaries',
                'id': kernel.get('id', 'unknown'),
                **core
            })

        # 9. Cubic Attractor (identity system)
        if 'cubic_attractor' in kernel:
            sections.append({
                'section': 'cubic_attractor',
                'title': 'Cubic Attractor (Identity)',
                'id': kernel.get('id', 'unknown'),
                'cubic_attractor': kernel['cubic_attractor']
            })

        # 10. Export & Closing
        export = {}
        for key in ['replication_notes', 'export_notes', 'closing_image', 'heat_at_close', 'sigil']:
            if key in kernel:
                export[key] = kernel[key]
        if export:
            sections.append({
                'section': 'export',
                'title': 'Export Notes',
                'id': kernel.get('id', 'unknown'),
                **export
            })

        return sections if len(sections) > 1 else [kernel]

    def process_chunks(self):
        """Parse the kernel deck and create chunks"""
        text = self.drop_zone.toPlainText().strip()
        if not text:
            self.status_label.setText("No input - paste or drop a kernel deck")
            return

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            self.status_label.setText(f"Invalid JSON: {e}")
            return

        # Extract kernels
        kernels = []
        is_sectioned = False
        if isinstance(data, dict):
            if 'kernels' in data:
                kernels = data['kernels']
            elif 'id' in data and ('emotional_arc' in data or 'heat_signature' in data or 'cubic_attractor' in data):
                # Single ETA/PRISM kernel - split into sections
                kernels = self.chunk_single_kernel(data)
                is_sectioned = len(kernels) > 1
            else:
                self.status_label.setText("No kernels found in JSON")
                return
        elif isinstance(data, list):
            kernels = data
        else:
            self.status_label.setText("Unexpected JSON format")
            return

        if not kernels:
            self.status_label.setText("No kernels found")
            return

        # Clear existing chunks
        self.clear_chunks()

        # Create chunk cards
        self.chunks = kernels
        self.current_chunk_index = 0

        for i, kernel in enumerate(kernels, 1):
            card = ChunkCard(i, kernel)
            self.chunks_layout.insertWidget(self.chunks_layout.count() - 1, card)

        if is_sectioned:
            self.status_label.setText(f"Split into {len(kernels)} sections - copy sequentially for best results")
        else:
            self.status_label.setText(f"Found {len(kernels)} kernels - click COPY on each or use sequential copy")
        self.copy_all_btn.setEnabled(True)
        self.update_copy_all_button()

    def clear_chunks(self):
        """Clear all chunk cards"""
        while self.chunks_layout.count() > 1:
            item = self.chunks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def clear_all(self):
        """Clear everything"""
        self.drop_zone.clear()
        self.clear_chunks()
        self.chunks = []
        self.current_chunk_index = 0
        self.status_label.setText("Cleared - ready for new input")
        self.copy_all_btn.setEnabled(False)

    def copy_next_chunk(self):
        """Copy the next chunk in sequence"""
        if self.current_chunk_index >= len(self.chunks):
            # Reset all cards when starting over
            self.current_chunk_index = 0
            self.reset_all_cards()
            self.update_copy_all_button()
            self.status_label.setText("Reset - ready to copy again")
            return  # Don't copy yet, just reset

        if self.chunks:
            kernel = self.chunks[self.current_chunk_index]
            clipboard = QApplication.clipboard()
            clipboard.setText(json.dumps(kernel, indent=2))

            # Grey out the corresponding card
            self.grey_out_card(self.current_chunk_index)

            self.current_chunk_index += 1
            self.update_copy_all_button()

    def grey_out_card(self, index):
        """Grey out a specific card by index"""
        card_index = 0
        for i in range(self.chunks_layout.count()):
            item = self.chunks_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChunkCard):
                if card_index == index:
                    item.widget().copy_kernel()
                    break
                card_index += 1

    def reset_all_cards(self):
        """Reset all cards to uncoped state"""
        for i in range(self.chunks_layout.count()):
            item = self.chunks_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChunkCard):
                item.widget().reset_style()

    def update_copy_all_button(self):
        if self.chunks:
            remaining = len(self.chunks) - self.current_chunk_index
            if remaining <= 0:
                self.copy_all_btn.setText("START OVER")
            else:
                self.copy_all_btn.setText(f"COPY NEXT ({self.current_chunk_index + 1}/{len(self.chunks)})")

    def open_kofi(self):
        """Open Ko-fi support page in browser"""
        webbrowser.open(KOFI_URL)


def main():
    app = QApplication(sys.argv)

    # Set app style
    app.setStyle('Fusion')

    widget = KernelChunker()
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
