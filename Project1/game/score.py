import pygame

from game.utils import only_text_sprite


# Score Class

class Score:
    def __init__(self, coords):
        self.coords = coords
        self.load_numbers()
        self.score = 0

    def set_score(self, score):
        self.score = score

    def increase_score(self):
        self.score += 1

    def decrease_score(self):
        self.score -= 1

    def load_numbers(self):
        self.numbers = []
        font = pygame.font.SysFont("Arial", 50)
        for i in range(0, 10):
            num = only_text_sprite(str(i), (0, 0, 0), self.coords, font)

            number = pygame.sprite.GroupSingle(num)
            self.numbers.append(number)

    def draw(self, screen):
        num1 = self.score // 100
        num2 = self.score % 100 // 10
        num3 = self.score % 10

        self.numbers[num1].sprite.rect.left = self.coords[0]
        self.numbers[num1].draw(screen)
        self.numbers[num2].sprite.rect.left = self.coords[0] + 35
        self.numbers[num2].draw(screen)
        self.numbers[num3].sprite.rect.left = self.coords[0] + 70
        self.numbers[num3].draw(screen)
