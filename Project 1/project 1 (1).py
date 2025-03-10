#!/usr/bin/env python3
import math
import random
import sys
import concurrent.futures
import numpy as np
from PIL import Image

#########################
# Utility Functions
#########################
def random_double():
    return random.random()

def random_double_range(min_val, max_val):
    return random.uniform(min_val, max_val)

def clamp(x, min_val, max_val):
    if x < min_val:
        return min_val
    if x > max_val:
        return max_val
    return x

#########################
# Vec3 Class and Functions
#########################
class Vec3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"{self.x} {self.y} {self.z}"

    def __add__(self, other):
        return Vec3(self.x + other.x,
                    self.y + other.y,
                    self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x,
                    self.y - other.y,
                    self.z - other.z)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    # Supports scalar multiplication or elementwise multiplication (needed for albedo)
    def __mul__(self, t):
        if isinstance(t, (int, float)):
            return Vec3(self.x * t, self.y * t, self.z * t)
        elif isinstance(t, Vec3):
            return Vec3(self.x * t.x, self.y * t.y, self.z * t.z)
        else:
            raise NotImplementedError("Multiplication not implemented for this type")

    def __rmul__(self, t):
        return self.__mul__(t)

    def __truediv__(self, t):
        return self * (1 / t)

    def length(self):
        return math.sqrt(self.length_squared())

    def length_squared(self):
        return self.x * self.x + self.y * self.y + self.z * self.z

    def unit(self):
        return self / self.length()

    def near_zero(self):
        s = 1e-8
        return (abs(self.x) < s) and (abs(self.y) < s) and (abs(self.z) < s)

    @staticmethod
    def random():
        return Vec3(random_double(), random_double(), random_double())

    @staticmethod
    def random_range(min_val, max_val):
        return Vec3(random_double_range(min_val, max_val),
                    random_double_range(min_val, max_val),
                    random_double_range(min_val, max_val))

def dot(u, v):
    return u.x * v.x + u.y * v.y + u.z * v.z

def cross(u, v):
    return Vec3(u.y * v.z - u.z * v.y,
                u.z * v.x - u.x * v.z,
                u.x * v.y - u.y * v.x)

def reflect(v, n):
    return v - 2 * dot(v, n) * n

def refract(uv, n, etai_over_etat):
    cos_theta = dot(-uv, n)
    r_out_parallel = etai_over_etat * (uv + cos_theta * n)
    r_out_perp = -math.sqrt(abs(1.0 - r_out_parallel.length_squared())) * n
    return r_out_parallel + r_out_perp

def random_in_unit_sphere():
    while True:
        p = Vec3.random_range(-1, 1)
        if p.length_squared() >= 1:
            continue
        return p

def random_unit_vector():
    a = random_double_range(0, 2 * math.pi)
    z = random_double_range(-1, 1)
    r = math.sqrt(1 - z * z)
    return Vec3(r * math.cos(a), r * math.sin(a), z)

def random_in_unit_disk():
    while True:
        p = Vec3(random_double_range(-1, 1), random_double_range(-1, 1), 0)
        if p.length_squared() >= 1:
            continue
        return p

def schlick(cosine, ref_idx):
    r0 = (1 - ref_idx) / (1 + ref_idx)
    r0 = r0 * r0
    return r0 + (1 - r0) * ((1 - cosine) ** 5)

#########################
# Ray Class
#########################
class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def at(self, t):
        return self.origin + self.direction * t

#########################
# Hit Record and Hittable Objects
#########################
class HitRecord:
    def __init__(self, p=None, normal=None, t=0, front_face=True, material=None):
        self.p = p
        self.normal = normal
        self.t = t
        self.front_face = front_face
        self.material = material

    def set_face_normal(self, ray, outward_normal):
        self.front_face = dot(ray.direction, outward_normal) < 0
        self.normal = outward_normal if self.front_face else -outward_normal

class Hittable:
    def hit(self, ray, t_min, t_max):
        pass

class Sphere(Hittable):
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def hit(self, ray, t_min, t_max):
        oc = ray.origin - self.center
        a = ray.direction.length_squared()
        half_b = dot(oc, ray.direction)
        c = oc.length_squared() - self.radius * self.radius
        discriminant = half_b * half_b - a * c
        if discriminant < 0:
            return None
        sqrtd = math.sqrt(discriminant)

        root = (-half_b - sqrtd) / a
        if root < t_min or root > t_max:
            root = (-half_b + sqrtd) / a
            if root < t_min or root > t_max:
                return None

        rec = HitRecord()
        rec.t = root
        rec.p = ray.at(rec.t)
        outward_normal = (rec.p - self.center) / self.radius
        rec.set_face_normal(ray, outward_normal)
        rec.material = self.material
        return rec

class HittableList(Hittable):
    def __init__(self):
        self.objects = []

    def add(self, obj):
        self.objects.append(obj)

    def hit(self, ray, t_min, t_max):
        hit_anything = None
        closest_so_far = t_max
        for obj in self.objects:
            rec = obj.hit(ray, t_min, closest_so_far)
            if rec is not None:
                closest_so_far = rec.t
                hit_anything = rec
        return hit_anything

