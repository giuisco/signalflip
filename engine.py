import os
import pygame.mixer as m
import time
import threading
import queue

# this is a FIFO queue to log the last 100 interactions the software did
global debuglog
debuglog = queue.Queue(100)

# boolean if the main engine loop is running this is true
global running
running = True

# a list with all the tracknames
global tracklist
tracklist = []

# channels that will be used
global channel1, channel2, channel3, channel4, channel5, channel6, channel7

# 2d array as overlay to map sounds to the space
global grid

# current position coordinates
global xcoord, ycoord
xcoord = 0
ycoord = 0

# last active location 
global oldx, oldy
oldx = 0
oldy = 0

# initialize the mixer module
m.init(frequency = 44100, size= -16, channels = 1, buffer= 2**12)



#--------- Main
#--- this is started when booting the software

def main(): 
    print("hello world")

    # load all available tracknames
    get_tracklist()

    # initialize channels to default
    init_channels()

    # create the grid
    init_grid()
    # map the audios to the grid
    map_audios()


    # start thread that is killing engine after time given by args
    t = threading.Thread(group=None, target=stop_loop, args=(10,))
    t.start()
    
    # start engine
    start_loop()

###########################

# this method is used to add a log message to the debuglog
def add_to_log(msg):
    global debuglog
    if debuglog.full():
        debuglog.get()
    debuglog.add(msg)


#---------- Overlay

# create a grid with 7x7 cells
def init_grid():
    global grid
    w = 8
    h = 8
    grid = [[0 for x in range(w)] for y in range(h)]


# define which grid position corresponds to which track
def map_audios():
    global tracklist, grid, channel1, channel2

    # currently only two tracks are mapped. for even position coordinates track1 else track2
    for x in range(len(grid)-1):
        for y in range(len(grid)-1):
            if x % 2 == 0:
                grid[x][y] = channel1
            else:
                grid[x][y] = channel2


## deprecated maybe needed later at some point for debugging
#def print_grid():
#    for x in range(len(grid)-1):
#        for y in range(len(grid)-1):
#            print(grid[x][y] + " | ", end='')
#        print("\n")




#------------------------ GPS

# this returns the currently active x position coordinate as int
def get_current_xpos():
    global xcoord
    return int(xcoord)

# this returns the currently active y position coordinate as int
def get_current_ypos():
    global ycoord
    return int(ycoord)

# this sets a new x coordinate as active and saves the old x coordinate for later reference
def set_current_xpos(xposition):
    global xcoord, oldx
    oldx = get_current_xpos()
    xcoord = xposition

# this sets a new x coordinate as active and saves the old x coordinate for later reference
def set_current_ypos(yposition):
    global ycoord, oldy
    oldy = get_current_ypos()
    ycoord = yposition


# this reads fake gps coordinates from a file and uses them as index without translation(!)
def read_pos_from_file():
    with open("positions.txt", "r") as file:
        positions = file.read().split(",")
        set_current_xpos(positions[0])
        set_current_ypos(positions[1])

# check if the current position is mapable to the grid
# true if inside the grid false else
def check_bounds():
    global grid
    if get_current_xpos() > grid.length or get_current_ypos() > grid.length:
        return False
    else:
        return True



#------------ Engine

# this is the main loop that gets executed and starts all subroutines
def start_loop():
    global running, oldx, oldy
    while running:
        

        # check current position
        read_pos_from_file()
        # translate position to grid
        
        # diff in audio? -> change needed?
        if diff_in_audio():
            # get channel that played old track
            oldchannel = grid[oldx][oldy]
            # get channel that is supposed to be played now
            newchannel = grid[get_current_xpos()][get_current_ypos()]

            # start new subroutine that fades out the old track
            t_old = threading.Thread(group=None, target=fade_out, args=(oldchannel,))
            t_old.start()
            print("changing tracks")

            # start new subroutine that fades in the new track
            t_new = threading.Thread(group=None, target=fade_in, args=(newchannel,))
            t_new.start()

        # pause all channels with 0 volume
        pause_muted_channels()
        # resume all channels with volume > 0
        play_channels()

        # check if the loop shall be continued
        running = check_running()

        # wait before executing update
        time.sleep(0.1)


# killswitch for testing purposes
def stop_loop(t):
    stopmsg = "\nstopping in {tim}s".format(tim=t)
    print(stopmsg)
    time.sleep(t)
    print("i died")
    exit(1)

# check if the loop shall be continued
def check_running():
    return running




#--------------- Audio

# this initializes all global defined channels
# setsvolume of channel to 0 
# plays and instantly pauses track that will be looped on this channel
def init_channels():
    global channel1, channel2, channel3, channel4, channel5, channel6, channel7

    channel1 = m.Channel(0)
    channel2 = m.Channel(1)
    # channel3 = m.Channel(2)
    # channel4 = m.Channel(3)
    # channel5 = m.Channel(4)
    # channel6 = m.Channel(5)
    # channel7 = m.Channel(6)

    channel1.set_volume(0)
    channel2.set_volume(0)

    channel1.play(m.Sound("tracklist/track01.wav"))
    channel1.pause()
    channel1.set_volume(0)

    channel2.play(m.Sound("tracklist/track02.wav"))
    channel2.pause()
    channel2.set_volume(0)

# this compares the current grid position with the old grid position
# if there is a difference this returns True
def diff_in_audio():
    global oldx,oldy
    if grid[get_current_xpos()][get_current_ypos()] == grid[oldx][oldy]:
        return False
    else:
        return True

# this checks all channels volume parameter, if its set to 0 the channel will be paused
def pause_muted_channels():
    if channel1.get_volume() == 0:
        channel1.pause()
    if channel2.get_volume() == 0:
        channel2.pause()

# this checks all channels vvolume parameter, if its higher than 0 the channel will be unpaused
def play_channels():
    if channel1.get_volume() > 0:
        channel1.unpause()
    if channel2.get_volume() > 0:
        channel2.unpause()


# fade in on the given channel 
def fade_in(channel):
    counter = 0
    starttime= time.time()
    while counter < 1:
        channel.set_volume(counter)
        counter = counter + 0.00025
        time.sleep(0.001 - (time.time() -starttime) % 0.001)
       

# fade out on the given channel
def fade_out(channel):
    counter = 1
    starttime= time.time()
    while counter > 0:
        channel.set_volume(counter)
        counter = counter - 0.00025
        time.sleep(0.001 - (time.time() -starttime) % 0.001)
       

# reads all songnames in the tracklist directory and creates a string list from it
def get_tracklist():
    global tracklist
    cmd = "cd tracklist && ls >tracklist.txt"
    os.system(cmd)
    with open("tracklist/tracklist.txt", "r") as file:
        data = file.read()
        data = data.split("\n")
        for i in range(0, len(data)-2):
            tracklist.append(data[i])
        print(tracklist)

## deprecated maybe used for debugging later
#def play_track(id):
#    global tracklist
#    m.init()
#    trackname = "tracklist/" + tracklist[id]
#    my_sound = m.Sound(trackname)
#    my_sound.play()
#


if __name__ == "__main__":
    main()