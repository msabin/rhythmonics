"""
Module for simulating all harmonic components: sound, polygons, balls.

This module contains all of the visual and audio objects that comprise 
the conceptual core of rhythmonics.  The `interface` module is simply 
visualizing, making audible, and allowing interaction with the 
simulations done in this module.

An Overtone at its core has a fundamental Hertz frequency it is an 
overtone of, its own Hz which is a multiple of the fundamental depending 
on which overtone it is, and a Sound object playing a note at that Hz 
which is generated by the Oscillator function.  It further has an 
associated Polygon object which, in turn, has a Ball object traversing 
that Polygon at a rate corresponding to its associated Overtone. Lastly, 
a Tail of Ball objects trails behind the path of Ball to simulate motion 
blur.

Together, these comprise the visual and audio components of a frequency 
for rhythmonics and the `interface` module provides a GUI to display 
these on and interact with.

Classes
-------
Overtone
    Store core attributes of an Overtone, including Sound and Polygon.
Polygon
    Regular polygon (or circle) that has an attached Ball.
Ball
    Ball to traverse the Polygon that it is on.
Tail
    List of semi-transparent Ball objects attached to a head Ball.

Functions
---------
Oscillator
    Return pygame Sound object of a pulse wave.
"""
import pygame
import numpy as np
import math

import config


class Overtone:
    """
    Store core attributes of an Overtone, including Sound and Polygon.

    This class mainly stores attributes associated with an overtone, 
    mostly crucially the `Hz` and `phase`, and has a method to update 
    these two core defining attributes.  Further, Overtone has 
    attributes `oscillator` and `poly` which, respectively, stores a 
    pygame.Sound object which plays a pulse wave at `Hz` frequency and 
    associates the appropriate polgyon whose ball hits its corners/ticks 
    at `Hz` frequency.

    Attributes
    ----------
    Hz : float
        Hertz of this overtone.
    phase : float
        [0,1] fractional value, how far into the wave's period we begin.
    overtone : int
        Natural number indicating which overtone this is over the 
        fundamental tone.
    numOvertones : int
        Natural number denoting total number of overtones.
    oscillator : pygame.Sound
        Sound object playing a pulse wave at `Hz` frequency when looped.
    poly : Polygon
        Corresponding polygon whose ball hits its corners/ticks at `Hz` 
        rate.
    active : bool
        Denotes whether the overtone is active: Playing sound and moving 
        ball.

    Methods
    -------
    updateHz
        Update the Hz attribute and corresponding oscillator.
    """

    def __init__(self, overtone, poly, numOvertones, fundHz, fundPhase=0):
        """
        Initialize an inactive, muted Overtone with attached Polygon.

        Given the Hertz and phase of a fundamental frequency that this 
        object is an overtone of, create its own Hz as a multiple of the 
        fundamental frequncy, create a (muted) sound wave at that Hz, 
        and attach its associated polygon to it as an attribute.

        Parameters
        ----------
        overtone : int
            Natural number denoting which overtone this is of a 
            fundamental frequency.
        poly : Polygon
            Polygon object that is asscociated with the overtone.
        numOvertones: int
            Total number of overtones, of which this is one of them.
        fundHz : float
            Hertz of the fundamental frequency that this is an overtone 
            to.  All overtones have a Hz that is a natural number 
            multiple of this fundamental frequency.
        fundPhase : float, default=0
            [0,1] fractional value of how far into the fundamental 
            frequency's wave's period it begins at.
        """
        self.Hz = fundHz * overtone
        self.phase = fundPhase * overtone
        self.overtone = overtone
        self.numOvertones = numOvertones

        # Create an oscillator (muted to begin with) with volume 
        # `1/numOvertones` (so that sound doesn't clip even when all 
        # `numOvertones` oscillators play at once.)
        self.oscillator = Oscillator(
            self.Hz, 1 / self.numOvertones, self.phase
        )
        self.oscillator.set_volume(0)

        self.poly = poly

        self.active = False

    def updateHz(self, fundHz, fundPhase):
        """
        Update the Hz and create a new corresponding soundwave.

        Update the Hz attribute to correspond to being an overtone over 
        a new fundamental frequency with a new phase.  Stop the old 
        oscillator object from playing and create a new one with
        updated Hz and phase.  The oscillators are muted even if the 
        oscillator is active and it is the main event loop of the 
        program's job to fade in the volumes of active oscillators.

        Parameters
        ----------
        fundHz : float
            Hertz of the fundamental frequency our Overtone object is an 
            overtone of. Strictly positive value.
        fundPhase : float
            [0,1] fractional value of how far into the wave's period we 
            begin of fundamental frequency.  It is OK to have any Real 
            value here; since it is periodic, modding by 1 for such 
            values has the same result.
        """
        self.Hz = fundHz * self.overtone

        self.phase = fundPhase * self.overtone
        self.oscillator.stop()

        self.oscillator = Oscillator(
            self.Hz, 1 / self.numOvertones, self.phase
        )
        self.oscillator.set_volume(0)