#########################
# Materials
#########################
class Material:
    def scatter(self, ray_in, hit_record):
        pass

class Lambertian(Material):
    def __init__(self, albedo):
        self.albedo = albedo

    def scatter(self, ray_in, hit_record):
        scatter_direction = hit_record.normal + random_unit_vector()
        if scatter_direction.near_zero():
            scatter_direction = hit_record.normal
        scattered = Ray(hit_record.p, scatter_direction)
        attenuation = self.albedo
        return (True, scattered, attenuation)

class Metal(Material):
    def __init__(self, albedo, fuzz):
        self.albedo = albedo
        self.fuzz = fuzz if fuzz < 1 else 1

    def scatter(self, ray_in, hit_record):
        reflected = reflect(ray_in.direction.unit(), hit_record.normal)
        scattered = Ray(hit_record.p, reflected + self.fuzz * random_in_unit_sphere())
        attenuation = self.albedo
        if dot(scattered.direction, hit_record.normal) > 0:
            return (True, scattered, attenuation)
        return (False, None, None)

class Dielectric(Material):
    def __init__(self, ref_idx):
        self.ref_idx = ref_idx

    def scatter(self, ray_in, hit_record):
        attenuation = Vec3(1.0, 1.0, 1.0)
        etai_over_etat = (1.0 / self.ref_idx) if hit_record.front_face else self.ref_idx

        unit_direction = ray_in.direction.unit()
        cos_theta = min(dot(-unit_direction, hit_record.normal), 1.0)
        sin_theta = math.sqrt(1.0 - cos_theta * cos_theta)

        if etai_over_etat * sin_theta > 1.0 or schlick(cos_theta, etai_over_etat) > random_double():
            direction = reflect(unit_direction, hit_record.normal)
        else:
            direction = refract(unit_direction, hit_record.normal, etai_over_etat)
        scattered = Ray(hit_record.p, direction)
        return (True, scattered, attenuation)

#########################
# Camera Class
#########################
class Camera:
    def __init__(self, lookfrom, lookat, vup, vfov, aspect_ratio, aperture, focus_dist):
        theta = math.radians(vfov)
        h = math.tan(theta / 2)
        viewport_height = 2.0 * h
        viewport_width = aspect_ratio * viewport_height

        self.w = (lookfrom - lookat).unit()
        self.u = cross(vup, self.w).unit()
        self.v = cross(self.w, self.u)

        self.origin = lookfrom
        self.horizontal = focus_dist * viewport_width * self.u
        self.vertical = focus_dist * viewport_height * self.v
        self.lower_left_corner = (self.origin - self.horizontal / 2 -
                                  self.vertical / 2 - focus_dist * self.w)
        self.lens_radius = aperture / 2

    def get_ray(self, s, t):
        rd = self.lens_radius * random_in_unit_disk()
        offset = self.u * rd.x + self.v * rd.y
        return Ray(self.origin,
                   self.lower_left_corner + s * self.horizontal + t * self.vertical - self.origin - offset)

#########################
# Ray Color Function
#########################
def ray_color(ray, world, depth):
    if depth <= 0:
        return Vec3(0, 0, 0)
    rec = world.hit(ray, 0.001, float('inf'))
    if rec:
        scatter_success, scattered, attenuation = rec.material.scatter(ray, rec)
        if scatter_success:
            return attenuation * ray_color(scattered, world, depth - 1)
        return Vec3(0, 0, 0)
    unit_direction = ray.direction.unit()
    t = 0.5 * (unit_direction.y + 1.0)
    return (1.0 - t) * Vec3(1.0, 1.0, 1.0) + t * Vec3(0.5, 0.7, 1.0)

#########################
# Scene Builder
#########################
def random_scene():
    world = HittableList()
    # Ground
    ground_material = Lambertian(Vec3(0.5, 0.5, 0.5))
    world.add(Sphere(Vec3(0, -1000, 0), 1000, ground_material))

    # Many small spheres
    for a in range(-11, 11):
        for b in range(-11, 11):
            choose_mat = random_double()
            center = Vec3(a + 0.9 * random_double(), 0.2, b + 0.9 * random_double())
            if (center - Vec3(4, 0.2, 0)).length() > 0.9:
                if choose_mat < 0.8:
                    # Diffuse
                    albedo = Vec3.random() * Vec3.random()
                    sphere_material = Lambertian(albedo)
                    world.add(Sphere(center, 0.2, sphere_material))
                elif choose_mat < 0.95:
                    # Metal
                    albedo = Vec3.random_range(0.5, 1)
                    fuzz = random_double_range(0, 0.5)
                    sphere_material = Metal(albedo, fuzz)
                    world.add(Sphere(center, 0.2, sphere_material))
                else:
                    # Glass
                    sphere_material = Dielectric(1.5)
                    world.add(Sphere(center, 0.2, sphere_material))

    # Three large spheres
    material1 = Dielectric(1.5)              # Middle ball (glass)
    world.add(Sphere(Vec3(0, 1, 0), 1.0, material1))
    material2 = Lambertian(Vec3(0.4, 0.2, 0.1))  # Left ball (diffuse)
    world.add(Sphere(Vec3(-4, 1, 0), 1.0, material2))
    material3 = Metal(Vec3(0.7, 0.6, 0.5), 0.0)    # Right ball (metal)
    world.add(Sphere(Vec3(4, 1, 0), 1.0, material3))
    return world

