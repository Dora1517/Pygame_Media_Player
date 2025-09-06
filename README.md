# Pygame_Media_Player
A MP3 Player was writen in Paygame

This project is a feature-rich audio player developed in Python, leveraging the Pygame library for its graphical user interface (GUI) and audio playback functionalities. It's designed to provide a comprehensive and visually engaging music experience on a desktop environment.

The application allows users to build and manage a playlist by loading multiple audio files, including MP3s, WAVs, and Oggs, via a simple file dialog. The player automatically extracts and displays song metadata, such as title, artist, and album, from the ID3 tags of the loaded files. If a file lacks embedded cover art, the application can intelligently search for and download album covers online to enhance the visual presentation.

Beyond standard controls (play, pause, stop, next, and previous), the player includes several advanced features:

Automatic Playback: Songs in the playlist are designed to play one after another without manual intervention.

Dynamic RGB Gradient: The song information text animates with a smooth, continuous RGB color gradient, providing a modern and dynamic visual effect.

Customization: Users can personalize the interface by selecting and applying a custom background image.

Built to be a self-contained application, the project can be compiled into a single executable file using PyInstaller, allowing it to run on any compatible system without requiring a Python installation. This makes it a portable and user-friendly solution for managing and listening to audio files
