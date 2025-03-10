import numpy as np
from PIL import Image

# Image dimensions
WIDTH, HEIGHT = 500, 500

# Sphere class
class Sphere:
    def __init__(self, center, radius, color):
        self.center = np.array(center)
        self.radius = radius
        self.color = np.array(color)
    
    def intersect(self, origin, direction):
        # Solve t^2*d.d + 2*d.(o-c) + (o-c).(o-c) - R^2 = 0
        oc = origin - self.center
        a = np.dot(direction, direction)
        b = 2.0 * np.dot(oc, direction)
        c = np.dot(oc, oc) - self.radius**2
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            return False, None
        t1 = (-b - np.sqrt(discriminant)) / (2*a)
        t2 = (-b + np.sqrt(discriminant)) / (2*a)
        if t1 > 0:
            return True, t1
        if t2 > 0:
            return True, t2
        return False, None

# Ray tracing function
def trace_ray(origin, direction, spheres):
    closest_t = float('inf')
    closest_sphere = None
    for sphere in spheres:
        hit, t = sphere.intersect(origin, direction)
        if hit and t < closest_t:
            closest_t = t
            closest_sphere = sphere
    if closest_sphere is None:
        return np.array([255, 255, 255])  # Background color (white)
    return closest_sphere.color

# Main rendering function
def render():
    camera = np.array([0, 0, 0])  # Camera position
    viewport_size = 1
    projection_plane_z = 1
    aspect_ratio = WIDTH / HEIGHT
    image = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    # Spheres in the scene
    spheres = [
        Sphere([0, -1, 3], 1, [255, 0, 0]),   # Red sphere
        Sphere([2, 0, 4], 1, [0, 0, 255]),   # Blue sphere
        Sphere([-2, 0, 4], 1, [0, 255, 0])   # Green sphere
    ]

    for x in range(WIDTH):
        for y in range(HEIGHT):
            # Convert pixel to viewport coordinates
            px = (x - WIDTH / 2) * viewport_size / WIDTH
            py = -(y - HEIGHT / 2) * viewport_size / WIDTH / aspect_ratio
            direction = np.array([px, py, projection_plane_z])
            direction = direction / np.linalg.norm(direction)  # Normalize the direction
            color = trace_ray(camera, direction, spheres)
            image[y, x] = color

    return image

# Save the rendered image
if __name__ == "__main__":
    image = render()
    img = Image.fromarray(image, 'RGB')
    img.save('rendered_scene.png')
    img.show()
