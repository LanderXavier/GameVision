import pygame
import numpy as np

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class AboutScreen:
# Añadimos sounds=None a la lista de argumentos
    def __init__(self, screen, tracker, sounds=None):
        self.screen = screen
        self.tracker = tracker
        # Guardamos los sonidos (aunque no los uses en esta pantalla, hay que recibirlos)
        self.sounds = sounds if sounds is not None else {}
        
        self.font_big   = pygame.font.SysFont("Arial", 42, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 90, 200, 50)
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

            title = self.font_big.render("ABOUT", True, (0, 220, 255))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 70)))

            lines = [
                ("Lander",      (255, 255, 255), 38),
                ("Mark",        (0, 220, 255),   32),
                ("Yachay Tech", (180, 180, 255), 26),
                ("ECR",         (180, 255, 180), 26),
            ]
            y = 150
            for text, color, size in lines:
                font = pygame.font.SysFont("Arial", size, bold=True)
                surf = font.render(text, True, color)
                self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, y)))
                y += size + 18

            is_hover = pos and self.back_button.collidepoint(pos)
            btn_surf = pygame.Surface((self.back_button.width, self.back_button.height), pygame.SRCALPHA)
            btn_surf.fill((0, 180, 255, 180) if is_hover else (20, 20, 80, 180))
            self.screen.blit(btn_surf, self.back_button.topleft)
            pygame.draw.rect(self.screen, (0, 220, 255) if is_hover else (80, 80, 160),
                             self.back_button, 3, border_radius=10)
            back_text = self.font_med.render("Volver", True, (255, 255, 255))
            self.screen.blit(back_text, back_text.get_rect(center=self.back_button.center))

            if is_hover and progress > 0:
                bar_w = int(self.back_button.width * progress)
                bar = pygame.Surface((bar_w, 6), pygame.SRCALPHA)
                bar.fill((0, 255, 100, 200))
                self.screen.blit(bar, (self.back_button.x, self.back_button.bottom - 6))

            if pos:
                p = progress if is_hover else 0
                color = (255, int(255 * (1 - p)), 0)
                pygame.draw.circle(self.screen, color, pos, 18, 3)

            if click and is_hover:
                self.sounds["pong"].play()
                return "MENU"

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sounds["accept"].play()
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.sounds["accept"].play()
                        return "QUIT"
                    if event.key == pygame.K_ESCAPE:
                        self.sounds["accept"].play()
                        return "MENU"

            clock.tick(30)