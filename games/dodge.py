import pygame
import numpy as np
import random

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class DodgeGame:
    # Debes incluir 'sounds=None' aquí arriba, después de party_mode
    def __init__(self, screen, hand_tracker, one_player=False, party_mode=False, sounds=None):
        self.screen = screen
        self.hand_tracker = hand_tracker
        self.one_player = one_player
        self.party_mode = party_mode
        
        # Ahora esta línea sí funcionará porque la cabecera ya reconoce 'sounds'
        self.sounds = sounds if sounds is not None else {}
        
        self.font_big = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.clock = pygame.time.Clock()
        self.setup_game()

    def setup_game(self):
        self.lives_p1 = 3
        self.lives_p2 = 3
        self.game_over = False
        self.winner_text = ""
        self.game_over_time = None
        self.obstacles = []
        self.start_button = pygame.Rect(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 110, 280, 60)
        self.spawn_timer = 0
        self.spawn_rate = 58  # un poco más de frecuencia inicial
        self.spawn_rate_min = 9  # un poco más de densidad final
        self.difficulty = 0.5
        self.timer_start = pygame.time.get_ticks()  # timer de 40 segundos
        self.timer_duration = 60000  # 60 segundos en milisegundos
        self.max_obstacle_speed = 34
        self.spawn_zone_toggle = "left"  # alterna zonas en 2 jugadores
        
        self.player1 = {"pos": (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2), "radius": 20, "color": (50, 100, 255)}
        self.player2 = {"pos": (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2), "radius": 20, "color": (255, 60, 60)}
        
        self.back_button = pygame.Rect(10, SCREEN_HEIGHT - 50, 110, 40)
        self.retry_button = pygame.Rect(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 45, 150, 52)
        self.menu_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 45, 150, 52)
        self.hand_pos = None

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
                self.screen.fill((10, 20, 40))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 175))
            self.screen.blit(overlay, (0, 0))

            title = self.font_big.render("DODGE", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 90)))

            line1 = font_small.render("Esquiva los bloques con tu mano.", True, (220, 220, 220))
            line2 = font_small.render("Sobrevive hasta el final con mas vidas.", True, (220, 220, 220))
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
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return "QUIT"
                    if event.key == pygame.K_ESCAPE and not self.party_mode:
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
                    self.screen.fill((10, 20, 40))

                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 175))
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

    def spawn_obstacle(self, count=1, zone=None):
        for _ in range(count):
            # En 2 jugadores, alternar zonas para evitar saturación
            zone_for_obstacle = zone
            if not self.one_player and zone_for_obstacle is None:
                zone_for_obstacle = self.spawn_zone_toggle
                self.spawn_zone_toggle = "right" if self.spawn_zone_toggle == "left" else "left"
            
            if zone_for_obstacle == "left" or (zone_for_obstacle is None and not self.one_player):
                x = random.randint(25, SCREEN_WIDTH // 2 - 25)
            elif zone_for_obstacle == "right" or (zone_for_obstacle is None and not self.one_player):
                x = random.randint(SCREEN_WIDTH // 2 + 25, SCREEN_WIDTH - 25)
            else:
                x = random.randint(50, SCREEN_WIDTH - 50)
            
            color = random.choice([(255, 100, 0), (255, 0, 100), (100, 255, 0), (0, 255, 255)])
            obstacle = {
                "x": x,
                "y": -30,
                "width": random.randint(110, 180),
                "height": 40,
                "color": color,
                "zone": zone_for_obstacle,
                "speed": min(12 + self.difficulty * 1.0, self.max_obstacle_speed)
            }
            self.obstacles.append(obstacle)

    def update(self, p1_pos, p2_pos):
        if self.game_over:
            return

        # Timer - termina el juego si llega a 0
        elapsed = pygame.time.get_ticks() - self.timer_start
        if elapsed >= self.timer_duration:
            if self.one_player:
                self.winner_text = "TIEMPO COMPLETO"
            else:
                if self.lives_p1 > self.lives_p2:
                    self.winner_text = "GANA JUGADOR 1"
                elif self.lives_p2 > self.lives_p1:
                    self.winner_text = "GANA JUGADOR 2"
                else:
                    self.winner_text = "EMPATE"
            self.game_over = True
            self.game_over_time = pygame.time.get_ticks()
            return

        # Actualizar posiciones de jugadores
        if p1_pos:
            self.player1["pos"] = (p1_pos[0], np.clip(p1_pos[1], self.player1["radius"], SCREEN_HEIGHT - self.player1["radius"]))
        
        if p2_pos and not self.one_player:
            self.player2["pos"] = (p2_pos[0], np.clip(p2_pos[1], self.player2["radius"], SCREEN_HEIGHT - self.player2["radius"]))

        # Generar más obstáculos por ciclo
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            spawn_count = 2
            self.spawn_obstacle(count=spawn_count)
            self.spawn_timer = 0
            # Mantener aumento progresivo de dificultad
            self.difficulty += 0.30
            self.spawn_rate = max(self.spawn_rate_min, int(self.spawn_rate - 0.8))

        # Mover y colisionar obstáculos
        obstacles_to_remove = []
        for i, obs in enumerate(self.obstacles):
            obs["speed"] = min(obs["speed"] + 0.03, self.max_obstacle_speed)
            obs["y"] += obs["speed"]
            
            # Detectar colisiones por jugador
            dist_p1 = np.hypot(
                obs["x"] - self.player1["pos"][0],
                obs["y"] - self.player1["pos"][1]
            )
            if dist_p1 < (self.player1["radius"] + obs["width"] // 2):
                self.lives_p1 -= 1
                self.sounds["break"].play()
                obstacles_to_remove.append(i)
                if self.one_player and self.lives_p1 <= 0:
                    self.winner_text = "SIN VIDAS"
                    self.game_over = True
                    self.game_over_time = pygame.time.get_ticks()

            if not self.one_player:
                dist_p2 = np.hypot(
                    obs["x"] - self.player2["pos"][0],
                    obs["y"] - self.player2["pos"][1]
                )
                if dist_p2 < (self.player2["radius"] + obs["width"] // 2):
                    self.sounds["break"].play()
                    self.lives_p2 -= 1
                    obstacles_to_remove.append(i)

                if self.lives_p1 <= 0 or self.lives_p2 <= 0:
                    if self.lives_p1 > self.lives_p2:
                        self.sounds["win"].play()
                        self.winner_text = "GANA JUGADOR 1"
                    elif self.lives_p2 > self.lives_p1:
                        self.sounds["win"].play()
                        self.winner_text = "GANA JUGADOR 2"
                    else:
                        self.winner_text = "EMPATE"
                    self.game_over = True
                    self.game_over_time = pygame.time.get_ticks()
            
            # Remover si salió de pantalla
            if obs["y"] > SCREEN_HEIGHT:
                obstacles_to_remove.append(i)

        # Eliminar obstáculos
        for i in sorted(obstacles_to_remove, reverse=True):
            if i < len(self.obstacles):
                del self.obstacles[i]

    def draw(self, bg_surface):
        if bg_surface is not None:
            self.screen.blit(bg_surface, (0, 0))
        else:
            self.screen.fill((10, 20, 40))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 40))
        self.screen.blit(overlay, (0, 0))

        # Divisor de zonas
        pygame.draw.line(self.screen, (100, 150, 255),
                         (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 4)
        
        # Rectángulos de zona (muy tenue)
        zone_left = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT), pygame.SRCALPHA)
        zone_left.fill((50, 100, 255, 10))
        self.screen.blit(zone_left, (0, 0))
        
        zone_right = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT), pygame.SRCALPHA)
        zone_right.fill((255, 60, 60, 10))
        self.screen.blit(zone_right, (SCREEN_WIDTH // 2, 0))
        
        # Dibujar obstáculos
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, obs["color"],
                           (obs["x"] - obs["width"] // 2, obs["y"], obs["width"], obs["height"]))

        # Dibujar jugadores
        pygame.draw.circle(self.screen, self.player1["color"],
                          self.player1["pos"], self.player1["radius"])
        if not self.one_player:
            pygame.draw.circle(self.screen, self.player2["color"],
                              self.player2["pos"], self.player2["radius"])

        # HUD
        elapsed = pygame.time.get_ticks() - self.timer_start
        remaining_ms = max(0, self.timer_duration - elapsed)
        remaining_sec = remaining_ms // 1000
        
        timer_color = (255, 100, 100) if remaining_sec <= 10 else (0, 255, 100)
        timer_text = self.font_med.render(f"Tiempo: {remaining_sec}s", True, timer_color)
        timer_box = pygame.Surface((180, 46), pygame.SRCALPHA)
        timer_box.fill((20, 20, 20, 155))
        self.screen.blit(timer_box, (SCREEN_WIDTH // 2 - 90, 18))
        self.screen.blit(timer_text, timer_text.get_rect(center=(SCREEN_WIDTH // 2, 41)))
        
        life_color_p1 = (255, 100, 100) if self.lives_p1 <= 1 else (255, 255, 255)
        life_color_p2 = (255, 100, 100) if self.lives_p2 <= 1 else (255, 255, 255)
        if self.one_player:
            life_box = pygame.Surface((150, 46), pygame.SRCALPHA)
            life_box.fill((20, 20, 20, 155))
            self.screen.blit(life_box, (20, 18))
            lives_text = self.font_med.render(f"Vidas: {self.lives_p1}", True, life_color_p1)
            self.screen.blit(lives_text, (30, 26))
        else:
            left_box = pygame.Surface((150, 46), pygame.SRCALPHA)
            left_box.fill((20, 20, 20, 155))
            self.screen.blit(left_box, (20, 18))
            right_box = pygame.Surface((150, 46), pygame.SRCALPHA)
            right_box.fill((20, 20, 20, 155))
            self.screen.blit(right_box, (SCREEN_WIDTH - 170, 18))
            lives_left = self.font_med.render(f"Vidas: {self.lives_p1}", True, life_color_p1)
            lives_right = self.font_med.render(f"Vidas: {self.lives_p2}", True, life_color_p2)
            self.screen.blit(lives_left, (30, 26))
            self.screen.blit(lives_right, (SCREEN_WIDTH - 160, 26))

        # Botón volver
        is_hover = False
        if not self.party_mode:
            is_hover = self.hand_pos and self.back_button.collidepoint(self.hand_pos)
            btn_surf = pygame.Surface((self.back_button.width, self.back_button.height), pygame.SRCALPHA)
            btn_surf.fill((0, 180, 255, 180) if is_hover else (20, 20, 80, 160))
            self.screen.blit(btn_surf, self.back_button.topleft)
            pygame.draw.rect(self.screen, (0, 220, 255) if is_hover else (80, 80, 160),
                            self.back_button, 2, border_radius=8)
            back_t = self.font_med.render("Volver", True, (255, 255, 255))
            self.screen.blit(back_t, back_t.get_rect(center=self.back_button.center))

        hover_retry = False
        hover_menu = False

        # Game Over
        if self.game_over:
            box = pygame.Surface((SCREEN_WIDTH, 200), pygame.SRCALPHA)
            box.fill((0, 0, 0, 200))
            self.screen.blit(box, (0, SCREEN_HEIGHT // 2 - 100))
            
            end_text = self.font_big.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(end_text, end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
            
            status_text = self.winner_text if self.winner_text else "FIN"
            status_color = (0, 255, 140)
            if "JUGADOR 1" in status_text:
                status_color = (80, 170, 255)
            elif "JUGADOR 2" in status_text:
                status_color = (255, 90, 90)
            elif "SIN VIDAS" in status_text:
                status_color = (255, 120, 120)
            status_surf = self.font_med.render(status_text, True, status_color)
            self.screen.blit(status_surf, status_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

            if not self.party_mode:
                hover_retry = self.hand_pos and self.retry_button.collidepoint(self.hand_pos)
                hover_menu = self.hand_pos and self.menu_button.collidepoint(self.hand_pos)

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
            
            restart = self.font_small.render("ESC para volver al menu", True, (200, 200, 200))
            self.screen.blit(restart, restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)))

        if self.hand_pos:
            pygame.draw.circle(self.screen, (255, 200, 0), self.hand_pos, 15, 2)

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
            self.hand_pos = hand_pos

            if bg is not None:
                bg_surface = pygame.surfarray.make_surface(np.transpose(bg, (1, 0, 2)))
            else:
                bg_surface = None

            hands = self.hand_tracker.get_positions()
            # Asignar manos por zona
            p1_pos = None
            p2_pos = None
            for hand in hands:
                if hand[0] < SCREEN_WIDTH // 2:
                    p1_pos = hand
                elif hand[0] >= SCREEN_WIDTH // 2:
                    p2_pos = hand

            if self.one_player:
                p2_pos = None

            is_hover_back, is_hover_retry, is_hover_menu = self.draw(bg_surface)
            self.update(p1_pos, p2_pos)

            if self.party_mode and self.game_over and self.game_over_time is not None:
                if pygame.time.get_ticks() - self.game_over_time >= 1200:
                    self.sounds["break"].play()
                    return self.winner_text 

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
