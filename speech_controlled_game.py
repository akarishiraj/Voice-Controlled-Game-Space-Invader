import pygame
import random
import math
from pygame import mixer
import pyaudio
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from threading import Thread
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from queue import Queue, Full
from threading import Thread

###############################################
#### Initalize queue to store the recordings ##
###############################################
CHUNK = 1024
# Note: It will discard if the websocket client can't consumme fast enough
# So, increase the max size as per your choice
BUF_MAX_SIZE = CHUNK * 10
# Buffer to store audio
q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK)))

# Create an instance of AudioSource
audio_source = AudioSource(q, True, True)

###############################################
#### Prepare Speech to Text Service ########
###############################################

# initialize speech to text service
authenticator = IAMAuthenticator('yTSSJ5GSmGhgIA95KnVPDf61KSZinztq909UBMfoqh7l')
speech_to_text = SpeechToTextV1(authenticator=authenticator)
speech_to_text.set_service_url("https://api.us-east.speech-to-text.watson.cloud.ibm.com/instances/77c94867-643f-431b-a593-0bc775c18bb7")

actions = []



def main():
    global actions
    bullet_state = "ready"
    # initialize the pygame
    pygame.init()
    # create the screen
    screen = pygame.display.set_mode((800, 600))  # width , height or x,y axis
    # Background
    background = pygame.image.load("images/background.png")
    running = True
    # Background Sound
    # mixer.music.load("background.wav")
    # mixer.music.play(-1)

    # title and icons
    pygame.display.set_caption("Space Invaders")
    icon = pygame.image.load("images/periscope.png")
    pygame.display.set_icon(icon)

    # Player
    playerImg = pygame.image.load("images/player.png")
    playerX = 370
    playerY = 480
    playerX_change = 0

    # enemy
    # Enemy
    enemyImg = []
    enemyX = []
    enemyY = []
    enemyX_change = []
    enemyY_change = []
    num_of_enemies = 6
    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load('images/enemy.png'))
        enemyX.append(random.randint(0, 736))
        enemyY.append(random.randint(50, 150))
        enemyX_change.append(4)
        enemyY_change.append(40)
    # Bullet
    bulletImg = pygame.image.load("images/bullet.png")
    bulletX = 0
    bulletY = 480  # coordinate of spaceship
    bulletX_change = 0
    bulletY_change = 10
    # ready- you cant see bullet on screen
    # fire- bullet is moving
    bullet_state = "ready"

    # Score
    score_value = 0
    font = pygame.font.Font('freesansbold.ttf', 32)

    textX = 10
    textY = 10

    # Game Over
    over_font = pygame.font.Font('freesansbold.ttf', 64)


    def game_over_text():
        over_text = over_font.render("GAME OVER", True, (255, 255, 255))
        screen.blit(over_text, (200, 250))


    def show_score(x, y):
        score = font.render("Score : " + str(score_value), True, (255, 255, 255))
        screen.blit(score, (x, y))


    def player(x, y):
        screen.blit(playerImg, (x, y))  # blit means draw


    def enemy(x, y, i):
        screen.blit(enemyImg[i], (x, y))  # blit means draw


    def fire_bullet(x, y):
        screen.blit(bulletImg, (x + 16, y + 10))  # 16 is added so that bullet look at the center of spaceship
        


    def isCollision(enemyX, enemyY, bulletX, bulletY):
        distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
        if distance < 25:
            return True
        else:
            return False


    # game loop
    while running:
        # RGB - red, green and blue
        screen.fill((0, 0, 0))
        # background image
        screen.blit(background, (0, 0))
        # playerX += 0.2 # to move right
        # playerX -=0.1  # to move left
        # playerY -= 0.1   # to move up

        for event in actions:
            if event == "quit":
                running = False
            if event == "left":
                playerX_change = -5
            if event == 'right':
                playerX_change = 5
            if event == 'shoot' or event == 'fire':
                if bullet_state == "ready":
                    bullet_sound = mixer.Sound("music/laser.wav")
                    bullet_sound.play()
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)
                    bullet_state = "fire"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # if keystroke is pressed check whether right or left
            if event.type == pygame.KEYDOWN:  # KEYDOWN means any key is pressed
                # print("KEY is pressed")
                if event.key == pygame.K_LEFT:
                    playerX_change = -5
                if event.key == pygame.K_RIGHT:
                    playerX_change = 5
                if event.key == pygame.K_SPACE:
                    if bullet_state == "ready":
                        bullet_sound = mixer.Sound("music/laser.wav")
                        bullet_sound.play()
                        bulletX = playerX
                        fire_bullet(bulletX, bulletY)
                        bullet_state = "fire"
            if event.type == pygame.KEYUP:  # when key is released
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0
        playerX += playerX_change
        # creating boundaries
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:  # 800-64 the size of spaceship
            playerX = 736
        for i in range(num_of_enemies):
            if enemyY[i] > 440:
                for j in range(num_of_enemies):
                    enemyY[j] = 2000
                game_over_text()
                break
            enemyX[i] += enemyX_change[i]
            # creating boundaries
            if enemyX[i] <= 0:
                enemyX_change[i] = 4
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 736:
                enemyX_change[i] = -4
                enemyY[i] += enemyY_change[i]

            collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                collision_sound = mixer.Sound("music/explosion.wav")
                collision_sound.play()
                bulletY = 480
                bullet_state = "ready"
                score_value += 1
                print(score_value)
                enemyX[i] = random.randint(0, 735)
                enemyY[i] = random.randint(50, 150)
            enemy(enemyX[i], enemyY[i], i)

        # bullet movement
        if bulletY <= 0:
            bulletY = 480
            bullet_state = "ready"
        if bullet_state is "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change

        player(playerX, playerY)  # remember to call player above screen.fill because player needs to be above on the
        # screen otherwise it
        # will not appear
        show_score(textX, textY)
        pygame.display.update()


