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


class Menu(QWidget):
    newGameSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Spacer to center content vertically
        layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        # Welcome label
        label = QLabel("Welcome to the Go Game!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
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
        layout.addWidget(button_new_game)

        # "How to Play" button
        button_rules = QPushButton("How to Play")
        button_rules.setToolTip("Learn the rules of Go")
        button_rules.clicked.connect(self.showRules)
        button_rules.setStyleSheet(
            "font-size: 16px; padding: 10px; background-color: #0275d8; color: white; border-radius: 5px;"
        )
        layout.addWidget(button_rules)

        # Spacer to center content vertically
        layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        self.setLayout(layout)

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
