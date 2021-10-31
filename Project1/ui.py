import functools
import json
import pygame
import time
import random
import copy

from game.endscreen import EndScreen
from game.menus import Menu, SettingsMenu, GameMenu
from game.musicplayer import MusicPlayer
from game.score import Score
from game.timer import Timer
from game.utils import load_sprite, text_to_sprite

from solver import Algorithm, solver, ids
from graph import Graph, Node, Tube, Game
from threading import Thread


# level box size: width-200 height-100


def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]

            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e

            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret

        return wrapper

    return deco


# Global Variables

mouse_timeout = 0.15

# Screen Dimensions
screen_width = 1400
screen_height = 1000

# Dictionaries
with open('levels.json') as f:
    levels = json.load(f)

for level in levels:
    tubes = levels[level]['tubes']
    new_tubes = []
    for tube in tubes:
        new_tubes.append(Tube(tube))
    levels[level] = new_tubes

ball_dict = {
    1: "blueBall.png",
    2: "pinkBall.png",
    3: "darkGreenBall.png",
    4: "orangeBall.png",
    5: "redBall.png",
    6: "purpleBall.png",
    7: "darkRedBall.png",
    8: "yellowBall.png",
    9: "darkPurpleBall.png",
    10: "lightBlueBall.png",
    11: "greenBall.png",
    12: "darkBlueBall.png"
}


# Flask Class

class Flask:
    def __init__(self, tube, coords):
        self.tube = tube
        self.coords = coords
        self.balls = pygame.sprite.Group()
        self.create_flask()
        self.load_balls()
        self.selected = False
        self.completed = False

    def create_flask(self):
        self.load_default_flask()
        self.load_selected_flask()
        self.load_completed_flask()

    # Load functions
    def load_default_flask(self):
        flask = load_sprite("assets/img/flasks/flask-white.png")
        flask.rect.left = self.coords[0]
        flask.rect.top = self.coords[1]
        self.flask = pygame.sprite.GroupSingle(flask)

    def load_selected_flask(self):
        selected = load_sprite("assets/img/flasks/flask-4-selected.png")
        selected.rect.left = self.coords[0]
        selected.rect.top = self.coords[1]
        self.flask_sel = pygame.sprite.GroupSingle(selected)

    def load_completed_flask(self):
        completed = load_sprite("assets/img/flasks/flask-4-completed.png")
        completed.rect.left = self.coords[0]
        completed.rect.top = self.coords[1]
        self.flask_comp = pygame.sprite.GroupSingle(completed)

    def load_balls(self):
        x = self.coords[0] + 12
        y = self.coords[1] + 290
        for num in self.tube.get_balls():
            y -= 73
            self.load_ball(num, [x, y])

    def load_ball(self, num, coords):
        ball_file = ball_dict.get(num)
        ball = load_sprite("assets/img/balls/" + ball_file)
        ball.rect.left = coords[0]
        ball.rect.top = coords[1]
        self.balls.add(ball)

    # Draw functions
    def draw(self, screen):
        self.balls.draw(screen)
        if self.selected:
            self.flask_sel.draw(screen)
        elif self.completed:
            self.flask_comp.draw(screen)
        else:
            self.flask.draw(screen)

    # Game functions
    def remove_ball(self):
        sprites = self.balls.sprites()
        ball = sprites[-1]
        pygame.sprite.Group.remove(self.balls, ball)
        self.completed = False
        return ball

    def add_ball(self, ball):
        ball.rect.left = self.coords[0] + 12
        ball.rect.top = self.coords[1] + 290 - 73 * (len(self.balls) + 1)
        self.balls.add(ball)
        if self.tube.is_completed():
            self.completed = True
            return 1
        return 0

    def select(self):
        self.selected = not self.selected
        if len(self.balls) > 0:
            if self.selected:
                ball = self.balls.sprites()[-1]
                ball.rect.top = self.coords[1] - 100
            if not self.selected:
                ball = self.balls.sprites()[-1]
                ball.rect.top = self.coords[1] + 290 - 73 * len(self.balls)

    def check_mouse_col(self, mouse_pos):
        return self.flask.sprite.rect.collidepoint(mouse_pos)

    def check_done(self):
        return self.tube.is_completed() or self.tube.is_empty()