# define callback for the speech to text service
class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_transcription(self, transcript):
        print("transcript\n",transcript)

    def on_connected(self):
        print('Connection was successful')

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))

    def on_listening(self):
        print('Service is listening')
        process = Thread(target=main)
        process.start()

        
    def on_hypothesis(self, hypothesis):
        print("hypothesis\n",hypothesis)
        if hypothesis:
            actions.extend(hypothesis.split())
    

    def on_data(self, data):
        pass
        # print(data)

    def on_close(self):
        print("Connection closed")




# this function will initiate the recognize service and pass in the AudioSource
def recognize_using_weboscket(*args):
    mycallback = MyRecognizeCallback()
    speech_to_text.recognize_using_websocket(audio=audio_source,
                                             content_type='audio/l16; rate=44100',
                                             recognize_callback=mycallback,
                                             interim_results=True)


###############################################
#### Prepare the for recording using Pyaudio ##
###############################################

# Variables for recording the speech
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# define callback for pyaudio to store the recording in queue
def pyaudio_callback(in_data, frame_count, time_info, status):
    try:
        q.put(in_data)
    except Full:
        pass # discard
    return (None, pyaudio.paContinue)

# instantiate pyaudio
audio = pyaudio.PyAudio()

# open stream using callback
stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=pyaudio_callback,
    start=False
)


if __name__ == '__main__':
    #########################################################################
    #### Start the recording and start service to recognize the stream ######
    #########################################################################

    print("Enter CTRL+C to end recording...")
    stream.start_stream()

    try:
        recognize_thread = Thread(target=recognize_using_weboscket, args=())
        recognize_thread.start()

        while True:
            pass
    except KeyboardInterrupt:
        # stop recording
        stream.stop_stream()
        stream.close()
        audio.terminate()
        audio_source.completed_recording()
    except Exception as e:
        print(e)