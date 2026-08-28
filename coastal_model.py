import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

g = 9.81
nx, ny = 120, 80
dx = dy = 1000.0
dt = 8.0
nt = 1000

x = np.arange(nx) * dx / 1000.0
y = np.arange(ny) * dy / 1000.0
X, Y = np.meshgrid(x, y)

# Idealised coastline and bathymetry
coast = 15 + 5 * np.sin(Y[:, 0] / 10)
H = np.zeros((ny, nx))

for j in range(ny):
    for i in range(nx):
        distance = X[j, i] - coast[j]
        if distance > 0:
            H[j, i] = 5 + 0.4 * distance

ocean = H > 0

# Sea-surface height and depth-averaged velocity
eta = np.zeros((ny, nx))
u = np.zeros((ny, nx))
v = np.zeros((ny, nx))

# Initial offshore sea-level disturbance
x0, y0 = 80, 40
eta += 0.8 * np.exp(-((X-x0)**2 / 200 + (Y-y0)**2 / 150))
eta[~ocean] = 0

history = []

for n in range(nt):

    # Sea-surface pressure gradient
    deta_dx = np.gradient(eta, dx, axis=1)
    deta_dy = np.gradient(eta, dy, axis=0)

    # Momentum equations
    u -= g * dt * deta_dx
    v -= g * dt * deta_dy

    # Simple friction
    friction = 0.0005
    u *= 1 - friction
    v *= 1 - friction
    u[~ocean] = 0
    v[~ocean] = 0

    # Depth-integrated water transport
    Hu = H * u
    Hv = H * v

    dHu_dx = np.gradient(Hu, dx, axis=1)
    dHv_dy = np.gradient(Hv, dy, axis=0)

    # Continuity equation
    eta -= dt * (dHu_dx + dHv_dy)
    eta[~ocean] = 0

    # Crude eastern open-boundary damping
    eta[:, -1] *= 0.98
    u[:, -1] *= 0.98
    v[:, -1] *= 0.98

    if n % 10 == 0:
        history.append((eta.copy(), u.copy(), v.copy()))

fig, ax = plt.subplots(figsize=(11, 6))

def update(frame):
    ax.clear()
    eta_now, u_now, v_now = history[frame]

    ax.contourf(
        X, Y, eta_now,
        levels=np.linspace(-0.8, 0.8, 31),
        cmap="RdBu_r", extend="both"
    )

    ax.contourf(
        X, Y, (~ocean).astype(int),
        levels=[0.5, 1.5], colors=["tan"]
    )

    skip = 6
    ax.quiver(
        X[::skip, ::skip], Y[::skip, ::skip],
        u_now[::skip, ::skip], v_now[::skip, ::skip],
        color="black", scale=5
    )

    ax.set_title(
        f"2-D Coastal Shallow-Water Model | "
        f"time = {frame*10*dt/60:.1f} min"
    )
    ax.set_xlabel("East-West distance (km)")
    ax.set_ylabel("North-South distance (km)")
    ax.set_xlim(0, x.max())
    ax.set_ylim(0, y.max())

ani = FuncAnimation(fig, update, frames=len(history), interval=80)
ani.save("figures/coastal_model.gif", writer="pillow", fps=10)
print("Saved figures/coastal_model.gif")
