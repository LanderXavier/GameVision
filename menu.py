import pygame
import numpy as np

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class Menu:
    # Se añade sounds=None al final
    def __init__(self, screen, tracker, sounds=None): 
        self.screen = screen
        self.tracker = tracker
        self.sounds = sounds if sounds is not None else {} # Guardar sonidos
        self.font_title = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_item  = pygame.font.SysFont("Arial", 34, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)

        self.items = ["Start Party", "About"]
        self.buttons = []
        card_w = 340
        card_h = 80
        gap_y = 24
        start_x = (SCREEN_WIDTH - card_w) // 2
        start_y = 190
        for i, name in enumerate(self.items):
            rect = pygame.Rect(
                start_x,
                start_y + i * (card_h + gap_y),
                card_w,
                card_h,
            )
            self.buttons.append((rect, name))

    def draw_hand_cursor(self, pos, progress):
        if pos is None:
            return
        color = (255, int(255 * (1 - progress)), 0)
        pygame.draw.circle(self.screen, color, pos, 18, 3)
        if progress > 0:
            rect = pygame.Rect(pos[0] - 22, pos[1] - 22, 44, 44)
            angle = np.radians(360 * progress)
            pygame.draw.arc(self.screen, (0, 255, 100), rect, 0, angle, 4)

    def run(self):
        clock = pygame.time.Clock()

        while True:
            rgb, pos, click = self.tracker.process()
            progress = self.tracker.get_close_progress()

            if rgb is not None:
                surface = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
                self.screen.blit(surface, (0, 0))
            else:
                self.screen.fill((10, 10, 30))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 20, 160))
            self.screen.blit(overlay, (0, 0))

            title = self.font_title.render("EYETOY GAMES", True, (0, 220, 255))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 90)))

            hovered = None
            for rect, name in self.buttons:
                is_hover = pos and rect.collidepoint(pos)
                if is_hover:
                    hovered = name

                btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                btn_surf.fill((0, 180, 255, 180) if is_hover else (20, 20, 80, 180))
                self.screen.blit(btn_surf, rect.topleft)
                pygame.draw.rect(self.screen, (0, 220, 255) if is_hover else (80, 80, 160),
                                 rect, 3, border_radius=12)

                text = self.font_item.render(name, True, (255, 255, 255))
                self.screen.blit(text, text.get_rect(center=rect.center))

                if is_hover and progress > 0:
                    bar_w = int(rect.width * progress)
                    bar = pygame.Surface((bar_w, 6), pygame.SRCALPHA)
                    bar.fill((0, 255, 100, 200))
                    self.screen.blit(bar, (rect.x, rect.bottom - 6))

            hint = self.font_small.render("Cierra para confirmar y abre para volver a elegir", True, (180, 180, 180))
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

            self.draw_hand_cursor(pos, progress if hovered else 0)

            if click and hovered:
                # Opcional: Reproducir sonido de confirmación
                if "accept" in self.sounds:
                    self.sounds["accept"].play()
                return hovered

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    return "QUIT"

            clock.tick(30)


