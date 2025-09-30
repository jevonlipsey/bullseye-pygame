# imports:
import pygame
# new module: pip3 install pygame_gui
import pygame_gui

from pygame.draw import circle as draw_circle
from pygame.draw import line as draw_line
from pygame.draw import rect as draw_rect
from pygame.draw import polygon as draw_poly
from pygame.locals import RESIZABLE

import math

# setup:
WIDTH = 720
HEIGHT = 1020
bg = pygame.image.load("assets/background.png")
# classes:
class Board():
    # initalize board:
    def __init__(self):
        self.radius = [175,140,130,100,90, 20,10]
        self.segment_scores = [6, 13, 4, 18, 1, 20, 5, 12, 9, 14]
        self.x = WIDTH//2
        self.y = HEIGHT//2.5
        self.x_speed = 4
        self.stopped = False
    # draw the board
    def draw(self, screen):
        # surface, color, center(x,y), radius, thickness
        for r in self.radius:
            # draw black circle for edge
            # draw white circle to fill board
            if r == 175:
                draw_circle(screen, (255,255,255), (self.x,self.y), r, 0)
                draw_circle(screen, (0,0,0), (self.x,self.y), r, 5)

            # draw green for rest of board
            else:
                draw_circle(screen, (119, 157, 37), (self.x,self.y), r, 5)
        # drawing segments & scores
        r = self.radius[1] # inside of board - outer edge
        for i in range(10):  # 10 segments
            angle = i * 36 # 10 angles to fit 360 degree board
            # find the end of the circle
            end_x = self.x + r * math.cos(math.radians(angle))
            end_y = self.y + r * math.sin(math.radians(angle))
            pygame.draw.line(screen, (119, 157, 37), (self.x, self.y), (end_x, end_y), 5)

            #draw segment scores

            score_angle = angle + 15  # 15 puts number in middle of segment
            # cos and sin used to put scores in a circle
            # numbers on the end used for fine tine adjustment
            score_x = self.x + (r + 15) * math.cos(math.radians(score_angle)) - 8
            score_y = self.y + (r + 15 ) * math.sin(math.radians(score_angle)) -5

            # display scores on board
            score_text = str(self.segment_scores[i])
            score_font = pygame.font.Font(None, 25)
            score_num = score_font.render(score_text, True, (0, 0, 0))
            screen.blit(score_num, (score_x, score_y))
    # update the board and stuck darts
    def update(self, stuck_darts):
        # if not stopped, move board with its given speed
        if not self.stopped:
            self.x += self.x_speed
            # stuck darts need to move at same speed as board
            for dart in stuck_darts:
                dart.x += self.x_speed
            # bounce off sides
            if self.x - self.radius[0] <= 0 or self.x + self.radius[0] >= WIDTH:
                self.x_speed = -self.x_speed
    # stop board movement
    def stop(self):
        self.stopped = True
    # start board movement
    def start(self):
        self.stopped = False
    # get score from the area on the board
    def get_score(self,dart):
        # store what radius the dart is in (distance)
        dart_radius = ((dart.x - self.x)**2 + (dart.y - self.y)**2)**0.5
        print(dart_radius)
        # get the angle of each segment and assign it to a value
        angle = (math.atan2(dart.y - self.y, dart.x - self.x) * 180 / math.pi) % 360
        segment = int(angle // 36)
        # check if a dart is in a certain zone
            # edge of board
        if dart_radius > self.radius[0]:
            print('the dart missed')
            return 0
        elif dart_radius > self.radius[1]:
            print('The dart hit the edge')
            return 0
            # double ring
        elif dart_radius > self.radius[2]:
            print('The dart hit a double ring')
            return 2 * self.segment_scores[segment]
            # 1st single area
        elif dart_radius > self.radius[3]:
            print('The dart hit the first single area')
            return self.segment_scores[segment]
            # triple ring
        elif dart_radius > self.radius[4]:
            print('The dart hit the triple ring')
            return 3 * self.segment_scores[segment]
            # 2nd single area
        elif dart_radius > self.radius[5]:
            print('The dart hit the second single area')
            return self.segment_scores[segment]
            #  bull
        elif dart_radius > self.radius[6]:
            print('The dart hit the single bull!')
            return 25
            # double bull
        else:
            print('The dart hit the double bull!')
            return 50

class Player():
    # initialize player 1 and 2
    def __init__(self, player_num, score, color):
        self.player_num = player_num
        self.score = score
        self.remaining_darts = 3
        self.color = color
        self.bust = False
    # get clean name return
    def __str__(self):
        return f"Player {self.player_num}"

class Dart():
    # initialize dart objects
    def __init__(self, x, y, velocity, color):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.color = color
        self.launched = False
        self.stuck = False
        self.missed = False
        self.distance_to_board = 0
        self.scored = False
    # update dart movement
    def update(self,dart_board):

        self.x += self.velocity[0] # could add x movement later
        self.y += self.velocity[1] # movement towards board



        if not self.stuck:
            # get distance from dart to dart_board
            distance_to_board = ((self.x - dart_board.x)**2 + (self.y - dart_board.y)**2)**0.5
            # if distance is in board radius and velocity = 0, get stuck
            if distance_to_board <= dart_board.radius[0] and abs(self.velocity[1]) < 0.01:
                self.stuck = True
                # set speed to 0 and stay on board
                self.velocity = (self.velocity[0],0)

                # testing
                print('The dart landed on a score of:',dart_board.get_score(self))
            elif self.launched and abs(self.velocity[1]) < 0.01:
                self.stuck = True
                self.missed = True

            else:
                # if not stuck, speed equation to slow dart's y speed
                self.velocity = (self.velocity[0], self.velocity[1] *.7)
    # draw darts on screen
    def draw(self, screen):
        draw_line(screen, self.color, (self.x, self.y), (self.x, self.y + 35), 5)
        draw_poly(screen, self.color, [(self.x, self.y + 35), (self.x - 10, self.y + 45), (self.x, self.y + 55), (self.x + 10, self.y + 45)])
    # draw stuck darts as circles
    def draw_stuck(self, screen):
        draw_circle(screen, self.color, (self.x,self.y),5)

class StrengthMeter():
    # initalize strength meter and arrow
    def __init__(self):
        self.x = WIDTH / 3.3  # position of meter to center it
        self.y = HEIGHT - 300 # adjust to put it lower/higher on screen
        self.width = 300
        self.height = 20
        self.arrow_pos = 0
        self.arrow_speed = 5
        self.arrow_direction = 1   # left right movement of arrow
        self.stopped = False
    # update meter movement
    def update(self):
        if not self.stopped:
            # move the arrow
            self.arrow_pos += self.arrow_speed * self.arrow_direction

            # switch the arrows direction
            if self.arrow_pos <= 0 or self.arrow_pos >= self.width:
                self.arrow_direction *= -1
    # draw meter
    def draw(self, screen):
        #MAP THE ARROW POSITION TO DIFFERENT COLORS
        color = (255 - int((self.arrow_pos / self.width) * 255), int((self.arrow_pos / self.width) * 255), 0)

        #DRAW NEW METER
        draw_rect(screen, color, (self.x, self.y, self.arrow_pos, self.height), 0)
        # black meter
        draw_rect(screen, (0, 0, 0), (self.x + self.arrow_pos, self.y, self.width - self.arrow_pos, self.height), 0)

        # draw arrow
        arrow_x = self.x + self.arrow_pos
        arrow_y = self.y - 5
        draw_poly(screen, (0, 255, 0), [(arrow_x, arrow_y), (arrow_x + 10, arrow_y - 10), (arrow_x + 20, arrow_y), (arrow_x + 10, arrow_y + 10)])
    # stop strength meter arrow
    def stop_arrow(self):
        self.stopped = True
    # get strength from arrow position
    def get_strength(self):
        # give a strength number
        return int((self.arrow_pos / self.width) * 150)

class PopText():
    # initalize pop up text
    def __init__(self,text,x,y,time,color):
        self.text = text
        self.x = x
        self.y = y
        self.time = time
        self.color = color
    # draw pop up text
    def draw(self,screen):
        font = pygame.font.Font(None, 60)
        text = font.render(self.text, True, self.color)
        screen.blit(text, (self.x, self.y))
        self.time += 1

class Game:
    # setup main game info and init all objects
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Bullseye')
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT),RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        # new: gui for setup screen
        self.manager = pygame_gui.UIManager((WIDTH,HEIGHT))
        # initalize board
        self.dart_board = Board()
        # initalize darts
        self.dart = None
        self.stuck_darts = []
        # initalize strength meter
        self.strength_meter = None
        # initialize players
        self.player_1 = Player(1,101, (255, 123, 13))
        self.player_2 = Player(2,101, (92, 207, 234))
        self.current_player = self.player_1
        # initalize round
        self.round = 1
        # set game state and win info
        self.game_state = 'start'
        self.game_over = False
        self.winner = None
        # init popups
        self.popups = []
    # run different game states - start, setup, play, end
    def run(self):
        # game state controls which screen is showing
        while self.running:
            if self.game_state == 'start':
                self.start_screen()
            elif self.game_state == 'setup':
                self.setup_screen()
                self.manager.update(self.clock.tick(60)/1000)
                self.manager.draw_ui(self.screen)
                pygame.display.flip()
            elif self.game_state == 'play':
                self.process_events()
                self.update()
                self.draw()
            elif self.game_state == 'end':
                self.end_screen()


            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
    # reset game back to init information
    def reset(self):
        # reinitializes all objects
        self.dart_board = Board()
        self.dart = None
        self.stuck_darts = []
        self.strength_meter = None
        self.player_1 = Player(1,101, (255, 123, 13))
        self.player_2 = Player(2,101, (92, 207, 234))
        self.current_player = self.player_1
        self.game_state = 'start'
        self.game_over = False
        self.winner = None
    # start gamestate: titlescreen
    def start_screen(self):
        self.screen.fill('white')
        # show game name and how to start
        font = pygame.font.Font(None, 36)
        bull_font = pygame.font.Font(None,70)

        text = font.render("Press SPACE to play Bullseye! or 'ESC' to quit", True, (0, 0, 0))
        bullseye = bull_font.render("BULLSEYE", True, (0, 0, 0))

        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        self.screen.blit(bullseye, (WIDTH // 2 - bullseye.get_width() // 2, HEIGHT // 2 - bullseye.get_height() - 200 // 2))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # space send gamestate to setup
                if event.key == pygame.K_SPACE:
                    self.game_state = 'setup'
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    # setup gamestate: set score, play
    def setup_screen(self):
        self.screen.fill('white')

        font = pygame.font.Font(None, 34)
        text = font.render("Select a score and press start to play!", True, (0, 0, 0))
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        # buttons for start and scores - called with object_id
        start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH//2 - 40, HEIGHT - 300), (100, 50)),
                                             text='Start!',
                                             manager=self.manager,
                                             object_id = '#start')
        one_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH//2 - 300, HEIGHT - 800), (100, 50)),
                                             text='101',
                                             manager=self.manager,
                                             object_id = '#one')

        three_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH//2 - 50, HEIGHT - 800), (100, 50)),
                                             text='301',
                                             manager=self.manager,
                                             object_id = '#three')

        five_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH//2 + 200, HEIGHT - 800), (100, 50)),
                                             text='501',
                                             manager=self.manager,
                                             object_id = '#five')
        # allow buttons to set score and set game state to play
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game_state = 'play'
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                # start button
                if event.ui_object_id == '#start':
                    self.game_state = 'play'
                    print('pressed')
                # 101 button
                elif event.ui_object_id == '#one':
                    print('101')
                    self.player_1.score = 101
                    self.player_2.score = 101
                # 301 button
                elif event.ui_object_id == '#three':
                    print('301')
                    self.player_1.score = 301
                    self.player_2.score = 301
                # 501
                elif event.ui_object_id == '#five':
                    print('501')
                    self.player_1.score = 501
                    self.player_2.score = 501
            self.manager.process_events(event)
    # end gamestate: display winner, play again, quit
    def end_screen(self):
        self.screen.fill('white')
        # display text
        font = pygame.font.Font(None, 34)
        text = font.render(f"{self.winner} is the winner! Press SPACE to play again or 'ESC' to quit", True, (0, 0, 0))
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        # allow space bar to play again
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.reset()
                    self.game_state = 'setup'
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    # play gamestate: all functions for main gameplay
    # can exit game, reset, or perform space key function
    def process_events(self):
        events = pygame.event.get()
        if len(events) > 0:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running=False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # this prevents dart from being thrown too fast
                        if self.dart == None or self.dart.stuck or not self.dart.launched:
                            self.space_key()
                    elif event.key == pygame.K_ESCAPE:
                        self.reset()
    # space key will stop the board, set strength, and throw a dart
    def space_key(self):
        # if board is moving
        if not self.dart_board.stopped:
            # initalize dart
            self.dart = Dart(WIDTH // 2, HEIGHT - 65, (0, 0), self.current_player.color)
            # stop board
            self.dart_board.stop()
            # initalize meter
            self.strength_meter = StrengthMeter()
        # if the board is stopped, strength meter initalized and moving
        elif self.strength_meter and not self.strength_meter.stopped:
            # space will throw the dart
            self.throw_dart()
        # if the dart exists and gets stuck to board
        elif self.dart and self.dart.stuck:
            # add to stuck darts []
            self.stuck_darts.append(self.dart)
            # move board again
            self.dart_board.start()
            # initalize next dart
            self.dart = Dart(WIDTH // 2, HEIGHT - 65, (0, 0), self.current_player.color)
        # else: (if the dart doesnt get stuck to the board)
        else:
            # move board again
            self.dart_board.start()
            # initalize next dart
            self.dart = Dart(WIDTH // 2, HEIGHT - 65, (0, 0), self.current_player.color)
    # launch a dart with velocity
    def throw_dart(self):
        # stop meter once dart is thrown
        self.strength_meter.stopped = True
        # send dart with initial velocity
        self.dart.velocity = (0, self.strength_meter.arrow_pos * -0.9)
        self.dart.launched = True
        # remove dart from current player
        self.current_player.remaining_darts -= 1
    # update all objects in game - includes main scoring logic
    #   also includes switch player logic, popup texts
    def update(self):
        # update dart board
        self.dart_board.update(self.stuck_darts)
        # update darts (MAIN THROWING AND SCORING LOGIC)
        if self.dart:
            self.dart.update(self.dart_board)
            # if dart is stuck and not scored
            if self.dart.stuck and not self.dart.scored:
                # get score from board
                dart_score = self.dart_board.get_score(self.dart)
                # if score will make player bust
                if self.current_player.score - dart_score < 0:
                    # set bust to true
                    self.current_player.bust = True
                    # subtract 0 from score
                    self.current_player.score -= 00
                    self.current_player.remaining_darts = 3
                    # score the dart
                    self.dart.scored = True

                     # create a new pop-up
                    popup = PopText('Bust!', WIDTH//2, HEIGHT//1.5, 1, self.current_player.color)
                    self.popups.append(popup)

                    print(self.current_player, 'BUST!!')

                else:
                    # if score wont make player bust, subtract and score the dart
                    self.current_player.score -= dart_score
                    self.dart.scored = True

                     # create a new pop-up
                    if dart_score == 0:
                        popup = PopText('Miss!', WIDTH//2 - 40, HEIGHT//1.5, 1, self.current_player.color)
                        self.popups.append(popup)
                    else:

                        popup = PopText(f"-{dart_score}", WIDTH//2 - 20, HEIGHT//1.5, 1, self.current_player.color)
                        self.popups.append(popup)

                    print('Launched:',self.current_player, 'score is now:', self.current_player.score)

                    print('player 1:', self.player_1.score, 'darts:', self.player_1.remaining_darts)
                    print('player 2:', self.player_2.score, 'darts:', self.player_2.remaining_darts)
                # if player missed
                if self.dart.stuck and self.dart.missed and not self.dart.scored:
                    # remove dart and score it
                    self.current_player.remaining_darts -= 1
                    self.dart.scored = True

            # switch players and check for round increment after dart has landed
            if self.dart.stuck and (self.current_player.remaining_darts <= 0 or self.current_player.bust):
                # swaps players and resets their darts
                self.current_player = self.player_2 if self.current_player == self.player_1 else self.player_1
                self.current_player.remaining_darts = 3

                # reset stuck darts and increase round if both players done
                if (self.player_1.remaining_darts == 3 and self.player_2.remaining_darts == 0) or \
               (self.player_1.bust and self.player_2.remaining_darts == 0) or \
               (self.player_2.bust and self.player_1.remaining_darts == 0) or \
               (self.player_1.bust and self.player_2.bust):
                    # un-bust both players
                    self.player_1.bust = False
                    self.player_2.bust = False
                    # remove darts from screen
                    self.stuck_darts = []
                    # increment round
                    self.round += 1
                    print('Round', self.round)

            # player win condition
            if self.player_1.score == 0 or self.player_2.score == 0:
                print(self.current_player, 'is the winner!')
                self.winner = self.current_player
                self.game_state = 'end'

        # update strength meter
        if self.strength_meter:
            self.strength_meter.update()

        # remove popups after 1 second (60 frames)
        for popup in self.popups:
            if popup.time > 60:
                self.popups.remove(popup)
    # draw all objects in game
    def draw(self):
        # set background
        self.screen.fill('light grey')
        self.screen.blit(bg,(0,0))
        # draw board
        self.dart_board.draw(self.screen)
        # draw current dart
        if self.dart is not None:
            self.dart.draw(self.screen)
        # draw all stuck darts
        for stuck_dart in self.stuck_darts:
            stuck_dart.draw_stuck(self.screen)
        # draw meter if its active and not stopped
        if self.strength_meter is not None and not self.strength_meter.stopped:
            self.strength_meter.draw(self.screen)

        # init scores
        font = pygame.font.Font(None, 36)
        player_1_score = font.render(f"Player 1 Score: {self.player_1.score}", True, self.player_1.color)
        player_2_score = font.render(f"Player 2 Score: {self.player_2.score}", True, self.player_2.color)

        # draw the scores on the screen
        self.screen.blit(player_1_score, (10, HEIGHT - 85))
        self.screen.blit(player_2_score, (WIDTH - player_2_score.get_width() - 10, HEIGHT -85))

        # draw popups
        for popup in self.popups:
                popup.draw(self.screen)

# run game:
game = Game()
game.run()
