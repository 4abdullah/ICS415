import numpy as np
import matplotlib.pyplot as plt

# Define the Sphere and Light objects
class Sphere:
    def __init__(self, center, radius, color, specular, reflective):
        self.center = np.array(center)
        self.radius = radius
        self.color = np.array(color)
        self.specular = specular
        self.reflective = reflective

class Light:
    def __init__(self, light_type, intensity, position=None, direction=None):
        self.light_type = light_type
        self.intensity = intensity
        self.position = np.array(position) if position else None
        self.direction = np.array(direction) if direction else None

# Utility functions
def reflect_ray(L, N):
    return 2 * N * np.dot(N, L) - L

def compute_lighting(P, N, V, s, lights, spheres):
    i = 0  # Accumulated intensity
    for light in lights:
        if light.light_type == "ambient":
            i += light.intensity
        else:
            # Compute light vector
            L = light.direction if light.light_type == "directional" else light.position - P
            L = L / np.linalg.norm(L)

            # Shadow check
            shadow_sphere, shadow_t = closest_intersection(P, L, 0.001, np.inf, spheres)
            if shadow_sphere is not None:
                continue

            # Diffuse reflection
            n_dot_l = np.dot(N, L)
            if n_dot_l > 0:
                i += light.intensity * n_dot_l

            # Specular reflection
            if s != -1:
                R = reflect_ray(L, N)
                r_dot_v = np.dot(R, V)
                if r_dot_v > 0:
                    i += light.intensity * (r_dot_v ** s)
    return i

def closest_intersection(O, D, t_min, t_max, spheres):
    closest_t = np.inf
    closest_sphere = None
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(O, D, sphere)
        if t_min < t1 < t_max and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if t_min < t2 < t_max and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere
    return closest_sphere, closest_t

def intersect_ray_sphere(O, D, sphere):
    CO = O - sphere.center
    a = np.dot(D, D)
    b = 2 * np.dot(CO, D)
    c = np.dot(CO, CO) - sphere.radius ** 2
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return np.inf, np.inf
    t1 = (-b + np.sqrt(discriminant)) / (2 * a)
    t2 = (-b - np.sqrt(discriminant)) / (2 * a)
    return t1, t2

# Ray tracing function with reflections
def trace_ray(O, D, t_min, t_max, spheres, lights, recursion_depth):
    closest_sphere, closest_t = closest_intersection(O, D, t_min, t_max, spheres)
    if closest_sphere is None:
        return np.array([0, 0, 0])  # Background color (white)

    # Compute intersection point and normal
    P = O + closest_t * D
    N = (P - closest_sphere.center) / np.linalg.norm(P - closest_sphere.center)
    V = -D
    local_color = closest_sphere.color * compute_lighting(P, N, V, closest_sphere.specular, lights, spheres)

    # If recursion depth is 0 or the sphere is not reflective, return local color
    r = closest_sphere.reflective
    if recursion_depth <= 0 or r <= 0:
        return local_color

    # Compute reflected color
    R = reflect_ray(-D, N)
    reflected_color = trace_ray(P, R, 0.001, np.inf, spheres, lights, recursion_depth - 1)
    return local_color * (1 - r) + reflected_color * r

# Render the scene
def render(scene, width, height, fov, recursion_depth):
    aspect_ratio = width / height
    camera = np.array([0, 0, 0])
    viewport_height = 1.0
    viewport_width = viewport_height * aspect_ratio
    image = np.zeros((height, width, 3))

    for y in range(height):
        for x in range(width):
            px = (x + 0.5) / width * viewport_width - viewport_width / 2
            py = -(y + 0.5) / height * viewport_height + viewport_height / 2
            D = np.array([px, py, 1])
            D = D / np.linalg.norm(D)
            color = trace_ray(camera, D, 1, np.inf, scene['spheres'], scene['lights'], recursion_depth)
            image[y, x] = color
    return image

# Define the scene
scene = {
    "spheres": [
        Sphere(center=(0, -1, 3), radius=1, color=(255, 0, 0), specular=500, reflective=0.2),
        Sphere(center=(2, 0, 4), radius=1, color=(0, 0, 255), specular=500, reflective=0.3),
        Sphere(center=(-2, 0, 4), radius=1, color=(0, 255, 0), specular=10, reflective=0.4),
        Sphere(center=(0, -5001, 0), radius=5000, color=(255, 255, 0), specular=1000, reflective=0.5),
    ],
    "lights": [
        Light(light_type="ambient", intensity=0.2),
        Light(light_type="point", intensity=0.6, position=(2, 1, 0)),
        Light(light_type="directional", intensity=0.2, direction=(1, 4, 4)),
    ],
}

# Render and display the image
width, height = 300, 300
fov = np.pi / 3
recursion_depth = 3  # Change this value to control the reflection depth
image = render(scene, width, height, fov, recursion_depth)
plt.imshow(image / 255)
plt.axis('off')
plt.show()