# UI Class

class UI:
    def __init__(self):
        self.state = "MAINMENU"
        self.algorithm = 0
        self.hint_available = True
        self.auto_solving = False
        self.paused = False
        self.auto_speed = 0
        self.init_screen()
        self.load_other()
        self.build_menu()
        self.build_main_menu()
        self.build_setting_menu()
        self.build_music_player()
        self.build_end_screen()
        self.timer = Timer(mouse_timeout)
        self.active = True

    # Init functions
    def init_screen(self):
        self.screen = pygame.display.set_mode((screen_width, screen_height))

    def build_menu(self):
        self.menu = GameMenu(levels)

    def build_music_player(self):
        self.dj = MusicPlayer()

    def build_main_menu(self):
        self.main_menu = Menu()

    def build_setting_menu(self):
        self.settings = SettingsMenu()

    def build_end_screen(self):
        self.end_screen = EndScreen()

    # Load functions
    def load_bg(self):
        self.bg = pygame.image.load('assets/img/lab.jpg')

    def load_level(self, num):
        if hasattr(self, 'curGame'):
            del self.cur_game
        level = copy.deepcopy(levels[str(num)])
        self.cur_game = Game(level)
        self.create_game()

    def load_tubes(self, num):
        self.flasks = pygame.sprite.Group()

    def load_other(self):
        self.load_bg()
        self.load_quit()
        self.load_undo()
        self.load_move_count()
        self.load_undo_count()
        self.load_hint()
        self.load_auto_solve()

    def load_auto_solve(self):
        self.load_speed()
        self.load_pause()
        self.load_algorithm_fail()

    def load_speed(self):

        speed_holder = pygame.image.load("assets/img/holders/speedHolder.png")
        value_holder = pygame.image.load("assets/img/holders/prevNext.png")

        font = pygame.font.SysFont("Arial", 45)
        font2 = pygame.font.SysFont("Arial", 40)
        speed = text_to_sprite("Speed", speed_holder, (230, 230, 230), [1075, 125], font)
        point_five = text_to_sprite("x0.5", value_holder, (230, 230, 230), [1250, 137.5], font2)
        normal = text_to_sprite("x1", value_holder, (230, 230, 230), [1250, 137.5], font2)
        x2 = text_to_sprite("x2", value_holder, (230, 230, 230), [1250, 137.5], font2)
        x4 = text_to_sprite("x4", value_holder, (230, 230, 230), [1250, 137.5], font2)
        x8 = text_to_sprite("x8", value_holder, (230, 230, 230), [1250, 137.5], font2)

        self.speed_holder = pygame.sprite.GroupSingle(speed)
        self.speeds = []
        self.speeds.append(pygame.sprite.GroupSingle(normal))
        self.speeds.append(pygame.sprite.GroupSingle(x2))
        self.speeds.append(pygame.sprite.GroupSingle(x4))
        self.speeds.append(pygame.sprite.GroupSingle(x8))
        self.speeds.append(pygame.sprite.GroupSingle(point_five))

    def load_pause(self):

        holder = pygame.image.load("assets/img/holders/speedHolder.png")
        font = pygame.font.SysFont("Arial", 40)
        pause = text_to_sprite("Pause", holder, (230, 230, 230), [1075, 225], font)
        resume = text_to_sprite("Resume", holder, (230, 230, 230), [1075, 225], font)
        self.pauseButton = pygame.sprite.GroupSingle(pause)
        self.resumeButton = pygame.sprite.GroupSingle(resume)

    def load_undo(self):
        undo_img = load_sprite("assets/img/buttons/undo.png")
        undo_img.rect.left = 1250
        undo_img.rect.top = 200
        self.undoB = pygame.sprite.GroupSingle(undo_img)

    def load_quit(self):
        quit_img = load_sprite("assets/img/buttons/menu.png")
        quit_img.rect.left = 20
        quit_img.rect.top = 20
        self.quit = pygame.sprite.GroupSingle(quit_img)

    def load_move_count(self):
        move_holder = load_sprite("assets/img/holders/numberBox.png")
        move_holder.rect.left, move_holder.rect.top = [1250, 50]
        self.moveHolder = pygame.sprite.GroupSingle(move_holder)
        move_count = load_sprite("assets/img/holders/moveCount.png")
        move_count.rect.left, move_count.rect.top = [1000, 45]
        self.moveCount = pygame.sprite.GroupSingle(move_count)

    def load_undo_count(self):
        undo_holder = load_sprite("assets/img/holders/numberBox.png")
        undo_holder.rect.left, undo_holder.rect.top = [1250, 120]
        self.undoHolder = pygame.sprite.GroupSingle(undo_holder)
        undo_count = load_sprite("assets/img/holders/undoCount.png")
        undo_count.rect.left, undo_count.rect.top = [1000, 115]
        self.undoCount = pygame.sprite.GroupSingle(undo_count)

    def load_hint(self):
        hint_up = load_sprite("assets/img/arrow_up.png")
        self.hint_up = pygame.sprite.GroupSingle(hint_up)
        hint_down = load_sprite("assets/img/arrow_down.png")
        self.hint_down = pygame.sprite.GroupSingle(hint_down)

        hint_b = load_sprite("assets/img/buttons/hint.png")
        hint_b.rect.left, hint_b.rect.top = [1250, 280]
        self.hint_b = pygame.sprite.GroupSingle(hint_b)

        hint_no = load_sprite("assets/img/buttons/no-hint.png")
        hint_no.rect.left, hint_no.rect.top = [1250, 280]
        self.hint_no = pygame.sprite.GroupSingle(hint_no)

    def load_algorithm_fail(self):
        self.solver_failed = False
        holder = pygame.image.load("assets/img/holders/failHolder.png")
        font = pygame.font.SysFont("Arial", 40)
        alg_fail = text_to_sprite("Algorithm couldn't reach a solution in due time", holder, (230, 230, 230),
                                  [300, 400],
                                  font)

        self.alg_fail = pygame.sprite.GroupSingle(alg_fail)

    ## Draw functions

    def draw_screen(self):
        self.screen.blit(self.bg, (0, 0))

    def draw_main_menu(self):
        self.main_menu.draw(self.screen)

    def draw_game_menu(self):
        self.menu.draw(self.screen)

    def draw_settings_menu(self):
        self.settings.draw(self.screen)

    def draw_quit(self):
        self.quit.draw(self.screen)

    def draw_undo(self):
        self.undoB.draw(self.screen)

    def draw_flasks(self):
        for flask in self.tubes:
            flask.draw(self.screen)

    def draw_hint(self):
        if self.hint_available:
            self.hint_b.draw(self.screen)
        else:
            self.hint_no.draw(self.screen)

    def draw_solved_hint(self):
        if self.display_hint:
            self.hint_up.draw(self.screen)
            self.hint_down.draw(self.screen)

    def drawMoveCount(self):
        self.moveCount.draw(self.screen)
        self.moveHolder.draw(self.screen)
        self.move_num.draw(self.screen)

    def drawUndoCount(self):
        self.undoCount.draw(self.screen)
        self.undoHolder.draw(self.screen)
        self.undo_num.draw(self.screen)

    def drawRun(self):
        if self.auto_solving:
            self.draw_watch()
        else:
            self.draw_play()

    def draw_watch(self):
        self.draw_solved_hint()
        self.draw_flasks()
        self.draw_quit()
        self.drawMoveCount()
        self.draw_speed()
        self.draw_pause()
        if self.solver_failed:
            self.alg_fail.draw(self.screen)

    def draw_play(self):
        self.draw_hint()
        self.draw_solved_hint()
        self.draw_flasks()
        self.draw_quit()
        self.draw_undo()
        self.drawMoveCount()
        self.drawUndoCount()

    def draw_pause(self):
        if self.paused:
            self.resumeButton.draw(self.screen)
        else:
            self.pauseButton.draw(self.screen)

    def draw_end(self):
        if self.auto_solving:
            self.end_screen.draw_solved(self.screen, self.move_num.score)
        else:
            self.end_screen.draw(self.screen, self.move_num.score, self.undo_num.score)

    def draw_speed(self):
        self.speed_holder.draw(self.screen)
        self.speeds[self.auto_speed].draw(self.screen)

    # Collision functions

    def check_flasks_cols(self, mouse_pos):
        i = 0
        for tube in self.tubes:
            if tube.check_mouse_col(mouse_pos):
                return i
            i += 1
        return -1

    def check_quit(self, mouse_pos):
        return self.quit.sprite.rect.collidepoint(mouse_pos)

    def check_undo(self, mouse_pos):
        return self.undoB.sprite.rect.collidepoint(mouse_pos)

    def check_hint(self, mouse_pos):
        return self.hint_b.sprite.rect.collidepoint(mouse_pos)

    def check_run_cols(self, mouse_pos):
        select = self.check_flasks_cols(mouse_pos)
        if select > -1:
            self.make_move(select)
            if self.check_completed():
                self.end_game()
        elif self.check_undo(mouse_pos):
            self.undo()
        elif self.check_quit(mouse_pos):
            self.return_to_menu()
        elif self.check_hint(mouse_pos):
            '''solver_thread = Thread(target=self.update_hint)
            solver_thread.start()'''
            self.update_hint()
            self.display_hint = True
            self.dj.click_hint()

    def check_solve_cols(self, mouse_pos):
        if self.check_quit(mouse_pos):
            self.return_to_menu()
        self.check_speed(mouse_pos)
        self.check_pause(mouse_pos)

    def check_speed(self, mouse_pos):
        if self.solver_failed:
            return
        if self.speeds[self.auto_speed].sprite.rect.collidepoint(mouse_pos):
            self.auto_speed += 1
            if self.auto_speed > 4:
                self.auto_speed = 0
                self.solve_timer.update_timer(1.5)
            elif self.auto_speed == 1:
                self.solve_timer.update_timer(0.75)
            elif self.auto_speed == 2:
                self.solve_timer.update_timer(0.375)
            elif self.auto_speed == 3:
                self.solve_timer.update_timer(0.19)
            elif self.auto_speed == 4:
                self.solve_timer.update_timer(3)

    def check_pause(self, mouse_pos):
        if self.solver_failed:
            return

        if self.paused:
            if self.resumeButton.sprite.rect.collidepoint(mouse_pos):
                self.paused = False
                self.solve_timer.start_timer()
        else:
            if self.pauseButton.sprite.rect.collidepoint(mouse_pos):
                self.paused = True

    def check_back_to_menu(self, mouse_pos):

        if self.end_screen.check_back_col(mouse_pos):
            self.return_to_menu()

    # Checking functions
    def check_completed(self):
        for tube in self.tubes:
            if not tube.check_done():
                return False
        return True

    def check_mouse_timeout(self, mouse):
        if (mouse):
            if (self.timer.check_timer()):
                self.timer.start_timer()
                return True
        return False

    # Run functions

    def run(self):
        self.draw_screen()
        if self.state == "MAINMENU":
            self.run_main_menu()
        elif self.state == "SETTINGS":
            self.run_settings_menu()
        elif self.state == "GAMEMENU":
            self.run_game_menu()
        elif self.state == "RUNNING":
            self.run_level()
        elif self.state == "END":
            self.run_end()

    def run_main_menu(self):
        self.draw_main_menu()
        mouse = pygame.mouse.get_pressed()[0]
        if self.check_mouse_timeout(mouse):
            select = self.main_menu.check_menu_cols()
            if select == 0:
                self.active = False

            elif select == 1:
                self.auto_solving = False
                self.level_selection()
            elif select == 2:
                self.auto_solving = True
                self.level_selection()
            elif select == 3:
                self.settings_menu()

    def run_game_menu(self):
        self.draw_game_menu()
        mouse = pygame.mouse.get_pressed()[0]
        if self.check_mouse_timeout(mouse):
            select = self.menu.check_menu_cols()
            if select == 0:
                self.return_to_main_menu()
            elif select > 0:
                self.start_game(select)
            elif select == -2:
                self.dj.clicked_button()

    def run_settings_menu(self):
        self.draw_settings_menu()
        mouse = pygame.mouse.get_pressed()[0]
        if self.check_mouse_timeout(mouse):
            select = self.settings.check_menu_cols()
            if select == 0:
                self.return_to_main_menu()
            elif select == 1:
                self.dj.switch_sfx()
            elif select == 2:
                self.dj.switch_music()
            elif select > 2:
                self.algorithm = select - 3

    def run_level(self):
        self.drawRun()

        mouse = pygame.mouse.get_pressed()[0]
        if self.check_mouse_timeout(mouse):
            mouse_pos = pygame.mouse.get_pos()
            if self.auto_solving:
                self.check_solve_cols(mouse_pos)
            else:
                self.check_run_cols(mouse_pos)
        if self.auto_solving and not self.solver_failed:
            if self.solve_timer.check_timer() and not self.paused:
                self.play_solved()

    def run_end(self):
        self.draw_end()
        mouse = pygame.mouse.get_pressed()[0]
        if self.check_mouse_timeout(mouse):
            mouse_pos = pygame.mouse.get_pos()
            self.check_back_to_menu(mouse_pos)

    # Level functions

    def create_game(self):
        if hasattr(self, 'tubes'):
            del self.tubes
        self.tubes = []
        x = 50
        y = 650

        for tube in self.cur_game.tubes:
            flask = Flask(tube, [x, y])
            self.tubes.append(flask)
            x += 112

    def start_game(self, level):
        if self.auto_solving:
            self.start_watch(level)
        else:
            self.start_normal(level)

    def start_watch(self, level):
        self.dj.enter_level()
        self.load_level(level)
        self.state = "RUNNING"
        self.moves = 0
        self.auto_speed = 0
        self.solver_failed = False
        self.move_num = Score([1256, 45])
        self.display_hint = False
        self.startSolved()
        if not self.solver_failed:
            self.solve_timer = Timer(1.5)
            self.display_hint = True

    def start_normal(self, level):
        self.display_hint = False
        self.dj.enter_level()
        self.load_level(level)
        self.state = "RUNNING"
        self.moves = 0
        self.selected = -1
        '''
        solver_thread = Thread(target=self.update_hint)
        solver_thread.start()
        '''
        self.saved_moves = []
        self.move_num = Score([1256, 45])
        self.undo_num = Score([1256, 115])

    def return_to_main_menu(self):
        self.state = "MAINMENU"

    def level_selection(self):
        self.state = "GAMEMENU"

    def return_to_menu(self):
        self.dj.in_menu()
        self.state = "GAMEMENU"
        self.selected = -1

    def settings_menu(self):
        self.state = "SETTINGS"

    def end_game(self):
        self.state = "END"
        self.selected = -1

    # Game functions

    def make_move(self, tube):
        if tube == self.selected:
            self.deselect()
        elif self.selected >= 0:
            if self.cur_game.move_ball(self.selected, tube):
                self.successful_move(tube)
        else:
            self.select(tube)

    def successful_move(self, tube):
        self.move_num.increase_score()
        ball = self.tubes[self.selected].remove_ball()
        if self.tubes[tube].add_ball(ball):
            self.dj.complete_tube()
        self.saved_moves.append([self.selected, tube])
        '''
        solver_thread = Thread(target=self.update_hint)
        solver_thread.start()
        '''
        self.deselect()
        self.display_hint = False

    def undo(self):
        if self.saved_moves:
            self.undo_num.increase_score()
            self.move_num.decrease_score()
            last_move = self.saved_moves.pop()
            self.undo_move(last_move)

    def undo_move(self, move):
        self.cur_game.move_ball(move[1], move[0])

        ball = self.tubes[move[1]].remove_ball()
        self.tubes[move[0]].add_ball(ball)
        '''
        solver_thread = Thread(target=self.update_hint)
        solver_thread.start()
        '''

    @timeout(20)
    def get_result(self, init_state):

        if self.algorithm == 0:
            return solver(init_state, Algorithm.A_STAR, 30)
        elif self.algorithm == 1:
            return solver(init_state, Algorithm.GREEDY, 30)
        elif self.algorithm == 2:
            return solver(init_state, Algorithm.DFS, 60)
        elif self.algorithm == 3:
            return solver(init_state, Algorithm.BFS, 15)
        elif self.algorithm == 4:
            return ids(init_state, 60)

    def startSolved(self):
        init_state = Node(self.cur_game)
        try:
            result = self.get_result(init_state)
            if result[1] is None:
                self.solver_failed = True
                self.display_hint = False
                self.hide_hint_arrows()
                return
            self.display_hint = True
            self.solvedPath = result[0].path(result[1])
            self.curNode = 0
        except:
            self.solver_failed = True
            self.display_hint = False
            self.hide_hint_arrows()

    def play_solved(self):

        move = self.get_next_move()
        if move[0] == -2:
            self.end_game()
            return

        self.cur_game.move_ball(move[0], move[1])
        self.watch_move(move)
        self.curNode += 1
        next_move = self.get_next_move()
        if next_move[0] != -2:
            self.update_hint_arrows(next_move)
        else:
            self.hide_hint_arrows()

    def watch_move(self, move):

        self.move_num.increase_score()
        ball = self.tubes[move[0]].remove_ball()
        if self.tubes[move[1]].add_ball(ball):
            self.dj.complete_tube()

    # Select/Deselect flasks
    def deselect(self):
        self.tubes[self.selected].select()
        self.selected = -1

    def select(self, tube):
        self.tubes[tube].select()
        self.selected = tube

    # Hint functions
    def update_hint(self):
        init_state = Node(self.cur_game)
        result = solver(init_state, Algorithm.A_STAR, 30)
        if result[1] is None:
            self.hint_available = False
            self.hide_hint_arrows()
            return
        path = result[0].path(result[1])
        if len(path) > 1:
            self.hint_available = True
            hint = self.find_differences(path[1])
            self.update_hint_arrows(hint)

    def update_hint_arrows(self, hint):
        self.hint_up.sprite.rect.left = self.tubes[hint[0]].coords[0] + 5
        self.hint_up.sprite.rect.top = self.tubes[hint[0]].coords[1] - 130
        self.hint_down.sprite.rect.left = self.tubes[hint[1]].coords[0] + 5
        self.hint_down.sprite.rect.top = self.tubes[hint[1]].coords[1] - 130

    def hide_hint_arrows(self):
        self.hint_up.sprite.rect.left = 8000
        self.hint_up.sprite.rect.top = 8000

        self.hint_down.sprite.rect.left = 8000
        self.hint_down.sprite.rect.top = 8000

    def find_differences(self, node):
        tube_from = -1
        tube_to = -1
        game1 = self.cur_game
        game2 = node.gamestate

        for i in range(0, len(game2.tubes)):
            if len(game1.tubes[i].balls) > len(game2.tubes[i].balls):
                tube_from = i
            elif len(game1.tubes[i].balls) < len(game2.tubes[i].balls):
                tube_to = i

            if (tube_from != -1 and tube_to != -1):
                return [tube_from, tube_to]
        return [tube_from, tube_to]

    def get_next_move(self):
        if (self.curNode == len(self.solvedPath) - 1):
            return [-2, -2]
        node1 = self.solvedPath[self.curNode]
        node2 = self.solvedPath[self.curNode + 1]
        tube_from = -1
        tube_to = -1
        game1 = node1.gamestate
        game2 = node2.gamestate
        for i in range(0, len(game2.tubes)):
            if len(game1.tubes[i].balls) > len(game2.tubes[i].balls):
                tube_from = i
            elif len(game1.tubes[i].balls) < len(game2.tubes[i].balls):
                tube_to = i

            if (tube_from != -1 and tube_to != -1):
                return [tube_from, tube_to]
        return [tube_from, tube_to]


pygame.init()

game = UI()

pygame.display.set_caption('Ballsort')

while game.active:
    game.run()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.active = False

    pygame.display.update()

pygame.quit()
