import pygame

from game.utils import load_sprite, text_to_sprite

# Screen Dimensions
screen_width = 1400
screen_height = 1000


# Menu Class

class Menu:
    def __init__(self):
        self.get_buttons()
        self.get_title()
        self.get_quit()

    def get_title(self):
        sprite = load_sprite("assets/img/titles/BallSort.png")
        sprite.rect.left, sprite.rect.top = [380, 50]
        self.title = pygame.sprite.GroupSingle(sprite)

    def get_buttons(self):
        img = pygame.image.load("assets/img/holders/MainMenuHolder.png")
        font = pygame.font.SysFont("Arial", 70)
        play = text_to_sprite("Play", img, (230, 230, 230), [500, 300], font)
        watch = text_to_sprite("Watch", img, (230, 230, 230), [500, 500], font)
        settings = text_to_sprite("Settings", img, (230, 230, 230), [500, 700], font)

        self.play = pygame.sprite.GroupSingle(play)
        self.watch = pygame.sprite.GroupSingle(watch)
        self.settings = pygame.sprite.GroupSingle(settings)

    def get_quit(self):
        quit = load_sprite("assets/img/buttons/quit.png")
        quit.rect.left = 20
        quit.rect.top = 20
        self.quit = pygame.sprite.GroupSingle(quit)

    def draw(self, screen):
        self.title.draw(screen)
        self.quit.draw(screen)
        self.play.draw(screen)
        self.watch.draw(screen)
        self.settings.draw(screen)

    def check_menu_cols(self):
        mouse_pos = pygame.mouse.get_pos()

        if self.play.sprite.rect.collidepoint(mouse_pos):
            return 1

        if self.watch.sprite.rect.collidepoint(mouse_pos):
            return 2

        if self.settings.sprite.rect.collidepoint(mouse_pos):
            return 3

        if (self.quit.sprite.rect.collidepoint(mouse_pos)):
            return 0
        return -1


# SettingsMenu Class
class SettingsMenu:
    def __init__(self):
        self.get_buttons()
        self.get_title()
        self.get_back()

    def get_title(self):
        sprite = load_sprite("assets/img/titles/Settings.png")
        sprite.rect.left, sprite.rect.top = [380, 50]
        self.title = pygame.sprite.GroupSingle(sprite)

    def get_buttons(self):
        self.sfx_active = True
        self.music_active = True
        self.curr_hint = 0

        img = pygame.image.load("assets/img/holders/SettingsHolders.png")
        hint_img = pygame.image.load("assets/img/holders/level.png")
        off_bg = pygame.image.load("assets/img/holders/offBg.png")
        on_bg = pygame.image.load("assets/img/holders/onBg.png")
        font = pygame.font.SysFont("Arial", 60)
        font2 = pygame.font.SysFont("Arial", 50)
        off1 = text_to_sprite("Off", off_bg, (0, 0, 0), [810, 410], font2)
        off2 = text_to_sprite("Off", off_bg, (0, 0, 0), [810, 560], font2)
        on1 = text_to_sprite("On", on_bg, (230, 230, 230), [810, 410], font2)
        on2 = text_to_sprite("On", on_bg, (230, 230, 230), [810, 560], font2)

        music = text_to_sprite("Music", img, (230, 230, 230), [390, 400], font)
        sfx = text_to_sprite("SFX", img, (230, 230, 230), [390, 550], font)

        hint = text_to_sprite("Hint", img, (230, 230, 230), [390, 700], font)
        greedy = text_to_sprite("greedy", hint_img, (230, 230, 230), [800, 700], font2)
        astar = text_to_sprite("A*", hint_img, (230, 230, 230), [800, 700], font2)
        bfs = text_to_sprite("BFS", hint_img, (230, 230, 230), [800, 700], font2)
        dfs = text_to_sprite("DFS", hint_img, (230, 230, 230), [800, 700], font2)
        ids = text_to_sprite("IDS", hint_img, (230, 230, 230), [800, 700], font2)

        self.music = pygame.sprite.GroupSingle(music)
        self.sfx = pygame.sprite.GroupSingle(sfx)
        self.music_off = pygame.sprite.GroupSingle(off1)
        self.music_on = pygame.sprite.GroupSingle(on1)
        self.sfx_off = pygame.sprite.GroupSingle(off2)
        self.sfx_on = pygame.sprite.GroupSingle(on2)

        self.hint = pygame.sprite.GroupSingle(hint)
        self.algorithms = []
        self.algorithms.append(pygame.sprite.GroupSingle(astar))
        self.algorithms.append(pygame.sprite.GroupSingle(greedy))
        self.algorithms.append(pygame.sprite.GroupSingle(dfs))
        self.algorithms.append(pygame.sprite.GroupSingle(bfs))
        self.algorithms.append(pygame.sprite.GroupSingle(ids))

    def get_back(self):
        back = load_sprite("assets/img/buttons/back.png")
        back.rect.left = 20
        back.rect.top = 20
        self.back = pygame.sprite.GroupSingle(back)

    def draw(self, screen):
        self.title.draw(screen)
        self.back.draw(screen)
        self.music.draw(screen)
        self.sfx.draw(screen)
        if self.sfx_active:
            self.sfx_on.draw(screen)
        else:
            self.sfx_off.draw(screen)

        if self.music_active:
            self.music_on.draw(screen)
        else:
            self.music_off.draw(screen)
        self.draw_hint(screen)

    def draw_hint(self, screen):
        self.hint.draw(screen)
        self.algorithms[self.curr_hint].draw(screen)

    def check_menu_cols(self):
        mouse_pos = pygame.mouse.get_pos()

        if self.sfx_on.sprite.rect.collidepoint(mouse_pos):
            self.sfx_active = not self.sfx_active
            return 1

        if self.music_on.sprite.rect.collidepoint(mouse_pos):
            self.music_active = not self.music_active
            return 2

        if (self.back.sprite.rect.collidepoint(mouse_pos)):
            return 0

        if (self.algorithms[self.curr_hint].sprite.rect.collidepoint(mouse_pos)):
            self.curr_hint += 1
            if (self.curr_hint >= 5):
                self.curr_hint = 0
            return self.curr_hint + 3
        return -1


