import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding='utf-8',
            errors='replace'
        )
    except Exception:
        pass

"""
FruitNinjaCV - main.py

Point d'entrée principal du jeu.
Coordonne la caméra, la CV et le moteur de jeu.
"""

import pygame

from src.camera.camera_manager import CameraManager
from src.vision.hand_tracker import HandTracker
from src.blade.blade_tracker import BladeTracker
from src.game.game_manager import GameManager
from src.render.renderer import Renderer
from src.ui.menu import Menu
from src.ui.game_over import GameOverScreen


# ──────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
WINDOW_TITLE = "Fruit Ninja CV"


def main() -> None:

    pygame.init()
    pygame.mixer.init()

    # Fenêtre redimensionnable
    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.RESIZABLE
    )

    pygame.display.set_caption(WINDOW_TITLE)

    clock = pygame.time.Clock()

    # ── Initialisation ─────────────────────────

    camera = CameraManager(
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT
    )

    hand_tracker = HandTracker()

    blade = BladeTracker(
        max_points=20
    )

    renderer = Renderer(
        screen,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT
    )

    menu = Menu(
        screen,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT
    )

    # ── Loading ────────────────────────────────

    if not renderer.loading_screen():
        pygame.quit()
        sys.exit()

    # ── Application ────────────────────────────

    app_running = True

    while app_running:

        # Toujours récupérer la taille actuelle
        current_width, current_height = screen.get_size()

        # Mettre à jour le menu
        menu.screen = screen
        menu.width = current_width
        menu.height = current_height

        # ── Menu ───────────────────────────────

        difficulty = menu.run()

        if difficulty is None:
            app_running = False
            break

        # Le gameplay reste LOGIQUEMENT en 800x600.
        # Le Renderer s'occupe ensuite de l'agrandissement visuel.

        game = GameManager(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            difficulty=difficulty
        )

        # Arrêter la musique du loading/menu
        pygame.mixer.music.stop()

        game.start()
        blade.clear()

        # ── Partie ─────────────────────────────

        playing = True

        while playing:

            # ── Événements ─────────────────────

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    playing = False
                    app_running = False

                elif event.type == pygame.VIDEORESIZE:

                    # Nouvelle taille de la fenêtre
                    screen = pygame.display.set_mode(
                        (event.w, event.h),
                        pygame.RESIZABLE
                    )

                    # Le Renderer utilise maintenant
                    # cette nouvelle fenêtre.
                    renderer.screen = screen

                    # Le menu aussi
                    menu.screen = screen
                    menu.width = event.w
                    menu.height = event.h

                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):

                    playing = False
                    app_running = False

            if not playing:
                break

            # ── Webcam ─────────────────────────

            frame_bgr = camera.read()

            if frame_bgr is None:
                continue

            # ── Détection de la main ───────────

            finger_pos = hand_tracker.get_index_tip(
                frame_bgr
            )

            # ── Lame ──────────────────────────

            blade.update(
                finger_pos
            )

            # ── Logique du jeu ─────────────────

            game.update(
                blade
            )

            # ── Rendu ─────────────────────────

            renderer.draw(
                frame_bgr,
                game,
                blade
            )

            # ── Game Over ──────────────────────

            if game.is_over():

                current_width, current_height = screen.get_size()

                go = GameOverScreen(
                    screen,
                    width=current_width,
                    height=current_height
                )

                action = go.run(
                    game.score_manager.score
                )

                if action == "restart":

                    game.restart()
                    blade.clear()

                elif action == "menu":

                    # Relancer la musique du menu
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.play(-1)

                    playing = False

                else:

                    playing = False
                    app_running = False

            clock.tick(FPS)

    # ── Nettoyage ──────────────────────────────

    camera.release()
    hand_tracker.close()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
