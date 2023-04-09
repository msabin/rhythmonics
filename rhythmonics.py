import pygame
import math
import numpy as np


# CONSTANTS

CONSOLE_WIDTH = 900
CONSOLE_HEIGHT = 500


NUM_OVERTONES = 7

BALL_RADIUS = 7


SMOOTH_SLIDE = True
TYPESET = True




class Console:
    def __init__(self, origin, size, startHz):
        self.surf = pygame.Surface(size)

        self.origin = origin

        self.baseColor = (0xff,0xb3,0xc6) #(169,193,255)
        self.secColor = (0,0x97,0x94)

        consoleSize = pygame.Vector2(size)


        screenSize = ((425/900)*size[0], (350/500)*size[1])

        screenCenter = pygame.Vector2(screenSize[0]/2, screenSize[1]/2)
        consoleCenter = consoleSize/2
        screenOrigin = consoleCenter - screenCenter - (0,20)

        screenColor = (112, 198, 169)
        self.screen = Screen(screenOrigin, screenSize, screenColor, startHz)

        self.overtones = self.screen.overtones

        self.radios = [overtone.radio for overtone in self.overtones]

        

    
        labelsFontSize = 18
        #path = pygame.font.match_font('Abadi MT Condensed Extra Bold')
        labelsFont = pygame.font.Font('Menlo.ttc', labelsFontSize)
        labelsCol = (0,0,0) #(76,100,161)

        labels = [labelsFont.render('Hz', True, labelsCol), labelsFont.render('BPM', True, labelsCol), 
                  labelsFont.render('FREEZE', True, labelsCol), labelsFont.render('GROOVE', True, labelsCol), 
                  labelsFont.render('CHAOS', True, labelsCol), labelsFont.render('HARMONY', True, labelsCol), 
                  labelsFont.render('EEEEEE', True, labelsCol)]
        

        digitalFontSize = 30
        digitalFont = pygame.font.Font('digital-7 (mono).ttf', digitalFontSize)

        digitalOn = (0,0xcf,0xdd)
        digitialOff = (0,0x52,0x60)
        digitialBG = (0,0x35,0x55)

        HzBox = digitalFont.render(' 8888.88 ', False, digitialOff, digitialBG)  #digital box to print Hz on
        BPM_Box = digitalFont.render(' 888888 ', False, digitialOff, digitialBG)
        displayBoxes = [HzBox, BPM_Box]


        sliderAreaOrigin = (20 , 30)
        sliderAreaHeight = consoleSize[1]*.9

        #Slider's "voltage" will control VCOs (oscillators) of the overtones
        self.slider = SliderArea(sliderAreaOrigin, sliderAreaHeight, self.overtones, self.secColor, labels, displayBoxes, digitalFont, digitalOn)

        self.ratioDisp = RatioDisp()


        

        

    def draw(self, targetSurf):
        self.surf.fill(self.baseColor)

        pygame.draw.rect(self.surf, self.secColor, (self.screen.origin - (50,15), (self.screen.size[0]+100,self.screen.size[1]+60)), border_radius=5, border_bottom_right_radius=40)
        self.screen.draw(self.surf)

        self.slider.draw(self.surf)
        for radio in self.radios: radio.draw(self.surf)

        targetSurf.blit(self.surf, self.origin)



class Screen:
    def __init__(self, origin, size, color, startHz):
        self.size = size
        self.surf = pygame.Surface(size)

        self.origin = origin
        self.color = color


        #Handcraft polygon aesthetics for the screen
        rootColor = (237,199,176)
        thirdColor = (118,150,222)
        fifthColor = (255,151,152)
        seventhColor = (139,72,82)
        
        rootRadius = (.9 * min(size[0], size[1]))/2
        center = pygame.Vector2(size[0]/2, size[1]/2)
        

        root1 = Polygon(1,rootRadius, center, rootColor, isPointy=False)
        root2 = Polygon(2,rootRadius/math.sqrt(2), center, rootColor, isPointy=False)
        fifth1 = Polygon(3, rootRadius/math.sqrt(2), center, fifthColor)
        root3 = Polygon(4,rootRadius, center, rootColor)
        third1 = Polygon(5,fifth1.inCirc, center, thirdColor)
        fifth2 = Polygon(6,rootRadius/math.sqrt(2), center, fifthColor)
        seventh1 = Polygon(7,third1.inCirc, center, seventhColor)

        self.polys = [root1, root2, fifth1, root3, third1, fifth2, seventh1]

        self.overtones = [Overtone(len(poly.verts), poly, startHz) for poly in self.polys]

    def draw(self, targetSurf):
        self.surf.fill(self.color)

        for overtone in self.overtones: 
            overtone.poly.draw(self.surf)

            if overtone.active: overtone.poly.ball.draw(self.surf)

        targetSurf.blit(self.surf, self.origin)


