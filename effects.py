import random
import pygame


class Particle:
    def __init__(self, pos, vel, color, radius, life, fade=True):
        self.x, self.y = pos
        self.vx, self.vy = vel
        self.color = color
        self.radius = radius
        self.life = life
        self.max_life = life
        self.fade = fade

    def update(self, dt):
        # dt in milliseconds
        t = dt / 1000.0
        self.x += self.vx * t
        self.y += self.vy * t
        # simple gravity
        self.vy += 300 * t
        self.life -= dt

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = 255
        if self.fade:
            alpha = int(255 * (self.life / max(1, self.max_life)))
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        c = (*self.color[:3], alpha)
        pygame.draw.circle(s, c, (self.radius, self.radius), int(self.radius))
        surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn_sparks(self, pos, color=(255, 220, 120), count=8, speed=180):
        px, py = pos
        for _ in range(count):
            ang = random.uniform(0, 2 * 3.1415)
            spd = random.uniform(0.3 * speed, 1.0 * speed)
            vx = spd * math_cos(ang)
            vy = spd * math_sin(ang) * -0.5
            r = random.uniform(2, 4)
            life = random.randint(300, 700)
            self.particles.append(Particle((px, py), (vx, vy), color, r, life))

    def spawn_blood(self, pos, color=(200, 40, 40), count=10, speed=120):
        px, py = pos
        for _ in range(count):
            ang = random.uniform(0, 2 * 3.1415)
            spd = random.uniform(0.2 * speed, 1.0 * speed)
            vx = spd * math_cos(ang)
            vy = spd * math_sin(ang) * -0.3
            r = random.uniform(2, 5)
            life = random.randint(500, 1000)
            self.particles.append(Particle((px, py), (vx, vy), color, r, life))

    def spawn_smoke(self, pos, count=6):
        px, py = pos
        for _ in range(count):
            vx = random.uniform(-20, 20)
            vy = random.uniform(-40, -10)
            r = random.uniform(6, 14)
            life = random.randint(600, 1400)
            self.particles.append(Particle((px, py), (vx, vy), (80, 80, 80), r, life))

    def spawn_explosion(self, pos, color=(255, 160, 60), count=18):
        px, py = pos
        for _ in range(count):
            ang = random.uniform(0, 2 * 3.1415)
            spd = random.uniform(0.2 * 300, 1.0 * 300)
            vx = spd * math_cos(ang)
            vy = spd * math_sin(ang) * -0.2
            r = random.uniform(3, 7)
            life = random.randint(500, 1000)
            self.particles.append(Particle((px, py), (vx, vy), color, r, life))

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.update(dt)
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


# small trig helpers without importing math heavy functions directly
def math_cos(a):
    import math

    return math.cos(a)


def math_sin(a):
    import math

    return math.sin(a)
