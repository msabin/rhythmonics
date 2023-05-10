"""
Module for GUI

Classes
-------
Console
Screen
SliderArea
Slider
RadioArea
RadioBtn
KillSwitch
RatioDisp
"""
import pygame
import math

import harmonics as hmx
import testSettings

SMOOTH_SLIDE = testSettings.SMOOTH_SLIDE
TYPESET = testSettings.TYPESET


class Console:
    """
    This class wraps all of the GUI elements and decides how they are displayed into a console.
    
    This class sets up the console aesthetics (e.g. colors, fonts, layout) and initializes 
    and collects all of its areas: Screen, SliderArea, RadioArea, and RatioDisp.  It also
    has a method for drawing itself and all of its areas onto a Surface.

    Attributes
    ----------
    origin : tuple
        Position relative to window/target Surface that Console will drawn on.
    size : tuple
        Size of console area as a rectangle.
    baseColor
        Color of console background, see pygame.Color for supported formats.
    secColor
        Color of console foreground pieces, see pygame.Color for supported formats.
    surf : pygame.Surface
        Surface to draw console and its components onto.
    screen : Screen
        Screen object for displaying polygons to.
    overtones : list of harmonics.Overtone
        Overtones that the console is for displaying and allowing interaction with.
    labelsFont : pygame.font.Font
        Font all labels on the console are written in.
    labelsCol
        Color of font of console's labels, see pygame.Color for supported formats.
    digitalFont : pygame.font.Font
        Font on the console's digital displays.
    digitalOn
        Color of digital font when "lit up," see pygame.Color for supported formats.
    digitalOff
        Color of idle digital font when not "lit," see pygame.Color for supported formats.
    digitalBG
        Background color of digital displays, see pygame.Color for supported formats.
    sliderArea : SliderArea
        Area for displaying and interacting with slider.
    radioArea : RadioArea
        Area for displaying and interacting with radio buttons and kill switch.
    ratioDisp : RatioDisp
        Area for digital displays of ratios between active overtones.

    Methods
    -------
    draw
        Draw console and all of its components/areas.
    """
    def __init__(self, origin, size, startHz):
        """
        Initialize the console and all of its area components it wraps.

        Initialize all of the console aesthetics (e.g. colors, fonts, layout) and initialize 
        and collect all of its areas: Screen, SliderArea, RadioArea, and RatioDisp.

        Parameters
        ----------
        origin : tuple
            Origin of the console's top left corner to display.
        size : tuple
            Size of the console area to display.
        startHz : float
            Positive number of the fundamental Hz the console will begin with.
        """
        self.origin = origin
        self.size = pygame.Vector2(size)

        self.baseColor = (0xff,0xbc,0xcf) #(169,193,255)
        self.secColor = (0,0x93,0x90)

        self.surf = pygame.Surface(self.size)

        # Initialize the screen and get the overtones from it afterwards.
        screenColor = (112, 198, 169)
        screenAreaSize = pygame.Vector2(515, 425)

        screenCenter = screenAreaSize/2
        consoleCenter = self.size/2
        screenAreaOrigin = consoleCenter - screenCenter - (0,35)
        self.screenArea = ScreenArea(screenAreaOrigin, screenAreaSize, screenColor, self.secColor, startHz)

        self.overtones = self.screenArea.screen.overtones
     
        # Set up all the fonts of the console so console areas can use them.
        labelsFontSize = 18
        self.labelsFont = pygame.font.Font('fonts/Menlo.ttc', labelsFontSize)
        self.labelsCol = (125,58,68) #(76,100,161)
        
        digitalFontSize = 30
        self.digitalFont = pygame.font.Font('fonts/digital-7 (mono).ttf', digitalFontSize)
        self.digitalOn = (0,0xcf,0xdd)
        self.digitalOff = (0,0x55,0x63)
        self.digitalBG = (0,0x35,0x55)

        # Initialize slider area.
        sliderAreaOrigin = (55, 45)
        sliderAreaHeight = self.size[1]*.85
        self.sliderArea = SliderArea(self, sliderAreaOrigin, sliderAreaHeight)

        # Initialize area for radio buttons and kill switch.
        radioAreaOrigin = (810, 65)
        radioAreaSize = (135 , 350)
        self.radioArea = RadioArea(self, radioAreaOrigin, radioAreaSize) 

        # Initialize area for digital displays of ratios between active overtones.
        ratioOrigin = screenAreaOrigin + (153, screenAreaSize[1] + 30)
        self.ratioDisp = RatioDisp(self, ratioOrigin)


    def draw(self, targetSurf):
        """
        Draw the console and all of its components onto a Surface.

        Parameters
        ----------
        targetSurf : pygame.Surface
            Surface to blit the console's surface to.
        """
        # Clear screen by drawing console base onto console's surface.
        pygame.draw.rect(self.surf, self.baseColor, ((0,0), self.size), border_radius=50)

        # Draw all of console's areas onto console's surface.
        self.screenArea.draw(self.surf)
        self.sliderArea.draw(self.surf)
        self.radioArea.draw(self.surf)
        self.ratioDisp.draw(self.surf)

        # Blit console's surface onto the target surface/window.
        targetSurf.blit(self.surf, self.origin)

