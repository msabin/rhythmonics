import pygame
import math
import numpy as np


# CONSTANTS

CONSOLE_WIDTH = 900
CONSOLE_HEIGHT = 500
CONSOLE_MIN = min(CONSOLE_WIDTH, CONSOLE_HEIGHT)
CONSOLE_COLOR =  (0xff,0xb3,0xc6) #(169,193,255)
CONSOLE_CENTER = pygame.Vector2(CONSOLE_WIDTH/2, CONSOLE_HEIGHT/2)


SCREEN_WIDTH = 425
SCREEN_HEIGHT = 350
SCREEN_MIN = min(SCREEN_WIDTH, SCREEN_HEIGHT)
SCREEN_COLOR = (112, 198, 169)
SCREEN_CENTER = pygame.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

SCREEN_ORIGIN = CONSOLE_CENTER - SCREEN_CENTER - (0,20)


NUM_OVERTONES = 7

ROOT_COLOR = (237,199,176)
THIRD_COLOR = (118,150,222)
FIFTH_COLOR = (255,151,152)
SEVENTH_COLOR = (139,72,82)

TEAL = (0,0x9c,0xaa)

ROOT_RADIUS = (.9*SCREEN_MIN)/2
BALL_RADIUS = 7
FADE_TIME = .1  #Fade time in ms

MIN_HZ = 0
MAX_HZ = 2000
START_HZ = 1 #1Hz = 60bpm



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
        if ms_per_beat == 0: return

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


        polyCover = self.perimeter/BALL_RADIUS #num of balls needed to cover its polygon's perimeter
        tailLength = int(2*polyCover)
        #alphaRate =1

        self.alphaTail = [Ball(self.head.poly, self.head.alpha*math.log(1 + (tailLength-(i+1))/tailLength, 2), isHead=False) for i in range(tailLength)]


    
    def updatePos(self, beat_offset, ms_per_beat):

        ms_per_ball = ms_per_beat/(self.perimeter/(1.5*BALL_RADIUS))  #ms required for a ball to travel the distance of its own radius*1.5

        ball_offset = min(FADE_TIME, ms_per_ball) #drop a trail ball back in time every FADE_TIME ms or " " ms so that there aren't gaps between balls
        for i, ball in enumerate(self.alphaTail, start=1):
            ball.updatePos(beat_offset - ball_offset*i, ms_per_beat)

    def draw(self, console):
        for ball in self.alphaTail:
            ball.draw(console)





class Slider:
    def __init__(self):
        self.miny = 75
        self.maxy = CONSOLE_HEIGHT-self.miny


        self.pos = pygame.Vector2(125, self.maxy-.25*(self.maxy-self.miny))


        self.color = TEAL


        self.fontSize = 20
        font = pygame.font.Font(None, self.fontSize)

        self.labels = [font.render('FREEZE', False, (0,0,0)), font.render('GROOVE', False, (0,0,0)), font.render('CHAOS', False, (0,0,0)),
                       font.render('HARMONY', False, (0,0,0)), font.render('EEEEEE', False, (0,0,0))]


                

    def draw(self, surface):
        pygame.draw.line(surface, (0,0,0), (self.pos[0], self.miny), (self.pos[0], self.maxy))
        pygame.draw.circle(surface, self.color, self.pos, 10)

        for i, label in enumerate(self.labels):
            surface.blit(label, (25, (self.maxy - self.fontSize/2) - (i/4)*(self.maxy - self.miny))) 


class RadioBtn:
    def __init__(self, num, color):
        miny = 75
        maxy = CONSOLE_HEIGHT-miny

        self.pos = pygame.Vector2(CONSOLE_WIDTH - 140, miny + (num-1)*(maxy-miny)/6)


        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, (230,230,230), self.pos, 7, 2)

        pygame.draw.circle(surface, self.color, self.pos, 5)


