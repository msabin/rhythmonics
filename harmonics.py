"""
    Module for simulating all overtone/harmonic properties and components: sound, polygons, balls.

    Classes
    -------
    Overtone
        Stores core attributes of an Overtone, including Sound and Polygon objects.
    Polygon

    Ball

    Tail

    Functions
    ---------
    Oscillator
        Return pygame Sound object of a pulse wave.
"""

import pygame
import numpy as np
import math

import testSettings

SMOOTH_SLIDE = testSettings.SMOOTH_SLIDE




class Overtone:
    """
        Stores core attributes of an Overtone, including corresponding Sound object and Polygon object.

        This class mainly stores attributes associated with an overtone, mostly crucially the `Hz` and 
        `phase`, and has a method to update these two core defining attributes.  Further, Overtone has
        attributes `oscillator` and `poly` which, respectively, stores a pygame.Sound object which plays 
        a pulse wave at `Hz` frequency and associates the appropriate polgyon whose ball hits its corners/
        ticks at `Hz` frequency.

        Attributes
        ----------
            Hz : float
                Hertz of this overtone.
            phase : float
                [0,1] fractional value of how far into the wave's period we begin.
            overtone : int
                Natural number indicating which overtone this is over the fundamental tone.
            numOvertones : int
                Natural number denoting total number of overtones.
            oscillator : pygame.Sound
                Sound object that plays pulse wave at `Hz` frequency when looped.
            poly : Polygon
                Corresponding polygon whose ball hits its corners/ticks at `Hz` rate.
            active : bool
                Denotes whether the overtone is active: Playing sound and moving ball.

        Methods
        -------
            updateHz
                Update the Hz attribute and corresponding oscillator.
    """

    def __init__(self, overtone, poly, numOvertones, fundHz, fundPhase = 0):
        """
            Initialize an inactive, muted Overtone object and attach it to its Polygon.

            Given the Hertz and phase of a fundamental frequency that this object is an overtone
            of, create its own Hz as a multiple of the fundamental frequncy, create a (muted) 
            sound wave at that Hz, and attach its associated polygon to it as an attribute.

            Parameters
            ----------
                overtone : int
                    Natural number denoting which overtone this is of a fundamental frequency.
                poly : Polygon
                    Polygon object that is asscociated with the overtone.
                numOvertones: int
                    Total number of overtones, of which this is one of them.
                fundHz : float
                    Hertz of the fundamental frequency that this is an overtone to.  All overtones
                    have a Hz that is a natural number multiple of this fundamental frequency.
                fundPhase : float, default=0
                    [0,1] fractional value of how far into the fundamental frequency's wave's period 
                    it begins at.  
        """
        self.Hz = fundHz * overtone
        self.phase = fundPhase * overtone
        self.overtone = overtone
        self.numOvertones = numOvertones

        # Create an oscillator (muted to begin with) with volume `1/numOvertones` (so that sound doesn't
        # clip even when all `numOvertones` oscillators play at once.)
        self.oscillator = Oscillator(self.Hz, 1/self.numOvertones, self.phase)
        self.oscillator.set_volume(0)

        self.poly = poly

        self.active = False

    def updateHz(self, fundHz, fundPhase):
        """
            Update the Hz attribute and create a new corresponding soundwave for the oscillator attribute.

            Update the Hz attribute to correspond to being an overtone over a new fundamental frequency
            with a new phase.  Stop the old oscillator object from playing and create a new one with 
            updated Hz and phase.  The oscillators are muted even if the oscillator is active and it is
            the main event loop of the program's job to fade in the volumes of active oscillators.

            Parameters
            ----------
            fundHz : float
                Hertz of the fundamental frequency our Overtone object is an overtone of. Strictly positive value.
            fundPhase : float
                [0,1] fractional value of how far into the wave's period we begin of fundamental frequency.  It is
                OK to have any Real value here; since it is periodic, modding by 1 for such values has the same result.
                
        """
        self.Hz = fundHz * self.overtone

        self.phase = fundPhase * self.overtone
        self.oscillator.stop()

        self.oscillator = Oscillator(self.Hz, 1/self.numOvertones, self.phase)
        if self.active:
            if not SMOOTH_SLIDE: self.oscillator.set_volume(1)
        else:
            self.oscillator.set_volume(0)



