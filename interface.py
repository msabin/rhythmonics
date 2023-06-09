"""
Module for all GUI of rhythmonics project, wrapped in a console aesthetic.

This module contains and lays out all GUI components for interacting with
the Overtone objects and all sound and math simulations of the harmonics
module of rhythmonics.  The GUI components are modular and can be added to
so long as all are added as attributes of the Console class as this wraps
the entire GUI and is what is interacted with in the main event loop of
rhythmonics.

While the harmonics module creates all the conceptual simulations of the
Overtones, this module visualizes, makes audible, and allows for interaction
with those objects.

The console is meant to be conceptually illustrative in its own right as
well, however, and each area of the console is meant to further convey
the formal equivalence of polyrhythms and harmony: Most centrally, the screen
conveys movement, time, and speed, turning a polygon-based rhythm into a pitch.
The slider area shows a clear gradient between rhythm and pitch, where it
can be read in BPM or Hz simultaneously.  The radio buttons pictorally show
the overtone sine waves correspond to the polygon rhythms.  And the ratios
between active overtones can both be read as polyrhythm ratios and as
ratio between frequency pitches, making clear how polyrhythms and harmonies
are one and the same as the slider moves from low Hz to high Hz for the same
ratios.

Classes
-------
Console
    Wrap all of the GUI elements and display them as a console.
ScreenArea
    Area for the console's Screen and the border around it.
Screen
    Screen displays polygons and balls.
SliderArea
    Area for displaying and interacting with the Slider.
Slider
    Draggable slider position updates the Hz of the overtones.
RadioArea
    Area containing all radio buttons and their kill switch.
RadioBtn
    Radio button that controls the `active` status of an Overtone.
KillSwitch
    Killswitch button that turns off all radio buttons.
RatioDisp
    Area of the console displaying the ratio of active overtones.

See Also
--------
harmonics.py : Module defining Overtone objects that this module acts as a GUI for.
"""
import pygame
import math

import harmonics as hmx
import config


