import math
import pygame
import random
import pyaudio
from pygame import mixer
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from command_service import activate, stop
from configuration import *
from threading import Thread
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

try:
    from Queue import Queue, Full
except ImportError:
    from queue import Queue, Full

CHUNK = 1024
BUF_MAX_SIZE = CHUNK * 10

# Variables for recording the speech
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# game actions
game_actions = ['left', 'right', 'shoot', 'jump', 'fire']

q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK)))
audio_source = AudioSource(q, True, True)


# define callback for pyaudio to store the recording in queue
def pyaudio_callback(in_data, frame_count, time_info, status):
    try:
        q.put(in_data)
    except Full:
        pass
    return (None, pyaudio.paContinue)


# define callback for the speech to text service


class Player:

    def __init__(self, player_img, x, y):
        self.playerImg = pygame.image.load(player_img)
        self.x = x
        self.y = y
        self.dx = 0

    def move(self, dx):
        self.x = self.x + dx

    def left(self):
        pass

    def right(self):
        pass

    def shoot(self, screen, bullet):
        if bullet.state == 'ready':
            bullet.sound.play()
            bullet.fire(screen, self.x, self.y)


class Bullet:
    def __init__(self, bullet_img, sound_file=BULLET_SOUND, x=0, y=PY):
        self.bulletImg = pygame.image.load(bullet_img)
        self.x = x
        self.y = y
        self.dx = 0
        self.state = "ready"
        self.sound = mixer.Sound(sound_file)

    def fire(self, screen, dx, dy):
        self.state = 'fire'
        screen.blit(self.bulletImg, (dx + 16, dy + 10))

    def isCollision(self, eX, eY, bX, bY):
        distance = math.sqrt(math.pow(eX - bX, 2) + (math.pow(eY - bY, 2)))
        return True if distance < 25 else False


class Game:
    textX = textY = 10

    def __init__(self,screen):
        self.screen = screen
        self.score = 0
        self.game_over = False
        self.running = False
        self.font = pygame.font.Font(FONT_PATH, 32)
        self.over_font = pygame.font.Font(FONT_PATH, 64)
        self.player = Player(PLAYER_PNG, PX, PY)
        self.enemyImg = []
        self.enemyX = []
        self.enemyY = []
        self.enemyX_change = []
        self.enemyY_change = []
        self.num_of_enemies = 6
        for i in range(self.num_of_enemies):
            self.enemyImg.append(pygame.image.load(ENEMY_PNG))
            self.enemyX.append(random.randint(0, 736))
            self.enemyY.append(random.randint(50, 150))
            self.enemyX_change.append(4)
            self.enemyY_change.append(40)

    def game_over_message(self, screen, msg=" GAME OVER !", whiteColor=(255, 255, 255)):
        over_text = self.over_font.render(msg, True, whiteColor)
        screen.blit(over_text, (200, 250))

    def show_score(self, screen, x, y):
        score = self.font.render("Score : " + str(self.score), True, (255, 255, 255))
        screen.blit(score, (x, y))


class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_transcription(self, transcript):
        # print(transcript)
        pass

    def on_connected(self):
        print('Connection was successful')

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))

    def on_listening(self):
        print('Service is listening')
        self.start_game()

    def on_hypothesis(self, hypothesis):
        actions = [word for word in hypothesis.split() if word in game_actions]
        for action in actions:
            self.update_game_world(action)

    def on_data(self, data):
        # print(data)
        pass

    def on_close(self):
        print("Connection closed")

    def start_game(self):
        self.game = Game()
        print(self.game)

    def update_game_world(self, action):
        print('game', action)
        pass


# setup speech service
stt = activate()

# instantiate pyaudio
audio = pyaudio.PyAudio()

# open stream using callback
stream = audio.open(
    format=FORMAT, channels=CHANNELS,
    rate=RATE, input=True, frames_per_buffer=CHUNK,
    stream_callback=pyaudio_callback, start=False)


# this function will initiate the recognize service and pass in the AudioSource
def recognize_using_weboscket(*args):
    mycallback = MyRecognizeCallback()
    stt.recognize_using_websocket(audio=audio_source,
                                  content_type='audio/l16; rate=44100',
                                  recognize_callback=mycallback,
                                  interim_results=True,
                                  )


def main(running=True):
    pygame.init()
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    background = pygame.image.load(BACKGROUND)
    pygame.display.set_caption(CAPTION)
    icon = pygame.image.load(ICON)
    pygame.display.set_icon(icon)
    game = Game()
    while running:
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))


if __name__ == '__main__':

    try:
        stream.start_stream()
        recognize_thread = Thread(target=recognize_using_weboscket, args=())
        recognize_thread.start()
        while True:
            pass
    except:
        stop(stream, audio, audio_source)
