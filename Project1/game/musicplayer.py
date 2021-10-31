import pygame


# Music Class

class MusicPlayer:
    def __init__(self):
        self.load_bg_music()
        self.load_game_sounds()
        self.SFX = True
        self.music = True

    def load_bg_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load("assets/sound/bgMusic.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1, 0, 10)

    def load_game_sounds(self):
        self.completed_tube = pygame.mixer.Sound("assets/sound/completedTubeSound.mp3")
        self.select_level = pygame.mixer.Sound("assets/sound/selectLevelSound.mp3")
        self.hint = pygame.mixer.Sound("assets/sound/hintSound.mp3")
        self.button = pygame.mixer.Sound("assets/sound/buttonSound.mp3")
        self.select_level.set_volume(0.05)
        self.completed_tube.set_volume(0.1)
        self.hint.set_volume(0.1)
        self.button.set_volume(0.1)

    def in_menu(self):
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.rewind()

    def enter_level(self):
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.rewind()
        if self.SFX:
            self.select_level.play()

    def click_hint(self):
        if self.SFX:
            self.hint.play()

    def complete_tube(self):
        if self.SFX:
            self.completed_tube.play()

    def clicked_button(self):
        if self.SFX:
            self.button.play()

    def switch_music(self):
        self.music = not self.music
        if self.music:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    def switch_sfx(self):
        self.SFX = not self.SFX