def Oscillator(Hz, volScale, phase=0, sampRate=44100):
    """
    Return pygame Sound object of a single period of a pulse wave.

    Create a single period of a pulse wave of the given Hz starting at 
    the given phase with the given volume. `sampRate` is how many 
    samples are taken in a second and should be coordinated with the 
    sample rate initialized in pygame.mixer.

    For high Hz the pulse wave will sound like a buzzy pitch 
    (square waves are like sine waves with lots of overtones) and for 
    very low Hz (e.g. below 20Hz) it will sound like a rhythmic click at 
    the pulses (1Hz = 60BPM).

    For `phase` in [0,1], this is interpreted as a fractional value of 
    how far into the wave's period we begin.  For `phase` set to 0 the 
    pulse always begins at the very beginning of the period.  For 
    `phase` set to, e.g., .75 we are .75 of the way through the default 
    period and the next pulse will happen in .25 fraction of the period 
    length. In general, the pulse will begin at a `1-phase` fraction of 
    the period length in construction of the pulse wave.

    Since only a single period of a pulse wave is returned (to be 
    looped), large `Hz` will be Sound objects created from small arrays 
    of samples, while small `Hz` will require more milliseconds (or even 
    seconds) to express a single period and are thus created from large 
    arrays.  For very small `Hz` then, this function becomes slow as
    large arrays are created and then large Sound objects are created 
    from them.

    Parameters
    ----------
    Hz : float
        Hertz of the sound wave to be generated. Strictly positive 
        value.  Beyond 20,000 Hz is beyond human hearing and nears the 
        sample limit of pygame's default 44100 sample rate when 
        initialized.
    volScale : float
        [0,1] fractional value to scale the maximum volume by.
    phase : float, default=0
        [0,1] fractional value of how far into the wave's period we 
        begin (value can be any Real number since it will be modded out 
        by 1 anyways).  Note that this differs from using phase to 
        denote phase offset (i.e. a value to add to the input of a 
        period function to consitute a phase shift) and is instead
        descriptive (i.e. where in a [0,1] fraction of the period length 
        to begin our sound wave).
    sampRate : int, default=44100
        Number of amplitude samples in a single second of a continuous 
        sound wave.  Defaults to the common 44100 sample rate used in 
        CDs and is above the Nyquist rate for a sound wave of 20,000Hz, 
        the limit human hearing.  pygame's mixer also defaults to this 
        rate and thus any changes to sampRate here should also either 
        initialize pygame's mixer to the same sample rate or at least be 
        wary that pygame and Sound objects returned by Oscillator will
        have different reference points for how long a second is (in 
        numbers of samples for sound).

    Returns
    -------
    pygame.Sound
        Sound object of a single period of the parameterized pulse wave.

    Notes
    -----
    A pulse is set to a constant small width since it will be used both 
    for low frequencies and high frequencies: for high frequencies a 
    given Hz will sound like the correct pitch reqardless of pulse 
    width, but for low frequencies a pulse must have small width to 
    sound like transient click.  If the pulse width is large then, for 
    low frequencies, a click at the beginning of the pulse will be heard 
    *distinctly* from a click at the end of the pulse and thus will -
    e.g. for a pulse width 1/2 of the period length - double the BPM 
    rhythm from what is wanted.  Thus a small pulse width assures that 
    the *rhythm* will be correct for low `Hz` while still maintaining 
    the correct *pitch* at high `Hz`.
    """
    dtype = "int8"
    maxVal = np.iinfo(dtype).max
    vol = maxVal * volScale

    secs = 1 / Hz  # Get exactly enough samples for a full wave cycle.
    periodLength = int(secs * sampRate)

    # Pulse width set to the small constant of 50 samples (out of the 
    # default 44100 sample rate) unless Hz is so high that 50 samples 
    # begins to span the length of the period.  In this case, for high
    # pitches, we default to never having a pulse longer than 1/3 of the 
    # period length.
    pulseWidth = min(50, (1 / 3) * periodLength)

    startPulse = ((1 - phase) % 1) * periodLength
    endPulse = startPulse + pulseWidth

    # Typically, for a pulse wave, we simply set all samples between 
    # startPulse and endPulse to vol and everything else to -vol.  
    # However, if the pulse wraps around the period length because of
    # the phase we started at, we have to put part of the bifurcated 
    # pulse at the beginning of the period and part at the end.
    endWrap = min(endPulse, endPulse % periodLength)
    wrap = bool(endWrap < endPulse)

    if not wrap:
        wave = np.array(
            [
                vol if (i >= startPulse and i <= endPulse) else -vol
                for i in range(periodLength)
            ],
            dtype=dtype,
        )
    else:
        wave = np.array(
            [
                vol if (i <= endWrap or i >= startPulse) else -vol
                for i in range(periodLength)
            ],
            dtype=dtype,
        )

    return pygame.sndarray.make_sound(wave)


