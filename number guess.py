import sys
import random
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QVBoxLayout, QWidget, QComboBox)
from PyQt6.QtCore import QPropertyAnimation, pyqtProperty, Qt, QTimer
from PyQt6.QtGui import QFont

class AnimatedLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opacity = 1.0

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.setStyleSheet(f"color: rgba(0, 0, 0, {value});")

class NumberGuessingGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.reset_game()

    def initUI(self):
        self.setWindowTitle("Number Guessing Game")
        self.setGeometry(100, 100, 500, 400)

        self.layout = QVBoxLayout()

        self.title = QLabel("Number Guessing Game", self)
        self.title.setFont(QFont('Arial', 24))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        self.difficulty_label = QLabel("Select Difficulty:", self)
        self.layout.addWidget(self.difficulty_label)

        self.difficulty_combo = QComboBox(self)
        self.difficulty_combo.addItems(["Easy (1-50)", "Medium (1-100)", "Hard (1-200)"])
        self.difficulty_combo.currentIndexChanged.connect(self.change_difficulty)
        self.layout.addWidget(self.difficulty_combo)

        self.input_label = QLabel("Guess a number:", self)
        self.layout.addWidget(self.input_label)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Enter your guess here")
        self.layout.addWidget(self.input)

        self.button = QPushButton("Guess", self)
        self.button.clicked.connect(self.check_guess)
        self.layout.addWidget(self.button)

        self.hint_button = QPushButton("Hint", self)
        self.hint_button.clicked.connect(self.give_hint)
        self.layout.addWidget(self.hint_button)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_game)
        self.layout.addWidget(self.reset_button)

        self.result = AnimatedLabel("", self)
        self.layout.addWidget(self.result)

        self.attempt_label = AnimatedLabel("Attempts: 0", self)
        self.layout.addWidget(self.attempt_label)

        self.high_score_label = QLabel("High Score: N/A", self)
        self.layout.addWidget(self.high_score_label)

        self.progress_label = QLabel("Progress:", self)
        self.layout.addWidget(self.progress_label)

        self.progress_bar = QLabel("", self)
        self.layout.addWidget(self.progress_bar)

        self.timer_label = QLabel("Time: 00:00", self)
        self.layout.addWidget(self.timer_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.time_start = 0

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.difficulty = 'Medium'
        self.update_difficulty_settings()

    def update_difficulty_settings(self):
        if self.difficulty == 'Easy':
            self.min_number = 1
            self.max_number = 50
        elif self.difficulty == 'Medium':
            self.min_number = 1
            self.max_number = 100
        elif self.difficulty == 'Hard':
            self.min_number = 1
            self.max_number = 200

    def change_difficulty(self):
        self.difficulty = self.difficulty_combo.currentText().split(' ')[0]
        self.update_difficulty_settings()
        self.reset_game()

    def check_guess(self):
        try:
            guess = int(self.input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")
            return

        if guess < self.min_number or guess > self.max_number:
            QMessageBox.warning(self, "Out of Range", f"Please enter a number between {self.min_number} and {self.max_number}.")
            return

        self.attempts += 1
        self.update_attempts()

        if guess < self.target_number:
            self.show_feedback("Too low! Try again.")
        elif guess > self.target_number:
            self.show_feedback("Too high! Try again.")
        else:
            self.show_feedback(f"Correct! You guessed it in {self.attempts} attempts.")
            self.button.setEnabled(False)
            self.timer.stop()
            self.update_high_score()

    def give_hint(self):
        if not hasattr(self, 'target_number'):
            QMessageBox.warning(self, "No Game Started", "Please start a game first.")
            return
        
        if self.attempts < 3:
            hint = "Try guessing closer to the middle of the range."
        else:
            diff = abs(self.target_number - int(self.input.text()))
            if diff <= 10:
                hint = "You're very close!"
            elif diff <= 20:
                hint = "You're close!"
            elif diff <= 30:
                hint = "You're getting there!"
            else:
                hint = "Keep trying!"
        
        QMessageBox.information(self, "Hint", hint)

    def show_feedback(self, message):
        self.result.setText(message)
        self.animate_opacity(self.result)

    def update_attempts(self):
        self.attempt_label.setText(f"Attempts: {self.attempts}")
        self.animate_opacity(self.attempt_label)
        self.update_progress_bar()

    def update_progress_bar(self):
        progress = int((self.attempts / (self.max_number - self.min_number + 1)) * 100)
        self.progress_bar.setText(f"[{'=' * (progress // 5)}{' ' * (20 - (progress // 5))}] {progress}%")
        self.progress_bar.setStyleSheet(f"background-color: lightblue; padding: 5px;")

    def update_timer(self):
        elapsed_time = int(time.time() - self.time_start)
        minutes, seconds = divmod(elapsed_time, 60)
        self.timer_label.setText(f"Time: {minutes:02}:{seconds:02}")

    def update_high_score(self):
        try:
            with open('high_score.txt', 'r') as f:
                high_score = int(f.read())
        except FileNotFoundError:
            high_score = float('inf')

        if self.attempts < high_score:
            with open('high_score.txt', 'w') as f:
                f.write(str(self.attempts))
            self.high_score_label.setText(f"High Score: {self.attempts}")
        else:
            self.high_score_label.setText(f"High Score: {high_score}")

    def animate_opacity(self, widget):
        animation = QPropertyAnimation(widget, b"opacity")
        animation.setDuration(1000)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()

    def reset_game(self):
        self.target_number = random.randint(self.min_number, self.max_number)
        self.attempts = 0
        self.result.setText("")
        self.update_attempts()
        self.input.clear()
        self.button.setEnabled(True)
        self.timer.start(1000)
        self.time_start = time.time()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NumberGuessingGame()
    ex.show()
    sys.exit(app.exec())