class SliderArea:
    def __init__(self, origin, height, overtones, color, labels, displayBoxes, digitalFont, digitalCol):
        self.overtones = overtones

        self.origin = origin
        self.height = height

        self.color = color



        self.HzLabel = labels.pop(0)
        self.BPM_Label = labels.pop(0)
        self.labels = labels

        self.HzBox = displayBoxes[0]
        self.BPM_Box = displayBoxes[1]

        self.digitalFont = digitalFont
        self.digitalCol = digitalCol
        self.HzDisp = digitalFont.render(" " + f'{self.overtones[0].Hz:07.2f}'.replace("1", " 1") + " ", False, self.digitalCol)
        self.BPM_Disp = digitalFont.render(" " + f'{self.overtones[0].Hz * 60:06.0f}'.replace("1", " 1") + " ", False, self.digitalCol)


    
        self.verticalBuf = 35

        self.sliderMiny = self.origin[1] + self.HzBox.get_height() + self.verticalBuf
        self.sliderMaxy = self.origin[1] + self.height - self.BPM_Box.get_height() - self.verticalBuf
        
        self.labelsWidth = max([label.get_width() for label in labels])
        self.horizontalBuf = 20
        sliderOffset = self.origin[0] + max(self.labelsWidth, self.BPM_Box.get_width()) + self.horizontalBuf
        sliderStart = .25        #slider knob starts at this fraction of the slider range

        self.sliderPos = pygame.Vector2(sliderOffset, self.sliderMaxy-sliderStart*(self.sliderMaxy-self.sliderMiny))

                

    def draw(self, surface):
        if TYPESET: pygame.draw.rect(surface, (0,0,0), (self.origin, (self.HzBox.get_width() + self.horizontalBuf + self.BPM_Label.get_width(), self.height)), 1)

        sliderRutCol = (150,150,150)
        pygame.draw.line(surface, sliderRutCol, (self.sliderPos[0], self.sliderMiny), (self.sliderPos[0], self.sliderMaxy), width=2) #slider track visualized
        sliderWidth = 10
        pygame.draw.circle(surface, self.color, self.sliderPos, 10)   #slider handle

        surface.blit(self.HzBox, (self.origin[0], self.origin[1]))
        surface.blit(self.HzDisp, (self.origin[0], self.origin[1]))
        surface.blit(self.HzLabel, (self.origin[0]+self.HzBox.get_width()+self.horizontalBuf,self.origin[1]))

        
        for i, label in enumerate(self.labels):
            surface.blit(label, (self.sliderPos[0] - sliderWidth - self.horizontalBuf - label.get_width(), (self.sliderMaxy - label.get_height()/2) - (i/4)*(self.sliderMaxy - self.sliderMiny))) 

        surface.blit(self.BPM_Box, (self.origin[0], self.origin[1] + self.height - self.BPM_Box.get_height()))
        surface.blit(self.BPM_Disp, (self.origin[0], self.origin[1] + self.height - self.BPM_Box.get_height()))
        surface.blit(self.BPM_Label, (self.origin[0]+self.BPM_Box.get_width()+self.horizontalBuf,self.origin[1] + self.height - self.BPM_Box.get_height()))



    def updateVolt(self, sliderSelected, beat_offset, clock):  #slider's position/"voltage" affects VCOs' Hz. Use clock to find phase

        HzScale = abs(self.sliderPos[1] - self.sliderMaxy)/(self.sliderMaxy - self.sliderMiny)

        if HzScale <= .25:
            Hz = HzScale/.25                                                    #Up to quarter of the way, linear scales up to 1Hz=60bpm
            if Hz <= .02: Hz = 0                                            #if it's too slow, just set it to 0
        elif HzScale <= .5:
            Hz = (1-(HzScale -.25)/.25) +   275/60 * (HzScale-.25)/.25     #linear scales up to 275/60Hz = 275bpm
        elif HzScale <= .75:
            Hz = 275/60 + (110-275/60)*math.log(1 + (HzScale - .5)/.25, 2)  #log scales up to 110Hz (4th harmonic/2nd octave will be 440Hz)    
        else:   
            Hz = 110 + (2000-110)*math.log(1 + (HzScale - .75)/.25, 2)        #caps at 2000 Hz (seventh harmonic will be at 14000Hz)


        hzStr = " " + f'{Hz:07.2f}'.replace("1", " 1") + " "
        self.HzDisp = self.digitalFont.render(hzStr, False, self.digitalCol)

        bpmStr = " " + f'{Hz*60:06.0f}'.replace("1", " 1") + " "
        self.BPM_Disp = self.digitalFont.render(bpmStr, False, self.digitalCol)



        ms_per_beat = 1000/self.overtones[0].Hz #Keep ms_per_beat based on fundamental freq unless slider is not selected and we update fundamental Hz

        if SMOOTH_SLIDE or (not sliderSelected):  #if slider isn't selected we *now* update the VCOs
        
            if Hz == 0: 
                ms_per_beat = 0
                for overtone in self.overtones: overtone.oscillator.stop() #kill all oscillators

            else: 
                ms_per_beat = 1000/Hz 

                buffer_time = (1/Hz)*26            #start updated soundwaves in the future by buffer_time and then wait to play them (sync with graphics)


                beat_offset = (beat_offset + clock.get_time()) % ms_per_beat
                clock.tick()

                for overtone in self.overtones: overtone.updateHz(Hz, (beat_offset+buffer_time)/ms_per_beat)

                if SMOOTH_SLIDE: 
                    for overtone in self.overtones: overtone.oscillator.set_volume(0)

                pygame.time.delay(int(max(buffer_time - clock.tick(), 0)))    #wait to play sounds until caught up to extra buffer time

                for overtone in self.overtones: overtone.oscillator.play(loops=-1) #play them all at the same time



        return (beat_offset, ms_per_beat)


