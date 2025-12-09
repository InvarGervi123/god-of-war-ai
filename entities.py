"""
entities.py
מכיל את המחלקות:
- Base  (בסיס)
- Unit  (לוחם)
"""

import pygame
from settings import (
    GROUND_Y,
    PLAYER_BASE_COLOR,
    ENEMY_BASE_COLOR,
    HP_BAR_BG,
    HP_GOOD,
    HP_MED,
    HP_BAD,
    PLAYER_COLOR,
    ENEMY_COLOR,
    TEXT_COLOR,
)
import visuals
from settings import (
    PLAYER_BASE_MAX_HP,
    ENEMY_BASE_MAX_HP,
    BASE_HIT_FLASH_DURATION,
    UNIT_WIDTH,
    UNIT_HEIGHT,
    UNIT_MAX_HP,
    UNIT_SPEED,
    UNIT_ATTACK_RANGE,
    UNIT_ATTACK_DAMAGE,
    UNIT_ATTACK_COOLDOWN,
    UNIT_ATTACK_ANIM_DURATION,
    UNIT_HIT_FLASH_DURATION,
    UNIT_RECOIL_AMOUNT,
)


class Base:
    """
    מייצגת בסיס (שחקן או אויב).
    לכל בסיס יש:
    - מקום (Rect)
    - חיים (HP)
    - צד (שחקן / אויב)
    """

    def __init__(self, x, width, side):
        """
        x = מיקום בציר X
        width = רוחב הבסיס
        side = "player" או "enemy"
        """
        self.side = side
        # גובה הבסיס 140 פיקסלים
        self.rect = pygame.Rect(x, GROUND_Y - 140, width, 140)
        # HP ניתן לכוונון ב- settings.py
        self.max_hp = PLAYER_BASE_MAX_HP if side == "player" else ENEMY_BASE_MAX_HP
        self.hp = self.max_hp
        # used to show a brief red flash when base is hit
        self.hit_flash_time = 0
        self.hit_flash_duration = BASE_HIT_FLASH_DURATION

    def take_damage(self, amount):
        """
        הפחתת חיים. אם מגיע ל-0, הבסיס מת (אין מינוס).
        """
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        # register hit time for flash effect
        try:
            self.hit_flash_time = pygame.time.get_ticks()
        except Exception:
            self.hit_flash_time = 0

    def is_dead(self):
        """
        בדיקה אם הבסיס מת.
        """
        return self.hp <= 0

    def draw(self, surface):
        """
        ציור הבסיס + פס חיים + טקסט.
        """
        color = PLAYER_BASE_COLOR if self.side == "player" else ENEMY_BASE_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)

        # "צריח" קטן למעלה בשביל היופי
        turret_rect = pygame.Rect(self.rect.centerx - 20, self.rect.top - 30, 40, 30)
        pygame.draw.rect(surface, (200, 200, 200), turret_rect, border_radius=8)

        # פס חיים
        bar_width = self.rect.width
        bar_height = 12
        bar_x = self.rect.left
        bar_y = self.rect.top - 15

        pygame.draw.rect(surface, HP_BAR_BG, (bar_x, bar_y, bar_width, bar_height))

        hp_ratio = self.hp / self.max_hp
        if hp_ratio > 0.5:
            hp_color = HP_GOOD
        elif hp_ratio > 0.25:
            hp_color = HP_MED
        else:
            hp_color = HP_BAD

        pygame.draw.rect(
            surface,
            hp_color,
            (bar_x, bar_y, int(bar_width * hp_ratio), bar_height),
        )

        # טקסט מעל הבסיס
        label = "Player Base" if self.side == "player" else "Enemy Base"
        # visuals.ensure_fonts() is called from main after pygame.init()
        text = visuals.font.render(f"{label}: {self.hp}", True, TEXT_COLOR)
        surface.blit(
            text,
            (self.rect.centerx - text.get_width() // 2, bar_y - 22),
        )

        # flash red briefly when hit
        now = pygame.time.get_ticks()
        if now - getattr(self, "hit_flash_time", 0) < getattr(self, "hit_flash_duration", 0):
            alpha = 160
            flash = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            flash.fill((220, 40, 40, alpha))
            surface.blit(flash, (self.rect.left, self.rect.top))


class Unit:
    """
    מייצגת לוחם אחד (חייל).
    לכל לוחם יש:
    - צד (שחקן / אויב)
    - מקום על המסך
    - חיים
    - מהירות הליכה
    - טווח תקיפה
    - נזק
    - זמן המתנה בין תקיפות (cooldown)
    """

    def __init__(self, x, side):
        """
        x = מיקום התחלה בציר X
        side = "player" או "enemy"
        """
        self.side = side

        # גודל הלוחם (ניתן לכוונן ב- settings.py)
        self.width = UNIT_WIDTH
        self.height = UNIT_HEIGHT

        # כיוון הליכה: שחקן הולך ימינה, אויב הולך שמאלה
        self.dir = 1 if side == "player" else -1

        # מיקום
        self.x = x
        self.y = GROUND_Y - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # חיים
        self.max_hp = UNIT_MAX_HP
        self.hp = self.max_hp

        # מהירות הליכה (פיקסלים לשניה)
        self.speed = UNIT_SPEED

        # נתוני תקיפה (ניתנים לכוונון ב- settings.py)
        self.attack_range = UNIT_ATTACK_RANGE
        self.attack_damage = UNIT_ATTACK_DAMAGE
        self.attack_cooldown = UNIT_ATTACK_COOLDOWN  # מילישניות
        self.last_attack_time = 0

        self.alive = True
        # animation / effects
        self.attacking = False
        self.attack_anim_time = 0
        self.attack_anim_duration = UNIT_ATTACK_ANIM_DURATION
        self.attack_target_pos = None

        # brief flash when hit
        self.hit_flash_time = 0
        self.hit_flash_duration = UNIT_HIT_FLASH_DURATION

        # recoil pixels when attacking
        self.recoil_amount = UNIT_RECOIL_AMOUNT

    def is_in_range(self, other_rect):
        """
        בדיקה אם מישהו (יחידה או בסיס) נמצא בטווח התקיפה שלנו.
        """
        dist = abs(self.rect.centerx - other_rect.centerx)
        return dist <= self.attack_range

    def find_target(self, enemies, enemy_base):
        """
        מחפשת מטרה קרובה:
        קודם יחידת אויב, אם אין – בסיס אויב (אם בטווח).
        """
        closest_enemy = None
        closest_dist = 999999

        # מחפשים יחידת אויב בטווח
        for enemy in enemies:
            if not enemy.alive:
                continue
            if not self.is_in_range(enemy.rect):
                continue

            dist = abs(self.rect.centerx - enemy.rect.centerx)
            if dist < closest_dist:
                closest_dist = dist
                closest_enemy = enemy

        if closest_enemy is not None:
            return closest_enemy

        # אם אין יחידות בטווח – נבדוק אם הבסיס קרוב
        if self.is_in_range(enemy_base.rect):
            return enemy_base

        return None

    def update(self, dt, now, enemies, enemy_base, particles=None):
        """
        עדכון הלוחם:
        1) אם יש אויב קרוב -> נתקוף.
        2) אחרת -> נלך קדימה.
        dt = זמן בין פריימים במילישניות.
        now = pygame.time.get_ticks()
        """
        if not self.alive:
            return

        target = self.find_target(enemies, enemy_base)

        if target is None:
            # אין אויב קרוב -> הולכים קדימה
            dx = self.dir * self.speed * (dt / 1000.0)
            self.x += dx
            self.rect.x = int(self.x)
        else:
            # יש אויב בטווח -> תוקפים אם עבר זמן מספיק
            if now - self.last_attack_time >= self.attack_cooldown:
                self.last_attack_time = now

                # mark attack animation and apply damage
                self.attacking = True
                self.attack_anim_time = now
                # prefer target center for the visual
                try:
                    self.attack_target_pos = (target.rect.centerx, target.rect.centery - 8)
                except Exception:
                    self.attack_target_pos = None

                if isinstance(target, Unit):
                    target.hp -= self.attack_damage
                    # show hit flash on the target
                    try:
                        target.hit_flash_time = now
                    except Exception:
                        pass
                    # spawn small blood/spark particles at target
                    try:
                        if particles is not None:
                            particles.spawn_blood((target.rect.centerx, target.rect.centery))
                    except Exception:
                        pass
                    if target.hp <= 0:
                        target.alive = False
                        try:
                            if particles is not None:
                                particles.spawn_explosion((target.rect.centerx, target.rect.centery), color=(200,60,60), count=10)
                        except Exception:
                            pass
                elif isinstance(target, Base):
                    target.take_damage(self.attack_damage)
                    # spawn impact explosion and notify caller that base was hit
                    try:
                        if particles is not None:
                            particles.spawn_explosion((target.rect.centerx, target.rect.centery))
                    except Exception:
                        pass
                    # return event so Game can trigger screen shake
                    return {"base_hit": True}

        # אם אין חיים -> מת
        if self.hp <= 0:
            self.alive = False

    def draw(self, surface):
        """
        ציור הלוחם: גוף + ראש + פס חיים.
        """
        if not self.alive:
            return

        # משיכה של אנימציית התקפה (ריקו) בזמן התקיפה
        now = pygame.time.get_ticks()
        dx_offset = 0
        anim_progress = 0.0
        if self.attacking and now - self.attack_anim_time < self.attack_anim_duration:
            anim_progress = (now - self.attack_anim_time) / float(self.attack_anim_duration)
            # recoil: small backward push then return
            dx_offset = -self.dir * self.recoil_amount * (1.0 - abs(0.5 - anim_progress) * 2)
        else:
            # ensure attacking flag is reset after animation
            if self.attacking:
                self.attacking = False

        # גוף
        color = PLAYER_COLOR if self.side == "player" else ENEMY_COLOR
        draw_rect = self.rect.move(int(dx_offset), 0)
        pygame.draw.rect(surface, color, draw_rect, border_radius=5)

        # ראש
        head_radius = 10
        head_center = (draw_rect.centerx, draw_rect.top - head_radius + 4)
        pygame.draw.circle(surface, (230, 220, 200), head_center, head_radius)

        # פס חיים
        hp_ratio = self.hp / self.max_hp
        bar_w = self.width
        bar_h = 5
        bar_x = self.rect.left
        bar_y = self.rect.top - 14

        pygame.draw.rect(surface, HP_BAR_BG, (bar_x, bar_y, bar_w, bar_h))

        if hp_ratio > 0.5:
            hp_color = HP_GOOD
        elif hp_ratio > 0.25:
            hp_color = HP_MED
        else:
            hp_color = HP_BAD

        pygame.draw.rect(
            surface,
            hp_color,
            (bar_x + int(dx_offset), bar_y, int(bar_w * hp_ratio), bar_h),
        )

        # hit flash overlay
        if now - getattr(self, "hit_flash_time", 0) < getattr(self, "hit_flash_duration", 0):
            alpha = 180
            flash = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            flash.fill((220, 40, 40, alpha))
            surface.blit(flash, (draw_rect.left, draw_rect.top))

        # attack visual (slash/spark) towards target
        if self.attack_target_pos and now - self.attack_anim_time < self.attack_anim_duration:
            prog = (now - self.attack_anim_time) / float(self.attack_anim_duration)
            # line thickness peaks then fades
            thickness = int(1 + 6 * (1 - prog))
            start = (draw_rect.centerx, draw_rect.centery - 8)
            end = self.attack_target_pos
            # bright line
            color_line = (255, 240, 120)
            pygame.draw.line(surface, color_line, start, end, thickness)
            # glow at hit
            glow_alpha = int(200 * (1 - prog))
            glow_s = pygame.Surface((20, 20), pygame.SRCALPHA)
            gx, gy = end
            glow_s.fill((0, 0, 0, 0))
            pygame.draw.circle(glow_s, (255, 200, 80, glow_alpha), (10, 10), 8)
            surface.blit(glow_s, (gx - 10, gy - 10))