# Game Menu Class

class GameMenu:
    def __init__(self, levels):
        self.get_levels(levels)
        self.get_next_prev()
        self.get_back()

    def get_levels(self, levels):
        self.levels = []
        self.curr_page = 0
        self.total_pages = 0
        levels_page = pygame.sprite.Group()
        img = pygame.image.load("assets/img/holders/level.png")
        font = pygame.font.SysFont("Arial", 70)

        x = 200
        y = 150
        rows = 3
        x_inc = (screen_width - x) // 3
        y_inc = (screen_height - y) // rows

        for i in range(1, len(levels) + 1):
            if i % 9 == 1 and i > 1:
                copy = levels_page.copy()
                self.levels.append(copy)
                pygame.sprite.Group.empty(levels_page)
                self.total_pages += 1
                x = 200
                y = 150

            sprite = text_to_sprite(str(i), img, (230, 230, 230), [x, y], font)
            levels_page.add(sprite)

            if i % 3 == 0 and i > 0:
                x = 200
                y += y_inc
            else:
                x += x_inc

        if len(levels) % 9 != 0:
            self.levels.append(levels_page)

    def get_next_prev(self):
        img = pygame.image.load("assets/img/holders/prevNext.png")
        font = pygame.font.SysFont("Arial", 35)
        next_sprite = text_to_sprite("Next", img, (230, 230, 230), [1200, 900], font)
        prev_sprite = text_to_sprite("Prev", img, (230, 230, 230), [1050, 900], font)
        self.next = pygame.sprite.GroupSingle(next_sprite)
        self.prev = pygame.sprite.GroupSingle(prev_sprite)

    def get_back(self):
        back = load_sprite("assets/img/buttons/back.png")
        back.rect.left = 20
        back.rect.top = 20
        self.back = pygame.sprite.GroupSingle(back)

    def draw(self, screen):
        self.back.draw(screen)
        self.levels[self.curr_page].draw(screen)
        if self.curr_page > 0:
            self.prev.draw(screen)
        if self.curr_page < self.total_pages:
            self.next.draw(screen)

    def check_menu_cols(self):
        mouse_pos = pygame.mouse.get_pos()

        if self.curr_page > 0 and self.prev.sprite.rect.collidepoint(mouse_pos):
            self.curr_page -= 1
            return -2
        if self.curr_page < self.total_pages and self.next.sprite.rect.collidepoint(mouse_pos):
            self.curr_page += 1
            return -2
        i = 0
        for k in self.levels[self.curr_page]:
            i += 1
            if k.rect.collidepoint(mouse_pos):
                return 9 * self.curr_page + i
        if (self.back.sprite.rect.collidepoint(mouse_pos)):
            return 0

        return -1