class Polygon:
    """
    Regular polygon/circle that draws itself and has an attached Ball.

    Given a radius, center, and a number of vertices, create a regular 
    polygon with those attributes by creating a list of its vertices.  
    The polygon can be draw as a polygon or as a circle with tick marks 
    at its vertex points depending whether isPointy is True or not, 
    respectively (this is most useful for when there is just one or two 
    vertices since a polygon shape is not defined well but can be used 
    for any polygon).  This class also creates the Ball object that will 
    traverse its shape and attaches it as an attribute.

    Attributes
    ----------
    radius : float
        Circumscribing radius, from center to a vertex.
    center : tuple
        Center of the regular polygon (or circle).
    color
        Color of the polygon, see pygame.Color for supported formats.
    isPointy : bool
        Boolean deciding if it is a polygon or circle.
    verts : list of pygame.Vector2 tuples
        List of polygon's vertices (created identically even if it is 
        drawn as a circle).
    ball : Ball
        Attached Ball object that will move along the Polygon's edges.
    tickLength : int
        Length of tick marks on circle's vertex points (only exists if 
        isPointy=False).
    tickColor
        Color of tick marks on circle's vertex points (only exists if 
        isPointy=False).
    inCirc : float
        Radius of the polygon's inscribed circle (only exists if 
        isPointy=True).

    Methods
    -------
    draw
        Draw polygon (or circle) on a Surface.

    See Also
    --------
    interface.Screen : Screen object that the polygons are drawn to.  
        All polygons are instantiated in Screen.__init__
    """

    def __init__(self, numVert, radius, center, color, isPointy=True):
        """
        Initialize a Polygon and create a Ball object to attach.

        This creates a list of vertices that comprise the polygon and 
        creates all the necessary attributes for a polygon as well 
        as the ball that will traverse its shape.  Further, isPointy 
        will decide whether it will be drawn as a circle or not and, if 
        it's a circle, will define the properties of the tick marks that 
        will be drawn at the vertices on the circle.  If its a polygon - 
        i.e. isPointy=True - then it also defines the radius of the 
        inscribing circle of the polygon as an easy-to-access attribute 
        so that another polygon can be easily nested inside of it.

        Parameters
        ----------
        numVert : int
            Natural number of how many vertices to construct polygon 
            from.
        radius : float
            Circumscribing radius to create vertices in.
        center : tuple
            Center of polygon that the vertices will be created around.
        color
            Color of the polygon, see pygame.Color for supported 
            formats.
        isPointy : bool, default = True
            Boolean of whether a polygon or circle should be drawn 
            around the vertices.
        """
        self.radius = radius
        self.center = center
        self.color = color
        self.isPointy = isPointy

        # Create list of regular polygon's vertices from center and 
        # radius.  Start at top (12 o'clock) and go clockwise in their 
        # creation.  Create this list even if it is a circle (i.e. 
        # isPointy=False) since we will put tick marks at the points.  
        # Ball traversing the polygon/circle will click at these points.
        self.verts = []
        for i in range(numVert):
            p = pygame.Vector2()

            p.x = center[0] + radius * math.cos(
                math.pi / 2 - 2 * math.pi / numVert * i
            )
            p.y = center[1] - radius * math.sin(
                math.pi / 2 - 2 * math.pi / numVert * i
            )

            self.verts.append(p)

        ballRadius = 7
        self.ball = Ball(self, ballRadius)

        # If the polygon is in fact a circle (i.e. isPointy=False) then 
        # we define the tick mark attributes that will be drawn on the 
        # circle.  Otherwise, for a polygon, define the radius of the 
        # inscribed circle so that other polygons can be easily nested 
        # inside each other's inscribing circle graphically as wanted.
        if not isPointy:
            self.tickLength = 5
            self.tickColor = config.MAROON
        else:
            self.inCirc = math.dist(
                center, (self.verts[0] + self.verts[1]) / 2
            )

    def draw(self, surface):
        """
        Draw the polygon (or circle with ticks) on the given surface.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw the shape onto.
        """
        if self.isPointy:
            pygame.draw.polygon(surface, self.color, self.verts, width=2)
        else:
            pygame.draw.circle(
                surface, self.color, self.center, self.radius, width=3
            )

            # Draw the tick marks on the circle where each vertex is.
            n = len(self.verts)
            for i, vert in enumerate(self.verts):
                xTick = (
                    math.cos(math.pi / 2 - 2 * math.pi * i / n)
                    * self.tickLength
                )
                yTick = (
                    math.sin(math.pi / 2 - 2 * math.pi * i / n)
                    * self.tickLength
                )
                pygame.draw.line(
                    surface,
                    self.tickColor,
                    vert - (xTick, -yTick),
                    vert + (xTick, -yTick),
                    2,
                )


