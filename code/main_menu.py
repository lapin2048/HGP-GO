from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QPalette, QBrush, QPixmap, QPen, QColor, QPainter

class Menu(QWidget):
    newGameSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the initial background image
        self.image_path = "../Assets/go_menu_background.png"  # Replace with your image path
        self.setAutoFillBackground(True)
        self.updateBackgroundImage()

        layout = QVBoxLayout()

        # Spacer to center content vertically
        layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        # Welcome label
        label = OutlinedLabel("Welcome to the Go Game!", outline_width=2)
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(label)

        # Add a space between the label and the buttons
        layout.addSpacing(20)

        # "New Game" button
        button_new_game = QPushButton("New Game")
        button_new_game.setToolTip("Start a new Go game")
        button_new_game.clicked.connect(self.newGameSignal.emit)
        button_new_game.setStyleSheet(
            "font-size: 16px; padding: 10px; background-color: #5cb85c; color: white; border-radius: 5px;"
        )
        button_new_game.setMaximumSize(500, 500)  # Set max width and height
        layout.addWidget(button_new_game, alignment=Qt.AlignmentFlag.AlignCenter)

        # "How to Play" button
        button_rules = QPushButton("How to Play")
        button_rules.setToolTip("Learn the rules of Go")
        button_rules.clicked.connect(self.showRules)
        button_rules.setStyleSheet(
            "font-size: 16px; padding: 10px; background-color: #0275d8; color: white; border-radius: 5px;"
        )
        button_rules.setMaximumSize(500, 500)  # Set max width and height
        layout.addWidget(button_rules, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer to center content vertically
        layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        self.setLayout(layout)

    def updateBackgroundImage(self):
        """Updates the background image dynamically."""
        palette = QPalette()
        pixmap = QPixmap(self.image_path)

        # Scale the image to fit the current window size
        pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)

        palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
        self.setPalette(palette)

    def resizeEvent(self, event):
        """Handles the window resize event to update the background."""
        self.updateBackgroundImage()
        super().resizeEvent(event)

    def showRules(self):
        """Display a dialog with the rules of Go."""
        rules = (
            "Rules of Go:\n"
            "1. Go is a territory control game played between Black and White.\n\n"
            "2. The game is played on a Goban (a square grid board), typically 9x9 here.\n\n"
            "3. Players take turns placing stones on free intersections.\n\n"
            "4. Stones are captured when completely surrounded by opponent's stones.\n\n"
            "5. The winner is determined by the player controlling the most territory and capturing the most stones.\n\n"
            "6. The game ends when both players pass consecutively."
        )
        QMessageBox.information(self, "Rules of Go", rules)

    def sizeHint(self):
        """Define a preferred size for the window."""
        return QSize(500, 300)

class OutlinedLabel(QLabel):
    def __init__(self, text, outline_width=4, parent=None):
        super().__init__(parent)
        self.text = text
        self.outline_width = outline_width  # Set outline width
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def paintEvent(self, event):
        """Custom painting for the label to add an outline."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = painter.font()
        font.setPointSize(24)  # Set font size
        font.setBold(True)  # Set font bold
        painter.setFont(font)

        # Draw the outline by drawing text offset in multiple directions
        outline_color = QColor("black")
        painter.setPen(outline_color)
        for dx in range(-self.outline_width, self.outline_width + 1):
            for dy in range(-self.outline_width, self.outline_width + 1):
                if dx != 0 or dy != 0:  # Skip the center
                    painter.drawText(self.rect().adjusted(dx, dy, dx, dy), Qt.AlignmentFlag.AlignCenter, self.text)

        # Draw the main text
        text_color = QColor("white")
        painter.setPen(text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)

        painter.end()
