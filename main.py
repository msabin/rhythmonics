"""
   main event loop running the rhythmonics program
   
   This file imports the local file interface.py to instantiate the GUI
   console of rhythmonics and run an event loop to allow interactions
   with the console, update the console components, and draw the console.
"""


import pygame
import math

import interface
import testSettings

SMOOTH_SLIDE = testSettings.SMOOTH_SLIDE



pygame.mixer.init(channels=1)
pygame.init()


pygame.mouse.set_cursor(pygame.cursors.tri_left)
#dispaySize = pygame.display.get_desktop_sizes()

windowSize = (1050, 625)
windowCenter = pygame.Vector2(windowSize[0]/2, windowSize[1]/2)
window = pygame.display.set_mode(windowSize)

consoleSize = (1000, 560)
consoleCenter = pygame.Vector2(consoleSize[0]/2, consoleSize[1]/2)
consoleOrigin = windowCenter - consoleCenter
Hz =  1
console = interface.Console(consoleOrigin, consoleSize, Hz)

screen = console.screen
overtones = console.overtones
slider = console.sliderArea.slider
radios = console.radioArea.radios
killSwitch = console.radioArea.killSwitch

polys = screen.polys
balls = [poly.ball for poly in polys]




radios[0].press()

console.draw(window)




clock = pygame.time.Clock()
clock.tick()

for overtone in overtones: overtone.oscillator.play(loops=-1)


user_done = False

ms_per_beat = 1000/Hz #how many milliseconds in a beat
beat_offset = 0

while not user_done:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            user_done = True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                posOnConsole = event.pos - console.origin

                if slider.handle.collidepoint(posOnConsole):
                    slider.isSelected = True

                    offset_y = slider.pos[1] - posOnConsole[1]

                elif killSwitch.button.collidepoint(posOnConsole):
                    killSwitch.press()
                    console.draw(window)
                    
                else:
                    for radio in radios:
                        if (math.dist(radio.pos, posOnConsole) <= radio.radius):  #if one of the overtones' radio buttons is clicked, toggle it on/off

                            radio.press()
                            console.draw(window)
        
        elif event.type == pygame.MOUSEMOTION:
            if slider.isSelected:                              #update slider position (but don't affect anything until mouse released)
                posOnConsole = event.pos - console.origin

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

                slider.isSelected = False 

                if killSwitch.isPressed:
                    killSwitch.press()
                    console.draw(window)

        elif event.type == pygame.KEYDOWN:
            for i, radio in enumerate(radios, 1):
                if pygame.key.key_code(f'{i}') == event.key:
                    radio.press()
                    console.draw(window)

        

        
    if ms_per_beat != 0:
        beat_offset = (beat_offset + clock.get_time()) % ms_per_beat

        clock.tick()

    for overtone in overtones:
        if overtone.active == True:
            #if ms_per_beat != 0: 
            overtone.poly.ball.updatePos(beat_offset, ms_per_beat)   #updates ball position (ball also updates the position of its tail)


    screen.draw(window, console.origin)
    pygame.display.flip()



    
    if SMOOTH_SLIDE:
        #fades volume in over event loops runs so that we don't get gross clicks as the Hz are adjusted with the slider
        for overtone in overtones:
            if overtone.active:
                vol = overtone.oscillator.get_volume()
                if vol < 1:
                    vol = min(vol + .05, 1)
                    overtone.oscillator.set_volume(vol)

    #clock.tick()                

pygame.QUIT