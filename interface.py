import pygame
import math

import harmonics as hmx
import testSettings

SMOOTH_SLIDE = testSettings.SMOOTH_SLIDE
TYPESET = testSettings.TYPESET


class Console:
    """
        Test
        
        Trying some things here
    """
    def __init__(self, origin, size, startHz):
        """Test3"""
        self.surf = pygame.Surface(size)

        self.origin = origin

        self.baseColor = (0xff,0xbc,0xcf) #(169,193,255)
        self.secColor = (0,0x93,0x90)

        consoleSize = pygame.Vector2(size)

        self.console = pygame.Rect((0,0), consoleSize)


        screenSize = (425, 350)

        screenCenter = pygame.Vector2(screenSize[0]/2, screenSize[1]/2)
        consoleCenter = consoleSize/2
        screenOrigin = consoleCenter - screenCenter - (0,35)

        screenColor = (112, 198, 169)
        self.screen = Screen(screenOrigin, screenSize, screenColor, startHz)

        self.overtones = self.screen.overtones
     

    
        labelsFontSize = 18
        #path = pygame.font.match_font('Abadi MT Condensed Extra Bold')
        self.labelsFont = pygame.font.Font('fonts/Menlo.ttc', labelsFontSize)
        self.labelsCol = (125,58,68) #(76,100,161)
        

        digitalFontSize = 30
        self.digitalFont = pygame.font.Font('fonts/digital-7 (mono).ttf', digitalFontSize)

        self.digitalOn = (0,0xcf,0xdd)
        self.digitalOff = (0,0x55,0x63)
        self.digitalBG = (0,0x35,0x55)


        sliderAreaOrigin = (55, 45)
        sliderAreaHeight = consoleSize[1]*.85

        #Slider's "voltage" will control VCOs (oscillators) of the overtones
        self.sliderArea = SliderArea(self, sliderAreaOrigin, sliderAreaHeight)


        radioAreaOrigin = (810, 65)
        radioAreaSize = (135 , 350)

        self.radioArea = RadioArea(self, radioAreaOrigin, radioAreaSize) 



        ratioOrigin = screenOrigin + (108, screenSize[1] + 80)
        #ratioLength = screenSize[0]-40

        self.ratioDisp = RatioDisp(self, ratioOrigin)


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
        

        root1 = hmx.Polygon(1,rootRadius, center, rootColor, isPointy=False)
        root2 = hmx.Polygon(2,rootRadius/math.sqrt(2), center, rootColor, isPointy=False)
        fifth1 = hmx.Polygon(3, rootRadius/math.sqrt(2), center, fifthColor)
        root3 = hmx.Polygon(4,rootRadius, center, rootColor)
        third1 = hmx.Polygon(5,fifth1.inCirc, center, thirdColor)
        fifth2 = hmx.Polygon(6,rootRadius/math.sqrt(2), center, fifthColor)
        seventh1 = hmx.Polygon(7,third1.inCirc, center, seventhColor)

        self.polys = [root1, root2, fifth1, root3, third1, fifth2, seventh1]

        numOvertones = len(self.polys)
        self.overtones = [hmx.Overtone(len(poly.verts), poly, numOvertones, startHz) for poly in self.polys]

    def draw(self, targetSurf, offset = pygame.Vector2(0,0)):
        self.surf.fill(self.color)

        for overtone in self.overtones: 
            poly = overtone.poly

            poly.draw(self.surf)

            # If polygon is actually a circle, then draw tick marks to indicate where ball will make a click sound when passed.
            tickLength = 5
            if not poly.isPointy: 
                for i, vert in enumerate(poly.verts):
                    xTick = math.cos(math.pi/2 - 2*math.pi * i/len(poly.verts))*tickLength
                    yTick = math.sin(math.pi/2 - 2*math.pi * i/len(poly.verts))*tickLength
                    pygame.draw.line(self.surf, (139,72,82), vert - (xTick , -yTick), vert + (xTick, -yTick), 2)


            if overtone.active: poly.ball.draw(self.surf)

        targetSurf.blit(self.surf, self.origin + offset)