class Console:
    """
    Wrap all GUI elements and decide how they're displayed as a console.

    This class sets up the console aesthetics (e.g. colors, fonts, 
    layout) and initializes and collects all of its areas: ScreenArea, 
    SliderArea, RadioArea, and RatioDisp.  It also has a method for 
    drawing itself and all of its areas onto a Surface.

    Its initialization will also create the Overtone objects that the console acts as a GUI for
    displaying, voicing, and interacting with.

    Attributes
    ----------
    origin : tuple
        Position relative to window/target Surface that Console will drawn on.
    size : tuple
        Size of rectangular console area.
    baseColor
        Color of console background, see pygame.Color for supported formats.
    secColor
        Color of console foreground pieces, see pygame.Color for supported formats.
    surf : pygame.Surface
        Surface to draw console and its components onto.
    screenArea : ScreenArea
        Area for screen that displays polygons and the border around it.
    overtones : list of harmonics.Overtone
        Overtones that the console displays/voices and allows interaction with.
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
        and collect all of its areas: ScreenArea, SliderArea, RadioArea, and RatioDisp.  The
        ScreenArea's initialization will instantiate the Polygon objects to display and, with
        them, the Overtone objects that the console acts as GUI for interacting with.

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

        self.baseColor = config.PALE_PINK
        self.secColor = config.TEAL

        self.surf = pygame.Surface(self.size)

        # Initialize the screen area that displays the polygons.  The Screen both creates the Polygon objects
        # and initializes all Overtone objects based on them that the console and all if its components will
        # use and interact with.  All other areas of the console can now be instantiated after this to interact
        # with these overtones.
        screenAreaSize = pygame.Vector2(515, 425)
        screenColor = config.SURF_GREEN

        screenCenter = screenAreaSize / 2
        consoleCenter = self.size / 2
        screenAreaOrigin = consoleCenter - screenCenter - (0, 22)
        self.screenArea = ScreenArea(
            screenAreaOrigin,
            screenAreaSize,
            screenColor,
            self.secColor,
            startHz,
        )

        self.overtones = self.screenArea.screen.overtones

        # Set up all the fonts of the console so console areas can use them.
        labelsFontSize = 18
        self.labelsFont = pygame.font.Font("fonts/Menlo.ttc", labelsFontSize)
        self.labelsCol = config.DARK_POMEGRANATE

        digitalFontSize = 30
        self.digitalFont = pygame.font.Font(
            "fonts/digital-7 (mono).ttf", digitalFontSize
        )
        self.digitalOn = config.CYAN
        self.digitalOff = config.MURKY_CYAN
        self.digitalBG = config.DARK_CYAN

        # Initialize slider area.
        sliderAreaOrigin = (55, 45)
        sliderAreaHeight = self.size[1] * 0.85
        self.sliderArea = SliderArea(self, sliderAreaOrigin, sliderAreaHeight)

        # Initialize area for radio buttons and kill switch.
        radioAreaOrigin = (810, 65)
        radioAreaSize = (135, 390)
        self.radioArea = RadioArea(self, radioAreaOrigin, radioAreaSize)

        # Initialize area for digital displays of ratios between active overtones.
        ratioOrigin = screenAreaOrigin + (138, screenAreaSize[1] + 30)
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
        pygame.draw.rect(
            self.surf, self.baseColor, ((0, 0), self.size), border_radius=50
        )

        # Draw all of console's areas onto console's surface.
        self.screenArea.draw(self.surf)
        self.sliderArea.draw(self.surf)
        self.radioArea.draw(self.surf)
        self.ratioDisp.draw(self.surf)

        # Blit console's surface onto the target surface/window.
        targetSurf.blit(self.surf, self.origin)


class ScreenArea:
    """
    Area for the Screen that displays polygons and the border around it.

    The screen area size and origin accounts for the border and a Screen
    object is initalized to be a smaller size and offsets its origin within
    the border area.

    Attributes
    ----------
    border : pygame.Rect
        Rectangle used to draw the border around the Screen on the Console.
    borderRadius : int
        Radius of corners of `border` to draw a border with rounded corners.
    bigBorderRadius : int
        Large radius to draw a very round corner if wanted.
    borderCol
        Color to draw `border` rectangle, see pygame.Color for supported formats.
    screen : Screen
        Screen object that Polygon objects are drawn on.

    Methods
    -------
    draw
        Draw the screen area (border and screen) on a surface.
    """

    def __init__(self, origin, size, screenCol, borderCol, startHz):
        """
        Initialize the screen area with a border and a Screen object.

        Initializing the Screen object will create the Overtone objects that
        the screen will display and the rest of the console will interact with.

        Parameters
        ----------
        origin : pygame.Vector2
            Position relative to Console origin that this area will be drawn onto.
        size : tuple
            Size of entire screen area, including border.
        screenCol
            Color of screen background, see pygame.Color for supported formats.
        borderCol
            Color of border around screen, see pygame.Color for supported formats.
        startHz : float
            Positive number of the fundamental Hz to initialize overtones with.
        """
        self.border = pygame.Rect(origin, size)
        self.borderRadius = 5
        self.bigBorderRad = 40
        self.borderCol = borderCol

        # Offset and size the screen within the border area and instantiate screen.
        screenOrigin = pygame.Vector2(origin) + (45, 25)
        screenSize = pygame.Vector2(size) - (90, 76)
        self.screen = Screen(screenOrigin, screenSize, screenCol, startHz)

    def draw(self, surf):
        """
        Draw the screen area (border and screen) on a surface.

        Parameters
        ----------
        surf : pygame.Surface
            Surface to draw the screen area onto.
        """
        # Draw the border on the Surface and then draw have the screen draw itself on top.
        pygame.draw.rect(
            surf,
            self.borderCol,
            self.border,
            border_radius=self.borderRadius,
            border_bottom_right_radius=self.bigBorderRad,
        )

        self.screen.draw(surf)


class Screen:
    """
    Screen displays polygons and balls and instantiates the console's overtones.

    This class creates and holds the overtones for the console and draws the polygons
    of those overtones and their balls.  This is where rhythms are visualized at low
    Hz: balls rhythmically traversing polygons at certain speeds.  It is still
    visualized at high speeds, although the balls' paths become blurred at high Hz.
    This is the main visual component of the console, the rest is for GUI interaction.

    Attributes
    ----------
    origin : pygame.Vector2
        Position relative to Console origin that this area will be drawn onto.
    size : pygame.Vector2
        Size of screen where polygons are displayed.
    color
        Color of screen background, see pygame.Color for supported formats.
    surf : pygame.Surface
        Surface of screen to draw onto.
    overtones : list of harmonics.Overtone
        Overtones whose polygons the screen will display.
    """

    def __init__(self, origin, size, color, startHz):
        """
        Initialize the screen, the polygons that will be on it, and the overtones.

        The polygons that will be drawn on the screen are all instantiated here with respect
        to the screen position.  Polygons are crafted and nested aesthetically but arbitrarily,
        their layout can be changed here.  Once the polgyons are instantiated they are used
        to instantiate the attached overtones that the rest of the console will use.

        Parameters
        ----------
        origin
            Position relative to Console origin that this area will be drawn onto.
        size
            Size of screen where polygons are displayed.
        color
            Color of screen background, see pygame.Color for supported formats.
        startHz
            Positive number of the fundamental Hz to initialize overtones with.
        """
        self.origin = origin
        self.size = size
        self.color = color
        self.surf = pygame.Surface(size)

        center = self.size / 2

        # Polygon aesthetics and nesting can be crafted here.  This is aesthetic and there
        # are many possible choices, there is nothing inherent about the choices made here.
        rootColor = config.KHAKI
        thirdColor = config.LIGHT_COBALT
        fifthColor = config.SORBET
        seventhColor = config.POMEGRANATE

        rootRadius = (0.94 * min(self.size[0], self.size[1])) / 2

        # Polygons are named by their scale degree relative to the fundamental root frequency, `root1`.
        # Order is mixed based on which polygons are inscribed in each other since they need to access
        # their circumscribing Polygon object's `inCirc` attribute.  The first parameter in the
        # instantiation of a Polygon object is the number of vertices - i.e. which overtone it is.
        root4 = hmx.Polygon(8, rootRadius, center, rootColor)

        root1 = hmx.Polygon(
            1, root4.inCirc - 10, center, rootColor, isPointy=False
        )
        root3 = hmx.Polygon(4, root4.inCirc - 10, center, rootColor)

        root2 = hmx.Polygon(2, root3.inCirc, center, rootColor, isPointy=False)
        fifth1 = hmx.Polygon(3, root3.inCirc, center, fifthColor)
        fifth2 = hmx.Polygon(6, root3.inCirc, center, fifthColor)

        third1 = hmx.Polygon(5, fifth1.inCirc, center, thirdColor)

        seventh1 = hmx.Polygon(7, third1.inCirc, center, seventhColor)

        polys = [root1, root2, fifth1, root3, third1, fifth2, seventh1, root4]

        numOvertones = len(polys)
        self.overtones = [
            hmx.Overtone(len(poly.verts), poly, numOvertones, startHz)
            for poly in polys
        ]

    def draw(self, targetSurf, offset=pygame.Vector2(0, 0)):
        """
        Draw the screen and everything on the screen (polygons and balls) onto a surface.

        All polygons are always drawn and only the balls of active overtones are drawn.  The
        screen can be offset from its origin but the default is no offset.  The screen origin
        is relative to the console the screen is on but if the screen is being drawn to a
        different surface, such as the main window so the console doesn't have to be redrawn
        as often as the screen, then the offset should be set accordingly to keep it drawn to
        the right spot on the console, see Examples.

        Parameters
        ----------
        targetSurf : pygame.Surface
            Surface to draw the screen onto
        offset : pygame.Vector2, default=pygame.Vector2(0,0)
            x, y distances to offset the screen's origin by when drawing.  E.g. If
            `targetSurf` is the main window, so that the screen is drawn directly to the
            window instead of the Console surface, that should be accounted for by
            offsetting our draw position by the console's origin.

        Examples
        --------
        To draw on the console, the offset can be ignored.

        >>> screen.draw(console.surf)

        If drawing on the main window, the origin should be offset by the console origin
        so that it continues to draw relative to its position on the console.

        >>> screen.draw(window, console.origin)
        """
        self.surf.fill(self.color)

        for overtone in self.overtones:
            overtone.poly.draw(self.surf)

            if overtone.active:
                overtone.poly.ball.draw(self.surf)

        targetSurf.blit(self.surf, self.origin + offset)


class SliderArea:
    """
    Area for the Slider and its UI: slider handle, labels, BPM/Hz digital displays.

    This class creates the slider, the labels along the slider, and the slider's digital
    display boxes and lays them all out visually with its draw method.

    Attributes
    ----------
    origin : pygame.Vector2
        Position relative to Console origin that this area will be drawn onto.
    height : int
        Height of entire slider area, including digital display boxes.
    color
        Color of slider handle, see pygame.Color for supported formats.
    HzLabel : pygame.Surface
        Surface with 'Hz' label of Hz digital display box rendered onto it.
    BPM_Label : pygame.Surface
        Surface with 'BPM' label of BPM digital display box rendered onto it.
    labels : list of pygame.Surface
        List of surfaces with the slider's labels rendered onto them.
    digitalFont : pygame.font.Font
        Font of the slider's digital displays.
    digitalOn
        Color of digital font when "lit up," see pygame.Color for supported formats.
    HzBox : pygame.Surface
        Surface with the digital display box for Hz rendered onto it.
    BPM_Box : pygame.Surface
        Surface with the digital display box for BPM rendered onto it.
    horizontalBuf : int
        Horizontal buffer space for laying out slider graphics visually.
    labelsWidth : int
        Maximum width of all the slider's labels.
    slider : Slider
        The Slider object of the slider's controllable handle.

    Methods
    -------
    draw
        Draw the entire slider area on a surface.
    """

    def __init__(self, console, origin, height):
        """
        Initialize and collect slider area components: slider, labels, and digital displays.

        Initializes the Slider object and renders all slider's label text and digital displays.
        Origin is relative to console's origin and height of slider area includes the digital
        display boxes.

        Parameters
        ----------
        console : Console
            Console that the slider controls and is a component of.
        origin : pygame.Vector2
            Position relative to Console origin that this area will be drawn onto.
        height : int
            Height of entire slider area, including digital display boxes.
        """
        self.origin = origin
        self.height = height

        # Color of slider handle is console's color for foreground pieces.
        self.color = console.secColor

        # Create all labels for the Slider Area.
        labelsFont = console.labelsFont
        self.labelsCol = console.labelsCol

        self.HzLabel = labelsFont.render("Hz", True, self.labelsCol)
        self.BPM_Label = labelsFont.render("BPM", True, self.labelsCol)

        labelsText = ["FREEZE", "GROOVE", "CHAOS", "HARMONY", "EEEEEE"]
        self.labels = [
            labelsFont.render(text, True, self.labelsCol)
            for text in labelsText
        ]

        # Create digital display boxes for Hz and BPM.
        self.digitalFont = console.digitalFont
        self.digitalOn = console.digitalOn
        digitalOff = console.digitalOff
        digitalBG = console.digitalBG

        self.HzBox = self.digitalFont.render(
            " 8888.88 ", False, digitalOff, digitalBG
        )
        self.BPM_Box = self.digitalFont.render(
            " 888888 ", False, digitalOff, digitalBG
        )

        # Set up parameters to instantiate the slider, nested between Hz and BPM digital displays.
        # Note, `sliderMaxy` will be the *lowest* on the screen that the slider handle can go since
        # the origin of things is the top left corner and y increases downwards.
        verticalBuf = 30
        self.horizontalBuf = 20
        sliderMiny = self.origin[1] + self.HzBox.get_height() + verticalBuf
        sliderMaxy = (
            self.origin[1]
            + self.height
            - self.BPM_Box.get_height()
            - verticalBuf
        )

        # Find the slider starting position (offset x coordinate with enough room for labels) and create slider.
        sliderSize = (20, 40)
        self.labelsWidth = max([label.get_width() for label in self.labels])
        sliderOffset = (
            self.origin[0]
            + self.labelsWidth
            + self.horizontalBuf
            + sliderSize[0]
        )
        sliderStart = 0.25  # Slider knob starts at this fraction of the slider range. GROOVE is at .25.
        sliderPos = pygame.Vector2(
            sliderOffset, sliderMaxy - sliderStart * (sliderMaxy - sliderMiny)
        )

        self.slider = Slider(
            sliderPos,
            sliderSize,
            self.color,
            console.overtones,
            sliderMiny,
            sliderMaxy,
        )

    def draw(self, surface):
        """
        Draw the entire slider area on a surface.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw the slider area onto.
        """
        # Draw slider track's rut and then the slider handle.
        sliderRutCol = (150, 150, 150)
        sliderMin = (self.slider.pos[0], self.slider.miny)
        sliderMax = (self.slider.pos[0], self.slider.maxy)
        pygame.draw.line(surface, sliderRutCol, sliderMin, sliderMax, width=2)

        self.slider.draw(surface)

        # Draw Hz display: HzBox and label and then current Hz in box.
        surface.blit(self.HzBox, (self.origin[0], self.origin[1]))

        HzLabelOffset = (
            self.origin[0] + self.HzBox.get_width() + self.horizontalBuf / 2
        )
        surface.blit(self.HzLabel, (HzLabelOffset, self.origin[1]))

        Hz = self.slider.overtones[0].Hz
        HzString = " " + f"{Hz:07.2f}".replace("1", " 1") + " "
        HzDisp = self.digitalFont.render(HzString, False, self.digitalOn)
        surface.blit(HzDisp, (self.origin[0], self.origin[1]))

        # Draw slider labels and arrows next to them.
        for i, label in enumerate(self.labels):
            fntHeight = label.get_height()
            xPos = self.origin[0]
            yPos = (self.slider.maxy - fntHeight / 2) - (i / 4) * (
                self.slider.maxy - self.slider.miny
            )

            surface.blit(label, (xPos, yPos))

            xOffset = xPos + self.labelsWidth + 10  # Draw arrow next to label.
            arrowWidth = 5
            arrowPoints = [
                (xOffset, yPos + 3),
                (xOffset, yPos + fntHeight - 3),
                (xOffset + arrowWidth, yPos + fntHeight / 2),
            ]
            pygame.draw.polygon(surface, self.labelsCol, arrowPoints)

        # Draw BPM display: BPM_Box and label and then current BPM in box.
        yOffset = self.origin[1] + self.height - self.BPM_Box.get_height()
        surface.blit(self.BPM_Box, (self.origin[0], yOffset))

        BPM_Label_Offset = (
            self.origin[0] + self.BPM_Box.get_width() + self.horizontalBuf / 2
        )
        surface.blit(self.BPM_Label, (BPM_Label_Offset, yOffset))

        BPM = Hz * 60
        BPM_String = " " + f"{BPM:06.0f}".replace("1", " 1") + " "
        BPM_Disp = self.digitalFont.render(BPM_String, False, self.digitalOn)
        surface.blit(BPM_Disp, (self.origin[0], yOffset))


class Slider:
    """
    Slider can be dragged and its position updates the Hz of the overtones.

    This class creates a slider handle whose position controls the Hz of the
    console's overtones.  This class' `updateVolt` method defines how the
    position of the slider is translated into voltage for the fundamental
    frequency for the overtones.

    Attributes
    ----------
    pos : pygame.Vector2
        Position of center of slider handle relative to Console origin.
    size : pygame.Vector2
        Size of the slider handle rectangle.
    color
        Color of slider handle, see pygame.Color for supported formats.
    overtones : list of harmonics.Overtone
        Overtones that the slider is controlling the Hz of.
    miny : int
        Minimum y value Slider.pos can take on relative to the Console its on.
        Note, this is positional and so will be the *highest* that the slider
        can go since the console origin is in the top left corner.
    maxy : int
        Maximum y value Slider.pos can take on relative to the Console its on.
        Note, this is positional and so will be the *lowest* that the slider
        can go since the console origin is in the top left corner.
    isSelected : bool
        Boolean of whether the slider handle is being controlled.
    handle : pygame.Rect
        Rect object that is visually displayed as the slider handle.
    quarterTarget : float
        Hz that fundamental overtone will be set to at the quarter point of
        the slider scale.
    halfTarget : float
        Hz that fundamental overtone will be set to at the halfway point of
        the slider scale.
    threeQuartTarget : float
        Hz that fundamental overtone will be set to at the three quarters
        point of the slider scale.
    topTarget : float
        Hz that fundamental overtone will be set to at the top of the slider
        scale.

    Methods
    -------
    updateVolt
        Update the Hz of the overtones' oscillators from slider's position.
    draw
        Draw the slider handle on a surface.
    """

    def __init__(self, position, size, color, overtones, miny, maxy):
        """
        Initialize the slider and the target Hz values it should hit.

        Create a slider handle, a boolean of whether it is currently selected, and
        the target Hz values at the quarter marks of the slider track that the slider
        should interpolate between when updating the Hz of the fundamental frequency
        of the overtones.

        Parameters
        ----------
        position : tuple
            Starting osition of center of slider handle relative to Console origin.
        size : tuple
            Size of the slider handle rectangle.
        color
            Color of slider handle, see pygame.Color for supported formats.
        overtones : list of harmonics.Overtone
            Overtones that the slider will be controlling the Hz of.
        miny
            Minimum y value Slider.pos can take on relative to the Console its on.
            Note, this is positional and so will be the *highest* that the slider
            can go since the console origin is in the top left corner.
        maxy
            Maximum y value Slider.pos can take on relative to the Console its on.
            Note, this is positional and so will be the *lowest* that the slider
            can go since the console origin is in the top left corner.
        """
        self.pos = pygame.Vector2(position)
        self.size = pygame.Vector2(size)
        self.color = color

        self.overtones = overtones

        self.miny = miny
        self.maxy = maxy

        self.isSelected = False

        self.handle = pygame.Rect(self.pos - self.size / 2, self.size)

        # Set the target Hz values the slider should affect at the quarter marks of the slider track.
        # The quarter and halfway point should not yet sound like a pitch and should sound like a
        # (possibly very fast) rhythm.  After the halfway point even the lowest overtone should sound
        # like a pitch.
        #
        # This both fits conceptually with rhythmonics in relating rhythm and pitch, where the slider
        # makes this relationship clear, and also matches the implementation: In this class' updateVolt
        # method, the quarter and halway point are scaled linearly while the other target points are
        # scaled to logarithmically.  The linear scaling in the rhythmic BPM half of the slider scale
        # matches a smooth scaling of rhythm, while the rest of the slider track fits human perception
        # of pitch since we hear increase in pitches logarithmically.  Choosing appropriately gives a
        # smooth and natural scaling in both conceptual components of rhythmonics: rhythm and pitch.
        self.quarterTarget = (
            1  # Up to quarter of the way, linearly scale up to 1Hz=60bpm.
        )
        self.halfTarget = 275 / 60  # Linearly scales up to 275/60Hz = 275bpm
        self.threeQuartTarget = 110
        self.topTarget = 2000

    def updateVolt(self, beat_offset, clock):
        """
        Update the Hz of all overtones based on the slider's position.

        The slider has target Hz values to be assigned at the quarter marks of the
        slider and either scales linearly or logarithmically towards those values
        depending on whether the Hz is in a range that sounds like discrete rhythms
        or a continuous pitch, respectively.  This function updates the Hz of all
        the overtones according to the scaling based on where the slider handle is
        positioned.

        This function uses takes as parameters the number of milliseconds since the
        last beat, `beat_offset`, and the main event loop's `clock` to make sure the
        the phase of the sound waves matches the beat offset so that the sound and
        graphics of the console system are matched up.  The new `beat_offset` and
        number of milliseconds in a beat, `ms_per_beat`, (updated with the new Hz)
        are returned to keep the event loop in sync with the sound.

        Parameters
        ----------
        beat_offset : int
            Number of milliseconds since last beat occurred.
        clock : pygame.time.Clock
            Clock of the main event loop keeping everything synced.

        Returns
        -------
        beat_offset : int
            Number of milliseconds since last beat occurred.
        ms_per_beat : int
            Number of milliseconds in a beat.

        Notes
        -----
        The name `updateVolt` is used to conceptually capture the analog sound systems
        this console conceptually emulates: Sounds are produced by the harmonics.Oscillator
        function which is inspired by analog circuits called Voltage-Controlled Oscillators
        (VCOs) which create a sound wave at a frequency that depends on the voltage supplied
        to it.  Conceptually, the slider is providing the voltage here and speeding up or
        slowing down the VCO, and thus increasing or decreasing the pitch of the sound,
        respectively.
        """
        # Translate the slider position to the new Hz.
        HzScale = abs(self.pos[1] - self.maxy) / (
            self.maxy - self.miny
        )  # [0,1] value of where slider is on track (1 is top).

        # TODO Define a log function for that is intuitive and parameterizable for scaling these.
        if HzScale <= 0.25:
            Hz = self.quarterTarget * HzScale / 0.25
            if Hz <= 0.02:
                Hz = 0  # Too low Hz takes too much time to make Sound object, just make it 0.
        elif HzScale <= 0.5:
            Hz = (1 - (HzScale - 0.25) / 0.25) + self.halfTarget * (
                HzScale - 0.25
            ) / 0.25
        elif HzScale <= 0.75:
            Hz = 275 / 60 + (110 - 275 / 60) * math.log(
                1 + (HzScale - 0.5) / 0.25, 2
            )  # log scales up to 110Hz (4th harmonic/2nd octave will be 440Hz)
        else:
            Hz = 110 + (2000 - 110) * math.log(
                1 + (HzScale - 0.75) / 0.25, 2
            )  # Caps at 2000 Hz (seventh harmonic will be at 14000Hz)

        # Update all the oscillators with the new Hz.
        if Hz == 0:
            ms_per_beat = 0
            for overtone in self.overtones:
                overtone.Hz = 0
                overtone.oscillator.stop()
        else:
            # Start updated soundwaves in the future by buffer_time and then wait to play them so that
            # they will be in sync with graphics.
            #
            # This is done since, at low Hz, the function harmonics.Oscillator can take a long time to
            # create a Sound object and so using the beat_offset time to shift the sound waves' phases
            # by may be stale by the time all the Sound objects are created and ready to be played.
            #
            # Giving ourselves enough buffer time to finish updating the Hz of the oscillators and play
            # them allows them to be in proper sync with the clock and thus the movement of the
            # polygons' balls.
            ms_per_beat = 1000 / Hz

            buffer_time = (
                1 / Hz
            ) * 26  # Chosen ad hoc; graphics sync well and doesn't take noticeably longer time.

            beat_offset = (beat_offset + clock.get_time()) % ms_per_beat
            clock.tick()

            for overtone in self.overtones:
                overtone.updateHz(
                    Hz, (beat_offset + buffer_time) / ms_per_beat
                )

            msLeftToWait = int(
                max(buffer_time - clock.tick(), 0)
            )  # Start immediately if we passed our buffer_time.
            pygame.time.wait(msLeftToWait)

            for overtone in self.overtones:
                overtone.oscillator.play(loops=-1)

        return beat_offset, ms_per_beat

    def draw(self, surface):
        """
        Update slider handle with position and draw it to a surface.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw slider handle onto.
        """
        self.handle = pygame.Rect(self.pos - self.size / 2, self.size)
        pygame.draw.rect(surface, self.color, self.handle)


class RadioArea:
    """
    Area containing all radio buttons, sine wave graphics, and kill switch.

    This area has radio buttons that allow for turning each overtone on or of - i.e.
    toggling the overtone `active` boolean attribute.  It has sine waves to graphically
    represent the overtone next to its associated radio button.  And there is a kill
    switch button that allows all the radio buttons to be turned off at once.

    Attributes
    ----------
    origin : pygame.Vector2
        Position relative to Console origin that this area will be drawn onto.
    size : pygame.Vector2
        Size of the radio area.
    radios : list of RadioBtn
        A radio button corresponding to each overtone of the Console.
    sines : list of pygame.Surface
        Each surface has a sine wave of an overtone drawn on it.
    killSwitch : KillSwitch
        Kill switch for turning off all radio buttons.
    killSwitchLabel : pygame.Surface
        Surface with a label for the kill switch rendered onto it.

    Methods
    -------
    draw
        Draw the radio button area onto a surface.
    """

    def __init__(self, console, origin, size):
        """
        Initialize the radio area: create radio and kill switch buttons, and draw sine waves.

        Make a radio button for each overtone and draw a sine wave representing the overtone on a
        surface.  Create a kill switch and a label for the kill switch.

        Parameters
        ----------
        console : Console
            Console that the radio area is a component of and controls.
        origin : tuple
            Position relative to Console origin that this area will be drawn onto.
        size : tuple
            Size of the radio area.
        """
        self.origin = pygame.Vector2(origin)
        self.size = pygame.Vector2(size)

        # For each overtone create a radio button and draw a representative sine wave.
        self.radios = []
        self.sines = []

        totalOvertones = len(console.overtones)
        self.horizontalBuf = 20

        radioRad = 5

        # Parameters for drawing sine waves
        sineLength = size[0] - self.horizontalBuf
        sampRate = 55
        peakHeight = 10
        tickLength = 4
        tickWidth = 1
        sineCol = config.LIGHT_MAROON
        for overtone in console.overtones:
            overtoneNum = overtone.overtone

            # Create radio button associated with the overtone.
            yOffset = origin[1] + (overtoneNum - 1) * size[1] / (
                totalOvertones - 1
            )
            radio = RadioBtn((origin[0], yOffset), radioRad, overtone)
            self.radios.append(radio)

            # Draw picture of the sine wave of the overtone.
            yOffset = (
                peakHeight + tickLength
            )  # Put sine wave (w/ tick mark) in middle of the surface.
            sineSurface = pygame.Surface((sineLength, yOffset * 2))
            sineSurface.fill(console.baseColor)

            wave = []
            for i in range(sampRate):
                xVal = (i / sampRate) * sineLength
                yVal = -peakHeight * math.sin(
                    2 * math.pi * i / sampRate * overtoneNum / 2
                )

                wave.append((xVal, yVal + yOffset))

            pygame.draw.aalines(sineSurface, sineCol, False, wave)

            # Draw a tick on each of the sine wave's peaks (pictorally represent rhythm at low Hz).
            for i in range(overtoneNum):
                peakOffset = (2 * i + 1) * sineLength / (overtoneNum * 2)
                peakParity = peakHeight * (-1) ** (i + 1) + yOffset

                tickStart = (peakOffset, peakParity + tickLength / 2)
                tickEnd = (peakOffset, peakParity - tickLength / 2)
                pygame.draw.line(
                    sineSurface, sineCol, tickStart, tickEnd, tickWidth
                )

            self.sines.append(sineSurface)

        # Create the kill switch for the radio buttons and its label.
        killSwitchSize = (15, 15)
        killSwitchOrigin = (origin[0], origin[1] + size[1] + 55)
        self.killSwitch = KillSwitch(
            killSwitchOrigin, killSwitchSize, console.secColor, self.radios
        )

        self.killSwitchLabel = console.labelsFont.render(
            "SSHHHHHHH!", True, console.labelsCol
        )

    def draw(self, surface):
        """
        Draw the radio area: Radio buttons, sine waves, and kill switch.

        For each overtone, draw its radio button and a sine wave representing it next to
        the button.  Draw the kill switch for the radio buttons underneath them all.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw the radio button area onto.
        """
        for radio, sine in zip(self.radios, self.sines):
            radio.draw(surface)

            surface.blit(
                sine, radio.pos + (self.horizontalBuf, -sine.get_height() / 2)
            )

        self.killSwitch.draw(surface)
        labelOffset = (
            self.horizontalBuf - 2,
            -self.killSwitch.size[1] / 2 - 3,
        )
        surface.blit(self.killSwitchLabel, self.killSwitch.pos + labelOffset)


class RadioBtn:
    """
    Radio button that controls the `active` status of an Overtone.

    A radio button is associated with an overtone and can be pressed, toggling whether
    that overtone is active or not.  The radio button lights up when active and can
    draw itsef.

    Attributes
    ----------
    overtone : harmonics.Overtone
        Overtone that the radio button controls.
    active : bool
        Boolean of whether the radio button (and corresponding overtone) is active.
    pos : pygame.Vector2
        Position of the center of radio button (relative to console origin).
    radius : int
        Radius of radio button.
    borderCol
        Color of the border around the radio button, see pygame.Color for supported formats.
    borderWidth : int
        Width of the border around the radio button.
    offCol
        Color of the button when `active=False`, see pygame.Color for supported formats.
    lightCol
        Color of the light when `active=True`, see pygame.Color for supported formats.
    light : pygame.Surface
        Surface with a "bloom effect" of `lightCol` when `active=True`.

    Methods
    -------
    press
        Press the radio button and toggle the associated overtone.
    draw
        Draw the radio button on a surface.
    """

    def __init__(self, position, radius, overtone):
        """
        Initialize the radio button and an image of its light when active.

        Parameters
        ----------
        position : tuple
            Position of the center of radio button (relative to console origin).
        radius : int
            Radius of radio button.
        overtone : pygame.Overtone
            Overtone that the radio button controls.
        """
        self.overtone = overtone

        self.active = self.overtone.active

        self.pos = pygame.Vector2(position)
        self.radius = radius

        self.borderCol = config.DARK_TEAL
        self.borderWidth = 2

        # Set color of radio button when `active=False` same as its overtone's color
        # except darken it a bit.
        self.offCol = pygame.Color(self.overtone.poly.color)
        hsva = self.offCol.hsva
        self.offCol.hsva = (hsva[0], hsva[1], hsva[2] - 40, hsva[3])

        # Set color of radio button when `active=True` same as its overtone's color
        # except lighten it a bit.
        self.lightCol = pygame.Color((self.overtone.poly.color))
        hsla = self.lightCol.hsla
        self.lightCol.hsla = (hsla[0], hsla[1], hsla[2] + 3, hsla[3])

        # Create surface whose color and alpha value can be set on a per-pixel basis to
        # draw `lightCol` on in a bloom effect sort of way to simulate light.
        #
        # This will be done by just having a bivariate Gaussian fade the light from the
        # center - i.e. alpha will descrease according to a Gaussian.
        self.light = pygame.Surface(
            (self.radius * 2, self.radius * 2), pygame.SRCALPHA
        )
        self.light.set_colorkey(config.BLACK)

        def bivarGauss(x, y, mu, sigma, height):
            """
            Bivariate Gaussian function of two i.i.d. variaables.

            Since variables are i.i.d., this function just takes one mu and one sigma for
            both variables.  The bivariate Gaussian will thus always be circular.

            The height of the peak of the Gaussian can be set arbitrarily.  Set height to
            1/(2*math.pi * sigma**2) for a valid pdf of a bivariate normal distribution.

            Parameters
            ----------
            x
                Value of first variable
            y
                Value of second variable
            mu
                Mean of both random variables: center of bivariate Gaussian.
            sigma
                Standard deviation of both variables, controls rate of fall-off.
            height
                Height of Gaussian (usually the normalizing constant in a pdf).

            Return
            ------
            float
                Value of parameterized Gaussian at (x,y).
            """
            return height * math.e ** (
                -1 / 2 * ((x - mu) ** 2 + (y - mu) ** 2) / sigma**2
            )

        mu = (
            self.radius
        )  # Center of Gaussian (which is center of radio button).
        sigma = (
            self.radius * 4 / 7
        )  # Fall-off rate chosen for visual aesthetics.
        height = (
            255  # Height is max opaque alpha and then fades to transparent.
        )

        # Go to each pixel on the surface and set its alpha according to the bivariate
        # Gaussian and color the pixel with the `lightCol`.
        for x in range(radius * 2):
            for y in range(radius * 2):
                alpha = int(bivarGauss(x, y, mu, sigma, height))
                self.lightCol.a = alpha
                self.light.set_at((x, y), self.lightCol)

    def press(self):
        """
        Press the button: toggle `active` and the associated overtone's `active`.

        Toggle `active` for both the button and the associated overtone. The
        oscillators are muted even if the oscillator is active and it is the main
        event loop of the program's job to fade in the volumes of active oscillators.
        """
        self.active = not self.active

        self.overtone.active = self.active
        self.overtone.oscillator.set_volume(0)

    def draw(self, surface):
        """
        Draw the radio button and border and, if active, light on the button.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw the radio button on.
        """
        # Draw unlit radio button
        pygame.draw.circle(surface, self.offCol, self.pos, self.radius)

        # If the button is active draw the light on the button
        if self.active:
            surface.blit(self.light, self.pos - (self.radius, self.radius))

        # Draw border around the button.
        pygame.draw.circle(
            surface,
            self.borderCol,
            self.pos,
            self.radius + self.borderWidth,
            2,
        )


class KillSwitch:
    """
    Killswitch button that turns off all radio buttons when pushed.

    The killswitch always turns off all radio buttons when pushed.  The button shrinks
    slightly when pressed and clicks when both pressed and released for skeumorphic
    effect.

    Attributes
    ----------
    pos : pygame.Vector2
        Position of the center of the killswitch button (relative to console origin).
    size : pygame.Vector2
        Size of the (unpressed) killswitch button.
    color
        Color of button, see pygame.Color for supported formats
    button : pygame.Rect
        Rectangle of the position and size of the killswitch button.
    pressedButton : pygame.Rect
        Smaller rectangle of the pushed in killswitch button.
    isPressed : bool
        Boolean of whether the button is pressed.
    downClick : pygame.Sound
        Sound to play when the button gets pressed.
    upClick : pygame.Sound
        Sound to play when the button gets released.
    borderRad : int
        Border radius of the button for rounded corners.

    Methods
    -------
    press
        Press the killswitch and turn off all the overtones.
    draw
        Draw the killswitch on a surface (smaller if it's pressed).
    """

    def __init__(self, position, size, color, radios):
        """
        Initialize the killswitch and create sounds for it being pressed.

        Parameters
        ----------
        position : tuple
            Position of the center of the killswitch button (relative to console origin).
        size : tuple
            Size of the (unpressed) killswitch button.
        color
            Color of the button, see pygame.Color for supported formats
        radios : list of RadioBtn
            Radio buttons that the killswitch turns off.
        """
        self.pos = pygame.math.Vector2(position)
        self.size = pygame.math.Vector2(size)
        self.color = color

        self.radios = radios

        self.button = pygame.Rect(self.pos - self.size / 2, self.size)

        pressedSize = self.size - (1, 1)
        self.pressedButton = pygame.Rect(
            self.pos - pressedSize / 2, pressedSize
        )

        self.isPressed = False

        self.downClick = pygame.mixer.Sound("sounds/down-click.wav")
        self.upClick = pygame.mixer.Sound("sounds/up-click.wav")

        self.borderRad = 4

    def press(self):
        """
        Press the killswitch: toggle `isPressed` and turn off all active overtones.
        """
        self.isPressed = not self.isPressed

        if self.isPressed:
            self.downClick.play()
            pygame.time.wait(
                100
            )  # Give enough time for sound to play before upClick.

            for radio in self.radios:
                if radio.active:
                    radio.press()
        else:
            self.upClick.play()

    def draw(self, surface):
        """
        Draw the killswitch on a surface (smaller if it's pressed).

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw the killswitch onto.
        """
        if not self.isPressed:
            pygame.draw.rect(
                surface, self.color, self.button, 0, self.borderRad
            )
        else:
            pygame.draw.rect(
                surface, self.color, self.pressedButton, 0, self.borderRad - 1
            )


class RatioDisp:
    """
    Area of the console that displays the ratio of active overtones on digital displays.

    Single-digit digital display boxes are spread out evenly with colons between them. There
    is one box for each overtone and the box lights up with the number of the overtone when
    that overtone is active.

    Attributes
    ----------
    origin : pygame.Vector2
        Position relative to Console origin that this area will be drawn onto.
    overtones : harmnonics.Overtone
        Overtones that this area will display the ratio of the active ones.
    digitalFont : pygame.font.Font
    digitalOn
        Color of digital font when "lit up," see pygame.Color for supported formats.
    digitalSlot : pygame.Surface
        Surface with a digital display slot rendered onto it.
    ratioColon : pygame.Surface
        Surface with a colon for the ratios rendered onto it.
    horizontalBuf : int
        Horizontal buffer space for laying out slider graphics visually.

    Methods
    -------
    draw
        Draw digital displays for the ratios of active overtones on a surface.
    """

    def __init__(self, console, origin):
        """
        Initialize the ratio display components: digital display box, digital font, and colon.

        Parameters
        ----------
        console : Console
            Console that this area is on and is displaying the active overtones of.
        origin : tuple
            Position relative to Console origin that this area will be drawn onto.
        """
        self.origin = pygame.Vector2(origin)
        self.overtones = console.overtones
        self.digitalFont = console.digitalFont
        self.digitalOn = console.digitalOn

        # Render digital display box and colon
        digitalOff = console.digitalOff
        digitalBG = console.digitalBG
        self.digitalSlot = self.digitalFont.render(
            f"8", False, digitalOff, digitalBG
        )
        self.ratioColon = console.labelsFont.render(
            ":", False, console.labelsCol
        )
        self.horizontalBuf = 4

    def draw(self, surface):
        """
        Draw digital displays for the ratios of active overtones on a surface.

        Draw digital display boxes with colons between them and display the number
        of active overtones in their appropriate box.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw the ratio displays onto.
        """
        slotWidth = self.digitalSlot.get_width()
        colonWidth = self.ratioColon.get_width()

        # Step size from digital display box to the next: slot, buffer space, and colon.
        offset = (
            slotWidth + self.horizontalBuf + colonWidth + self.horizontalBuf
        )
        for i, overtone in enumerate(self.overtones):
            # Draw digital box
            surface.blit(
                self.digitalSlot, (self.origin[0] + offset * i, self.origin[1])
            )

            # Draw overtone number in digital box if overtone is active.
            if overtone.active:
                overtoneStr = f"{overtone.overtone}".replace("1", " 1")
                ratioDisp = self.digitalFont.render(
                    overtoneStr, False, self.digitalOn
                )
                surface.blit(
                    ratioDisp, (self.origin[0] + offset * i, self.origin[1])
                )

            # Draw colon after digtial box (unless it's the last box).
            if overtone != self.overtones[-1]:
                colonOffset = (
                    self.origin[0]
                    + offset * i
                    + slotWidth
                    + self.horizontalBuf
                )
                surface.blit(self.ratioColon, (colonOffset, self.origin[1]))