class RadioBtn:
    def __init__(self, num, color):
        miny = 75
        maxy = CONSOLE_HEIGHT-miny

        self.pos = pygame.Vector2(CONSOLE_WIDTH - 140, miny + (num-1)*(maxy-miny)/6)


        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, (255,255,255), self.pos, 6, 1)

        pygame.draw.circle(surface, self.color, self.pos, 5)


class RatioDisp:
    def __init__(self) -> None:
        pass





class Overtone:
    def __init__(self, overtone, poly, fundHz, fundPhase = 0):       #Hz and phase all with respect to the fundamental tone of the overtones
        self.Hz = fundHz * overtone
        self.phase = fundPhase * overtone
        self.overtone = overtone


        self.oscillator = Oscillator(self.Hz, self.phase)
        self.oscillator.set_volume(0)

        self.poly = poly

        self.radio = RadioBtn(overtone, poly.color)

        self.active = False

    def updateHz(self, fundHz, fundPhase):
        self.Hz = fundHz * self.overtone

        self.phase = fundPhase * self.overtone
        self.oscillator.stop()

        self.oscillator = Oscillator(self.Hz, self.phase)
        if self.active:
            if not SMOOTH_SLIDE: self.oscillator.set_volume(1)
        else:
            self.oscillator.set_volume(0)

    def setActive(self, active):
        self.active = active

        if active: 
            if not SMOOTH_SLIDE: self.oscillator.set_volume(1)
        else:
            self.oscillator.set_volume(0)