class SliderArea:
    def __init__(self, console, origin, height):
        self.origin = origin
        self.height = height

        self.overtones = console.overtones

        self.color = console.secColor

        # Create all labels for the Slider Area.
        labelsFont = console.labelsFont
        labelsCol = console.labelsCol

        self.HzLabel = labelsFont.render('Hz', True, labelsCol)
        self.BPM_Label = labelsFont.render('BPM', True, labelsCol)

        labelsText = ['FREEZE', 'GROOVE', 'CHAOS', 'HARMONY', 'EEEEEE']
        self.labels = [labelsFont.render(text, True, labelsCol) for text in labelsText]
        
        # Create digital display boxes for Hz and BPM.
        self.digitalFont = console.digitalFont
        self.digitalOn = console.digitalOn

        digitalOff = console.digitalOff
        digitalBG = console.digitalBG
        
        self.HzBox = self.digitalFont.render(' 8888.88 ', False, digitalOff, digitalBG)  #digital box to print Hz on
        self.BPM_Box = self.digitalFont.render(' 888888 ', False, digitalOff, digitalBG)
        


        self.horizontalBuf = 20
    
        sliderSize = pygame.math.Vector2(20,40) #size of rectangular slider handle

        verticalBuf = 30
        sliderMiny = self.origin[1] + self.HzBox.get_height() + verticalBuf
        sliderMaxy = self.origin[1] + self.height - self.BPM_Box.get_height() - verticalBuf
        
        labelsWidth = max([label.get_width() for label in self.labels])
        sliderOffset = self.origin[0] + labelsWidth + self.horizontalBuf + sliderSize[0]
        sliderStart = .25        #slider knob starts at this fraction of the slider range

        sliderPos = pygame.Vector2(sliderOffset, sliderMaxy-sliderStart*(sliderMaxy-sliderMiny))


        self.slider = Slider(sliderPos, sliderSize, self.color, self.overtones, sliderMiny, sliderMaxy)

                

    def draw(self, surface):
        if TYPESET: pygame.draw.rect(surface, (0,0,0), (self.origin, (self.HzBox.get_width() + self.horizontalBuf + self.BPM_Label.get_width(), self.height)), 1)

        #draw slider groove and slider
        sliderRutCol = (150,150,150)
        pygame.draw.line(surface, sliderRutCol, (self.slider.pos[0], self.slider.miny), (self.slider.pos[0], self.slider.maxy), width=2) #slider track visualized

        self.slider.draw(surface)

        #Draw Hz display
        surface.blit(self.HzBox, (self.origin[0], self.origin[1]))

        HzDisp = self.digitalFont.render(" " + f'{self.overtones[0].Hz:07.2f}'.replace("1", " 1") + " ", False, self.digitalOn)
        surface.blit(HzDisp, (self.origin[0], self.origin[1]))

        surface.blit(self.HzLabel, (self.origin[0]+self.HzBox.get_width()+self.horizontalBuf/2,self.origin[1]))

        #Draw slider labels
        for i, label in enumerate(self.labels):
            surface.blit(label, (self.origin[0], (self.slider.maxy - label.get_height()/2) - (i/4)*(self.slider.maxy - self.slider.miny))) 

        #Draw BPM display
        surface.blit(self.BPM_Box, (self.origin[0], self.origin[1] + self.height - self.BPM_Box.get_height()))

        BPM_Disp = self.digitalFont.render(" " + f'{self.overtones[0].Hz * 60:06.0f}'.replace("1", " 1") + " ", False, self.digitalOn)
        surface.blit(BPM_Disp, (self.origin[0], self.origin[1] + self.height - self.BPM_Box.get_height()))

        surface.blit(self.BPM_Label, (self.origin[0]+self.BPM_Box.get_width()+self.horizontalBuf/2,self.origin[1] + self.height - self.BPM_Box.get_height()))


class Slider:
    def __init__(self, position, size, color, overtones, miny, maxy):
        self.pos = position
        self.size = size
        self.color = color

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

                pygame.time.wait(int(max(buffer_time - clock.tick(), 0)))    #wait to play sounds until caught up to extra buffer time

                for overtone in self.overtones: overtone.oscillator.play(loops=-1) #play them all at the same time



        return (beat_offset, ms_per_beat)
    
    def draw(self, surface):
        self.handle = pygame.Rect(self.pos - self.size/2, self.size)
        pygame.draw.rect(surface, self.color, self.handle)


class RadioArea:
    def __init__(self, console, origin, size):

        self.origin = origin
        self.size = size

        radioRad = 5
        self.radios = [
            RadioBtn(pygame.math.Vector2(origin[0], origin[1] + (overtone.overtone-1)*size[1]/(len(console.overtones)-1)), radioRad, overtone) for overtone in console.overtones
            ]
        
        killSwitchSize = (15,15)
        killSwitchOrigin = (origin[0], origin[1] + size[1] + 60)
        self.killSwitch = KillSwitch(killSwitchOrigin, killSwitchSize, console.secColor, self.radios)

        self.killSwitchLabel = console.labelsFont.render('SSHHHHHHH!', True, console.labelsCol)

        #constants for drawing the sine waves next to the radio buttons
        self.horizontalBuf = 20
        self.sineLength = size[0] - self.horizontalBuf
        self.sampRate = 55
        self.peakHeight = 10
        self.tickLength = 4
        self.tickWidth = 1

    def draw(self, surface):
        if TYPESET: pygame.draw.rect(surface, (0,0,0), (self.origin, self.size), 1)

        for radio in self.radios:
            radio.draw(surface)

            overtoneNum = radio.overtone.overtone
            offset = radio.pos + (self.horizontalBuf, 0)
            sine = [((i/self.sampRate)*self.sineLength + offset[0], -self.peakHeight*math.sin(2*math.pi * i/self.sampRate * overtoneNum/2) + offset[1]) for i in range(self.sampRate)]

            pygame.draw.aalines(surface, (147,80,90), False, sine)

            for i in range(overtoneNum):
                peakOffset = offset[0] + (2*i+1)*self.sineLength/(overtoneNum*2)
                peakHeight = offset[1] + self.peakHeight*(-1)**(i+1)
                pygame.draw.line(surface, (147,80,90), (peakOffset, peakHeight + self.tickLength/2), (peakOffset, peakHeight - self.tickLength/2), self.tickWidth)

        self.killSwitch.draw(surface)
        surface.blit(self.killSwitchLabel, self.killSwitch.pos + (self.horizontalBuf - 2, -self.killSwitch.size[1]/2 - 3))


