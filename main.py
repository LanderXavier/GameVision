import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import pygame
import cv2
from hand_tracker import HandTracker
from pose_tracker import PoseTracker
from menu import Menu, PlayerSelectScreen, PartyResultScreen
from menu_about import AboutScreen
from games.pong import PongGame
from games.dodge import DodgeGame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
SOUNDTRACK_DIR = os.path.join(SOUNDS_DIR, "soundtrack")

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("EyeToy Games")

    sounds = {}
    try:
        sounds["accept"] = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "acept.wav"))
        sounds["break"] = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "break.wav"))
        sounds["point"] = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "point.wav"))
        sounds["pong"] = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "pong.wav"))
        sounds["win"] = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "win.wav"))
        sounds["accept"].set_volume(0.40)
        sounds["break"].set_volume(0.50)
        sounds["point"].set_volume(0.6)
        sounds["pong"].set_volume(0.5)
        sounds["win"].set_volume(0.8)
    except Exception:
        sounds = {}

    try:
        soundtrack_files = [
            f for f in os.listdir(SOUNDTRACK_DIR)
            if f.lower().endswith((".wav", ".ogg", ".mp3"))
        ]
        if soundtrack_files:
            pygame.mixer.music.load(os.path.join(SOUNDTRACK_DIR, soundtrack_files[0]))
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)
    except Exception:
        pass

    # Cámara para hand tracker (menú)
    cap_hand = None
    for i in range(4):
        c = cv2.VideoCapture(i)
        if c.isOpened():
            print(f"Cámara encontrada en índice {i}")
            cap_hand = c
            break
        c.release()

    if cap_hand is None:
        print("No se encontró ninguna cámara")
        pygame.quit()
        return

    cap_hand.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
    cap_hand.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)

    hand_tracker = HandTracker(cap_hand)
    pose_tracker = PoseTracker(cap_hand)  # misma cámara

    def normalize_winner(label, one_player):
        if label is None:
            return "EMPATE"
        text = str(label).upper()
        if one_player:
            if "CPU" in text:
                return "CPU"
            if "PLAYER" in text or "JUGADOR 1" in text:
                return "PLAYER"
            if "TIEMPO" in text:
                return "PLAYER"
            if "SIN VIDAS" in text:
                return "CPU"
            return "EMPATE"
        if "JUGADOR 1" in text or text == "P1":
            return "JUGADOR 1"
        if "JUGADOR 2" in text or text == "P2":
            return "JUGADOR 2"
        return "EMPATE"

    def run_party(one_player):
        game_results = []
        if one_player:
            total_score = {"PLAYER": 0, "CPU": 0}
        else:
            total_score = {"JUGADOR 1": 0, "JUGADOR 2": 0}

        pong_result = PongGame(
            screen,
            hand_tracker,
            pose_tracker,
            one_player=one_player,
            party_mode=True,
            sounds=sounds,
        ).run()
        if pong_result == "QUIT":
            return "QUIT"
        pong_winner = normalize_winner(pong_result, one_player)
        if pong_winner in total_score:
            total_score[pong_winner] += 1
        game_results.append(("Pong", pong_winner))

        dodge_result = DodgeGame(
            screen,
            hand_tracker,
            one_player=one_player,
            party_mode=True,
            sounds=sounds,
        ).run()
        if dodge_result == "QUIT":
            return "QUIT"
        dodge_winner = normalize_winner(dodge_result, one_player)
        if dodge_winner in total_score:
            total_score[dodge_winner] += 1
        game_results.append(("Dodge", dodge_winner))

        return PartyResultScreen(screen, hand_tracker, one_player, game_results, total_score, sounds=sounds).run()

    state = "MENU"
    while state != "QUIT":
        if state == "MENU":
            state = Menu(screen, hand_tracker, sounds=sounds).run()
        elif state == "Start Party":
            selected = PlayerSelectScreen(screen, hand_tracker, sounds=sounds).run()
            if selected == "QUIT":
                state = "QUIT"
            elif selected == "MENU":
                state = "MENU"
            elif selected == 1:
                state = run_party(one_player=True)
            elif selected == 2:
                state = run_party(one_player=False)
            else:
                state = "MENU"
        elif state == "About":
            state = AboutScreen(screen, hand_tracker, sounds=sounds).run()
        else:
            state = "MENU"

    cap_hand.release()
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    pygame.quit()

if __name__ == "__main__":
    os.makedirs("games", exist_ok=True)
    open("games/__init__.py", "a").close()
    main()