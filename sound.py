import pygame
import time
import threading

global fading
fading = True

pygame.mixer.init(frequency = 44100, size= -16, channels = 1, buffer= 2**12)

def main():
    print("")


    channel1 = pygame.mixer.Channel(0)
    channel2 = pygame.mixer.Channel(1)
    
    track01 = pygame.mixer.Sound("tracklist/track01.wav")
    track02 = pygame.mixer.Sound("tracklist/track02.wav")

    channel1.play(track01)
    channel1.fadeout(8000)
    time.sleep(8)
    
    
    t = threading.Thread(group=None, target=fade_in, args=(channel2,))
    t.start()

    channel2.play(track02)
    
    time.sleep(4)




def fade_in(channel):
    global fading
    counter = 0
    starttime= time.time()
    while fading:
        channel.set_volume(counter)
        counter = counter + 0.00025
        if counter == 1:
            fading = False
            break
        time.sleep(0.001 - (time.time() -starttime) % 0.001)
       






if __name__ == "__main__":
    main()