import os
import pygame, random, time
from pygame.locals import *

# permanent base directory where flappy.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset(*parts):
    """Build an absolute path to an asset inside the pr object."""
    return os.path.join(BASE_DIR, *parts)


# VARIABLES
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150

wing = asset('assets', 'audio', 'wing.wav')
hit = asset('assets', 'audio', 'hit.wav')

pygame.mixer.init()


class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images = [pygame.image.load(asset('assets', 'sprites', 'bluebird-upflap.png')).convert_alpha(),
                       pygame.image.load(asset('assets', 'sprites', 'bluebird-midflap.png')).convert_alpha(),
                       pygame.image.load(asset('assets', 'sprites', 'bluebird-downflap.png')).convert_alpha()]

        self.speed = SPEED

        self.current_image = 0
        self.image = pygame.image.load(asset('assets', 'sprites', 'bluebird-upflap.png')).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDTH / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY

        # UPDATE HEIGHT
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]


class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(asset('assets', 'sprites', 'pipe-green.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)
        self.passed = False
        self.inverted = inverted

    def update(self):
        self.rect[0] -= GAME_SPEED


class Ground(pygame.sprite.Sprite):

    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(asset('assets', 'sprites', 'base.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED


def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])


def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Get the folder where flappy.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build a path relative to flappy.py
path = asset("assets", "sprites", "background-day.png")

# Load and scale background image
BACKGROUND = pygame.image.load(path).convert_alpha()
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
BEGIN_IMAGE = pygame.image.load(asset('assets', 'sprites', 'message.png')).convert_alpha()
GAMEOVER_IMAGE = pygame.image.load(asset('assets', 'sprites', 'gameover.png')).convert_alpha()


def main():
    while True:
        bird_group = pygame.sprite.Group()
        bird = Bird()
        bird_group.add(bird)

        ground_group = pygame.sprite.Group()

        for i in range(2):
            ground = Ground(GROUND_WIDTH * i)
            ground_group.add(ground)

        pipe_group = pygame.sprite.Group()
        for i in range(2):
            pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])

        clock = pygame.time.Clock()

        begin = True

        score = 0
        font = pygame.font.SysFont('Helvetica', 30, bold=True)

        while begin:

            clock.tick(15)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                if event.type == KEYDOWN:
                    if event.key == K_SPACE or event.key == K_UP:
                        bird.bump()
                        pygame.mixer.music.load(wing)
                        pygame.mixer.music.play()
                        begin = False

            screen.blit(BACKGROUND, (0, 0))
            screen.blit(BEGIN_IMAGE, (120, 150))

            if is_off_screen(ground_group.sprites()[0]):
                ground_group.remove(ground_group.sprites()[0])

                new_ground = Ground(GROUND_WIDTH - 20)
                ground_group.add(new_ground)

            bird.begin()
            ground_group.update()

            bird_group.draw(screen)
            ground_group.draw(screen)

            pygame.display.update()

        game_active = True
        while game_active:

            clock.tick(15)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                if event.type == KEYDOWN:
                    if event.key == K_SPACE or event.key == K_UP:
                        bird.bump()
                        pygame.mixer.music.load(wing)
                        pygame.mixer.music.play()

            screen.blit(BACKGROUND, (0, 0))

            if is_off_screen(ground_group.sprites()[0]):
                ground_group.remove(ground_group.sprites()[0])

                new_ground = Ground(GROUND_WIDTH - 20)
                ground_group.add(new_ground)

            if is_off_screen(pipe_group.sprites()[0]):
                pipe_group.remove(pipe_group.sprites()[0])
                pipe_group.remove(pipe_group.sprites()[0])

                pipes = get_random_pipes(SCREEN_WIDTH * 2)

                pipe_group.add(pipes[0])
                pipe_group.add(pipes[1])

            bird_group.update()
            ground_group.update()
            pipe_group.update()

            bird_group.draw(screen)
            pipe_group.draw(screen)
            ground_group.draw(screen)

            # Score check
            for pipe in pipe_group:
                if not pipe.passed and bird.rect.left > pipe.rect.right:
                    pipe.passed = True
                    # Only add score for one pipe in the pair (e.g., the bottom one which is not inverted)
                    if not pipe.inverted:
                        score += 1

            score_surface = font.render(f"Score = {score}", True, (255, 255, 255))
            screen.blit(score_surface, (SCREEN_WIDTH / 2 - score_surface.get_width() / 2, 15))

            pygame.display.update()

            if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
                    pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
                pygame.mixer.music.load(hit)
                pygame.mixer.music.play()
                game_active = False

        # Game Over Loop
        while True:
            # Redraw the game scene to clear the top score
            screen.blit(BACKGROUND, (0, 0))
            bird_group.draw(screen)
            pipe_group.draw(screen)
            ground_group.draw(screen)

            screen.blit(GAMEOVER_IMAGE, (SCREEN_WIDTH / 2 - GAMEOVER_IMAGE.get_width() / 2, 200))

            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (SCREEN_WIDTH / 2 - score_text.get_width() / 2, 260))

            restart_text = font.render("Press Spacebar to restart", True, (255, 255, 255))
            screen.blit(restart_text, (SCREEN_WIDTH / 2 - restart_text.get_width() / 2, 300))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        # Break to restart
                        break
            else:
                continue
            break


if __name__ == "__main__":
    main()