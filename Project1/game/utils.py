import pygame


# Load Sprite functions

def load_sprite(file):
    img = pygame.image.load(file)
    sprite = pygame.sprite.Sprite()
    sprite.image = img
    sprite.rect = img.get_rect()
    return sprite


def text_to_sprite(text, img, color, pos, font):
    text_surf = font.render(text, 1, color)

    background = pygame.Surface((img.get_width(), img.get_height()))

    background.blit(img, [0, 0])

    width = text_surf.get_width()
    height = text_surf.get_height()

    background.blit(text_surf, [img.get_width() / 2 - width / 2, img.get_height() / 2 - height / 2])

    sprite = pygame.sprite.Sprite()
    sprite.image = background
    sprite.rect = background.get_rect()
    sprite.rect.left, sprite.rect.top = pos

    return sprite


def only_text_sprite(text, color, pos, font):
    text_surf = font.render(text, 1, color)
    sprite = pygame.sprite.Sprite()

    background = pygame.Surface((text_surf.get_width() * 1.1, text_surf.get_height() * 1.1), pygame.SRCALPHA)

    background.blit(text_surf, [text_surf.get_width() * 0.05, text_surf.get_height() * 0.05])
    sprite.image = background
    sprite.rect = background.get_rect()
    sprite.rect.left, sprite.rect.top = pos

    return sprite
