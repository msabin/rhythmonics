import pygame
import math
import numpy as np



# CONSTANTS
SMOOTH_SLIDE = True
TYPESET = False



class Console:
    def __init__(self, origin, size, startHz):
        self.surf = pygame.Surface(size)

        self.origin = origin

        self.baseColor = (0xff,0xbc,0xcf) #(169,193,255)
        self.secColor = (0,0x97,0x94)

        consoleSize = pygame.Vector2(size)

        self.console = pygame.Rect((0,0), consoleSize)


        screenSize = (425, 350)

        screenCenter = pygame.Vector2(screenSize[0]/2, screenSize[1]/2)
        consoleCenter = consoleSize/2
        screenOrigin = consoleCenter - screenCenter - (0,35)

        screenColor = (112, 198, 169)
        self.screen = Screen(screenOrigin, screenSize, screenColor, startHz)

        self.overtones = self.screen.overtones



        radioAreaOrigin = (810, 75)
        radioAreaSize = (135 , 350)

        self.radioArea = RadioArea(radioAreaOrigin, radioAreaSize, self.overtones)

        self.radios = self.radioArea.radios

        

    
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
        digitalOff = (0,0x55,0x63)
        digitalBG = (0,0x35,0x55)

        HzBox = digitalFont.render(' 8888.88 ', False, digitalOff, digitalBG)  #digital box to print Hz on
        BPM_Box = digitalFont.render(' 888888 ', False, digitalOff, digitalBG)
        displayBoxes = [HzBox, BPM_Box]


        sliderAreaOrigin = (55, 45)
        sliderAreaHeight = consoleSize[1]*.85

        #Slider's "voltage" will control VCOs (oscillators) of the overtones
        self.sliderArea = SliderArea(sliderAreaOrigin, sliderAreaHeight, self.overtones, self.secColor, labels, displayBoxes, digitalFont, digitalOn)



        ratioOrigin = screenOrigin + (108, screenSize[1] + 80)
        #ratioLength = screenSize[0]-40

        digitalSlot = digitalFont.render(f'8', False, digitalOff, digitalBG)
        ratioColon = labelsFont.render(':', False, labelsCol)

        self.ratioDisp = RatioDisp(ratioOrigin, self.overtones, digitalSlot, digitalFont, digitalOn, ratioColon)


    def draw(self, targetSurf):
        pygame.draw.rect(self.surf, self.baseColor, self.console, border_radius=50)

        pygame.draw.rect(self.surf, self.secColor, (self.screen.origin - (45,25), (self.screen.size[0]+90,self.screen.size[1]+75)), border_radius=5, border_bottom_right_radius=40)
        self.screen.draw(self.surf)

        self.sliderArea.draw(self.surf)
        
        self.radioArea.draw(self.surf)

        self.ratioDisp.draw(self.surf)

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
        seventhColor = (171,103,114) #(0xb1,0x9c, 0xd8)
        
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

        numOvertones = len(self.polys)
        self.overtones = [Overtone(len(poly.verts), poly, numOvertones, startHz) for poly in self.polys]

    def draw(self, targetSurf, offset = pygame.Vector2(0,0)):
        self.surf.fill(self.color)

        for overtone in self.overtones: 
            poly = overtone.poly

            poly.draw(self.surf)

            #if polygon is actually a circle, then draw tick marks to indicate where ball will make a click sound when it passed it
            if not poly.isPointy: 
                tickLength = 5
                for i, vert in enumerate(poly.verts):
                    xTick = math.cos(math.pi/2 - 2*math.pi * i/len(poly.verts))*tickLength
                    yTick = math.sin(math.pi/2 - 2*math.pi * i/len(poly.verts))*tickLength
                    pygame.draw.line(self.surf, (139,72,82), vert - (xTick , -yTick), vert + (xTick, -yTick), 2)


            if overtone.active: poly.ball.draw(self.surf)

        targetSurf.blit(self.surf, self.origin + offset)


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


        self.horizontalBuf = 20
    
        sliderSize = pygame.math.Vector2(20,40) #size of rectangular slider handle

        verticalBuf = 30
        sliderMiny = self.origin[1] + self.HzBox.get_height() + verticalBuf
        sliderMaxy = self.origin[1] + self.height - self.BPM_Box.get_height() - verticalBuf
        
        labelsWidth = max([label.get_width() for label in labels])
        sliderOffset = self.origin[0] + labelsWidth + self.horizontalBuf + sliderSize[0]
        sliderStart = .25        #slider knob starts at this fraction of the slider range

        sliderPos = pygame.Vector2(sliderOffset, sliderMaxy-sliderStart*(sliderMaxy-sliderMiny))


        self.slider = Slider(sliderPos, sliderSize, self.overtones, sliderMiny, sliderMaxy)

                

    def draw(self, surface):
        if TYPESET: pygame.draw.rect(surface, (0,0,0), (self.origin, (self.HzBox.get_width() + self.horizontalBuf + self.BPM_Label.get_width(), self.height)), 1)

        #draw slider groove and slider
        sliderRutCol = (150,150,150)
        pygame.draw.line(surface, sliderRutCol, (self.slider.pos[0], self.slider.miny), (self.slider.pos[0], self.slider.maxy), width=2) #slider track visualized
        self.slider.handle = pygame.Rect(self.slider.pos - self.slider.size/2, self.slider.size)
        pygame.draw.rect(surface, self.color, self.slider.handle)

        #Draw Hz display
        surface.blit(self.HzBox, (self.origin[0], self.origin[1]))

        HzDisp = self.digitalFont.render(" " + f'{self.overtones[0].Hz:07.2f}'.replace("1", " 1") + " ", False, self.digitalCol)
        surface.blit(HzDisp, (self.origin[0], self.origin[1]))

        surface.blit(self.HzLabel, (self.origin[0]+self.HzBox.get_width()+self.horizontalBuf/2,self.origin[1]))

        #Draw slider labels
        for i, label in enumerate(self.labels):
            surface.blit(label, (self.origin[0], (self.slider.maxy - label.get_height()/2) - (i/4)*(self.slider.maxy - self.slider.miny))) 

        #Draw BPM display
        surface.blit(self.BPM_Box, (self.origin[0], self.origin[1] + self.height - self.BPM_Box.get_height()))

        BPM_Disp = self.digitalFont.render(" " + f'{self.overtones[0].Hz * 60:06.0f}'.replace("1", " 1") + " ", False, self.digitalCol)
        surface.blit(BPM_Disp, (self.origin[0], self.origin[1] + self.height - self.BPM_Box.get_height()))

        surface.blit(self.BPM_Label, (self.origin[0]+self.BPM_Box.get_width()+self.horizontalBuf/2,self.origin[1] + self.height - self.BPM_Box.get_height()))


