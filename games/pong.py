import pygame
import numpy as np

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class PongGame:
    def __init__(self, screen, hand_tracker, pose_tracker, one_player=False, party_mode=False, sounds=None):
        self.screen = screen
        self.hand_tracker = hand_tracker  # para el botón volver
        self.pose_tracker = pose_tracker  # se conserva por compatibilidad
        self.one_player = one_player
        self.party_mode = party_mode
        # --- LÍNEA NUEVA PARA ARREGLAR EL ERROR ---
        self.sounds = sounds if sounds is not None else {} 
        # ------------------------------------------
        self.font_big = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 28, bold=True)
        self.clock = pygame.time.Clock()
        self.setup_game()
    def setup_game(self):
        self.ball_x = float(SCREEN_WIDTH // 2)
        self.ball_y = float(SCREEN_HEIGHT // 2)
        self.ball_dx = 8.0
        self.ball_dy = 8.0
        self.ball_radius = 15

        self.score_1 = 0
        self.score_2 = 0
        self.paddle_radius = 40
        self.p1_pos = (50, SCREEN_HEIGHT // 2)
        self.p2_pos = (SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2)

        self.p1_vel = (0, 0)
        self.p2_vel = (0, 0)
        self.p1_prev = (50, SCREEN_HEIGHT // 2)
        self.p2_prev = (SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2)

        self.game_over = False
        self.winner_text = ""
        self.winner_code = None
        self.game_over_time = None
        self.start_button = pygame.Rect(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 110, 280, 60)
        self.back_button = pygame.Rect(10, 10, 110, 40)
        self.retry_button = pygame.Rect(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 25, 150, 52)
        self.menu_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 25, 150, 52)

    def show_intro(self):
        cap = self.hand_tracker.cap
        font_small = pygame.font.SysFont("Arial", 22)

        while True:
            ret, frame = cap.read()
            if not ret:
                return "QUIT"

            bg, hand_pos, click = self.hand_tracker.process_frame(frame)
            progress = self.hand_tracker.get_close_progress()

            if bg is not None:
                bg_surface = pygame.surfarray.make_surface(np.transpose(bg, (1, 0, 2)))
                self.screen.blit(bg_surface, (0, 0))
            else:
                self.screen.fill((0, 0, 0))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.screen.blit(overlay, (0, 0))

            title = self.font_big.render("PONG", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 90)))

            line1 = font_small.render("Mueve tu mano para controlar la paleta.", True, (220, 220, 220))
            line2 = font_small.render("Gana quien llegue primero a 5 puntos.", True, (220, 220, 220))
            self.screen.blit(line1, line1.get_rect(center=(SCREEN_WIDTH // 2, 170)))
            self.screen.blit(line2, line2.get_rect(center=(SCREEN_WIDTH // 2, 205)))

            hover_start = hand_pos and self.start_button.collidepoint(hand_pos)
            btn_surf = pygame.Surface((self.start_button.width, self.start_button.height), pygame.SRCALPHA)
            btn_surf.fill((0, 190, 120, 200) if hover_start else (20, 90, 70, 180))
            self.screen.blit(btn_surf, self.start_button.topleft)
            pygame.draw.rect(self.screen, (0, 255, 170) if hover_start else (90, 190, 160), self.start_button, 2, border_radius=10)
            start_t = self.font_med.render("Start", True, (255, 255, 255))
            self.screen.blit(start_t, start_t.get_rect(center=self.start_button.center))

            if hover_start and progress > 0:
                bar_w = int(self.start_button.width * progress)
                bar = pygame.Surface((bar_w, 5), pygame.SRCALPHA)
                bar.fill((0, 255, 120, 220))
                self.screen.blit(bar, (self.start_button.x, self.start_button.bottom - 5))

            if hand_pos:
                p = progress if hover_start else 0
                color = (255, int(255 * (1 - p)), 0)
                pygame.draw.circle(self.screen, color, hand_pos, 18, 3)

            if click and hover_start:
                self.sounds["accept"].play()
                return "START"
            

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sounds["accept"].play()
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.sounds["accept"].play()
                        return "QUIT"
                    if event.key == pygame.K_ESCAPE and not self.party_mode:
                        self.sounds["accept"].play()
                        return "MENU"

            self.clock.tick(30)

    def show_countdown(self):
        cap = self.hand_tracker.cap
        for value in (3, 2, 1):
            start_tick = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start_tick < 700:
                ret, frame = cap.read()
                if not ret:
                    self.sounds["accept"].play()
                    return "QUIT"

                bg, _, _ = self.hand_tracker.process_frame(frame)
                if bg is not None:
                    bg_surface = pygame.surfarray.make_surface(np.transpose(bg, (1, 0, 2)))
                    self.screen.blit(bg_surface, (0, 0))
                else:
                    self.screen.fill((0, 0, 0))

                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 170))
                self.screen.blit(overlay, (0, 0))

                text = self.font_big.render(str(value), True, (255, 255, 255))
                self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "QUIT"
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                        return "QUIT"

                self.clock.tick(30)

        return "OK"

    def update(self, p1_pos, p2_pos):
        if self.game_over:
            return

        if p1_pos:
            self.p1_vel = (p1_pos[0] - self.p1_prev[0], p1_pos[1] - self.p1_prev[1])
            self.p1_prev = self.p1_pos
            self.p1_pos = p1_pos

        if p2_pos and not self.one_player:
            self.p2_vel = (p2_pos[0] - self.p2_prev[0], p2_pos[1] - self.p2_prev[1])
            self.p2_prev = self.p2_pos
            self.p2_pos = p2_pos
        elif self.one_player:
            target_y = self.ball_y
            current_x, current_y = self.p2_pos
            step = np.clip(target_y - current_y, -10.0, 10.0)
            next_y = int(np.clip(current_y + step, self.paddle_radius, SCREEN_HEIGHT - self.paddle_radius))
            self.p2_vel = (0, next_y - current_y)
            self.p2_prev = self.p2_pos
            self.p2_pos = (current_x, next_y)

        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        if self.ball_y >= SCREEN_HEIGHT - self.ball_radius or self.ball_y <= self.ball_radius:
            self.ball_dy *= -1
            if "pong" in self.sounds:
                self.sounds["pong"].play()

        dist_p1 = np.hypot(self.ball_x - self.p1_pos[0], self.ball_y - self.p1_pos[1])
        dist_p2 = np.hypot(self.ball_x - self.p2_pos[0], self.ball_y - self.p2_pos[1])

        if dist_p1 < (self.ball_radius + self.paddle_radius) and self.ball_dx < 0:
            self.sounds["pong"].play()
            speed = np.hypot(*self.p1_vel)
            boost = np.clip(speed * 0.4, 0, 10)
            self.ball_dx = abs(self.ball_dx) * 1.05 + boost
            self.ball_dy += np.clip(self.p1_vel[1] * 0.5, -8, 8)
        elif dist_p2 < (self.ball_radius + self.paddle_radius) and self.ball_dx > 0:
            self.sounds["pong"].play()
            speed = np.hypot(*self.p2_vel)
            boost = np.clip(speed * 0.4, 0, 10)
            self.ball_dx = -(abs(self.ball_dx) * 1.05 + boost)
            self.ball_dy += np.clip(self.p2_vel[1] * 0.5, -8, 8)

        self.ball_dx = max(-25.0, min(25.0, self.ball_dx))
        self.ball_dy = max(-25.0, min(25.0, self.ball_dy))

        if self.ball_x < 0:
            self.score_2 += 1
            self.sounds["point"].play()
            self.reset_ball()
        elif self.ball_x > SCREEN_WIDTH:
            self.score_1 += 1
            self.sounds["point"].play()
            self.reset_ball()

        if self.score_1 >= 5:
            self.game_over = True
            self.winner_text = "¡JUGADOR 1 GANA!"
            self.winner_code = "P1"
            self.game_over_time = pygame.time.get_ticks()
        elif self.score_2 >= 5:
            self.game_over = True
            self.winner_text = "¡CPU GANA!" if self.one_player else "¡JUGADOR 2 GANA!"
            self.winner_code = "CPU" if self.one_player else "P2"
            self.game_over_time = pygame.time.get_ticks()

    def reset_ball(self):
        self.ball_x = float(SCREEN_WIDTH // 2)
        self.ball_y = float(SCREEN_HEIGHT // 2)
        self.ball_dx = 8.0 if self.ball_dx < 0 else -8.0
        self.ball_dy = 8.0

    def draw(self, bg_surface, hand_pos, progress):
        if bg_surface is not None:
            self.screen.blit(bg_surface, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 60))
        self.screen.blit(overlay, (0, 0))

        # Divisor de zonas más visible
        pygame.draw.line(self.screen, (100, 150, 255),
                         (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 4)
        
        # Rectángulos de zona (muy tenue)
        zone_left = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT), pygame.SRCALPHA)
        zone_left.fill((50, 100, 255, 10))
        self.screen.blit(zone_left, (0, 0))
        
        zone_right = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT), pygame.SRCALPHA)
        zone_right.fill((255, 60, 60, 10))
        self.screen.blit(zone_right, (SCREEN_WIDTH // 2, 0))

        pygame.draw.circle(self.screen, (50, 100, 255), self.p1_pos, self.paddle_radius, 4)
        pygame.draw.circle(self.screen, (255, 60, 60),  self.p2_pos, self.paddle_radius, 4)
        pygame.draw.circle(self.screen, (255, 255, 0),
                           (int(self.ball_x), int(self.ball_y)), self.ball_radius)

        s1 = self.font_big.render(str(self.score_1), True, (255, 255, 255))
        s2 = self.font_big.render(str(self.score_2), True, (255, 255, 255))
        self.screen.blit(s1, (100, 20))
        self.screen.blit(s2, (SCREEN_WIDTH - 140, 20))

        # Botón volver
        is_hover = False
        if not self.party_mode:
            is_hover = hand_pos and self.back_button.collidepoint(hand_pos)
            btn_surf = pygame.Surface((self.back_button.width, self.back_button.height), pygame.SRCALPHA)
            btn_surf.fill((0, 180, 255, 180) if is_hover else (20, 20, 80, 160))
            self.screen.blit(btn_surf, self.back_button.topleft)
            pygame.draw.rect(self.screen, (0, 220, 255) if is_hover else (80, 80, 160),
                             self.back_button, 2, border_radius=8)
            back_t = self.font_med.render("Volver", True, (255, 255, 255))
            self.screen.blit(back_t, back_t.get_rect(center=self.back_button.center))

            if is_hover and progress > 0:
                bar_w = int(self.back_button.width * progress)
                bar = pygame.Surface((bar_w, 4), pygame.SRCALPHA)
                bar.fill((0, 255, 100, 200))
                self.screen.blit(bar, (self.back_button.x, self.back_button.bottom - 4))

        hover_retry = False
        hover_menu = False

        if self.game_over:
            box = pygame.Surface((SCREEN_WIDTH, 140), pygame.SRCALPHA)
            box.fill((0, 0, 0, 180))
            self.screen.blit(box, (0, SCREEN_HEIGHT // 2 - 70))
            win_surf = self.font_big.render(self.winner_text, True, (0, 255, 80))
            self.screen.blit(win_surf, win_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 15)))

            if not self.party_mode:
                hover_retry = hand_pos and self.retry_button.collidepoint(hand_pos)
                hover_menu = hand_pos and self.menu_button.collidepoint(hand_pos)

                retry_surf = pygame.Surface((self.retry_button.width, self.retry_button.height), pygame.SRCALPHA)
                retry_surf.fill((0, 180, 120, 190) if hover_retry else (20, 90, 70, 170))
                self.screen.blit(retry_surf, self.retry_button.topleft)
                pygame.draw.rect(self.screen, (0, 255, 170) if hover_retry else (80, 180, 150), self.retry_button, 2, border_radius=10)
                retry_t = self.font_med.render("Otra vez", True, (255, 255, 255))
                self.screen.blit(retry_t, retry_t.get_rect(center=self.retry_button.center))

                menu_surf = pygame.Surface((self.menu_button.width, self.menu_button.height), pygame.SRCALPHA)
                menu_surf.fill((0, 180, 255, 190) if hover_menu else (20, 70, 90, 170))
                self.screen.blit(menu_surf, self.menu_button.topleft)
                pygame.draw.rect(self.screen, (0, 220, 255) if hover_menu else (80, 140, 180), self.menu_button, 2, border_radius=10)
                menu_t = self.font_med.render("Menu", True, (255, 255, 255))
                self.screen.blit(menu_t, menu_t.get_rect(center=self.menu_button.center))

        if hand_pos:
            p = progress if (is_hover or hover_retry or hover_menu) else 0
            color = (255, int(255 * (1 - p)), 0)
            pygame.draw.circle(self.screen, color, hand_pos, 18, 3)

        pygame.display.flip()
        return is_hover, hover_retry, hover_menu

    def run(self):
        cap = self.hand_tracker.cap

        intro_state = self.show_intro()
        if intro_state == "QUIT":
            return "QUIT"
        if intro_state == "MENU" and not self.party_mode:
            return "MENU"
        countdown_state = self.show_countdown()
        if countdown_state == "QUIT":
            return "QUIT"

        while True:
            ret, frame = cap.read()
            if not ret:
                return "QUIT"

            bg, hand_pos, click = self.hand_tracker.process_frame(frame)
            progress = self.hand_tracker.get_close_progress()

            if bg is not None:
                bg_surface = pygame.surfarray.make_surface(np.transpose(bg, (1, 0, 2)))
            else:
                bg_surface = None

            hands = sorted(self.hand_tracker.get_positions(), key=lambda point: point[0])
            # Solo asignar manos si están en su mitad correspondiente
            p1_pos = None
            p2_pos = None
            for hand in hands:
                if hand[0] < SCREEN_WIDTH // 2:
                    p1_pos = hand
                elif hand[0] >= SCREEN_WIDTH // 2:
                    p2_pos = hand

            if self.one_player:
                p2_pos = None

            is_hover_back, is_hover_retry, is_hover_menu = self.draw(bg_surface, hand_pos, progress)
            self.update(p1_pos, p2_pos)

            if self.party_mode and self.game_over and self.game_over_time is not None:
                if pygame.time.get_ticks() - self.game_over_time >= 1200:
                    return self.winner_code

            if click and is_hover_back and not self.party_mode:
                return "MENU"
            if self.game_over and click and is_hover_retry and not self.party_mode:
                self.setup_game()
            if self.game_over and click and is_hover_menu and not self.party_mode:
                return "MENU"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return "QUIT"
                    if event.key == pygame.K_ESCAPE:
                        return "MENU"
                    if event.key == pygame.K_r and self.game_over:
                        self.setup_game()

            self.clock.tick(30)