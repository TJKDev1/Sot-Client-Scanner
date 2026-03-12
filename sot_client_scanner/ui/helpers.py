"""Reusable widget factory functions."""

from PySide6.QtWidgets import QLabel, QFrame


def make_value_label(text="—", color="#d4d4d8", size=12, bold=False):
    """Create a styled data-value label."""
    label = QLabel(text)
    weight = "bold" if bold else "normal"
    label.setStyleSheet(f"font-size: {size}px; color: {color}; font-weight: {weight}; padding: 2px 0;")
    label.setWordWrap(True)
    return label


def make_header_label(text, color="#71717a", size=10):
    """Create a small, dim header label."""
    label = QLabel(text)
    label.setStyleSheet(f"font-size: {size}px; color: {color}; font-weight: bold; padding: 0; margin: 0;")
    return label


def make_separator():
    """Create a thin horizontal line separator."""
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet("background-color: #1e2733; max-height: 1px; margin: 6px 0;")
    return line