class Slider:
    def __init__(self, position, size, overtones, miny, maxy):
        self.pos = position
        self.size = size

        self.overtones = overtones

        self.miny = miny
        self.maxy = maxy

        self.isSelected = False

        self.handle = pygame.Rect(self.pos - self.size/2, self.size)

    def updateVolt(self, beat_offset, clock):  #slider's position/"voltage" affects VCOs' Hz. Use clock to find phase

        HzScale = abs(self.pos[1] - self.maxy)/(self.maxy - self.miny)

        if HzScale <= .25:
            Hz = HzScale/.25                                                    #Up to quarter of the way, linear scales up to 1Hz=60bpm
            if Hz <= .02: Hz = 0                                            #if it's too slow, just set it to 0
        elif HzScale <= .5:
            Hz = (1-(HzScale -.25)/.25) +   275/60 * (HzScale-.25)/.25     #linear scales up to 275/60Hz = 275bpm
        elif HzScale <= .75:
            Hz = 275/60 + (110-275/60)*math.log(1 + (HzScale - .5)/.25, 2)  #log scales up to 110Hz (4th harmonic/2nd octave will be 440Hz)    
        else:   
            Hz = 110 + (2000-110)*math.log(1 + (HzScale - .75)/.25, 2)        #caps at 2000 Hz (seventh harmonic will be at 14000Hz)
            

        if not SMOOTH_SLIDE:
            if self.overtones[0].Hz != 0:
                ms_per_beat = 1000/self.overtones[0].Hz #Keep ms_per_beat based on fundamental freq unless slider is not selected and we update fundamental Hz
            else:
                ms_per_beat = 0

        if SMOOTH_SLIDE or (not self.isSelected):  #if slider isn't selected we *now* update the VCOs
        
            if Hz == 0: 
                ms_per_beat = 0
                for overtone in self.overtones: 
                    overtone.Hz = 0
                    overtone.oscillator.stop() #kill all oscillators

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


class RadioArea:
    def __init__(self, origin, size, overtones):

        radioRad = 5
        self.radios = [
            RadioBtn(pygame.math.Vector2(origin[0], origin[1] + (overtone.overtone-1)*size[1]/(len(overtones)-1)), radioRad, overtone) for overtone in overtones
            ]

        #constants for drawing the sine waves next to the radio buttons
        self.horizontalBuf = 20
        self.sineLength = size[0] - self.horizontalBuf
        self.sampRate = 55

    def draw(self, surface):

        for radio in self.radios:
            radio.draw(surface)

            offset = radio.pos + (self.horizontalBuf, 0)
            sine = [((i/self.sampRate)*self.sineLength + offset[0], -10*math.sin(2*math.pi * i/self.sampRate * radio.overtone.overtone/2) + offset[1]) for i in range(self.sampRate)]

            pygame.draw.aalines(surface, (147,80,90), False, sine)