class RadioBtn:
    def __init__(self, position, radius, overtone):

        self.overtone = overtone

        self.active = self.overtone.active

        self.pos = position
        self.radius = radius

        self.borderCol = (0,0x79,0x87)
        self.borderWidth = 2

        self.offCol = pygame.Color(self.overtone.poly.color)
        hsva = self.offCol.hsva
        self.offCol.hsva = (hsva[0], hsva[1], hsva[2] - 40, hsva[3])

        self.lightCol = pygame.Color((self.overtone.poly.color))
        hsla = self.lightCol.hsla
        self.lightCol.hsla = (hsla[0], hsla[1], hsla[2] + 3, hsla[3])

        self.light = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        self.light.set_colorkey((0,0,0))

        #Bivariate Gaussian function of two i.i.d. vars.  Since i.i.d. it just takes one mu and one sigma for both vars.
        #Height defaults can be set to arbitary height of peak.  Set height to 1/(2*math.pi * sigma**2) for valid pdf normal distr
        def bivarGauss(x, y, mu, sigma, height):
            return height * math.e**(-1/2 * ((x-mu)**2 + (y-mu)**2)/sigma**2)

        mu = self.radius
        sigma = self.radius*4/7
        height = 255 #height is max opaque alpha and then fades to transparent
        for x in range(radius*2):
            for y in range(radius*2):
                alpha = int(bivarGauss(x, y, mu, sigma, height))
                self.lightCol.a = alpha
                self.light.set_at((x,y), self.lightCol)

    def press(self):
        self.active = not self.active

        self.overtone.active = self.active

        if self.active: 
            if not SMOOTH_SLIDE: self.overtone.oscillator.set_volume(1)
        else:
            self.overtone.oscillator.set_volume(0)

    def draw(self, surface):
        pygame.draw.circle(surface, self.offCol, self.pos, self.radius)

        if self.active: 
            surface.blit(self.light, self.pos - (self.radius,self.radius))

        pygame.draw.circle(surface, self.borderCol, self.pos, self.radius + self.borderWidth, 2)


class KillSwitch:
    def __init__(self, position, size, color, radios):
        self.pos = pygame.math.Vector2(position)
        self.size = pygame.math.Vector2(size)
        self.color = color

        self.radios = radios

        self.button = pygame.Rect(self.pos - self.size/2, self.size)

        self.isPressed = False
        self.pressedSize = self.size - (1,1)

        self.downClick = pygame.mixer.Sound('sounds/down-click.wav')
        self.upClick = pygame.mixer.Sound('sounds/up-click.wav')

        self.borderRad = 4

    def press(self):
        self.isPressed = not self.isPressed

        if self.isPressed:
            self.downClick.play()
            pygame.time.wait(100)

            for radio in self.radios:
                if radio.active: radio.press()

        else:
            self.upClick.play()


    def draw( self, surface):
        if not self.isPressed:
            pygame.draw.rect(surface, self.color, self.button, 0, self.borderRad)
        else:
            pygame.draw.rect(surface, self.color, ((self.pos-self.pressedSize/2), self.pressedSize), 0, self.borderRad-1)


class RatioDisp:
    def __init__(self, console, origin):
        self.origin = origin
        self.overtones = console.overtones
        self.digitalFont = console.digitalFont
        self.digitalOn = console.digitalOn

        self.digitalSlot = self.digitalFont.render(f'8', False, console.digitalOff, console.digitalBG)
        self.ratioColon = console.labelsFont.render(':', False, console.labelsCol)
        self.horizontalBuf = 4

    def draw(self, surface):
        #if TYPESET: pygame.draw.rect(surface, (0,0,0), (self.origin, (self.length, self.digitalSlots[0].get_height())), 1)
        offset = self.digitalSlot.get_width() + self.horizontalBuf + self.ratioColon.get_width() + self.horizontalBuf
        for i, overtone in enumerate(self.overtones):
            surface.blit(self.digitalSlot, (self.origin[0] + offset*i, self.origin[1]))
            if overtone.active:
                ratioDisp = self.digitalFont.render(f'{overtone.overtone}'.replace("1", " 1"), False, self.digitalOn)
                surface.blit(ratioDisp, (self.origin[0] + offset*i, self.origin[1]))

            if overtone != self.overtones[-1]:
                surface.blit(self.ratioColon, (self.origin[0] + offset*i + self.digitalSlot.get_width() + self.horizontalBuf, self.origin[1]))