class Ball:
    """
    Ball to traverse its Polygon, as the head or as part of the tail.

    A ball will have a circle drawn onto a small surface with its own 
    alpha transparency set and is attached to a Polygon that it will 
    traverse with its updatePos method.  If a ball is the head ball, 
    then it will have a tail attached to it that is a list of Ball 
    objects of increasing transparency (to simulate motion blur 
    visually).

    Attributes
    ----------
    poly : Polygon
        The Polygon object that the ball is attached to and traverses.
    radius : float
        Radius of the ball.
    alpha : int
        Alpha value in [0,255] of the surface the ball is drawn on.
    isHead : bool
        Boolean of whether the ball is the head with a tail attached or 
        just a ball.
    pos : pygame.Vector2
        Position of the center of the ball.
    color
        Color of the ball, see pygame.Color for supported formats.
    surf : pygame.Surface
        Small surface to draw only the ball on, set to `alpha` 
        transparency.
    tail : Tail
        Tail object attached to the head ball, only exists if 
        isHead=True.

    Methods
    -------
    updatePos
        Update position on `poly` based on time offset within beat.
    draw
        Draw the ball on a Surface.
    """

    def __init__(self, poly, radius, alpha=255, isHead=True):
        """
        Initialize a ball with alpha transparency and possibly a tail.

        On a polygon there will be a ball with a trailing tail of balls 
        that fades to be transparent. The head ball and tail are all 
        composed of instances of this Ball class.  Each polygon has one 
        opaque head ball (which the optional arguments are defaulted to) 
        of which this instantiation creates a Tail object as an 
        attribute.  The Tail object is composed of semi-transparent Ball
        objects that don't have a tail.  All of these balls use the 
        updatePos and draw methods here to update their positions and 
        draw themselves.

        Parameters
        ----------
        poly : Polygon
            The Polygon object that the ball is attached to and 
            traverses.
        radius : float
            Radius of the ball, value greater than 1 (used in 
            pygame.draw.circle).
        alpha : int
            Alpha in [0,255] to set the transparency of the ball.
        isHead : bool
            Boolean of whether the ball is the head with a tail attached 
            or just a ball.
        """
        self.poly = poly
        self.radius = radius
        self.alpha = alpha
        self.isHead = isHead

        self.pos = poly.verts[
            0
        ]  # All balls start at the top of their polygon.
        self.color = (
            poly.color
        )  # A ball will take on the color of the polygon it is on.

        # To draw transparent objects in pygame the surface itself must 
        # have its alpha set.  We create a surface just large enought to 
        # draw a ball on it here and set its transparency
        self.surf = pygame.Surface((self.radius * 2, self.radius * 2))
        self.surf.set_colorkey(config.BLACK)
        self.surf.set_alpha(self.alpha)
        pygame.draw.circle(
            self.surf, self.color, (self.radius, self.radius), self.radius
        )

        if isHead:
            self.tail = Tail(self)  # Only make a tail for the head ball.

    def updatePos(self, beat_offset, ms_per_beat):
        """
        Update position of ball based on time offset within beat.

        Parameters
        ----------
        beat_offset : float
            Number of milliseconds since last beat occurred.
        ms_per_beat : float
            Number of milliseconds in a beat.
        """
        if ms_per_beat == 0:
            return

        subDiv = beat_offset / ms_per_beat

        if self.poly.isPointy:
            # If we're on a polygon, find the vertices we should be 
            # between on our subdivision of a beat and interpolate 
            # between to place the ball.
            n = len(self.poly.verts)

            bigSubDiv = (subDiv * n) % n  # In [0,n), subDiv can be negative.

            # Biggest integer below bigSubDiv is the most recent vertex
            # the ball has left.
            k = math.floor(bigSubDiv)

            # In [0,1): the fraction traveled between vertex k and vertex k+1.
            t = (bigSubDiv - k)

            # Interpolate between vertex k and vertex k+1 by fraction t.
            self.pos = self.poly.verts[k].lerp(self.poly.verts[(k + 1) % n], t)
        else:
            # If we're on a circle, our subdivision of the beat tells us 
            # where the ball should be by translating from polar space 
            # to Cartesian.
            xPos = self.poly.center[0] + self.poly.radius * math.cos(
                math.pi / 2 - 2 * math.pi * subDiv
            )
            yPos = self.poly.center[1] - self.poly.radius * math.sin(
                math.pi / 2 - 2 * math.pi * subDiv
            )

            self.pos = pygame.math.Vector2(xPos, yPos)

        if self.isHead:
            self.tail.updatePos(
                beat_offset, ms_per_beat
            )  # Tail follows the head.

    def draw(self, surface):
        """
        Draw the ball (and possibly its tail) on the given Surface.

        Blit the (possibly transparent) surface attribute `surf` that 
        the ball's circle is drawn to onto the given `surface` 
        parameter.  If the Ball object is the head ball - i.e. 
        isHead=True - then draw its Tail object first underneath and 
        then blit the head.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to blit the Ball's surface onto.
        """
        if self.isHead:
            self.tail.draw(
                surface
            )  # Draw tail underneath head by drawing first.

        surface.blit(
            self.surf, self.pos - pygame.math.Vector2(self.radius, self.radius)
        )


