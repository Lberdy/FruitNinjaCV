import math

from pathlib import Path

import pygame


_ASSETS = Path(__file__).resolve().parents[2] / "assets"
_IMAGES = _ASSETS / "images"
_FONTS = _ASSETS / "fonts"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 220, 0)
GRAY = (180, 180, 180)


class Menu:

    # (clé de difficulté, libellé affiché)
    DIFFICULTIES = [
        ("easy", "FACILE"),
        ("normal", "INTERMÉDIAIRE"),
        ("hard", "DIFFICILE"),
    ]

    # Surface logique du menu
    LOGICAL_WIDTH = 800
    LOGICAL_HEIGHT = 600

    def __init__(
        self,
        screen: pygame.Surface,
        width: int,
        height: int
    ) -> None:

        self.screen = screen

        # Taille réelle de la fenêtre
        self.width = width
        self.height = height

        # Surface logique fixe 800x600
        self.menu_surface = pygame.Surface(
            (self.LOGICAL_WIDTH, self.LOGICAL_HEIGHT)
        )

        font_path = _FONTS / "game_font.ttf"

        if font_path.exists():
            self.font_title = pygame.font.Font(str(font_path), 56)
            self.font_sub = pygame.font.Font(str(font_path), 26)
            self.font_option = pygame.font.Font(str(font_path), 24)
            self.font_hint = pygame.font.Font(str(font_path), 18)
        else:
            self.font_title = pygame.font.SysFont(
                "Arial", 56, bold=True
            )
            self.font_sub = pygame.font.SysFont(
                "Arial", 26, bold=True
            )
            self.font_option = pygame.font.SysFont(
                "Arial", 24, bold=True
            )
            self.font_hint = pygame.font.SysFont(
                "Arial", 18
            )

        # Fond du menu
        bg_path = _IMAGES / "menu_background.png"

        self._bg = None

        if bg_path.exists():
            bg = pygame.image.load(str(bg_path)).convert()

            self._bg = pygame.transform.scale(
                bg,
                (self.LOGICAL_WIDTH, self.LOGICAL_HEIGHT)
            )

        self._anim = 0

        # "Intermédiaire" sélectionné par défaut
        self._selected = 1

        self._option_rects = []

    def run(self) -> "str | None":
        """
        Boucle du menu.

        Retourne la difficulté choisie
        ("easy"/"normal"/"hard"),
        ou None si le joueur quitte.
        """

        clock = pygame.time.Clock()

        while True:

            self._anim += 1

            for event in pygame.event.get():

                # Quitter
                if event.type == pygame.QUIT:
                    return None

                # Redimensionnement de la fenêtre
                if event.type == pygame.VIDEORESIZE:

                    self.screen = pygame.display.set_mode(
                        (event.w, event.h),
                        pygame.RESIZABLE
                    )

                    self.width = event.w
                    self.height = event.h

                # Clavier
                if event.type == pygame.KEYDOWN:

                    if event.key in (
                        pygame.K_UP,
                        pygame.K_LEFT
                    ):
                        self._selected = (
                            self._selected - 1
                        ) % len(self.DIFFICULTIES)

                    elif event.key in (
                        pygame.K_DOWN,
                        pygame.K_RIGHT
                    ):
                        self._selected = (
                            self._selected + 1
                        ) % len(self.DIFFICULTIES)

                    elif event.key in (
                        pygame.K_RETURN,
                        pygame.K_SPACE
                    ):
                        return self.DIFFICULTIES[
                            self._selected
                        ][0]

                    elif event.key == pygame.K_ESCAPE:
                        return None

                # Souris
                if event.type == pygame.MOUSEBUTTONDOWN:

                    # Conversion des coordonnées de la fenêtre
                    # vers les coordonnées logiques 800x600
                    mouse_x = int(
                        event.pos[0]
                        * self.LOGICAL_WIDTH
                        / self.width
                    )

                    mouse_y = int(
                        event.pos[1]
                        * self.LOGICAL_HEIGHT
                        / self.height
                    )

                    logical_mouse_pos = (
                        mouse_x,
                        mouse_y
                    )

                    for i, rect in enumerate(
                        self._option_rects
                    ):

                        if rect.collidepoint(
                            logical_mouse_pos
                        ):
                            return self.DIFFICULTIES[i][0]

            # Dessiner le menu
            self._draw()

            # Adapter le menu 800x600
            # à la taille réelle de la fenêtre
            scaled_menu = pygame.transform.smoothscale(
                self.menu_surface,
                (self.width, self.height)
            )

            self.screen.blit(
                scaled_menu,
                (0, 0)
            )

            pygame.display.flip()

            clock.tick(60)

    def _draw(self) -> None:

        # =====================================================
        # TOUT EST DESSINÉ SUR LA SURFACE LOGIQUE 800x600
        # =====================================================

        # Fond
        if self._bg:
            self.menu_surface.blit(
                self._bg,
                (0, 0)
            )
        else:
            self.menu_surface.fill(
                (15, 15, 30)
            )

        # Centre logique
        cx = self.LOGICAL_WIDTH // 2

        # Overlay sombre
        overlay = pygame.Surface(
            (
                self.LOGICAL_WIDTH,
                self.LOGICAL_HEIGHT
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 140)
        )

        self.menu_surface.blit(
            overlay,
            (0, 0)
        )

        # =====================================================
        # TITRE
        # =====================================================

        y_offset = int(
            math.sin(self._anim * 0.04) * 6
        )

        title = self.font_title.render(
            "FRUIT NINJA CV",
            True,
            ORANGE
        )

        shadow = self.font_title.render(
            "FRUIT NINJA CV",
            True,
            (100, 50, 0)
        )

        tx = (
            cx
            - title.get_width() // 2
        )

        ty = (
            self.LOGICAL_HEIGHT // 6
            + y_offset
        )

        self.menu_surface.blit(
            shadow,
            (
                tx + 3,
                ty + 3
            )
        )

        self.menu_surface.blit(
            title,
            (
                tx,
                ty
            )
        )

        # =====================================================
        # SOUS-TITRE
        # =====================================================

        sub = self.font_sub.render(
            "CHOISIR LA DIFFICULTÉ",
            True,
            WHITE
        )

        self.menu_surface.blit(
            sub,
            (
                cx - sub.get_width() // 2,
                ty + 80
            )
        )

        # =====================================================
        # OPTIONS
        # =====================================================

        self._option_rects = []

        opt_w = 280
        opt_h = 55
        gap = 18

        start_y = ty + 140

        for i, (_key, label) in enumerate(
            self.DIFFICULTIES
        ):

            rect = pygame.Rect(
                cx - opt_w // 2,
                start_y + i * (opt_h + gap),
                opt_w,
                opt_h
            )

            self._option_rects.append(rect)

            is_selected = (
                i == self._selected
            )

            bg_color = (
                ORANGE
                if is_selected
                else (50, 50, 65)
            )

            pygame.draw.rect(
                self.menu_surface,
                bg_color,
                rect,
                border_radius=10
            )

            pygame.draw.rect(
                self.menu_surface,
                WHITE,
                rect,
                2,
                border_radius=10
            )

            txt_color = (
                BLACK
                if is_selected
                else GRAY
            )

            txt = self.font_option.render(
                label,
                True,
                txt_color
            )

            self.menu_surface.blit(
                txt,
                (
                    rect.centerx
                    - txt.get_width() // 2,

                    rect.centery
                    - txt.get_height() // 2
                )
            )

        # =====================================================
        # INSTRUCTIONS
        # =====================================================

        instructions_y = (
            start_y
            + len(self.DIFFICULTIES)
            * (opt_h + gap)
            + 15
        )

        instructions = [
            "Levez votre main devant la webcam",
            "Tranchez les fruits avec un geste rapide — évitez les bombes !",
        ]

        for i, line in enumerate(instructions):

            s = self.font_hint.render(
                line,
                True,
                GRAY
            )

            self.menu_surface.blit(
                s,
                (
                    cx - s.get_width() // 2,
                    instructions_y + i * 24
                )
            )

        # =====================================================
        # RAPPEL DES CONTRÔLES
        # =====================================================

        if (self._anim // 30) % 2 == 0:

            hint = self.font_hint.render(
                "↑ ↓ pour choisir   •   Entrée pour valider   •   Clic pour jouer",
                True,
                YELLOW
            )

            self.menu_surface.blit(
                hint,
                (
                    cx - hint.get_width() // 2,
                    self.LOGICAL_HEIGHT - 40
                )
            )