def Oscillator(Hz, phase=0, sampRate=44100): #phase in relative terms: in [0,1] and represents fraction of period of Hz to offset
        
        dtype = "int8"
        maxVal = np.iinfo(dtype).max

        secs = 1/Hz  #Get exactly enough samples for a full wave cycle
        periodLength = int(secs*sampRate)
        pulseWidth = min(50, (1/3)*periodLength)

        startPulse = ((1-phase)%1)*periodLength           #for phase in [0,1] of one cycle, start pulse at 1-phase fraction of periodLength (neg vals work via mod 1)
        endPulse = startPulse + pulseWidth                #end pulse after its width, with possilbe wrap-around
        endWrap = min(endPulse, endPulse % periodLength)
        wrap = bool(endWrap < endPulse)

        wave = np.array([maxVal/NUM_OVERTONES if (i >= startPulse and i <= endPulse) or (wrap and i <= endWrap) else -maxVal/NUM_OVERTONES for i in range(periodLength)], dtype=dtype)

  
        return pygame.sndarray.make_sound(wave)


class Polygon:
    def __init__(self, numVert, radius, center, color, isPointy = True):
        self.radius = radius   #should I include these as attributes here?
        self.center = center
        self.color = color
        self.isPointy = isPointy

        self.verts = []
        
        for i in range(numVert):
            p = pygame.Vector2()

            p.x = center[0] + radius * math.cos(math.pi/2 - 2*math.pi/numVert * i)      
            p.y = center[1] - radius * math.sin(math.pi/2 - 2*math.pi/numVert * i)

            self.verts.append(p)  
      
        if isPointy:
            self.inCirc = math.dist(center, (self.verts[0]+self.verts[1])/2)
        #self.outCirc = self.inCirc/math.cos(math.pi/numVert)

        self.ball = Ball(self)

    
    def draw(self, surface):
        if self.isPointy:
            pygame.draw.polygon(surface, self.color, self.verts, width=2)
        else:
            pygame.draw.circle(surface, self.color, self.center, self.radius, width=3)
    

class Ball:
    def __init__(self, poly, alpha=255, isHead=True):
        self.poly = poly
        self.alpha = alpha
        self.isHead = isHead

        self.pos = poly.verts[0]
        self.color = poly.color

        self.surf = pygame.Surface((BALL_RADIUS*2, BALL_RADIUS*2))
        self.surf.set_colorkey((0,0,0))
        self.surf.set_alpha(alpha)
        pygame.draw.circle(self.surf, self.color, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)

        if isHead: self.tail = Tail(self)
        

    def updatePos(self, beat_offset, ms_per_beat): #subDiv in [0,1]
        if ms_per_beat == 0: return    #ARE THERE BEST PRACTICES FOR WHERE TO CHECK FOR DIV BY 0? TOOK THIS OUT BECAUSE DONE WHEN CALLED IN EVENT LOOP

        subDiv = beat_offset/ms_per_beat
        
        if self.poly.isPointy:
            n = len(self.poly.verts)

            bigSubDiv = (subDiv * n) % n  #bigSubDiv in [0,n), subDiv can be negative
            k = math.floor(bigSubDiv)     #biggest integer below bigSubDiv is the most recent vertex the ball has left

            self.pos = self.poly.verts[k].lerp(self.poly.verts[(k+1)%n], bigSubDiv - k) #interpolate the vertices by normalized sub-division between them


        else:
            radius = self.poly.radius
            center = self.poly.center

            self.pos = pygame.math.Vector2(center[0] + radius * math.cos(math.pi/2 - 2*math.pi*subDiv), center[1] - radius * math.sin(math.pi/2 - 2*math.pi*subDiv))

        if self.isHead: self.tail.updatePos(beat_offset, ms_per_beat)


    def draw(self, screen): 
        if self.isHead: self.tail.draw(screen)

        screen.blit(self.surf, self.pos - pygame.math.Vector2(BALL_RADIUS, BALL_RADIUS))
        

