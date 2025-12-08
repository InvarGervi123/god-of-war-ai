import pygame
from settings import (
    WIDTH,
    HEIGHT,
    TEXT_COLOR,
    font,
    draw_gradient_background,
    draw_ground,
)
from settings import (
    PLAYER_BASE_WIDTH,
    ENEMY_BASE_WIDTH,
    UNIT_COST,
    MONEY_PER_SECOND,
    XP_PER_SECOND,
    ENEMY_SPAWN_INTERVAL,
    MONEY_MAX,
    XP_MAX,
    BASE_TURRET_MAX_LEVEL,
    BASE_TURRET_XP_COSTS,
    BASE_TURRET_RANGES,
    BASE_TURRET_DAMAGES,
    BASE_TURRET_COOLDOWNS,
    DEFAULT_SCREEN_SHAKE_DURATION,
    DEFAULT_SCREEN_SHAKE_MAGNITUDE,
)
from entities import Base, Unit
from effects import ParticleSystem, Background


class Game:
    """
    Game:
    - בסיס שחקן/אויב
    - יחידות
    - כסף ו-XP
    - טורט בסיס עם שדרוגים + אנימציית ירי
    """

    def __init__(self):
        # בסיסים
        self.player_base = Base(x=40, width=PLAYER_BASE_WIDTH, side="player")
        self.enemy_base = Base(x=WIDTH - 40 - ENEMY_BASE_WIDTH, width=ENEMY_BASE_WIDTH, side="enemy")

        # יחידות
        self.player_units = []
        self.enemy_units = []

        # כסף ו-XP
        self.money = 100
        self.xp = 0
        self.money_per_second = MONEY_PER_SECOND
        self.xp_per_second = XP_PER_SECOND

        # עלות יצירת יחידה
        self.unit_cost = UNIT_COST

        # טיימרים
        self.last_income_time = pygame.time.get_ticks()
        self.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL
        self.last_enemy_spawn_time = pygame.time.get_ticks()

        # טורט בסיס (שחקן)
        self.base_turret_level = 0
        self.base_turret_max_level = BASE_TURRET_MAX_LEVEL

        # עלות XP לכל רמה (אינדקס = רמה)
        self.base_turret_xp_costs = BASE_TURRET_XP_COSTS

        # פרמטרים לכל רמה
        self.base_turret_ranges = BASE_TURRET_RANGES
        self.base_turret_damages = BASE_TURRET_DAMAGES
        self.base_turret_cooldowns = BASE_TURRET_COOLDOWNS
        self.base_turret_last_shot = 0

        # יריות טורט (לאנימציה)
        # כל ירייה: {"start": (x,y), "end": (x,y), "time": ms}
        self.turret_shots = []

        # particle effects
        self.particles = ParticleSystem()

        # dynamic background
        self.background = Background(self.particles)

        # screen shake
        self.shake_time = 0
        self.shake_duration = 0
        self.shake_magnitude = 0

        # סוף משחק
        self.game_over = False
        self.winner = None

    # ---------- יצירת יחידות ----------

    def spawn_player_unit(self):
        if self.game_over:
            return
        if self.money >= self.unit_cost:
            self.money -= self.unit_cost
            # spawn a bit closer to the front so new units can immediately engage
            start_x = self.player_base.rect.right - 10
            self.player_units.append(Unit(start_x, "player"))

    def spawn_enemy_unit(self):
        if self.game_over:
            return
        # spawn enemy slightly closer so they can hit newly spawned defenders
        start_x = self.enemy_base.rect.left - 15
        self.enemy_units.append(Unit(start_x, "enemy"))

    # ---------- כסף ו-XP ----------

    def give_time_income(self, now):
        delta = now - self.last_income_time
        if delta <= 0:
            return

        seconds = delta / 1000.0
        self.money += int(self.money_per_second * seconds)
        self.xp += int(self.xp_per_second * seconds)

        if self.money > MONEY_MAX:
            self.money = MONEY_MAX
        if self.xp > XP_MAX:
            self.xp = XP_MAX

        self.last_income_time = now

    def reward_for_kills_and_damage(self, enemy_before, enemy_after, base_hp_before):
        killed = enemy_before - enemy_after
        if killed > 0:
            self.money += killed * 150
            self.xp += killed * 100

        base_damage = base_hp_before - self.enemy_base.hp
        if base_damage > 0:
            self.money += base_damage // 10
            self.xp += base_damage // 5

    # ---------- טורט בסיס ----------

    def can_upgrade_turret(self):
        if self.base_turret_level >= self.base_turret_max_level:
            return False
        next_level = self.base_turret_level + 1
        cost = self.base_turret_xp_costs[next_level]
        return self.xp >= cost

    def upgrade_base_turret(self):
        if self.game_over:
            return
        if not self.can_upgrade_turret():
            return

        next_level = self.base_turret_level + 1
        cost = self.base_turret_xp_costs[next_level]
        self.xp -= cost
        self.base_turret_level = next_level

    def update_base_turret(self, now):
        lvl = self.base_turret_level
        if lvl <= 0:
            return

        rng = self.base_turret_ranges[lvl]
        cd = self.base_turret_cooldowns[lvl]
        dmg = self.base_turret_damages[lvl]

        if now - self.base_turret_last_shot < cd:
            return

        # חיפוש אויב קרוב בתוך טווח הטורט
        base_x = self.player_base.rect.centerx
        base_y = self.player_base.rect.top - 15  # גובה הצריח בערך
        target = None
        closest = 999999

        for enemy in self.enemy_units:
            if not enemy.alive:
                continue
            dist = abs(enemy.rect.centerx - base_x)
            if dist <= rng and dist < closest:
                closest = dist
                target = enemy

        if target is None:
            return

        # ירייה (פגיעה + אנימציה)
        self.base_turret_last_shot = now

        # פגיעה
        target.hp -= dmg
        if target.hp <= 0:
            target.alive = False

        # יצירת "ירייה" לרינדור (קו מהבסיס לאויב)
        start_pos = (base_x, base_y)
        end_pos = (target.rect.centerx, target.rect.centery - 8)
        self.turret_shots.append({"start": start_pos, "end": end_pos, "time": now})

        # visual feedback: sparks at hit
        try:
            self.particles.spawn_sparks(end_pos, color=(255, 220, 120), count=10)
        except Exception:
            pass

        # if hit base, larger explosion + shake
        if isinstance(target, Base):
            try:
                self.particles.spawn_explosion(end_pos)
            except Exception:
                pass
            self.trigger_shake(DEFAULT_SCREEN_SHAKE_DURATION, DEFAULT_SCREEN_SHAKE_MAGNITUDE)

    def update_turret_shots(self, now):
        # משאירים רק יריות חדשות (אנימציה קצרה ~120ms)
        self.turret_shots = [
            s for s in self.turret_shots if now - s["time"] < 120
        ]

    # ---------- עדכון ----------

    def update(self, dt):
        if self.game_over:
            return

        now = pygame.time.get_ticks()

        self.give_time_income(now)

        if now - self.last_enemy_spawn_time >= self.enemy_spawn_interval:
            self.spawn_enemy_unit()
            self.last_enemy_spawn_time = now

        # update background
        try:
            self.background.update(dt)
        except Exception:
            pass

        enemy_before = len(self.enemy_units)
        base_hp_before = self.enemy_base.hp

        for u in self.player_units:
            ev = u.update(dt, now, self.enemy_units, self.enemy_base, self.particles)
            if ev and ev.get("base_hit"):
                self.trigger_shake(DEFAULT_SCREEN_SHAKE_DURATION, DEFAULT_SCREEN_SHAKE_MAGNITUDE)

        for u in self.enemy_units:
            ev = u.update(dt, now, self.player_units, self.player_base, self.particles)
            if ev and ev.get("base_hit"):
                self.trigger_shake(DEFAULT_SCREEN_SHAKE_DURATION, DEFAULT_SCREEN_SHAKE_MAGNITUDE)

        # טורט בסיס
        self.update_base_turret(now)
        self.update_turret_shots(now)

        # update particles system
        try:
            self.particles.update(dt)
        except Exception:
            pass

        self.player_units = [u for u in self.player_units if u.alive]
        self.enemy_units = [u for u in self.enemy_units if u.alive]

        enemy_after = len(self.enemy_units)

        self.reward_for_kills_and_damage(enemy_before, enemy_after, base_hp_before)

        if self.player_base.is_dead():
            self.game_over = True
            self.winner = "enemy"
        elif self.enemy_base.is_dead():
            self.game_over = True
            self.winner = "player"

    # ---------- ציור ----------

    def draw_turret_shots(self, surface):
        shot_color = (255, 255, 120)
        glow_color = (255, 200, 80)

        for s in self.turret_shots:
            start = s["start"]
            end = s["end"]
            pygame.draw.line(surface, shot_color, start, end, 3)
            pygame.draw.circle(surface, glow_color, end, 6)

    def trigger_shake(self, duration_ms, magnitude):
        self.shake_time = pygame.time.get_ticks()
        self.shake_duration = duration_ms
        self.shake_magnitude = magnitude

    def draw_ui(self, surface):
        money_text = font.render(f"Money: {self.money}", True, TEXT_COLOR)
        surface.blit(money_text, (20, 10))

        xp_text = font.render(f"XP: {self.xp}", True, TEXT_COLOR)
        surface.blit(xp_text, (20, 35))

        turret_text = font.render(
            f"Base Turret Level: {self.base_turret_level}", True, TEXT_COLOR
        )
        surface.blit(turret_text, (20, 60))

        lines = [
            f"SPACE - Spawn soldier (cost: {self.unit_cost} money)",
            "Goal: protect your base and destroy the enemy base.",
        ]

        if self.base_turret_level < self.base_turret_max_level:
            next_level = self.base_turret_level + 1
            cost = self.base_turret_xp_costs[next_level]
            lines.append(f"1 - Upgrade base turret (XP cost: {cost})")
        else:
            lines.append("Base turret is at max level")

        for i, line in enumerate(lines):
            t = font.render(line, True, TEXT_COLOR)
            surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 10 + i * 22))

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            msg = "YOU WIN!" if self.winner == "player" else "YOU LOSE!"
            t = font.render(msg, True, (255, 255, 255))
            surface.blit(
                t,
                (
                    WIDTH // 2 - t.get_width() // 2,
                    HEIGHT // 2 - t.get_height() // 2 - 15,
                ),
            )

            t2 = font.render("Press R to restart, ESC to quit", True, (230, 230, 230))
            surface.blit(
                t2,
                (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 20),
            )

    def draw(self, surface):
        # draw everything to a temp surface so we can apply screen shake
        temp = pygame.Surface((WIDTH, HEIGHT))
        # dynamic background (includes gradient)
        try:
            self.background.draw(temp)
        except Exception:
            draw_gradient_background(temp)
        draw_ground(temp)

        self.player_base.draw(temp)
        self.enemy_base.draw(temp)

        for u in self.player_units:
            u.draw(temp)
        for u in self.enemy_units:
            u.draw(temp)

        # turret shots and UI
        self.draw_turret_shots(temp)
        self.draw_ui(temp)

        # particles on top
        try:
            self.particles.draw(temp)
        except Exception:
            pass

        # compute shake offset
        ox = oy = 0
        if self.shake_duration > 0:
            now = pygame.time.get_ticks()
            elapsed = now - self.shake_time
            if elapsed < self.shake_duration:
                # damping factor
                rem = 1.0 - (elapsed / float(self.shake_duration))
                mag = int(self.shake_magnitude * rem)
                import random

                ox = random.randint(-mag, mag)
                oy = random.randint(-mag // 2, mag // 2)
            else:
                self.shake_duration = 0
                self.shake_magnitude = 0

        # blit temp to main surface with offset
        surface.fill((0, 0, 0))
        surface.blit(temp, (ox, oy))

    # ---------- איפוס ----------

    def reset(self):
        self.__init__()
