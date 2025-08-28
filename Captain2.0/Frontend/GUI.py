from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
old_chat_message = ""

# Directory paths
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

# ---------- small helpers ----------

def ensure_dirs_and_defaults():
    """Make sure Frontend/Files exists and Mic.data has a sane default."""
    os.makedirs(TempDirPath, exist_ok=True)
    mic_file = TempDirectoryPath('Mic.data')
    if not os.path.exists(mic_file):
        # default to muted on first run
        with open(mic_file, 'w', encoding='utf-8') as f:
            f.write("False")
    status_file = TempDirectoryPath('Status.data')
    if not os.path.exists(status_file):
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write("")

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words  = new_query.split()
    question_words = ['how','what','who','where','when','why','which','whom','can you',"what's", "where's","how's"]
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'
    return new_query.capitalize()

def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}\{Filename}'

def TempDirectoryPath(Filename):
    return rf'{TempDirPath}\{Filename}'

def ShowTextToScreen(Text):
    with open (rf'{TempDirPath}\Responses.data','w', encoding='utf-8') as file:
        file.write(Text)

# ---------- mic status I/O ----------

def SetMicrophoneStatus(value: str):
    # value must be "True" or "False"
    with open(TempDirectoryPath('Mic.data'), 'w', encoding='utf-8') as file:
        file.write(value)

def GetMicrophoneStatus() -> str:
    try:
        with open(TempDirectoryPath('Mic.data'), 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        # default to muted if file missing
        return "False"

def SetAsssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data','w',encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    try:
        with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ""

# Manual control functions (kept simple; GUI handles icons)
def MicButtonInitiated():
    SetMicrophoneStatus("True")

def MicButtonClosed():
    SetMicrophoneStatus("False")

# ---------- UI parts ----------

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(rf"{GraphicsDirPath}\Jarvis.gif")
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)  # no need for 5ms; 100ms is plenty

        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
            }
            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(rf'{TempDirPath}\Responses.data', 'r', encoding='utf-8') as file:
                messages = file.read()
            if messages and messages != old_chat_message:
                self.addMessage(message=messages, color='White')
                old_chat_message = messages
        except FileNotFoundError:
            pass

    def SpeechRecogText(self):
        try:
            with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
                messages = file.read()
            self.label.setText(messages)
        except FileNotFoundError:
            pass

    # (the icon functions in ChatSection are not used; leaving them harmless)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        # self.icon_label may not exist in this widget; kept for backward compat

    def toggle_icon(self, event=None):
        # not used in ChatSection
        pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):
    """
    Home screen with mic icon that reflects Mic.data and toggles it.
    Also auto-updates when wake word flips Mic.data from backend.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # GIF
        gif_label = QLabel()
        movie = QMovie(GraphicsDirPath + r'\Jarvis.gif')
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Mic icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # click-to-toggle
        self.icon_label.mousePressEvent = self._on_icon_click

        # First draw based on file
        self._apply_icon_from_status(GetMicrophoneStatus())

        # Status label
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-bottom: 0;")

        # Layout
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)

        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        # Timers: status text & mic icon polling
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_status_text)
        self.status_timer.start(100)

        self.mic_poll_timer = QTimer(self)
        self.mic_poll_timer.timeout.connect(self._poll_mic_and_update_icon)
        self.mic_poll_timer.start(200)

        self._last_mic_state = GetMicrophoneStatus()

    def _on_icon_click(self, event=None):
        # Toggle mic state
        current = GetMicrophoneStatus()
        if current == "True":
            MicButtonClosed()
            new_state = "False"
        else:
            MicButtonInitiated()
            new_state = "True"
        self._apply_icon_from_status(new_state)
        self._last_mic_state = new_state

    def _apply_icon_from_status(self, mic_state: str):
        # Choose icon by state
        icon_file = 'Mic_on.png' if mic_state == "True" else 'Mic_off.png'
        pixmap = QPixmap(GraphicsDirectoryPath(icon_file)).scaled(
            60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.icon_label.setPixmap(pixmap)

    def _poll_mic_and_update_icon(self):
        # If some other process changed Mic.data, reflect it
        current = GetMicrophoneStatus()
        if current != self._last_mic_state:
            self._apply_icon_from_status(current)
            self._last_mic_state = current

    def _update_status_text(self):
        try:
            with open(TempDirPath + r'\Status.data', 'r', encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except FileNotFoundError:
            pass


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.current_screen = None
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirPath + r'\Home.png')
        home_button.setIcon(home_icon)
        home_button.setText("   Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black")
        home_button.clicked.connect(self.showInitialScreen)

        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirPath + r'\Message.png')
        message_button.setIcon(message_icon)
        message_button.setText("   Message")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black")
        message_button.clicked.connect(self.showMessageScreen)

        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirPath + r'\Minimize.png')
        minimize_button.setIcon(minimize_icon)
        minimize_button.setFlat(True)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirPath + r'\Maximize.png')
        self.restore_icon = QIcon(GraphicsDirPath + r'\Restore.png')
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirPath + r'\Close.png')
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def showMessageScreen(self):
        self.stacked_widget.setCurrentIndex(1)

    def showInitialScreen(self):
        self.stacked_widget.setCurrentIndex(0)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        ensure_dirs_and_defaults()  # make sure files & defaults exist
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
