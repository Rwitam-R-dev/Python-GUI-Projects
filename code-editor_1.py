import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QFileDialog, QMessageBox,
    QVBoxLayout, QWidget, QMenuBar, QMenu, QPushButton, QSplitter
)
from PySide6.QtGui import QKeySequence, QAction, QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor
from PySide6.QtCore import Qt, QRegularExpression, QPoint, QRect

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define text formats for different types of syntax
        self.highlighting_rules = []

        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("blue"))
        keywords = ["def", "class", "import", "from", "return", "if", "elif", "else", "for", "while", "break", "continue", "try", "except", "finally", "with"]
        self.highlighting_rules += [(QRegularExpression(f"\\b{keyword}\\b"), keyword_format) for keyword in keywords]

        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("green"))
        self.highlighting_rules.append((QRegularExpression('".*?"'), string_format))
        self.highlighting_rules.append((QRegularExpression("'.*?'"), string_format))

        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("gray"))
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            index = expression.match(text).capturedStart()
            while index >= 0:
                length = expression.match(text).capturedLength()
                self.setFormat(index, length, format)
                index = expression.match(text, index + length).capturedStart()

class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Editor")
        self.setGeometry(100, 100, 800, 600)
        
        self.init_ui()
        self.init_menu()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2e2e2e;
            }
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                border: 1px solid #444;
                font-family: Courier New;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14pt;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
            QMenuBar {
                background-color: #333;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QMenu {
                background-color: #333;
                color: white;
            }
            QMenu::item:selected {
                background-color: #555;
            }
        """)

    def init_ui(self):
        self.splitter = QSplitter(Qt.Horizontal, self)
        
        self.text_area = QPlainTextEdit(self)
        self.output_area = QPlainTextEdit(self)
        self.output_area.setReadOnly(True)

        # Apply syntax highlighting to text_area
        self.highlighter = PythonHighlighter(self.text_area.document())

        self.splitter.addWidget(self.text_area)
        self.splitter.addWidget(self.output_area)
        
        self.run_button = QPushButton("Run Code", self)
        self.run_button.clicked.connect(self.run_code)

        layout = QVBoxLayout()
        layout.addWidget(self.splitter)
        layout.addWidget(self.run_button)
        layout.setStretch(0, 3)
        layout.setStretch(1, 0)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("File")
        
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_editor)
        file_menu.addAction(exit_action)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)")
        if file_path:
            try:
                with open(file_path, "r") as file:
                    self.text_area.setPlainText(file.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)")
        if file_path:
            try:
                with open(file_path, "w") as file:
                    file.write(self.text_area.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def exit_editor(self):
        if QMessageBox.question(self, "Quit", "Do you want to quit?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.close()

    def run_code(self):
        code = self.text_area.toPlainText()
        try:
            process = subprocess.Popen(
                [sys.executable, '-c', code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            self.output_area.setPlainText(stdout.decode('utf-8') + stderr.decode('utf-8'))
        except Exception as e:
            self.output_area.setPlainText(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = CodeEditor()
    editor.show()
    sys.exit(app.exec())