def Oscillator(Hz, phase=0, sampRate=44100):
        
        dtype = "int8"
        maxVal = np.iinfo(dtype).max

        secs = 1/Hz  #Get exactly enough samples for a full wave cycle
        periodLength = int(secs*sampRate)
        pulseWidth = min(50, (1/3)*periodLength)

        startPulse = ((1-phase)%1)*periodLength                           #for phase in [0,1] of one cycle, start pulse at 1 - phase fraction of periodLength
        endPulse = startPulse + pulseWidth                #end pulse after its width, with possilbe wrap-around
        endWrap = min(endPulse, endPulse % periodLength)
        wrap = bool(endWrap < endPulse)

        wave = np.array([maxVal/NUM_OVERTONES if (i >= startPulse and i <= endPulse) or (wrap and i <= endWrap) else -maxVal/NUM_OVERTONES for i in range(periodLength)], dtype=dtype)

        #if wrap: print(f'wrapped!    {wave}')

        #wave = np.array([maxVal if math.sin(Hz*2*math.pi*(i/sampRate + phase)) >= 0 else -maxVal for i in range(int(secs*sampRate))], dtype=dtype)
  
        return pygame.sndarray.make_sound(wave)


class Overtone:
    def __init__(self, Hz, overtone, poly, phase = 0):       #Hz and phase all with respect to the fundamental tone of the overtones
        self.Hz = Hz
        self.phase = phase
        self.overtone = overtone

        self.oscillator = Oscillator(self.Hz*self.overtone, self.phase*self.overtone)
        self.oscillator.set_volume(0)

        self.poly = poly

        self.radio = RadioBtn(overtone, poly.color)

        self.active = False

    def updateHz(self, Hz, subDiv):
        self.Hz = Hz

        self.phase = subDiv
        self.oscillator.stop()

        self.oscillator = Oscillator(self.Hz*self.overtone, self.phase*self.overtone)
        if self.active:
            self.oscillator.set_volume(1)
        else:
            self.oscillator.set_volume(0)

    def setActive(self, active):
        self.active = active

        if active: 
            self.oscillator.set_volume(1)
        else:
            self.oscillator.set_volume(0)

        

def updateBeatOffset(clock, beat_offset, ms_per_beat):

    if ms_per_beat != 0:
            beat_offset += clock.get_time()

            while beat_offset >= ms_per_beat:
                beat_offset -= ms_per_beat

            clock.tick()
            
    return beat_offset

    






