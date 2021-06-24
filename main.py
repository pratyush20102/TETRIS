import pygame
import random
from pygame import mixer
# Mixer library imported for implementation of the Sound Effects

# This list contains RGB codes of all colours available in our TETRIS Game
# Colour of figure will be chosen randomly from these options.
colors = [
    (0, 0, 0),  # black
    (153, 51, 255),  # purple
    (31, 219, 255),  # blue
    (144, 250, 82),  # green
    (250, 19, 66),  # pink
    (255, 102, 153),  # orange
]

class Figure:
    """
    Starting off with the Figure class,our goal is to store the figure types together with the rotations
    where the main list contains figure types, and the inner lists contain their rotations.
    The numbers in each figure represent the positions in a 4x4 matrix where the figure is solid.
    For example -> [1, 5, 9, 13] represents a vertical line
    whereas its rotation [4, 5, 6, 7] represents a horizontal line.
    """
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        """
        Randomly picks one of the types of figures and colours provided above
        """
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        """
        Returns the Figure considering the type,current (clockwise) rotation and colour of figure picked
        """
        return self.figures[self.type][self.rotation]

    def rotate(self):
        """
        Determines the number of clockwise rotations to be carried out in the figure
        """
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])

# Stores background_display.png in 'background'
background = pygame.image.load('background_display.png')

class Tetris:
    """
    Game initialization is carried out by making use of certain variables
    state-> Determines whether or not the game is continuing ."start" ->Game On ; "game_over" ->Game Over.
    field-> Determines the field/grid of the game which contains 0 if empty and colours of figures if not.
    height, width-> Specify the height and width of the field to be created.
    line, score-> Determines the number of lines completed and the score correspondingly.
    """
    level = 2
    score = 0
    line = 0
    state = "start"
    field = []
    height = 0
    width = 0
    x = 100
    y = 60
    zoom = 20
    figure = None

    def __init__(self, height, width):
        """
        Creates a field with the size height x width. (Parameters)
        """
        self.height = height
        self.width = width
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        """
        Creating a new figure and positioning it at coordinates (3,0)
        """
        self.figure = Figure(3, 0)

    def intersects(self):
        """
        Confirms whether the currently flying figure intersects with something fixed on the field.
        This may happen when the figure is moving left, right, down, or rotating.
        Returns False if there is no intersection and True in case, there is an intersection.
        """
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection

    def break_lines(self):
        """
        Called in freeze function.
        Confirms the completion of some line in the field due to the Figure frozen by the freeze func().
        Increments the value of 'line' by the number of lines completed
        Increments the value of 'score' by the square of the number of lines completed
        Plays block_touch.wav whenever a Figure freezes and line_comp.wav whenever a line is completed
        """
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines ** 2
        self.line += lines
        block_touch = mixer.Sound("block_touch.wav")
        block_touch.play()
        if lines > 0:
            line_comp = mixer.Sound("line_comp.wav")
            line_comp.play()

    def go_space(self):
        """
        Movement Function 1: Called when the player presses SPACE
        Directly pushes the Figure to the bottom of the Field in the same line
        in which it was existing when the SPACE was pressed.
        """
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        """
        Movement Function 2: Called when the Figure needs to go down in the field
        Causes the Figure to move down in its own line in the field
        """
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        """
        Confirms whether the Figure is still allowed to move or rotate. Intersection while moving down
        indicates that the Figure has reached the bottom or some other pre-existing Figure in the field
        In this case, func-> freeze is needed to freeze the figure on our field.
        Moving ahead, self.break_lines()-> confirms the completion of some line due to the frozen figure
        self.new_figure()-> creates a new figure as the previous figure has already been frozen in the field.
        self.intersects()-> Return of boolean value True to the func self.intersects() ends the
        game as it confirms the Figure to be fixed is exceeding the limit of the grid.
        """
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            game.state = "game_over"

    def go_side(self, dx):
        """
        Movement Function 3: Called when the player presses RIGHT or LEFT
        Pressing RIGHT and LEFT causes the Figure to move rightwards and leftwards respectively
        """
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        """
        Movement Function 4: Called when the player presses UP
        Causes one clockwise rotation of the Figure in the field
        """
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

