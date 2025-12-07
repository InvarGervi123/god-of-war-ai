import random
import math
import pygame
from settings import WIDTH, HEIGHT, GROUND_Y


# =========================
#   מערכת חלקיקים כללית
# =========================


class Particle:
    """חלקיק אחד קטן (ניצוץ / עשן / אש וכו')."""

    def __init__(self, pos, vel, color, radius, life, fade=True, gravity=300):
        self.x, self.y = pos
        self.vx, self.vy = vel
        self.color = color
        self.radius = radius
        self.life = life  # כמה זמן נשאר (במילישניות)
        self.max_life = life
        self.fade = fade
        self.gravity = gravity  # כמה החלקיק "נופל" למטה

    def update(self, dt: int) -> None:
        """עדכון מיקום, מהירות וזמן חיים.

        dt במילישניות
        """
        t = dt / 1000.0
        self.x += self.vx * t
        self.y += self.vy * t

        # גרביטציה קלה
        self.vy += self.gravity * t

        # פחות חיים
        self.life -= dt

    def draw(self, surface: pygame.Surface) -> None:
        """ציור החלקיק כעיגול קטן עם אלפא (שקיפות)."""
        if self.life <= 0:
            return

        # חישוב אלפא (שקיפות) לפי כמה זמן נשאר
        alpha = 255
        if self.fade:
            alpha = int(255 * (self.life / max(1, self.max_life)))

        size = int(self.radius * 2)
        temp = pygame.Surface((size, size), pygame.SRCALPHA)
        c = (*self.color[:3], alpha)
        pygame.draw.circle(temp, c, (self.radius, self.radius), int(self.radius))
        surface.blit(temp, (int(self.x - self.radius), int(self.y - self.radius)))