def Oscillator(Hz, volScale, phase=0, sampRate=44100):
    """ 
        Return pygame Sound object of a single period of a pulse wave.

        Create a single period of a pulse wave of the given Hz starting at the given phase with the given volume. `sampRate`
        is how many samples are taken in a second and should be coordinated with the sample rate initialized in pygame.mixer.
        
        A pulse is set to a constant small width since it will be used both for low frequencies and high frequencies: for
        high frequencies a given Hz will sound like the correct pitch reqardless of pulse width, but for low frequencies
        a pulse must have small width to sound like transient click.  If the pulse width is large then, for low frequencies, 
        a click at the beginning of the pulse will be heard *distinctly* from a click at the end of the pulse and thus will - 
        e.g. for a pulse width 1/2 of the period length - double the BPM rhythm from what is wanted.  Thus a small pulse width 
        assures that the *rhythm* will be correct for low `Hz` while still maintaining the correct *pitch* at high `Hz`.

        For `phase` in [0,1], this is interpreted as a fractional value of how far into the wave's period we begin.  For
        `phase` set to 0 the pulse always begins at the very beginning of the period.  For `phase` set to, e.g., .75 we
        are .75 of the way through the default period and the next pulse will happen in .25 fraction of the period length.
        In general, the pulse will begin at a 1-`phase` fraction of the period length in construction of the pulse wave.
        
        Since only a single period of a pulse wave is returned (to be looped), large `Hz` will be Sound objects created
        from small arrays of samples, while small `Hz` will require more milliseconds (or even seconds) to express a
        single period and are thus created from large arrays.  For very small `Hz` then, this function becomes slow as
        large arrays are created and then large Sound objects are created from them.

        Parameters
        ----------
        Hz : float
            Hertz of the sound wave to be generated. Strictly positive value.
        volScale : float
            [0,1] fractional value to scale the maximum volume by.
        phase : float, default=0
            [0,1] fractional value of how far into the wave's period we begin (value can be any Real number since 
            it will be modded out by 1 anyways).  Note that this differs from using phase to denote phase offset 
            (i.e. a value to add to the input of a period function to consitute a phase shift) and is instead 
            descriptive (i.e. where in a [0,1] fraction of the period length to begin our sound wave).
        sampRate : int, default=44100
            Number of amplitude samples in a single second of a continuous sound wave.  Defaults to the common 44100 sample
            rate used in CDs and is above the Nyquist rate for a sound wave of 20,000Hz, the limit human hearing.  pygame's
            mixer also defaults to this rate and thus any changes to sampRate here should also either initialize pygame's 
            mixer to the same sample rate or at least be wary that pygame and Sound objects returned by Oscillator will
            have different reference points for how long a second is (in numbers of samples for sound).

        Returns
        -------
        pygame.Sound
            Sound object of a single period of the parameterized pulse wave.
    """
    dtype = "int8"
    maxVal = np.iinfo(dtype).max
    vol = maxVal*volScale

    secs = 1/Hz  # Get exactly enough samples for a full wave cycle.
    periodLength = int(secs*sampRate)

    # Pulse width set to the small constant of 50 samples (out of the default 44100 sample rate) unless
    # Hz is so high that 50 samples begins to span the length of the period.  In this case, for high 
    # pitches, we default to never having a pulse longer than 1/3 of the period length.
    pulseWidth = min(50, (1/3)*periodLength)

    startPulse = ((1-phase)%1)*periodLength
    endPulse = startPulse + pulseWidth

    # Typically, for a pulse wave, we simply set all samples between startPulse and endPulse to vol
    # and everything else to -vol.  However, if the pulse wraps around the period length because of
    # the phase we started at, we have to put part of the bifurcated pulse at the beginning of the
    # period and part at the end.
    endWrap = min(endPulse, endPulse % periodLength)
    wrap = bool(endWrap < endPulse)

    if not wrap:
        wave = np.array([vol if (i >= startPulse and i <= endPulse) else -vol for i in range(periodLength)], dtype=dtype)
    else:
        wave = np.array([vol if (i >= startPulse or i <= endWrap) else -vol for i in range(periodLength)], dtype=dtype)


    return pygame.sndarray.make_sound(wave)


class Polygon:
    """
        Parameters
        ----------
        num1 : int
            First number to add.
        num2 : int
            Second number to add.

        Attributes
        ----------
        radius

        See Also
        --------
        subtract : Subtract one integer from another.

        Examples
        --------
        >>> add(2, 2)
        4
        >>> add(25, 0)
        25
        >>> add(10, -10)
        0
    """
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