# Initializing pygame
pygame.init()

# Stores dank.png in 'dank'
dank = pygame.image.load('dank.png')

# Plays background_music.mp3 continuously in the background
mixer.music.load("background_music.mp3")
mixer.music.play(-1)

# Sets the size of the screen to 400 by 500 pixels and creates the pygame window
size = (400, 500)
screen = pygame.display.set_mode(size)

# Sets icon.png as the icon of the pygame window and TETRIS as the caption of the pygame window
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)
pygame.display.set_caption("TETRIS")

# Loop until the user clicks the close button
done = False
clock = pygame.time.Clock()
fps = 25
game = Tetris(20, 10)
counter = 0

pressing_down = False

while not done:
    if game.figure is None:
        game.new_figure()
    counter += 1
    if counter > 100000:
        counter = 0

    if counter % (fps // game.level // 2) == 0 or pressing_down:
        if game.state == "start":
            game.go_down()

    for event in pygame.event.get():
        # Pressing the Close Button closes the game right away
        if event.type == pygame.QUIT:
            done = True

        # Confirms whether or not a key has been pressed
        if event.type == pygame.KEYDOWN:
            """
            Confirms whether or not the UP, DOWN, LEFT, RIGHT, SPACE keys have been pressed respectively
            in the 5 if statements sequentially.
            """

            if event.key == pygame.K_UP:
                # Causes one clockwise rotation of the Figure
                game.rotate()

            if event.key == pygame.K_DOWN:
                # Results in increase in drop speed of Figure
                pressing_down = True

            if event.key == pygame.K_LEFT:
                # Shifts the Figure leftwards
                game.go_side(-1)

            if event.key == pygame.K_RIGHT:
                # Shifts the Figure rightwards
                game.go_side(1)

            if event.key == pygame.K_SPACE:
                """
                Directly shifts the Figure downwards thus sending it down until it collides with the 
                bottom of the field or some other pre-existing Figure
                """
                game.go_space()

        # Confirms whether or not a key has been released
        if event.type == pygame.KEYUP:

            # Confirms whether or not DOWN key has been released
            if event.key == pygame.K_DOWN:
                pressing_down = False

    screen.blit(background, (0, 0))
    # Sets background_display.png which was stored in 'background' as the Background Display

    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, (128, 128, 128), [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
            if game.field[i][j] > 0:
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                 [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(screen, colors[game.figure.color],
                                     [game.x + game.zoom * (j + game.figure.x) + 1,
                                      game.y + game.zoom * (i + game.figure.y) + 1,
                                      game.zoom - 2, game.zoom - 2])

    font = pygame.font.Font('font.otf', 20)
    font1 = pygame.font.Font('font.otf', 50)
    text = font.render("Score: " + str(game.score * 100), True, (255, 255, 255))
    text1 = font.render("Lines: " + str(game.line), True, (255, 255, 255))
    text_game_over = font1.render("Game Over :( ", True, (255, 255, 255))

    # Presents the Score and Number of Lines completed in the top left hand corner of game window
    screen.blit(text, [10, 5])
    screen.blit(text1, [10, 35])

    if game.state == "game_over":
        """
        This if statement is executed only when the Game is Over.
        "Game Over :( " is displayed in the game window along with dank.png.Simultaneously "game_over.wav" 
        continues playing until the game is closed thus indicating that the Game is Over.
        """
        game_over = mixer.Sound("game_over.wav")
        game_over.play()
        screen.blit(dank, (120, 170))
        screen.blit(text_game_over, [20, 100])

    pygame.display.flip()
    # Update the contents of the entire display
    clock.tick(fps)
    # Decides the frame per seconds to be displayed

pygame.quit()