class ParticleSystem:
    """מערכת שמחזיקה את כל החלקיקים במשחק (ניצוצות, פיצוצים, עשן וכו')."""

    def __init__(self) -> None:
        self.particles: list[Particle] = []

    # ---------- סוגי חלקיקים נוחים לשימוש ----------

    def spawn_sparks(
        self,
        pos: tuple[float, float],
        color: tuple[int, int, int] = (255, 220, 120),
        count: int = 8,
        speed: float = 180,
    ) -> None:
        """ניצוצות קטנים (ירי / פגיעה)."""
        px, py = pos
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(0.3 * speed, 1.0 * speed)
            vx = spd * math.cos(ang)
            vy = spd * math.sin(ang) * -0.5
            r = random.uniform(2, 4)
            life = random.randint(220, 620)
            self.particles.append(
                Particle((px, py), (vx, vy), color, r, life, fade=True, gravity=260)
            )

    def spawn_blood(
        self,
        pos: tuple[float, float],
        color: tuple[int, int, int] = (200, 40, 40),
        count: int = 10,
        speed: float = 120,
    ) -> None:
        """קשת חלקיקים אדומים – אפשר להשתמש כ"דם" אם תרצה."""
        px, py = pos
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(0.2 * speed, 1.0 * speed)
            vx = spd * math.cos(ang)
            vy = spd * math.sin(ang) * -0.3
            r = random.uniform(2, 5)
            life = random.randint(450, 950)
            self.particles.append(
                Particle((px, py), (vx, vy), color, r, life, fade=True, gravity=320)
            )

    def spawn_smoke(self, pos: tuple[float, float], count: int = 6) -> None:
        """עשן שעולה למעלה (אפור)."""
        px, py = pos
        for _ in range(count):
            vx = random.uniform(-20, 20)
            vy = random.uniform(-40, -10)
            r = random.uniform(8, 16)
            life = random.randint(800, 1600)
            self.particles.append(
                Particle(
                    (px, py),
                    (vx, vy),
                    (80, 80, 80),
                    r,
                    life,
                    fade=True,
                    gravity=35,
                )
            )

    def spawn_explosion(
        self,
        pos: tuple[float, float],
        color: tuple[int, int, int] = (255, 160, 60),
        count: int = 18,
    ) -> None:
        """פיצוץ – כדורים זוהרים שמתפזרים לכל הכיוונים + קצת עשן."""
        px, py = pos
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(60, 310)
            vx = spd * math.cos(ang)
            vy = spd * math.sin(ang) * -0.2
            r = random.uniform(3, 7)
            life = random.randint(520, 1100)
            self.particles.append(
                Particle((px, py), (vx, vy), color, r, life, fade=True, gravity=260)
            )

        # עשן עבה מעל הפיצוץ
        self.spawn_smoke((px, py - 10), count=8)

    def spawn_tracer(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        color: tuple[int, int, int] = (255, 240, 210),
        life: int = 130,
    ) -> None:
        """שובל ירי לאורך קו (מספר חלקיקים קטנים מאוד)."""
        sx, sy = start
        ex, ey = end
        steps = 6
        for i in range(steps + 1):
            t = i / steps
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t
            r = random.uniform(1.5, 3.0)
            self.particles.append(
                Particle((x, y), (0, 0), color, r, life, fade=True, gravity=0)
            )

    def update(self, dt: int) -> None:
        """עדכון כל החלקיקים וניקוי מתים."""
        alive: list[Particle] = []
        for p in self.particles:
            p.update(dt)
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def draw(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            p.draw(surface)


# =========================
#        רקע עתידני
# =========================


class Background:
    """רקע עתידני מלחמתי.

    מה יש פה:
    - שמיים עם גרדיאנט וכוכב/ירח גדול
    - עיר הרוסה רחוקה עם חלונות מהבהבים
    - ענני עשן/גז (פרלקסה)
    - ספינות מלחמה גדולות + דרונים קטנים
    - זרקורים שנסרקים בשמיים
    - טילים/פצצות שעפים ומשאירים שובל
    - פיצוצים רחוקים על קו האופק
    - ויגנטה כהה שמסגרת את כל התמונה
    """

    def __init__(self, particles: ParticleSystem | None = None) -> None:
        self.particles = particles

        # זמן מצטבר למטרת אנימציות (ms)
        self.time = 0

        # בסיס סטטי (גרדיאנט שמיים + עיר + כוכב/ירח)
        self.base_surface = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self._build_static_background()

        # שכבות עננים (פרלקסה)
        self.clouds: list[dict] = []
        for i in range(6):
            y = random.randint(40, HEIGHT // 2)
            speed = random.uniform(14 + i * 2.0, 26 + i * 2.8)
            w = random.randint(240, 560)
            alpha = random.randint(35, 75)
            self.clouds.append(
                {
                    "x": random.randint(-w, WIDTH),
                    "y": y,
                    "w": w,
                    "speed": speed,
                    "alpha": alpha,
                    "layer": i,
                }
            )

        # ספינות גדולות בשמיים
        self.gunships: list[dict] = []
        for _ in range(3):
            sx = random.randint(-260, WIDTH + 260)
            sy = random.randint(70, HEIGHT // 2 - 60)
            vx = random.choice([1, -1]) * random.uniform(40, 70)
            phase = random.uniform(0, 2 * math.pi)
            size = random.randint(42, 70)
            self.gunships.append(
                {"x": sx, "y": sy, "vx": vx, "phase": phase, "size": size}
            )

        # דרונים קטנים ומהירים
        self.drones: list[dict] = []
        for _ in range(6):
            sx = random.randint(-150, WIDTH + 150)
            sy = random.randint(40, HEIGHT // 2 - 40)
            vx = random.choice([1, -1]) * random.uniform(65, 130)
            self.drones.append({"x": sx, "y": sy, "vx": vx, "timer": 0})

        # זרקורים (searchlights)
        self.searchlights: list[dict] = []
        city_line_y = int(HEIGHT * 0.58)
        for _ in range(4):
            bx = random.randint(40, WIDTH - 40)
            by = city_line_y
            base_angle = random.uniform(-0.8, 0.2)
            sweep_speed = random.uniform(0.5, 0.85)
            length = random.randint(190, 260)
            width = random.randint(35, 55)
            self.searchlights.append(
                {
                    "x": bx,
                    "y": by,
                    "base_angle": base_angle,
                    "sweep_speed": sweep_speed,
                    "length": length,
                    "width": width,
                    "phase": random.uniform(0, 2 * math.pi),
                }
            )

        # מוקדי אש ועשן על האופק
        self.horizon_fires: list[dict] = []
        for _ in range(6):
            fx = random.randint(40, WIDTH - 40)
            fy = city_line_y + random.randint(10, 40)
            self.horizon_fires.append(
                {"x": fx, "y": fy, "size": random.randint(18, 30)}
            )

        # טילים / פצצות
        self.missiles: list[dict] = []
        self.next_missile_time = 1500

        # פיצוצים רחוקים על האופק
        self.next_far_explosion_time = 1200

    # ---------- בניית רקע סטטי ----------

    def _build_static_background(self) -> None:
        surf = self.base_surface

        # גרדיאנט שמיים (מלמעלה כהה לכיוון ירקרק/ערפל קרוב לאדמה)
        top_color = (6, 8, 20)
        mid_color = (20, 40, 60)
        bottom_color = (20, 90, 70)
        for y in range(HEIGHT):
            t = y / HEIGHT
            if t < 0.45:
                # בין top ל-mid
                k = t / 0.45
                r = int(top_color[0] * (1 - k) + mid_color[0] * k)
                g = int(top_color[1] * (1 - k) + mid_color[1] * k)
                b = int(top_color[2] * (1 - k) + mid_color[2] * k)
            else:
                # בין mid ל-bottom
                k = (t - 0.45) / 0.55
                r = int(mid_color[0] * (1 - k) + bottom_color[0] * k)
                g = int(mid_color[1] * (1 - k) + bottom_color[1] * k)
                b = int(mid_color[2] * (1 - k) + bottom_color[2] * k)
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

        # כוכב/ירח גדול בצד ימין
        planet_center = (int(WIDTH * 0.80), int(HEIGHT * 0.18))
        planet_radius = 86
        planet_surf = pygame.Surface((planet_radius * 2, planet_radius * 2), pygame.SRCALPHA)
        for r in range(planet_radius, 0, -1):
            alpha = int(180 * (r / planet_radius))
            color = (110, 170, 210, alpha)
            pygame.draw.circle(planet_surf, color, (planet_radius, planet_radius), r)
        surf.blit(
            planet_surf,
            (planet_center[0] - planet_radius, planet_center[1] - planet_radius),
        )

        # טבעת/הילה מסביב לכוכב
        ring = pygame.Surface((planet_radius * 4, planet_radius * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(
            ring,
            (120, 200, 230, 38),
            (0, planet_radius // 2, planet_radius * 4, planet_radius),
            2,
        )
        surf.blit(ring, (planet_center[0] - planet_radius * 2, planet_center[1] - planet_radius // 2))

        # כוכבים בשמיים
        for _ in range(120):
            sx = random.randint(0, WIDTH - 1)
            sy = random.randint(0, HEIGHT // 2)
            brightness = random.randint(150, 255)
            surf.set_at((sx, sy), (brightness, brightness, brightness))

        # קו אופק עם עיר הרוסה
        city_y = int(HEIGHT * 0.58)
        x = -60
        buildings: list[tuple[int, int, int, int]] = []
        while x < WIDTH + 80:
            w = random.randint(40, 120)
            h = random.randint(50, 150)
            b_x = x
            b_y = city_y - h
            color = (22, 24, 32)
            pygame.draw.rect(surf, color, (b_x, b_y, w, h))

            # גג שבור/משונן
            if random.random() < 0.4:
                pts = [
                    (b_x, b_y),
                    (b_x + w, b_y),
                    (b_x + w, b_y + 8),
                ]
                for i in range(0, w, 10):
                    pts.append((b_x + i, b_y + random.randint(0, 12)))
                pygame.draw.polygon(surf, color, pts)

            buildings.append((b_x, b_y, w, h))
            x += random.randint(35, 120)

        # חלונות – חלקם כבויים, חלקם דולקים (אווירה אחרי קרב)
        for (bx, by, bw, bh) in buildings:
            for i in range(0, bw, 10):
                for j in range(8, bh - 10, 14):
                    if random.random() < 0.12:
                        wx = bx + i + random.randint(0, 4)
                        wy = by + j + random.randint(0, 3)
                        if random.random() < 0.65:
                            w_color = (
                                random.randint(120, 230),
                                random.randint(90, 180),
                                random.randint(40, 120),
                            )
                        else:
                            # אש בוערת בפנים
                            w_color = (
                                random.randint(200, 255),
                                random.randint(100, 160),
                                random.randint(60, 120),
                            )
                        pygame.draw.rect(surf, w_color, (wx, wy, 4, 6))

        # שכבת עשן דקה מעל העיר כדי לחזק תחושת מלחמה
        smoke = pygame.Surface((WIDTH, HEIGHT // 3), pygame.SRCALPHA)
        for i in range(6):
            wx = random.randint(0, WIDTH - 200)
            wy = random.randint(0, smoke.get_height() - 60)
            ww = random.randint(200, 420)
            wh = random.randint(40, 120)
            alpha = random.randint(25, 60)
            pygame.draw.ellipse(
                smoke,
                (30, 40, 50, alpha),
                (wx, wy, ww, wh),
            )
        surf.blit(smoke, (0, city_y - smoke.get_height() + 40))

    # ---------- לוגיקה דינמית ----------

    def _update_clouds(self, dt: int) -> None:
        for c in self.clouds:
            layer_factor = 0.4 + c["layer"] * 0.12
            c["x"] += c["speed"] * (dt / 1000.0) * layer_factor
            if c["x"] - c["w"] > WIDTH + 60:
                c["x"] = -c["w"] - random.randint(50, 200)
                c["y"] = random.randint(40, HEIGHT // 2)

    def _update_gunships(self, dt: int) -> None:
        t = self.time / 1000.0
        for ship in self.gunships:
            ship["x"] += ship["vx"] * (dt / 1000.0)
            ship["y"] += math.sin(t * 0.45 + ship["phase"]) * 0.08 * dt

            if ship["vx"] > 0 and ship["x"] > WIDTH + 220:
                ship["x"] = -220
                ship["y"] = random.randint(60, HEIGHT // 2 - 60)
                ship["phase"] = random.uniform(0, 2 * math.pi)
            elif ship["vx"] < 0 and ship["x"] < -220:
                ship["x"] = WIDTH + 220
                ship["y"] = random.randint(60, HEIGHT // 2 - 60)
                ship["phase"] = random.uniform(0, 2 * math.pi)

            # ירי / ניצוצות מנועים
            if self.particles is not None and random.random() < 0.003:
                muzzle_x = ship["x"] + random.randint(-6, 6)
                muzzle_y = ship["y"] + random.randint(8, 18)
                self.particles.spawn_sparks(
                    (muzzle_x, muzzle_y),
                    color=(255, 200, 150),
                    count=5,
                    speed=220,
                )

    def _update_drones(self, dt: int) -> None:
        for d in self.drones:
            d["x"] += d["vx"] * (dt / 1000.0)
            d["timer"] += dt
            d["y"] += math.sin(self.time / 420.0 + d["x"] * 0.01) * 0.04 * dt

            if d["vx"] > 0 and d["x"] > WIDTH + 120:
                d["x"] = -120
                d["y"] = random.randint(40, HEIGHT // 2 - 40)
                d["timer"] = 0
            elif d["vx"] < 0 and d["x"] < -120:
                d["x"] = WIDTH + 120
                d["y"] = random.randint(40, HEIGHT // 2 - 40)
                d["timer"] = 0

            if self.particles is not None and d["timer"] > random.randint(320, 880):
                d["timer"] = 0
                self.particles.spawn_sparks(
                    (int(d["x"]), int(d["y"])),
                    color=(200, 110, 255),
                    count=3,
                    speed=90,
                )

    def _update_missiles(self, dt: int) -> None:
        # שיגור טיל חדש כל פרק זמן
        if self.time > self.next_missile_time:
            self.next_missile_time = self.time + random.randint(2200, 5200)
            if random.random() < 0.8:
                side = random.choice(["left", "right"])
                if side == "left":
                    x = -50
                    vx = random.uniform(140, 230)
                else:
                    x = WIDTH + 50
                    vx = random.uniform(-230, -140)

                y = random.randint(80, HEIGHT // 2 - 30)
                vy = random.uniform(-15, 15)
                life = random.randint(1700, 2600)
                self.missiles.append(
                    {
                        "x": x,
                        "y": y,
                        "vx": vx,
                        "vy": vy,
                        "life": life,
                        "max_life": life,
                    }
                )

        alive: list[dict] = []
        for m in self.missiles:
            t = dt / 1000.0
            m["x"] += m["vx"] * t
            m["y"] += m["vy"] * t
            m["vy"] += 28 * t
            m["life"] -= dt

            if self.particles is not None and random.random() < 0.65:
                tail_x = m["x"] - m["vx"] * 0.03
                tail_y = m["y"] - m["vy"] * 0.03
                self.particles.spawn_tracer(
                    (m["x"], m["y"]), (tail_x, tail_y), color=(255, 245, 220), life=220
                )

            # תנאי פיצוץ
            if (
                m["life"] <= 0
                or m["y"] > GROUND_Y - 30
                or m["x"] < -90
                or m["x"] > WIDTH + 90
            ):
                if self.particles is not None:
                    self.particles.spawn_explosion(
                        (m["x"], min(m["y"], GROUND_Y - 20)),
                        color=(255, 150, 95),
                        count=22,
                    )
            else:
                alive.append(m)
        self.missiles = alive

    def _update_far_explosions(self, dt: int) -> None:
        if self.particles is None:
            return
        if self.time > self.next_far_explosion_time:
            self.next_far_explosion_time = self.time + random.randint(1600, 4200)
            ex_x = random.randint(80, WIDTH - 80)
            ex_y = random.randint(int(HEIGHT * 0.48), int(HEIGHT * 0.62))
            self.particles.spawn_explosion(
                (ex_x, ex_y), color=(255, 135, 80), count=14
            )

    def update(self, dt: int) -> None:
        """עדכון כל האלמנטים הדינמיים של הרקע."""
        self.time += dt
        self._update_clouds(dt)
        self._update_gunships(dt)
        self._update_drones(dt)
        self._update_missiles(dt)
        self._update_far_explosions(dt)

    # ---------- ציור ----------

    def _draw_clouds(self, surface: pygame.Surface) -> None:
        for c in self.clouds:
            w = c["w"]
            h = 72
            cloud_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            alpha = c["alpha"]
            pygame.draw.ellipse(
                cloud_surface,
                (35, 60, 80, alpha),
                (0, 0, w, h),
            )
            surface.blit(cloud_surface, (int(c["x"]), int(c["y"])))

    def _draw_horizon_fires(self, surface: pygame.Surface) -> None:
        for f in self.horizon_fires:
            x = f["x"]
            y = f["y"]
            size = f["size"]

            flame = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            base = random.randint(170, 255)
            color = (base, int(base * 0.6), int(base * 0.3), 190)
            pygame.draw.circle(flame, color, (size, size), size)
            surface.blit(flame, (x - size, y - size))

    def _draw_searchlights(self, surface: pygame.Surface) -> None:
        light_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for s in self.searchlights:
            bx, by = s["x"], s["y"]
            base_angle = s["base_angle"]
            sweep_speed = s["sweep_speed"]
            length = s["length"]
            phase = s["phase"]

            t = self.time / 1000.0
            angle = base_angle + math.sin(t * sweep_speed + phase) * 0.55

            left_angle = angle - 0.18
            right_angle = angle + 0.18

            x1 = bx + math.cos(left_angle) * length
            y1 = by + math.sin(left_angle) * length
            x2 = bx + math.cos(right_angle) * length
            y2 = by + math.sin(right_angle) * length

            points = [(bx, by), (x1, y1), (x2, y2)]

            pygame.draw.polygon(
                light_surface,
                (220, 240, 255, 40),
                [(int(px), int(py)) for (px, py) in points],
            )
        surface.blit(light_surface, (0, 0))

    def _draw_gunships(self, surface: pygame.Surface) -> None:
        for ship in self.gunships:
            x = int(ship["x"])
            y = int(ship["y"])
            size = ship["size"]

            body_w = size
            body_h = size // 4

            body_rect = pygame.Rect(
                x - body_w // 2,
                y - body_h // 2,
                body_w,
                body_h,
            )
            pygame.draw.rect(surface, (80, 105, 145), body_rect, border_radius=9)

            bridge_rect = pygame.Rect(
                x - body_w // 4,
                y - body_h // 2 - body_h // 2,
                body_w // 2,
                body_h // 2,
            )
            pygame.draw.rect(surface, (120, 145, 195), bridge_rect, border_radius=5)

            for i in range(-body_w // 2 + 6, body_w // 2 - 4, 11):
                if random.random() < 0.6:
                    pygame.draw.rect(
                        surface,
                        (235, 225, 170),
                        (x + i, y + body_h // 4, 3, 3),
                    )

            engine = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(engine, (150, 220, 255, 210), (6, 6), 5)
            if ship["vx"] > 0:
                surface.blit(engine, (body_rect.left - 6, y - 4))
            else:
                surface.blit(engine, (body_rect.right - 6, y - 4))

    def _draw_drones(self, surface: pygame.Surface) -> None:
        for d in self.drones:
            dx = int(d["x"])
            dy = int(d["y"])

            pygame.draw.polygon(
                surface,
                (140, 140, 215),
                [(dx - 7, dy), (dx + 7, dy), (dx + 10, dy + 4), (dx - 10, dy + 4)],
            )
            pygame.draw.line(
                surface,
                (110, 110, 185),
                (dx - 12, dy + 2),
                (dx + 12, dy + 2),
                2,
            )

            glow = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(glow, (200, 120, 255, 190), (3, 3), 3)
            surface.blit(glow, (dx - 3, dy + 3))

    def _draw_missiles(self, surface: pygame.Surface) -> None:
        for m in self.missiles:
            x = int(m["x"])
            y = int(m["y"])
            alpha = max(80, int(220 * (m["life"] / max(1, m["max_life"]))))
            color = (255, 240, 210, alpha)

            missile_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(missile_surf, color, (5, 5), 4)
            surface.blit(missile_surf, (x - 5, y - 5))

    def _draw_vignette(self, surface: pygame.Surface) -> None:
        vign = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(80):
            alpha = int(95 * (i / 80))
            pygame.draw.rect(
                vign,
                (0, 0, 0, alpha),
                (i, i, WIDTH - i * 2, HEIGHT - i * 2),
                1,
            )
        surface.blit(vign, (0, 0))

    def draw(self, surface: pygame.Surface) -> None:
        """ציור הרקע השלם.

        החלקיקים עצמם (פיצוצים, ניצוצות וכו') מצוירים ע"י ParticleSystem
        מחוץ למחלקה הזו – כאן מצויר רק הרקע והאלמנטים ה"רחוקים".
        """
        surface.blit(self.base_surface, (0, 0))
        self._draw_clouds(surface)
        self._draw_horizon_fires(surface)
        self._draw_searchlights(surface)
        self._draw_gunships(surface)
        self._draw_drones(surface)
        self._draw_missiles(surface)
        self._draw_vignette(surface)
