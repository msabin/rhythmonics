"""
Run the main event loop for the rhythmonics program.

This file imports the local file interface.py to instantiate the GUI
console of rhythmonics and runs an event loop to allow interactions
with the console, update the console components, and draw the console.
"""

import pygame
import math

import interface
import testSettings

SMOOTH_SLIDE = testSettings.SMOOTH_SLIDE

# Initialize pygame's mixer to be a mono channel then initialize the rest of pygame.
pygame.mixer.init(channels=1)
pygame.init()

pygame.mouse.set_cursor(pygame.cursors.tri_left)

# TODO: should I get the screen size or something like that?  Should I set the os at top?
windowSize = (1050, 625)
windowCenter = pygame.Vector2(windowSize[0]/2, windowSize[1]/2)
window = pygame.display.set_mode(windowSize)

# Instantiate rythmonics' console interface and create variables for the components of the console that will be used in the event loop.
Hz =  1
consoleSize = (1000, 560)
consoleCenter = pygame.Vector2(consoleSize[0]/2, consoleSize[1]/2)
consoleOrigin = windowCenter - consoleCenter
console = interface.Console(consoleOrigin, consoleSize, Hz)

screen = console.screen
overtones = console.overtones
slider = console.sliderArea.slider
radios = console.radioArea.radios
killSwitch = console.radioArea.killSwitch

polys = screen.polys
balls = [poly.ball for poly in polys]


# Begin the clock that will sync movement and sound.
clock = pygame.time.Clock()
clock.tick()

# Initially start all the overtones (silently) playing at the same time to be in sync.
for overtone in overtones: overtone.oscillator.play(loops=-1)

# Turn the second and third overtones on for the user to begin with and draw the console.
radios[1].press()
radios[2].press()

console.draw(window)

# Set variables to begin the main event loop
user_done = False

ms_per_beat = 1000/Hz  # Set how many milliseconds are in a beat.
beat_offset = 0

# Begin the event loop that runs until a user quits.
while not user_done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            user_done = True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                posOnConsole = event.pos - console.origin  # Set position relative to console origin instead of window origin.

                if slider.handle.collidepoint(posOnConsole):
                    slider.isSelected = True

                    offset_y = slider.pos[1] - posOnConsole[1]

                elif killSwitch.button.collidepoint(posOnConsole):
                    killSwitch.press()
                    console.draw(window)
                    
                else:
                    for radio in radios:
                        if math.dist(radio.pos, posOnConsole) <= radio.radius:
                            radio.press()
                            console.draw(window)
        
        elif event.type == pygame.MOUSEMOTION:
            # If the slider is selected, update its position and the "voltage" it controls which, in turn, controls the speed of the oscillators
            if slider.isSelected:
                posOnConsole = event.pos - console.origin  # Set position relative to console origin instead of window origin.

                # If the cursor is beyond the slider's range, clip it into the range.
                y = min(posOnConsole[1], slider.maxy - offset_y)
                y = max(y, slider.miny - offset_y)

                slider.pos[1] = offset_y + y

                (beat_offset, ms_per_beat) = slider.updateVolt(beat_offset, clock)

                console.draw(window)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:                           
                if slider.isSelected and not SMOOTH_SLIDE: 

                    slider.isSelected = False 

                    (beat_offset, ms_per_beat) = slider.updateVolt(beat_offset, clock)
                    console.draw(window)

                slider.isSelected = False 

                if killSwitch.isPressed:
                    killSwitch.press()
                    console.draw(window)

        elif event.type == pygame.KEYDOWN:
            for i, radio in enumerate(radios, 1):
                if pygame.key.key_code(f'{i}') == event.key:
                    radio.press()
                    console.draw(window)

            if event.key == pygame.K_m:
                killSwitch.press()
                console.draw(window)

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_m and killSwitch.isPressed:
                killSwitch.press()
                console.draw(window)


    # Update how many milliseconds(ms) we are into a beat, tick the clock, and then update the positions of all the active balls on polygons.
    if ms_per_beat != 0:
        beat_offset = (beat_offset + clock.get_time()) % ms_per_beat

        clock.tick()

    for overtone in overtones:
        if overtone.active == True:
            overtone.poly.ball.updatePos(beat_offset, ms_per_beat)

    # Draw only the screen directly to the window.  The console only redraws itself for relevant events in the 
    # event loop, but the screen redraws every event loop to update the balls' movements.  Then update the whole
    # display on the screen.
    screen.draw(window, console.origin)
    pygame.display.flip()

    if SMOOTH_SLIDE:
        # Fade the volume of active oscillators in over event loop runs to maximum volume.  All oscillators are 
        # started muted and this loop increments the volume of active oscillators by a constant each event loop 
        # until they're at maximum volume.  
        # 
        # This per-loop fading-in of volume is done so that we don't get gross clicks as the Hz are adjusted with 
        # the slider and all the oscillators are restarted repeatedly during the slide.  With the fade-in, it now 
        # sounds like an aesthic digital glitch instead of jarring clicks.  The constant that the volume is incremented
        # by is chosen low enough so that the noise during slider movement is pleasant and quiet but not so low that
        # the oscillators have too much delay in fading in.
        for overtone in overtones:
            if overtone.active:
                vol = overtone.oscillator.get_volume()
                if vol < 1:
                    vol = min(vol + .05, 1)
                    overtone.oscillator.set_volume(vol)              

pygame.QUIT # Event loop complete since userDone = True, so we should quit.