class main:

    pygame.mixer.init(channels=1)
    pygame.init()
    #pygame.display.init()


    pygame.mouse.set_cursor(pygame.cursors.tri_left)



    dispaySize = pygame.display.get_desktop_sizes()


    console = pygame.display.set_mode((CONSOLE_WIDTH, CONSOLE_HEIGHT))

    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))




    root1 = Polygon(1,ROOT_RADIUS, SCREEN_CENTER, ROOT_COLOR, isPointy=False)
    root2 = Polygon(2,ROOT_RADIUS/math.sqrt(2), SCREEN_CENTER, ROOT_COLOR, isPointy=False)
    fifth1 = Polygon(3, ROOT_RADIUS/math.sqrt(2), SCREEN_CENTER, FIFTH_COLOR)
    root3 = Polygon(4,ROOT_RADIUS, SCREEN_CENTER, ROOT_COLOR)
    third1 = Polygon(5,fifth1.inCirc, SCREEN_CENTER, THIRD_COLOR)
    fifth2 = Polygon(6,ROOT_RADIUS/math.sqrt(2), SCREEN_CENTER, FIFTH_COLOR)
    seventh1 = Polygon(7,third1.inCirc, SCREEN_CENTER, SEVENTH_COLOR)

    polys = [root1, root2, fifth1, root3, third1, fifth2, seventh1]



    Hz = START_HZ
    overtones = [Overtone(START_HZ, len(poly.verts), poly) for poly in polys]

    

    
    slider = Slider()




    
    

    
    user_done = False
    sliderSelected = False

    ms_per_beat = 1000/Hz #how many milliseconds in a beat
    beat_offset = 0



    clock = pygame.time.Clock()
    clock.tick()

    for overtone in overtones: overtone.oscillator.play(loops=-1)

    overtones[0].active = True
    overtones[0].oscillator.set_volume(1)

    
    while not user_done:


        console.fill(CONSOLE_COLOR)
        screen.fill(SCREEN_COLOR)

        

        for overtone in overtones:
            overtone.poly.draw(screen)

            
            if overtone.active == True:
                beat_offset = updateBeatOffset(clock, beat_offset, ms_per_beat)

                overtone.poly.ball.updatePos(beat_offset, ms_per_beat)   #updates ball position (ball also updates the position of its tail)

                overtone.poly.ball.draw(screen)                          #draws ball (ball also tells its tail to draw itself)


            overtone.radio.draw(console)
        
        pygame.draw.rect(console, TEAL, (SCREEN_ORIGIN - (50,15), (SCREEN_WIDTH+100,SCREEN_HEIGHT+60)), border_radius=5, border_bottom_right_radius=40)
        console.blit(screen, SCREEN_ORIGIN)

        slider.draw(console)

        
        pygame.display.update()



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                user_done = True
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if math.dist(slider.pos, event.pos) <= 10:
                        sliderSelected = True

                        offset_y = slider.pos[1] - event.pos[1]

                    else:
                        for overtone in overtones:
                            if (math.dist(overtone.radio.pos, event.pos) <= 5):  #if one of the overtones' radio buttons is clicked, toggle it on/off

                                overtone.setActive(not overtone.active)

            
            elif (event.type == pygame.MOUSEMOTION):
                if sliderSelected:                              #update slider position (but don't affect anything until mouse released)
                    y = min(event.pos[1], slider.maxy - offset_y)
                    y = max(y, slider.miny - offset_y)

                    slider.pos[1] = offset_y + y



            elif event.type == pygame.MOUSEBUTTONUP:
                if (event.button == 1) and sliderSelected:         #update Hz if the slider was selected and now released

                    sliderSelected = False                    #unselect slider and then update Hz


                    HzScale = abs(slider.pos[1] - slider.maxy)/(slider.maxy - slider.miny)

                    if HzScale <= .25:
                        Hz = HzScale/.25                                                    #Up to quarter of the way, linear scales up to 1Hz=60bpm
                    elif HzScale <= .5:
                        Hz = (1-(HzScale -.25)/.25) +   275/60 * (HzScale-.25)/.25     #linear scales up to 275/60Hz = 275bpm
                    elif HzScale <= .75:
                        Hz = 275/60 + (110-275/60)*math.log(1 + (HzScale - .5)/.25, 2)  #log scales up to 110Hz (4th harmonic/2nd octave will be 440Hz)    
                    else:   
                        Hz = 110 + (2000-110)*math.log(1 + (HzScale - .75)/.25, 2)        #caps at 2000 Hz (seventh harmonic will be at 14000Hz)


                        

                    
                    if Hz == 0: 
                        ms_per_beat = 0
                        for overtone in overtones: overtone.oscillator.stop() #kill all oscillators

                    else: 
                        ms_per_beat = 1000/Hz 

                        buffer_time = (1/Hz)*26            #start updated soundwaves in the future by buffer_time and then wait to play them (sync with graphics)

                        beat_offset = updateBeatOffset(clock, beat_offset, ms_per_beat)

                        for overtone in overtones: overtone.updateHz(Hz, subDiv = (beat_offset+buffer_time)/ms_per_beat)

                        pygame.time.delay(int(max(buffer_time - clock.tick(), 0)))    #wait to play sounds until caught up to extra buffer time

                        for overtone in overtones: overtone.oscillator.play(loops=-1)






        #clock.tick()                

    pygame.QUIT

main()