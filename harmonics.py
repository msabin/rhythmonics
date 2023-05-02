import pygame
import numpy as np
import math

import testSettings

SMOOTH_SLIDE = testSettings.SMOOTH_SLIDE




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
