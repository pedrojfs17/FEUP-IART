import json
import pygame

from game.utils import load_sprite, text_to_sprite, only_text_sprite


# End Screen Class

class EndScreen:
    def __init__(self):
        self.coords = [800, 450]
        self.load_numbers()
        self.load_level_passed()
        self.load_holders()
        self.load_text()
        self.load_back_to_menu()

    def load_numbers(self):
        self.numbers = []
        font = pygame.font.SysFont("Arial", 70)
        for i in range(0, 10):
            num = only_text_sprite(str(i), (0, 0, 0), self.coords, font)

            number = pygame.sprite.GroupSingle(num)
            self.numbers.append(number)

    def load_level_passed(self):
        sprite = load_sprite("assets/img/titles/levelPassed.png")
        sprite.rect.left, sprite.rect.top = [350, 200]
        self.passed = pygame.sprite.GroupSingle(sprite)

    def load_holders(self):
        sprite = load_sprite("assets/img/holders/endScoreHolder.png")
        sprite.rect.left, sprite.rect.top = [self.coords[0] - 10, self.coords[1]]
        self.score_holder = pygame.sprite.GroupSingle(sprite)
        copy = load_sprite("assets/img/holders/endScoreHolder.png")
        copy.rect.left, copy.rect.top = [self.coords[0] - 10, self.coords[1] + 190]
        self.undo_holder = pygame.sprite.GroupSingle(copy)

    def load_text(self):
        font = pygame.font.SysFont("Arial", 50)
        img = pygame.image.load("assets/img/holders/TextHolder.png")
        move = text_to_sprite("Move Count: ", img, (230, 230, 230), [350, self.coords[1] - 10], font)
        undo = text_to_sprite("Undo Count: ", img, (230, 230, 230), [350, self.coords[1] + 180], font)
        self.move_text = pygame.sprite.Group(move)
        self.undo_text = pygame.sprite.Group(undo)

    def load_back_to_menu(self):
        back = load_sprite("assets/img/buttons/backToMenu.png")
        back.rect.left, back.rect.top = [500, 800]
        self.back_to_menu = pygame.sprite.GroupSingle(back)

    def draw(self, screen, score, undo):
        self.passed.draw(screen)
        self.draw_back_to_menu(screen)
        self.draw_holders(screen)
        self.draw_score(screen, score)
        self.draw_undo(screen, undo)

    def draw_solved(self, screen, score):
        self.passed.draw(screen)
        self.draw_back_to_menu(screen)
        self.score_holder.draw(screen)
        self.move_text.draw(screen)
        self.draw_score(screen, score)

    def draw_holders(self, screen):
        self.score_holder.draw(screen)
        self.undo_holder.draw(screen)
        self.move_text.draw(screen)
        self.undo_text.draw(screen)

    def draw_score(self, screen, score):
        num1 = score // 100
        num2 = score % 100 // 10
        num3 = score % 10

        self.numbers[num1].sprite.rect.top = self.coords[1] - 5
        self.numbers[num1].sprite.rect.left = self.coords[0]
        self.numbers[num1].draw(screen)

        self.numbers[num2].sprite.rect.top = self.coords[1] - 5
        self.numbers[num2].sprite.rect.left = self.coords[0] + 70
        self.numbers[num2].draw(screen)

        self.numbers[num3].sprite.rect.top = self.coords[1] - 5
        self.numbers[num3].sprite.rect.left = self.coords[0] + 140
        self.numbers[num3].draw(screen)

    def draw_undo(self, screen, undo):
        num1 = undo // 100
        num2 = undo % 100 // 10
        num3 = undo % 10

        self.numbers[num1].sprite.rect.top = self.coords[1] + 185
        self.numbers[num1].sprite.rect.left = self.coords[0]
        self.numbers[num1].draw(screen)

        self.numbers[num2].sprite.rect.top = self.coords[1] + 185
        self.numbers[num2].sprite.rect.left = self.coords[0] + 70
        self.numbers[num2].draw(screen)

        self.numbers[num3].sprite.rect.top = self.coords[1] + 185
        self.numbers[num3].sprite.rect.left = self.coords[0] + 140
        self.numbers[num3].draw(screen)

    def draw_back_to_menu(self, screen):
        self.back_to_menu.draw(screen)

    def check_back_col(self, mouse_pos):
        return self.back_to_menu.sprite.rect.collidepoint(mouse_pos)