class RadioBtn:
    def __init__(self, position, radius, overtone):

        self.overtone = overtone

        self.active = self.overtone.active

        self.pos = position
        self.radius = radius

        self.onCol = pygame.Color((self.overtone.poly.color))
        hsla = self.onCol.hsla
        self.onCol.hsla = (hsla[0], hsla[1], hsla[2] + 3, hsla[3])

        self.surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        self.surf.set_colorkey((0,0,0))

        #Bivariate Gaussian function of two i.i.d. vars.  Since i.i.d. it just takes one mu and one sigma for both vars.
        #Height defaults can be set to arbitary height of peak.  Set height to 1/(2*math.pi*sigma**2) for valid pdf normal distr
        def bivarGauss(x, y, mu, sigma, height):
            return height * math.e**(-1/2 * ((x-mu)**2 + (y-mu)**2)/sigma**2)

        mu = self.radius
        sigma = self.radius*1/2
        height = 255 #height is max opaque alpha and then fades to transparent
        for x in range(radius*2):
            for y in range(radius*2):
                alpha = int(bivarGauss(x, y, mu, sigma, height))
                self.onCol.a = alpha
                self.surf.set_at((x,y), self.onCol)
                

        self.offCol = pygame.Color(self.overtone.poly.color)
        hsva = self.offCol.hsva
        self.offCol.hsva = (hsva[0], hsva[1], hsva[2] - 40, hsva[3])

        self.borderCol = (0,0x79,0x87)
        self.borderWidth = 2



    def draw(self, surface):
        pygame.draw.circle(surface, self.offCol, self.pos, self.radius)

        if self.active: 
            surface.blit(self.surf, self.pos - (self.radius,self.radius))

        pygame.draw.circle(surface, self.borderCol, self.pos, self.radius + self.borderWidth, 2)
            


    def updateActive(self, active):
        self.active = active

        self.overtone.active = self.active

        if active: 
            if not SMOOTH_SLIDE: self.overtone.oscillator.set_volume(1)
        else:
            self.overtone.oscillator.set_volume(0)


class RatioDisp:
    def __init__(self, origin, overtones, digitalSlot, digitalFont, digitalCol, ratioColon):
        self.origin = origin
        self.overtones = overtones
        self.digitalFont = digitalFont
        self.digitalCol = digitalCol
        self.digitalSlot = digitalSlot
        self.ratioColon = ratioColon
        self.horizontalBuf = 4

    def draw(self, surface):
        #if TYPESET: pygame.draw.rect(surface, (0,0,0), (self.origin, (self.length, self.digitalSlots[0].get_height())), 1)
        offset = self.digitalSlot.get_width() + self.horizontalBuf + self.ratioColon.get_width() + self.horizontalBuf
        for i, overtone in enumerate(self.overtones):
            surface.blit(self.digitalSlot, (self.origin[0] + offset*i, self.origin[1]))
            if overtone.active:
                ratioDisp = self.digitalFont.render(f'{overtone.overtone}'.replace("1", " 1"), False, self.digitalCol)
                surface.blit(ratioDisp, (self.origin[0] + offset*i, self.origin[1]))

            if overtone != self.overtones[-1]:
                surface.blit(self.ratioColon, (self.origin[0] + offset*i + self.digitalSlot.get_width() + self.horizontalBuf, self.origin[1]))






class Overtone:
    def __init__(self, overtone, poly, numOvertones, fundHz, fundPhase = 0):       #Hz and phase all with respect to the fundamental tone of the overtones
        self.Hz = fundHz * overtone
        self.phase = fundPhase * overtone
        self.overtone = overtone
        self.numOvertones = numOvertones


        self.oscillator = Oscillator(self.Hz, 1/self.numOvertones, self.phase)
        self.oscillator.set_volume(0)

        self.poly = poly

        self.active = False

    def updateHz(self, fundHz, fundPhase):
        self.Hz = fundHz * self.overtone

        self.phase = fundPhase * self.overtone
        self.oscillator.stop()

        self.oscillator = Oscillator(self.Hz, 1/self.numOvertones, self.phase)
        if self.active:
            if not SMOOTH_SLIDE: self.oscillator.set_volume(1)
        else:
            self.oscillator.set_volume(0)