class PlayerSelectScreen:
    def __init__(self, screen, tracker, sounds=None): # Añadido sounds
        self.screen = screen
        self.tracker = tracker
        self.sounds = sounds if sounds is not None else {}
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_item = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.buttons = [
            (pygame.Rect(SCREEN_WIDTH // 2 - 170, 165, 340, 80), "1 Jugador", 1),
            (pygame.Rect(SCREEN_WIDTH // 2 - 170, 265, 340, 80), "2 Jugadores", 2),
            (pygame.Rect(SCREEN_WIDTH // 2 - 170, 365, 340, 80), "Volver", "MENU"),
        ]

    def run(self):
        clock = pygame.time.Clock()

        while True:
            rgb, pos, click = self.tracker.process()
            progress = self.tracker.get_close_progress()

            if rgb is not None:
                surface = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
                self.screen.blit(surface, (0, 0))
            else:
                self.screen.fill((10, 10, 30))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 20, 170))
            self.screen.blit(overlay, (0, 0))

            title = self.font_title.render("Cuantos Jugadores?", True, (0, 220, 255))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 90)))

            hovered_value = None
            for rect, label, value in self.buttons:
                is_hover = pos and rect.collidepoint(pos)
                if is_hover:
                    hovered_value = value

                btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                btn_surf.fill((0, 180, 255, 180) if is_hover else (20, 20, 80, 180))
                self.screen.blit(btn_surf, rect.topleft)
                pygame.draw.rect(self.screen, (0, 220, 255) if is_hover else (80, 80, 160), rect, 3, border_radius=12)

                text = self.font_item.render(label, True, (255, 255, 255))
                self.screen.blit(text, text.get_rect(center=rect.center))

                if is_hover and progress > 0:
                    bar_w = int(rect.width * progress)
                    bar = pygame.Surface((bar_w, 6), pygame.SRCALPHA)
                    bar.fill((0, 255, 100, 200))
                    self.screen.blit(bar, (rect.x, rect.bottom - 6))

            hint = self.font_small.render("Cierra la mano para elegir", True, (190, 190, 190))
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

            if pos:
                p = progress if hovered_value is not None else 0
                color = (255, int(255 * (1 - p)), 0)
                pygame.draw.circle(self.screen, color, pos, 18, 3)

            if click and hovered_value is not None:
                if "accept" in self.sounds:
                    self.sounds["accept"].play()
                return hovered_value

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return "QUIT"
                    if event.key == pygame.K_ESCAPE:
                        return "MENU"

            clock.tick(30)


class PartyResultScreen:
    # Se añade sounds al final del constructor
    def __init__(self, screen, tracker, one_player, game_results, total_score, sounds=None): 
        self.screen = screen
        self.tracker = tracker
        self.one_player = one_player
        self.game_results = game_results
        self.total_score = total_score
        self.sounds = sounds if sounds is not None else {}
        self.font_title = pygame.font.SysFont("Arial", 46, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 30, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 22)
        self.menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT - 90, 340, 60)

    def run(self):
        clock = pygame.time.Clock()

        if self.one_player:
            side_a, side_b = "PLAYER", "CPU"
        else:
            side_a, side_b = "JUGADOR 1", "JUGADOR 2"

        a_score = self.total_score.get(side_a, 0)
        b_score = self.total_score.get(side_b, 0)
        if a_score > b_score:
            winner = f"Gana {side_a}"
            winner_color = (80, 220, 120)
        elif b_score > a_score:
            winner = f"Gana {side_b}"
            winner_color = (255, 120, 120)
        else:
            winner = "Empate"
            winner_color = (255, 230, 120)

        while True:
            rgb, pos, click = self.tracker.process()
            progress = self.tracker.get_close_progress()

            if rgb is not None:
                surface = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
                self.screen.blit(surface, (0, 0))
            else:
                self.screen.fill((10, 10, 30))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 20, 180))
            self.screen.blit(overlay, (0, 0))

            title = self.font_title.render("Resultado Party", True, (0, 220, 255))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 75)))

            y = 145
            for game_name, game_winner in self.game_results:
                line = self.font_small.render(f"{game_name}: {game_winner}", True, (230, 230, 230))
                self.screen.blit(line, line.get_rect(center=(SCREEN_WIDTH // 2, y)))
                y += 36

            score_line = self.font_med.render(f"{side_a}: {a_score}   |   {side_b}: {b_score}", True, (255, 255, 255))
            self.screen.blit(score_line, score_line.get_rect(center=(SCREEN_WIDTH // 2, y + 18)))

            winner_line = self.font_med.render(winner, True, winner_color)
            self.screen.blit(winner_line, winner_line.get_rect(center=(SCREEN_WIDTH // 2, y + 64)))

            is_hover = pos and self.menu_button.collidepoint(pos)
            btn_surf = pygame.Surface((self.menu_button.width, self.menu_button.height), pygame.SRCALPHA)
            btn_surf.fill((0, 180, 255, 180) if is_hover else (20, 20, 80, 180))
            self.screen.blit(btn_surf, self.menu_button.topleft)
            pygame.draw.rect(self.screen, (0, 220, 255) if is_hover else (80, 80, 160), self.menu_button, 3, border_radius=12)
            text = self.font_med.render("Volver al Menu", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=self.menu_button.center))

            if is_hover and progress > 0:
                bar_w = int(self.menu_button.width * progress)
                bar = pygame.Surface((bar_w, 6), pygame.SRCALPHA)
                bar.fill((0, 255, 100, 200))
                self.screen.blit(bar, (self.menu_button.x, self.menu_button.bottom - 6))

            if pos:
                p = progress if is_hover else 0
                color = (255, int(255 * (1 - p)), 0)
                pygame.draw.circle(self.screen, color, pos, 18, 3)

            if click and is_hover:
                if "accept" in self.sounds:
                    self.sounds["accept"].play()
                return "MENU"

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    return "QUIT"

            clock.tick(30)