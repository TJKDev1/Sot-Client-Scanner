"""Application-wide dark stylesheet."""

DARK_STYLE = """
QMainWindow {
    background-color: #0d1117;
}
QWidget {
    background-color: #0d1117;
    color: #d4d4d8;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}
QGroupBox {
    background-color: #13171e;
    border: 1px solid #1e2733;
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    margin-top: 18px;
    padding: 14px 10px 10px 10px;
    font-size: 11px;
    font-weight: 600;
    color: #a1a1aa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 3px 10px;
    background-color: #13171e;
    border: 1px solid #1e2733;
    border-radius: 6px;
    color: #e4e4e7;
    font-size: 11px;
    letter-spacing: 0.5px;
}
QPushButton {
    background-color: #1c2028;
    color: #d4d4d8;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #27272a;
    border-color: #3b82f6;
    color: #f4f4f5;
}
QPushButton:pressed {
    background-color: #0d1117;
}
QPushButton:disabled {
    background-color: #13171e;
    color: #3f3f46;
    border-color: #1e2733;
}
QPushButton#startBtn {
    background-color: #166534;
    border-color: #22c55e;
    color: #ffffff;
    font-size: 13px;
}
QPushButton#startBtn:hover {
    background-color: #15803d;
    border-color: #4ade80;
}
QPushButton#startBtn:disabled {
    background-color: #0f291a;
    border-color: #0f291a;
    color: #2d5a3e;
}
QPushButton#stopBtn {
    background-color: #991b1b;
    border-color: #ef4444;
    color: #ffffff;
    font-size: 13px;
}
QPushButton#stopBtn:hover {
    background-color: #b91c1c;
    border-color: #f87171;
}
QPushButton#stopBtn:disabled {
    background-color: #1c0d0e;
    border-color: #1c0d0e;
    color: #5c2d30;
}
QTextEdit {
    background-color: #0a0e14;
    color: #a3e635;
    border: 1px solid #1e2733;
    border-radius: 6px;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    padding: 6px;
    selection-background-color: #1e3a5f;
    line-height: 1.4;
}
QLabel {
    background-color: transparent;
    border: none;
}
QTabWidget::pane {
    border: 1px solid #1e2733;
    background-color: #13171e;
    border-radius: 6px;
    padding: 2px;
}
QTabBar::tab {
    background-color: #1c2028;
    color: #71717a;
    border: 1px solid #1e2733;
    border-bottom: none;
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background-color: #13171e;
    color: #e4e4e7;
    font-weight: 700;
    border-bottom: 2px solid #3b82f6;
}
QTabBar::tab:hover {
    background-color: #27272a;
    color: #d4d4d8;
}
QProgressBar {
    background-color: #1c2028;
    border: 1px solid #1e2733;
    border-radius: 4px;
    height: 16px;
    text-align: center;
    font-size: 9px;
    color: #d4d4d8;
}
QProgressBar::chunk {
    border-radius: 3px;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background: #0d1117;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #27272a;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #3f3f46;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #0d1117;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #27272a;
    border-radius: 4px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
    background: #3f3f46;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QSplitter::handle {
    background-color: #1e2733;
    height: 3px;
    border-radius: 1px;
}
"""