#########################
# Globals for Parallel Processing
#########################
# These globals are set in the initializer of the ProcessPoolExecutor.
GLOBAL_IMAGE_WIDTH = None
GLOBAL_IMAGE_HEIGHT = None
GLOBAL_SAMPLES_PER_PIXEL = None
GLOBAL_MAX_DEPTH = None
GLOBAL_CAM = None
GLOBAL_WORLD = None

def init_globals(image_width, image_height, samples_per_pixel, max_depth, cam, world):
    global GLOBAL_IMAGE_WIDTH, GLOBAL_IMAGE_HEIGHT, GLOBAL_SAMPLES_PER_PIXEL, GLOBAL_MAX_DEPTH, GLOBAL_CAM, GLOBAL_WORLD
    GLOBAL_IMAGE_WIDTH = image_width
    GLOBAL_IMAGE_HEIGHT = image_height
    GLOBAL_SAMPLES_PER_PIXEL = samples_per_pixel
    GLOBAL_MAX_DEPTH = max_depth
    GLOBAL_CAM = cam
    GLOBAL_WORLD = world

#########################
# Worker Function: Render a Single Scanline
#########################
def render_scanline(j):
    """Compute and return the list of pixel values for scanline j.
       j is in [0, image_height-1], where 0 is the bottom scanline."""
    scanline_pixels = []
    for i in range(GLOBAL_IMAGE_WIDTH):
        pixel_color = Vec3(0, 0, 0)
        for s in range(GLOBAL_SAMPLES_PER_PIXEL):
            u = (i + random_double()) / (GLOBAL_IMAGE_WIDTH - 1)
            v = (j + random_double()) / (GLOBAL_IMAGE_HEIGHT - 1)
            r = GLOBAL_CAM.get_ray(u, v)
            pixel_color += ray_color(r, GLOBAL_WORLD, GLOBAL_MAX_DEPTH)
        scale = 1.0 / GLOBAL_SAMPLES_PER_PIXEL
        r_val = math.sqrt(pixel_color.x * scale)
        g_val = math.sqrt(pixel_color.y * scale)
        b_val = math.sqrt(pixel_color.z * scale)
        ir = int(256 * clamp(r_val, 0.0, 0.999))
        ig = int(256 * clamp(g_val, 0.0, 0.999))
        ib = int(256 * clamp(b_val, 0.0, 0.999))
        scanline_pixels.append((ir, ig, ib))
    return j, scanline_pixels

#########################
# Main Rendering Function
#########################
def main():
    # Image settings
    image_width = 400
    image_height = 200
    samples_per_pixel = 50
    max_depth = 50

    # Build the world
    world = random_scene()

    # Camera settings
    lookfrom = Vec3(13, 2, 3)
    lookat = Vec3(0, 0, 0)
    vup = Vec3(0, 1, 0)
    dist_to_focus = 10.0
    aperture = 0.0
    cam = Camera(lookfrom, lookat, vup, 20, image_width / image_height, aperture, dist_to_focus)

    # Prepare for parallel rendering
    scanlines = list(range(image_height))  # j in [0, image_height-1], 0 = bottom
    results = {}
    total_scanlines = image_height

    # Use ProcessPoolExecutor for parallel processing.
    with concurrent.futures.ProcessPoolExecutor(initializer=init_globals,
                                                initargs=(image_width, image_height, samples_per_pixel, max_depth, cam, world)) as executor:
        futures = {executor.submit(render_scanline, j): j for j in scanlines}
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            j, scanline_data = future.result()
            results[j] = scanline_data
            completed += 1
            # Progress tracker printed to stderr.
            print(f"Progress: {completed}/{total_scanlines} scanlines rendered", file=sys.stderr)

    # Assemble the image. Our workers produced scanlines where j=0 is the bottom.
    # Image arrays usually have row 0 at the top. So we flip the order.
    image_array = np.zeros((image_height, image_width, 3), dtype=np.uint8)
    for j in range(image_height):
        # Flip vertically: row (image_height-1 - j) gets scanline j.
        image_array[image_height - 1 - j, :] = np.array(results[j], dtype=np.uint8)

    # Create and save the PNG image using Pillow.
    img = Image.fromarray(image_array, 'RGB')
    img.save("outputcompleteee.png")
    print("Rendered image saved as outputcompleteee.png", file=sys.stderr)

if __name__ == '__main__':
    main()
