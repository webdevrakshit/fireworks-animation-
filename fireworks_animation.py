import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
import matplotlib.colors as mcolors

rng = np.random.default_rng(42)

fig, ax = plt.subplots(figsize=(7, 10))
ax.set_facecolor("black")
ax.set_xlim(-80, 80)
ax.set_ylim(0, 140)
ax.axis("off")

# ---- Stars ----
num_stars = 200
sx = rng.uniform(-80, 80, num_stars)
sy = rng.uniform(70, 140, num_stars)
salpha = rng.uniform(0.3, 1.0, num_stars)
ssize = rng.uniform(5, 25, num_stars)
stars = ax.scatter(sx, sy, s=ssize, color="silver", alpha=salpha)

# ---- Skyline ----
def skyline():
    x = -80
    heights = [8, 15, 10, 25, 20, 30, 12, 28, 14, 18]
    for h in heights:
        rect = plt.Rectangle((x, 0), 10, h, color="#0b0b0b")
        ax.add_patch(rect)
        x += 12
skyline()

# ---- Physics ----
gravity = -0.08
drag = 0.985
PARTICLES = 130

colors = ["#FF5733", "#FFD700", "#00FFFF", "#7FFF00",
          "#FF1493", "#1E90FF", "#FFA500", "#FF33EC"]

# ---- Rocket ----
class Rocket:
    def __init__(self):
        self.x = rng.uniform(-60, 60)
        self.y = 0
        self.vy = rng.uniform(4.0, 6.5)
        self.color = rng.choice(colors)
        self.exploded = False
        self.trail = []

    def update(self):
        self.y += self.vy
        self.vy *= 0.99

        self.trail.append((self.x, self.y - rng.uniform(0.5, 1.8)))
        if len(self.trail) > 25:
            self.trail.pop(0)

        if self.vy < 1 or self.y > rng.uniform(60, 100):
            self.exploded = True

# ---- Firework Explosion ----
class Firework:
    def __init__(self, x0, y0, color, pattern):
        self.N = PARTICLES
        self.alpha = np.ones(self.N)
        self.rgb = np.array(mcolors.to_rgb(color))
        self.pattern = pattern

        if pattern == "heart":
            t = np.linspace(0, 2*np.pi, self.N)
            self.x = x0 + 6 * (16 * np.sin(t)**3)
            self.y = y0 + 6 * (13*np.cos(t) - 5*np.cos(2*t) -
                               2*np.cos(3*t) - np.cos(4*t))
            self.vx = rng.normal(0, 0.8, self.N)
            self.vy = rng.normal(0, 0.8, self.N)

        elif pattern == "ring":
            ang = np.linspace(0, 2*np.pi, self.N)
            r = rng.uniform(10, 14)
            self.x = x0 + r * np.cos(ang)
            self.y = y0 + r * np.sin(ang)
            sp = rng.uniform(0.8, 2.5, self.N)
            self.vx = np.cos(ang) * sp
            self.vy = np.sin(ang) * sp

        elif pattern == "spiral":
            ang = np.linspace(0, 6*np.pi, self.N)
            rad = np.linspace(1, 18, self.N)
            self.x = x0 + rad * np.cos(ang)
            self.y = y0 + rad * np.sin(ang)
            self.vx = np.cos(ang)
            self.vy = np.sin(ang)

        elif pattern == "glitter":
            ang = rng.uniform(0, 2*np.pi, self.N)
            sp = rng.uniform(1, 6, self.N)
            self.x = x0 + np.cos(ang)*sp*0.2
            self.y = y0 + np.sin(ang)*sp*0.2
            self.vx = np.cos(ang)*sp
            self.vy = np.sin(ang)*sp
            self.rgb = np.array(mcolors.to_rgb("#FFD700"))

        else:  # normal
            ang = rng.uniform(0, 2*np.pi, self.N)
            sp = rng.uniform(1, 5, self.N)
            self.x = x0 + np.cos(ang)*sp*0.2
            self.y = y0 + np.sin(ang)*sp*0.2
            self.vx = np.cos(ang)*sp
            self.vy = np.sin(ang)*sp

    def update(self):
        self.vy += gravity
        self.vx *= drag
        self.vy *= drag

        self.x += self.vx * 0.12
        self.y += self.vy * 0.12
        self.alpha -= 0.012
        self.alpha = np.clip(self.alpha, 0, 1)

# ---- Graphics Objects ----
rockets = []
explosions = []

rocket_sc = ax.scatter([], [], color="white", s=30)
trail_sc = ax.scatter([], [], s=15, color="white", alpha=0.6)
smoke_sc = ax.scatter([], [], s=10, color="#666666", alpha=0.5)
particle_sc = ax.scatter([], [], s=25)

# ---- Animation ----
def animate(i):
    # twinkle stars
    tw = 0.25*np.sin(i*0.1 + np.arange(num_stars))
    stars.set_alpha(np.clip(salpha + tw, 0.2, 1))

    # launch rockets
    if rng.random() < 0.06:
        rockets.append(Rocket())

    # rocket lists
    rx, ry = [], []
    tx, ty = [], []
    sx, sy = [], []
    sal = []

    new_expl = []

    # update rockets
    for r in rockets[:]:
        r.update()
        if r.exploded:
            rockets.remove(r)
            pattern = rng.choice(
                ["normal", "ring", "spiral", "heart", "glitter"],
                p=[0.45, 0.2, 0.15, 0.12, 0.08]
            )
            new_expl.append(Firework(r.x, r.y, r.color, pattern))
        else:
            rx.append(r.x)
            ry.append(r.y)

        # trails
        for (tx0, ty0) in r.trail:
            tx.append(tx0 + rng.normal(0, 0.1))
            ty.append(ty0)
            sx.append(tx0 + rng.normal(0, 0.8))
            sy.append(ty0 + rng.normal(0, 0.8))
            sal.append(0.4)

    # update explosions
    px, py = [], []
    colors_rgba = []
    for fw in explosions[:]:
        fw.update()
        if fw.alpha.max() <= 0:
            explosions.remove(fw)
            continue

        px.extend(fw.x)
        py.extend(fw.y)

        a = fw.alpha
        rgb = fw.rgb

        rgba = np.zeros((fw.N, 4))
        rgba[:, :3] = rgb
        rgba[:, 3] = a
        colors_rgba.append(rgba)

    explosions.extend(new_expl)

    # combine all explosion RGBA
    if colors_rgba:
        all_rgba = np.vstack(colors_rgba)
        particle_sc.set_offsets(np.column_stack((px, py)))
        particle_sc.set_facecolor(all_rgba)
    else:
        particle_sc.set_offsets(np.empty((0, 2)))
        particle_sc.set_facecolor([])

    # trails
    if tx:
        trail_sc.set_offsets(np.column_stack((tx, ty)))
    else:
        trail_sc.set_offsets(np.empty((0, 2)))

    # smoke
    if sx:
        smoke_sc.set_offsets(np.column_stack((sx, sy)))
        smoke_sc.set_alpha(0.4)
    else:
        smoke_sc.set_offsets(np.empty((0, 2)))
        smoke_sc.set_alpha(0.4)   # SAFE value

    # rockets
    rocket_sc.set_offsets(np.column_stack((rx, ry)) if rx else np.empty((0,2)))

    return particle_sc, rocket_sc, trail_sc, smoke_sc

# Display animation
ani = FuncAnimation(fig, animate, frames=500, interval=40)
HTML(ani.to_jshtml())