class Tail:
    def __init__(self, ball):
        self.head = ball


        # perimeter of the polygon the trail is on that it will need to cover
        self.perimeter = 0
        if self.head.poly.isPointy:
            self.perimeter = len(self.head.poly.verts) * math.dist(self.head.poly.verts[0], self.head.poly.verts[1])
        else:
            self.perimeter = 2*math.pi*self.head.poly.radius


        polyCover = self.perimeter/(2*BALL_RADIUS) #num of balls needed to cover its polygon's perimeter
        self.tailLength = int(3.5*polyCover)         #Make the num of balls in tail longer than polyCover so it can wrap into its tail at high Hz and become opaque
        #alphaRate =1

        self.alphaTail = [Ball(self.head.poly, self.head.alpha*(1 - math.log(1 + (i+1)/self.tailLength, 2)), isHead=False) for i in range(self.tailLength)]


    
    def updatePos(self, beat_offset, ms_per_beat):
        fadeTime = 22  #ms it takes for ball image to fade completely
                       #operationally, this will determine how far back in time the tail reaches back before fading completely


        #When the Hz gets too high, the balls will separate from each other because fadeTime is too long relative to Hz
        #So we create a max distance that they can go back so the tail sticks together at high Hz
        maxDist = self.tailLength*BALL_RADIUS  #trail can get long enough to pull the balls apart more than them overlapping by their radius
        ms_per_pixel = ms_per_beat/self.perimeter
        ms_per_dist = ms_per_pixel * maxDist        #ms required for a ball to travel the maxDist on its polygon

        fadeTime = min(fadeTime, ms_per_dist) #drop a trail ball back in time by the default fadeTime ms or only back enough that the tail sticks together
        for i, ball in enumerate(self.alphaTail):
            ball.updatePos(beat_offset - fadeTime*((i+1)/self.tailLength), ms_per_beat)

    def draw(self, console):
        for ball in reversed(self.alphaTail): #draw the lightest, furthest tail elements under the rest
            ball.draw(console)




    




class main:

    pygame.mixer.init(channels=1)
    pygame.init()


    pygame.mouse.set_cursor(pygame.cursors.tri_left)
    #dispaySize = pygame.display.get_desktop_sizes()

    windowSize = (900, 500)
    window = pygame.display.set_mode(windowSize)

    Hz =  1

    consoleOrigin = (0,0)
    consoleSize = windowSize
    console = Console(consoleOrigin, consoleSize, Hz)

    overtones = console.overtones
    slider = console.slider
    radios = console.radios
    screen = console.screen

    polys = screen.polys
    balls = [poly.ball for poly in polys]

    
    

    console.draw(window)

    clock = pygame.time.Clock()
    clock.tick()

    for overtone in overtones: overtone.oscillator.play(loops=-1)

    overtones[0].active = True
    overtones[0].oscillator.set_volume(1)

    
    user_done = False
    sliderSelected = False

    ms_per_beat = 1000/Hz #how many milliseconds in a beat
    beat_offset = 0

    while not user_done:


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                user_done = True
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if math.dist(slider.sliderPos, event.pos) <= 10:
                        sliderSelected = True

                        offset_y = slider.sliderPos[1] - event.pos[1]

                    else:
                        for overtone in overtones:
                            if (math.dist(overtone.radio.pos, event.pos) <= 5):  #if one of the overtones' radio buttons is clicked, toggle it on/off

                                overtone.setActive(not overtone.active)

            
            elif (event.type == pygame.MOUSEMOTION):
                if sliderSelected:                              #update slider position (but don't affect anything until mouse released)
                    y = min(event.pos[1], slider.sliderMaxy - offset_y)
                    y = max(y, slider.sliderMiny - offset_y)

                    slider.sliderPos[1] = offset_y + y

                    (beat_offset, ms_per_beat) = slider.updateVolt(sliderSelected, beat_offset, clock)

                    console.draw(window)



            elif event.type == pygame.MOUSEBUTTONUP:
                if (event.button == 1) and sliderSelected:         #update Hz if the slider was selected and now released

                    sliderSelected = False                    #unselect slider and then update slider's affect on Hz

                    #if not SMOOTH_SLIDE: (beat_offset, ms_per_beat) = slider.updateVolt(sliderSelected, beat_offset, clock)

            

            
        if ms_per_beat != 0:
            beat_offset = (beat_offset + clock.get_time()) % ms_per_beat

            clock.tick()

        for overtone in overtones:
            if overtone.active == True:
                #if ms_per_beat != 0: 
                overtone.poly.ball.updatePos(beat_offset, ms_per_beat)   #updates ball position (ball also updates the position of its tail)


        screen.draw(window)
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

main()