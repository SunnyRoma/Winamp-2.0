import sys
import os
import pygame
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QListWidget, QLabel, 
                           QSlider, QFileDialog, QMessageBox, QFrame, QMenu)
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QAction

class WinampButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(23, 14)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                border: 1px solid #000000;
                color: #c0c0c0;
                font-size: 8pt;
            }
            QPushButton:hover {
                background-color: #3b3b3b;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """)

class WinampSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #000000;
                height: 3px;
                background: #2b2b2b;
                margin: 0px;
            }
            QSlider::handle:horizontal {
                background: #c0c0c0;
                border: 1px solid #000000;
                width: 6px;
                height: 10px;
                margin: -3px 0;
            }
        """)

class Visualization(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.bars = [0] * 32
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_bars)
        self.timer.start(50)  # Update every 50ms
        
    def update_bars(self):
        if pygame.mixer.music.get_busy():
            for i in range(len(self.bars)):
                self.bars[i] = max(0, self.bars[i] - 1)
                if random.random() < 0.3:
                    self.bars[i] = random.randint(10, 60)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        width = self.width() / len(self.bars)
        for i, height in enumerate(self.bars):
            x = int(i * width)
            gradient = QLinearGradient(x, self.height(), x, self.height() - height)
            gradient.setColorAt(0, QColor(0, 255, 0))
            gradient.setColorAt(1, QColor(255, 255, 0))
            painter.fillRect(QRect(x, int(self.height() - height), int(width - 1), int(height)), QBrush(gradient))

class WinampFrame(QFrame):
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0x33, 0x33, 0x33))
        gradient.setColorAt(1, QColor(0x22, 0x22, 0x22))
        painter.fillRect(self.rect(), QBrush(gradient))

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Winamp 2.0")
        self.setFixedSize(275, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Variables
        self.current_song = None
        self.playlist = []
        self.paused = False
        self.volume = 0.7
        self.song_length = 0
        self.current_position = 0
        pygame.mixer.music.set_volume(self.volume)
        
        # Create timer for updating position
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(1000)
        
        # Create main frame
        main_frame = WinampFrame()
        self.setCentralWidget(main_frame)
        layout = QVBoxLayout(main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(14)
        title_bar.setStyleSheet("background-color: #000000;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(5, 0, 5, 0)
        
        title_label = QLabel("Winamp 2.0")
        title_label.setStyleSheet("color: #c0c0c0; font-size: 8pt;")
        title_layout.addWidget(title_label)
        
        close_button = WinampButton("X")
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button)
        
        layout.addWidget(title_bar)
        
        # Main content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(2)
        
        # Visualization
        self.visualization = Visualization()
        content_layout.addWidget(self.visualization)
        
        # Time display
        time_layout = QHBoxLayout()
        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet("color: #c0c0c0; font-size: 8pt;")
        time_layout.addWidget(self.time_label)
        
        self.time_slider = WinampSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.sliderMoved.connect(self.set_position)
        time_layout.addWidget(self.time_slider)
        
        self.duration_label = QLabel("00:00")
        self.duration_label.setStyleSheet("color: #c0c0c0; font-size: 8pt;")
        time_layout.addWidget(self.duration_label)
        
        content_layout.addLayout(time_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)
        
        self.prev_button = WinampButton("|<")
        self.prev_button.clicked.connect(self.prev_song)
        button_layout.addWidget(self.prev_button)
        
        self.play_button = WinampButton(">")
        self.play_button.clicked.connect(self.play_music)
        button_layout.addWidget(self.play_button)
        
        self.pause_button = WinampButton("||")
        self.pause_button.clicked.connect(self.pause_music)
        button_layout.addWidget(self.pause_button)
        
        self.stop_button = WinampButton("[]")
        self.stop_button.clicked.connect(self.stop_music)
        button_layout.addWidget(self.stop_button)
        
        self.next_button = WinampButton(">|")
        self.next_button.clicked.connect(self.next_song)
        button_layout.addWidget(self.next_button)
        
        content_layout.addLayout(button_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(2)
        
        volume_label = QLabel("Vol:")
        volume_label.setStyleSheet("color: #c0c0c0; font-size: 8pt;")
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = WinampSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.volume * 100))
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        
        content_layout.addLayout(volume_layout)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #c0c0c0; font-size: 8pt;")
        content_layout.addWidget(self.status_label)
        
        # Playlist
        self.playlist_widget = QListWidget()
        self.playlist_widget.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #000000;
                color: #c0c0c0;
                font-size: 8pt;
            }
            QListWidget::item {
                padding: 2px;
            }
            QListWidget::item:selected {
                background-color: #4a4a4a;
                color: #ffffff;
            }
        """)
        self.playlist_widget.itemClicked.connect(self.play_selected)
        content_layout.addWidget(self.playlist_widget)
        
        layout.addWidget(content)
        
        # Make window draggable
        self.dragging = False
        self.offset = None
        
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        add_action = QAction("Add Song", self)
        add_action.triggered.connect(self.add_song)
        menu.addAction(add_action)
        menu.exec(event.globalPos())
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()
            
    def mouseMoveEvent(self, event):
        if self.dragging and self.offset is not None:
            self.move(self.mapToGlobal(event.position().toPoint() - self.offset))
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.offset = None
            
    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
        
    def update_position(self):
        if pygame.mixer.music.get_busy() and self.current_song:
            self.current_position = pygame.mixer.music.get_pos() / 1000
            self.time_label.setText(self.format_time(self.current_position))
            if self.song_length > 0:
                self.time_slider.setValue(int((self.current_position / self.song_length) * 100))
        
    def set_position(self, value):
        if self.current_song and self.song_length > 0:
            position = (value / 100) * self.song_length
            # Store current playback state
            was_playing = pygame.mixer.music.get_busy()
            # Stop current playback
            pygame.mixer.music.stop()
            # Load the song again
            pygame.mixer.music.load(self.current_song)
            # Start playing from the new position
            pygame.mixer.music.play(start=int(position))
            # If it was paused before seeking, pause it again
            if not was_playing:
                pygame.mixer.music.pause()
            self.current_position = position
            self.time_label.setText(self.format_time(position))
            self.paused = not was_playing
        
    def set_volume(self, value):
        self.volume = value / 100.0
        pygame.mixer.music.set_volume(self.volume)
        
    def add_song(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Songs",
            "",
            "MP3 files (*.mp3);;All files (*.*)"
        )
        for file in files:
            self.playlist.append(file)
            self.playlist_widget.addItem(os.path.basename(file))
            
    def prev_song(self):
        if not self.playlist:
            return
        if self.current_song is None:
            self.current_song = self.playlist[0]
        else:
            current_index = self.playlist.index(self.current_song)
            if current_index > 0:
                self.current_song = self.playlist[current_index - 1]
            else:
                self.current_song = self.playlist[-1]
        self.play_selected(None)
            
    def next_song(self):
        if not self.playlist:
            return
        if self.current_song is None:
            self.current_song = self.playlist[0]
        else:
            current_index = self.playlist.index(self.current_song)
            if current_index < len(self.playlist) - 1:
                self.current_song = self.playlist[current_index + 1]
            else:
                self.current_song = self.playlist[0]
        self.play_selected(None)
            
    def play_music(self):
        if not self.playlist:
            QMessageBox.warning(self, "Warning", "Please add songs to the playlist first!")
            return
            
        if self.current_song is None:
            self.current_song = self.playlist[0]
            pygame.mixer.music.load(self.current_song)
            
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.music.play()
            
        sound = pygame.mixer.Sound(self.current_song)
        self.song_length = sound.get_length()
        self.duration_label.setText(self.format_time(self.song_length))
        self.time_slider.setValue(0)
            
        self.status_label.setText(os.path.basename(self.current_song))
        
    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True
            self.status_label.setText("Paused")
            
    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_song = None
        self.paused = False
        self.current_position = 0
        self.time_slider.setValue(0)
        self.time_label.setText("00:00")
        self.status_label.setText("Stopped")
        
    def play_selected(self, item):
        if item is None:
            index = self.playlist.index(self.current_song)
        else:
            index = self.playlist_widget.row(item)
        self.current_song = self.playlist[index]
        pygame.mixer.music.load(self.current_song)
        pygame.mixer.music.play()
        
        sound = pygame.mixer.Sound(self.current_song)
        self.song_length = sound.get_length()
        self.duration_label.setText(self.format_time(self.song_length))
        self.time_slider.setValue(0)
        
        self.status_label.setText(os.path.basename(self.current_song))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec())