def Oscillator(Hz, volScale, phase=0, sampRate=44100): #phase in relative terms: in [0,1] and represents fraction of period of Hz to offset
        
        dtype = "int8"
        maxVal = np.iinfo(dtype).max
        vol = maxVal*volScale

        secs = 1/Hz  #Get exactly enough samples for a full wave cycle
        periodLength = int(secs*sampRate)
        pulseWidth = min(50, (1/3)*periodLength)

        startPulse = ((1-phase)%1)*periodLength           #for phase in [0,1] of one cycle, start pulse at 1-phase fraction of periodLength (neg vals work via mod 1)
        endPulse = startPulse + pulseWidth                #end pulse after its width, with possilbe wrap-around
        endWrap = min(endPulse, endPulse % periodLength)
        wrap = bool(endWrap < endPulse)

        wave = np.array([vol if (i >= startPulse and i <= endPulse) or (wrap and i <= endWrap) else -vol for i in range(periodLength)], dtype=dtype)

  
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

        ballRadius = 7
        self.ball = Ball(self, ballRadius)

    
    def draw(self, surface):
        if self.isPointy:
            pygame.draw.polygon(surface, self.color, self.verts, width=2)
        else:
            pygame.draw.circle(surface, self.color, self.center, self.radius, width=3)
    

class Ball:
    def __init__(self, poly, radius, alpha=255, isHead=True):
        self.poly = poly
        self.radius = radius
        self.alpha = alpha
        self.isHead = isHead

        self.pos = poly.verts[0]
        self.color = poly.color

        self.surf = pygame.Surface((self.radius*2, self.radius*2))
        self.surf.set_colorkey((0,0,0))
        self.surf.set_alpha(self.alpha)
        pygame.draw.circle(self.surf, self.color, (self.radius, self.radius), self.radius)

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

        screen.blit(self.surf, self.pos - pygame.math.Vector2(self.radius, self.radius))
        

class Tail:
    def __init__(self, ball):
        self.head = ball


        # perimeter of the polygon the trail is on that it will need to cover
        self.perimeter = 0
        if self.head.poly.isPointy:
            self.perimeter = len(self.head.poly.verts) * math.dist(self.head.poly.verts[0], self.head.poly.verts[1])
        else:
            self.perimeter = 2*math.pi*self.head.poly.radius


        polyCover = self.perimeter/(2*self.head.radius) #num of balls needed to cover its polygon's perimeter
        self.tailLength = int(3.5*polyCover)         #Make the num of balls in tail longer than polyCover so it can wrap into its tail at high Hz and become opaque
        #alphaRate =1

        self.alphaTail = [Ball(self.head.poly, self.head.radius, self.head.alpha*(1 - math.log(1 + (i+1)/self.tailLength, 2)), isHead=False) for i in range(self.tailLength)]


    
    def updatePos(self, beat_offset, ms_per_beat):
        fadeTime = 22  #ms it takes for ball image to fade completely
                       #operationally, this will determine how far back in time the tail reaches back before fading completely


        #When the Hz gets too high, the balls will separate from each other because fadeTime is too long relative to Hz
        #So we create a max distance that they can go back so the tail sticks together at high Hz
        maxDist = self.tailLength*self.head.radius  #trail can get long enough to pull the balls apart more than them overlapping by their radius
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

    windowSize = (1050, 625)
    windowCenter = pygame.Vector2(windowSize[0]/2, windowSize[1]/2)
    window = pygame.display.set_mode(windowSize)

    consoleSize = (1000, 560)
    consoleCenter = pygame.Vector2(consoleSize[0]/2, consoleSize[1]/2)
    consoleOrigin = windowCenter - consoleCenter
    Hz =  1
    console = Console(consoleOrigin, consoleSize, Hz)

    overtones = console.overtones
    slider = console.sliderArea.slider
    radios = console.radios
    screen = console.screen

    polys = screen.polys
    balls = [poly.ball for poly in polys]



    
    radios[0].updateActive(True)

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

                    else:
                        for radio in radios:
                            if (math.dist(radio.pos, posOnConsole) <= radio.radius):  #if one of the overtones' radio buttons is clicked, toggle it on/off

                                radio.updateActive(not radio.active)
                                console.draw(window)

            
            elif (event.type == pygame.MOUSEMOTION):
                if slider.isSelected:                              #update slider position (but don't affect anything until mouse released)
                    posOnConsole = event.pos - console.origin

                    y = min(posOnConsole[1], slider.maxy - offset_y)
                    y = max(y, slider.miny - offset_y)

                    slider.pos[1] = offset_y + y

                    (beat_offset, ms_per_beat) = slider.updateVolt(beat_offset, clock)

                    console.draw(window)



            elif event.type == pygame.MOUSEBUTTONUP:
                if (event.button == 1) and slider.isSelected:         #update Hz if the slider was selected and now released

                    slider.isSelected = False                    #unselect slider and then update slider's affect on Hz

                    if not SMOOTH_SLIDE: (beat_offset, ms_per_beat) = slider.updateVolt(beat_offset, clock)

            

            
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

main()