class Tail:
    """
    Tail is a list of (semi-transparent) Balls attached to a head Ball.

    The main attribute of Tail is alphaTail, a list of Ball objects of 
    decreasing alpha.  These are positionally placed back in time behind 
    a head ball to create a fading tail and visually look like motion 
    blur. Faster speeds will stretch the tail across the Polygon that 
    the head ball is attached to.  The alphaTail list is not changed 
    once instantiated but contains enough Ball objects to fully wrap its 
    Polygon a few times when stretched at high speeds.

    Attributes
    ----------
    head : Ball
        The head Ball object that this tail will be attached to and 
        trailing.
    perimeter : float
        Perimeter of the Polygon that the tail is on.
    tailLength : int
        Number of Ball objects in the tail.
    alphaTail : list of Ball
        List of Ball objects.  This conceptually and visually is the 
        tail.  The alpha of the Balls in this list decreases: the 
        beginning of the list is opaque and fades to transparent by the 
        end.

    Methods
    -------
    updatePos
        Update position of all Ball objects in tail based on time offset 
        within beat.
    draw
        Draw the tail of Ball objects on a Surface.

    See Also
    --------
    Ball : Tail's key attribute is a list of Ball objects.  Tail's 
        updatePos and draw methods use Ball class' methods of the same 
        name.
    """

    def __init__(self, ball):
        """
        Create a list of Ball objects of increasing transparency.

        The given parameter `ball` will become the `head` attribute and 
        all balls in the tail's list will take on the head's dimensions 
        and attached polygon.  The list will be long enough that the 
        balls, placed side-by-side, will cover the polygon's perimeter a 
        few times so that the translucent tail can wrap into itself and 
        become opaque at high speeds.

        Parameters
        ----------
        ball : Ball
            The head Ball object that this tail will be attached to.
        """
        self.head = ball

        # Perimeter of the polygon the tail is on that it will need to cover.
        self.perimeter = 0
        if self.head.poly.isPointy:
            self.perimeter = len(self.head.poly.verts) * math.dist(
                self.head.poly.verts[0], self.head.poly.verts[1]
            )
        else:
            self.perimeter = 2 * math.pi * self.head.poly.radius

        # Calculate the number of balls needed (when placed side by 
        # side) to cover the polygon's perimeter.  Then scale that by 
        # some fixed amount to have a tail length that can wrap the 
        # perimeter a few times so that, at high speeds, the tail can 
        # wrap into itself and make the trail become opaque.
        polyCover = self.perimeter / (2 * self.head.radius)
        self.tailLength = int(3.5 * polyCover)

        # TODO Make alphaFade more intuitive and parameterizable.
        # Alpha fades at a logarithmic rate along the balls in the tail.  
        # Create the list alphaTail of all balls in the tail by 
        # instantiating each of them as a Ball object with decreasing 
        # alpha according to the logarithmic alphaFade function.
        def alphaFade(i):
            return self.head.alpha * (
                1 - math.log(1 + (i + 1) / self.tailLength, 2)
            )

        poly = self.head.poly
        radius = self.head.radius
        self.alphaTail = [
            Ball(poly, radius, alphaFade(i), isHead=False)
            for i in range(self.tailLength)
        ]

    def updatePos(self, beat_offset, ms_per_beat):
        """
        Update position of Tail's Balls based on time offset in beat.

        The Ball objects in the alphaTail list trail the head ball by 
        sending them positionally back in time to where the head was a 
        fixed amount of time ago, faded.  This creates a visual motion 
        blur.

        The faster the balls are traversing the polygon - i.e. the 
        smaller `ms_per_beat` - the more pronounced sending the end of 
        the list back by a fixed amount of time becomes, resulting in an 
        apparently longer tail.  While alphaTail is the same length 
        always, it is stretched across more distance of the polygon at 
        higher speeds and is compressed to be mostly overlapping on top 
        of each other at lower speeds.  The trail is never stretched so 
        far that the balls separate from each other to make a visually 
        broken tail; a cap is artifically placed to keep the tail 
        cohesively together no matter how small ms_per_beat.

        Parameters
        ----------
        beat_offset : float
            Number of milliseconds since last beat occurred.
        ms_per_beat : float
            Number of milliseconds in a beat.
        """
        # Conceptually, fadeTime is the milliseconds it takes for ball 
        # image to fade completely. Operationally, this will determine 
        # how far back in time the tail reaches back before fading 
        # completely.  Namely, where the ball was `fadeTime` 
        # milliseconds ago based on `ms_per_beat` is where the last and 
        # most transparent Ball in alphaTail will be placed.
        #
        # However, for a fixed fadeTime, if the speed is too high, the 
        # balls in the tail will separate from each other because 
        # fadeTime is too long relative to ms_per_beat.  For this, we 
        # create a maximum distance, maxDist, so that the tail never 
        # stretches apart.  Then we calculate the milliseconds for a 
        # ball to travel this distance on its polygon as ms_per_dist.  
        # Thus, fadeTime is is a fixed constant unless ms_per_dist is 
        # smaller and then we cap it at that.
        fadeTime = 22

        maxDist = (
            self.tailLength * self.head.radius
        )  # Tail balls should overlap by at least their radius
        ms_per_pixel = (
            ms_per_beat / self.perimeter
        )  # Rate of travel per beat on Tail's polygon.
        ms_per_dist = ms_per_pixel * maxDist

        fadeTime = min(fadeTime, ms_per_dist)

        # Use Ball.updatePos method for each Ball in alphaTail.  The 
        # last Ball in alphaTail, which signifies a fully faded image
        # of a moving ball having faded after `fadeTime`, is 
        # positionally sent back in time from the head ball by 
        # `fadeTime`. All other balls in the list are spaced out evenly 
        # in time between this last ball and the head ball (which is at 
        # the given `beat_offset` time in the beat).
        for i, ball in enumerate(self.alphaTail):
            ball.updatePos(
                beat_offset - fadeTime * ((i + 1) / self.tailLength),
                ms_per_beat,
            )

    def draw(self, surface):
        """
        Draw all the Ball objects in the tail on the given Surface.

        Draw all the Ball objects in the alphaTail list attribute onto 
        `surface` in reverse order so that the balls further from the 
        head and more transparent are drawn under those closer to the 
        head. Each ball in alphaTail simply uses the Ball.draw method.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw the tail onto.  Passed to Ball's draw method 
            for each Ball in the tail.
        """
        for ball in reversed(
            self.alphaTail
        ):  # Draw the lightest, furthest tail elements under the rest.
            ball.draw(surface)