class ScreenArea:
    """
    
    Attributes
    ----------
    origin : tuple
        Position relative to Console origin that this area will be drawn onto.
    """
    def __init__(self, origin, size, screenCol, borderCol, startHz):
        self.border = pygame.Rect(origin, size)
        self.borderRadius = 5
        self.bigBorderRad = 40
        self.borderCol = borderCol

        screenOrigin = pygame.Vector2(origin) + (45,25)
        screenSize = pygame.Vector2(size) - (90, 75)
        self.screen = Screen(screenOrigin, screenSize, screenCol, startHz)

    def draw(self, surf):
        pygame.draw.rect(surf, self.borderCol, self.border, 
                         border_radius=self.borderRadius, 
                         border_bottom_right_radius=self.bigBorderRad)

        self.screen.draw(surf)

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
            overtone.poly.draw(self.surf)

            if overtone.active: overtone.poly.ball.draw(self.surf)

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

        HzString = " " + f'{self.overtones[0].Hz:07.2f}'.replace("1", " 1") + " "
        HzDisp = self.digitalFont.render(HzString, False, self.digitalOn)
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

        self.quarterTarget = 1 # Up to quarter of the way, linearly scale up to 1Hz=60bpm.
        self.halfTarget = 275/60   # Linearly scales up to 275/60Hz = 275bpm
        self.threeQuartTarget = 110
        self.topTarget = 2000

    def updateVolt(self, beat_offset, clock):  #slider's position/"voltage" affects VCOs' Hz. Use clock to find phase

        HzScale = abs(self.pos[1] - self.maxy)/(self.maxy - self.miny)

        if HzScale <= .25:
            Hz = self.quarterTarget * HzScale/.25  
            if Hz <= .02: Hz = 0  # Too low Hz take too much time to make Sound object, just make it 0.
        elif HzScale <= .5:
            Hz = (1-(HzScale -.25)/.25) +   self.halfTarget * (HzScale-.25)/.25
        elif HzScale <= .75:
            Hz = 275/60 + (110-275/60)*math.log(1 + (HzScale - .5)/.25, 2)  # log scales up to 110Hz (4th harmonic/2nd octave will be 440Hz)    
        else:   
            Hz = 110 + (2000-110)*math.log(1 + (HzScale - .75)/.25, 2)  # Caps at 2000 Hz (seventh harmonic will be at 14000Hz)
            

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

                # Wait to play sounds until we're caught up to the buffer time we gave ourselves and then play them all
                # in sync at the same time (even though they start off silent).
                pygame.time.wait(int(max(buffer_time - clock.tick(), 0)))
                for overtone in self.overtones: overtone.oscillator.play(loops=-1)



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