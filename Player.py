import pygame
import tkinter as tk
from tkinter import filedialog, simpledialog
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
from io import BytesIO
import requests
import urllib.parse
import math  # <-- Importiere das 'math'-Modul für Sinus-Funktionen

# Fenster-Dimensionen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

class AudioPlayer:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Audio Player")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 30)

        self.file_path = None
        self.is_playing = False
        self.is_paused = False
        self.song_info = {"title": "Kein Titel", "artist": "Kein Interpret", "album": "Kein Album"}
        self.cover_image = None
        self.background_image = None
        self.playlist = []
        self.current_track_index = -1

        # NEU: Variable für den Farbverlauf
        self.gradient_phase = 0

        # NEU: Event für das Ende eines Liedes
        self.SONG_END = pygame.USEREVENT + 1

        # UI-Elemente
        self.btn_select = pygame.Rect(40, 300, 100, 40)
        self.btn_play_pause = pygame.Rect(150, 300, 120, 40)
        self.btn_stop = pygame.Rect(280, 300, 100, 40)
        self.btn_next = pygame.Rect(390, 300, 80, 40)
        self.btn_prev = pygame.Rect(480, 300, 80, 40)
        self.btn_bg_select = pygame.Rect(40, 350, 160, 40)
        self.btn_save_playlist = pygame.Rect(210, 350, 160, 40)

    def search_for_cover(self, artist, album):
        """Sucht online nach einem Album-Cover und gibt es als Pygame-Image zurück."""
        try:
            search_term = urllib.parse.quote(f"{artist} {album}")
            search_url = f"https://itunes.apple.com/search?term={search_term}&media=music&entity=album&limit=1"
            response = requests.get(search_url)
            data = response.json()

            if data['resultCount'] > 0:
                artwork_url = data['results'][0]['artworkUrl100']
                high_res_url = artwork_url.replace("100x100bb", "600x600bb")

                response_image = requests.get(high_res_url, stream=True)
                if response_image.status_code == 200:
                    image_data = BytesIO(response_image.content)
                    return pygame.image.load(image_data)
        except Exception as e:
            print(f"Fehler bei der Online-Suche nach Cover: {e}")
        return None

    def get_audio_info(self, file_path):
        """Liest ID3-Tags und Coverbild aus der Datei oder sucht online danach."""
        self.cover_image = None
        self.song_info = {"title": "Lade...", "artist": "Lade...", "album": "Lade..."}

        # 1. Versuche, Metadaten aus der Datei zu lesen
        if file_path.lower().endswith('.mp3'):
            try:
                audio = ID3(file_path)
                self.song_info["title"] = audio.get("TIT2", ["Unbekannter Titel"])[0]
                self.song_info["artist"] = audio.get("TPE1", ["Unbekannter Interpret"])[0]
                self.song_info["album"] = audio.get("TALB", ["Unbekanntes Album"])[0]

                if 'APIC:' in audio:
                    apic_data = audio['APIC:'].data
                    image_stream = BytesIO(apic_data)
                    self.cover_image = pygame.image.load(image_stream)
                    self.cover_image = pygame.transform.scale(self.cover_image, (200, 200))
            except Exception as e:
                print(f"Fehler beim Lesen der Metadaten aus Datei: {e}")
        else:
            self.song_info = {"title": os.path.basename(file_path), "artist": "N/A", "album": "N/A"}

        # 2. Wenn kein Cover gefunden wurde, suche online danach
        if self.cover_image is None and self.song_info["artist"] != "N/A" and self.song_info["album"] != "N/A":
            print("Kein eingebettetes Cover gefunden. Suche online...")
            found_cover = self.search_for_cover(self.song_info["artist"], self.song_info["album"])
            if found_cover:
                self.cover_image = pygame.transform.scale(found_cover, (200, 200))
                print("Online-Cover erfolgreich geladen.")
            else:
                print("Kein Online-Cover gefunden.")

    def draw_text(self, text, rect, color=BLACK, font_size=24):
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_ui(self):
        if self.background_image:
            self.screen.blit(pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        else:
            self.screen.fill(WHITE)

        # Überprüfe, ob ein Coverbild vorhanden ist
        if self.cover_image:
            # Das Coverbild wird jetzt 150 Pixel vom rechten Rand zentriert
            cover_rect = self.cover_image.get_rect(center=(SCREEN_WIDTH - 150, 140))
            self.screen.blit(self.cover_image, cover_rect)
        else:
            # Zeichne einen grauen Platzhalter, wenn kein Bild vorhanden ist
            placeholder_rect = pygame.Rect(SCREEN_WIDTH - 250, 40, 200, 200)
            pygame.draw.rect(self.screen, GRAY, placeholder_rect)

        # NEU: Berechne die RGB-Farbwerte basierend auf der aktuellen Phase
        red = (math.sin(self.gradient_phase + 0) * 127 + 128)
        green = (math.sin(self.gradient_phase + 2) * 127 + 128)
        blue = (math.sin(self.gradient_phase + 4) * 127 + 128)
        rgb_gradient_color = (int(red), int(green), int(blue))

        # Song-Informationen anzeigen (jetzt mit Farbverlauf)
        title_text = f"Titel: {self.song_info['title']}"
        artist_text = f"Interpret: {self.song_info['artist']}"
        album_text = f"Album: {self.song_info['album']}"

        title_surface = self.big_font.render(title_text, True, rgb_gradient_color)
        artist_surface = self.font.render(artist_text, True, rgb_gradient_color)
        album_surface = self.font.render(album_text, True, rgb_gradient_color)

        self.screen.blit(title_surface, (20, 20))
        self.screen.blit(artist_surface, (20, 50))
        self.screen.blit(album_surface, (20, 80))

        # Tasten zeichnen
        pygame.draw.rect(self.screen, GRAY, self.btn_select)
        pygame.draw.rect(self.screen, GRAY, self.btn_play_pause)
        pygame.draw.rect(self.screen, GRAY, self.btn_stop)
        pygame.draw.rect(self.screen, GRAY, self.btn_next)
        pygame.draw.rect(self.screen, GRAY, self.btn_prev)
        pygame.draw.rect(self.screen, GRAY, self.btn_bg_select)
        pygame.draw.rect(self.screen, GRAY, self.btn_save_playlist)

        self.draw_text("Dateien laden", self.btn_select, color=RED, font_size=20)
        self.draw_text("Pause" if self.is_playing else "Play", self.btn_play_pause, color=RED)
        self.draw_text("Stopp", self.btn_stop, color=RED)
        self.draw_text("Nächstes", self.btn_next, color=RED)
        self.draw_text("Vorheriges", self.btn_prev, color=RED)
        self.draw_text("Hintergrund", self.btn_bg_select, color=RED, font_size=20)
        self.draw_text("Playlist sichern", self.btn_save_playlist, color=RED, font_size=20)

    def select_file(self):
        """Wählt eine oder mehrere Dateien aus und fügt sie zur Playlist hinzu."""
        self.stop()
        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames(
            title="Wähle Dateien zur Playlist-Ergänzung aus",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
        )
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.playlist:
                    self.playlist.append(file_path)
                    print(f"'{os.path.basename(file_path)}' zur Playlist hinzugefügt.")

            print(f"Playlist hat jetzt {len(self.playlist)} Lieder.")

            if not self.is_playing:
                self.current_track_index = 0
                self.file_path = self.playlist[self.current_track_index]
                self.get_audio_info(self.file_path)
                pygame.mixer.music.load(self.file_path)
                self.play_pause()

    def select_bg_image(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Wähle ein Hintergrundbild aus",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            try:
                self.background_image = pygame.image.load(file_path).convert()
            except pygame.error as e:
                print(f"Fehler beim Laden des Bildes: {e}")

    def save_playlist(self):
        if not self.playlist:
            print("Playlist ist leer. Nichts zu speichern.")
            return

        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            title="Speichere die Playlist",
            defaultextension=".m3u",
            filetypes=[("Playlist Files", "*.m3u"), ("Text Files", "*.txt")]
        )
        if file_path:
            with open(file_path, 'w') as f:
                for track in self.playlist:
                    f.write(track + '\n')
            print(f"Playlist erfolgreich unter '{file_path}' gespeichert.")

    def next_track(self):
        if not self.playlist: return
        self.stop()
        self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        self.file_path = self.playlist[self.current_track_index]
        self.get_audio_info(self.file_path)
        pygame.mixer.music.load(self.file_path)
        self.play_pause()

    def prev_track(self):
        if not self.playlist: return
        self.stop()
        self.current_track_index = (self.current_track_index - 1 + len(self.playlist)) % len(self.playlist)
        self.file_path = self.playlist[self.current_track_index]
        self.get_audio_info(self.file_path)
        pygame.mixer.music.load(self.file_path)
        self.play_pause()

    def play_pause(self):
        if self.file_path:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.is_playing = True
            elif self.is_playing:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.is_playing = False
            else:
                # NEU: Setze das Event, das beim Ende des Songs ausgelöst wird
                pygame.mixer.music.set_endevent(self.SONG_END)
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False

    def stop(self):
        if self.is_playing or self.is_paused:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False

    def run(self):
        running = True
        while running:
            # NEU: Aktualisiere die Phase für den Farbverlauf
            self.gradient_phase += 0.01

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.btn_select.collidepoint(event.pos):
                        self.select_file()
                    elif self.btn_play_pause.collidepoint(event.pos):
                        self.play_pause()
                    elif self.btn_stop.collidepoint(event.pos):
                        self.stop()
                    elif self.btn_next.collidepoint(event.pos):
                        self.next_track()
                    elif self.btn_prev.collidepoint(event.pos):
                        self.prev_track()
                    elif self.btn_bg_select.collidepoint(event.pos):
                        self.select_bg_image()
                    elif self.btn_save_playlist.collidepoint(event.pos):
                        self.save_playlist()

                # NEU: Wenn das Lied endet, spiele den nächsten Track
                elif event.type == self.SONG_END:
                    self.next_track()

            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    player = AudioPlayer()
    player.run()