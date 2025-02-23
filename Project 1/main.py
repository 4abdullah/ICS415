import glfw
import numpy as np
import OpenGL.GL as gl
import sys
import time
import random

def compile_shader(source, shader_type):
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        err = gl.glGetShaderInfoLog(shader)
        raise RuntimeError("Shader compile error: " + str(err))
    return shader

def create_program(vertex_source, fragment_source):
    program = gl.glCreateProgram()
    vertex_shader = compile_shader(vertex_source, gl.GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_source, gl.GL_FRAGMENT_SHADER)
    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)
    # Check link status
    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
        err = gl.glGetProgramInfoLog(program)
        raise RuntimeError("Program link error: " + str(err))
    gl.glDeleteShader(vertex_shader)
    gl.glDeleteShader(fragment_shader)
    return program

# --- Data structure for our scene ---
# materialType: 0 = Lambertian, 1 = Metal, 2 = Dielectric
class SphereData:
    def __init__(self, center, radius, materialType, albedo, fuzz=0.0, ref_idx=1.0):
        self.center = center      # (x, y, z)
        self.radius = radius      # float
        self.materialType = materialType  # int
        self.albedo = albedo      # (r, g, b)
        self.fuzz = fuzz          # float (for Metal)
        self.ref_idx = ref_idx    # float (for Dielectric)

def build_scene():
    """
    Build a scene with:
      - A ground sphere
      - Three large spheres
      - Many small random spheres (increased from 8 to 64)
    """
    spheres = []

    # 1) Ground (big sphere)
    spheres.append(SphereData(center=(0.0, -1000.0, 0.0),
                              radius=1000.0,
                              materialType=0,
                              albedo=(0.5, 0.5, 0.5)))

    # 2) Three large spheres
    #    - Middle: Dielectric (glass)
    spheres.append(SphereData(center=(0.0, 1.0, 0.0),
                              radius=1.0,
                              materialType=2,
                              albedo=(1.0, 1.0, 1.0),
                              ref_idx=1.5))
    #    - Left: Lambertian (diffuse)
    spheres.append(SphereData(center=(-4.0, 1.0, 0.0),
                              radius=1.0,
                              materialType=0,
                              albedo=(0.4, 0.2, 0.1)))
    #    - Right: Metal
    spheres.append(SphereData(center=(4.0, 1.0, 0.0),
                              radius=1.0,
                              materialType=1,
                              albedo=(0.7, 0.6, 0.5),
                              fuzz=0.0))

    # 3) Add many small random spheres (increase this count to 64)
    random.seed(time.time())  # seed randomness
    num_small_spheres = 64
    for _ in range(num_small_spheres):
        # You can adjust these ranges as needed.
        center_x = random.uniform(-8.0, 8.0)
        center_z = random.uniform(-8.0, 8.0)
        radius   = random.uniform(0.1, 0.3)
        choose_mat = random.random()

        # Lambertian
        if choose_mat < 0.6:
            albedo = (random.random() * random.random(),
                      random.random() * random.random(),
                      random.random() * random.random())
            spheres.append(SphereData(center=(center_x, radius, center_z),
                                      radius=radius,
                                      materialType=0,
                                      albedo=albedo))
        # Metal
        elif choose_mat < 0.85:
            albedo = (random.uniform(0.5,1.0),
                      random.uniform(0.5,1.0),
                      random.uniform(0.5,1.0))
            fuzz = random.uniform(0.0, 0.5)
            spheres.append(SphereData(center=(center_x, radius, center_z),
                                      radius=radius,
                                      materialType=1,
                                      albedo=albedo,
                                      fuzz=fuzz))
        # Dielectric
        else:
            spheres.append(SphereData(center=(center_x, radius, center_z),
                                      radius=radius,
                                      materialType=2,
                                      albedo=(1.0, 1.0, 1.0),
                                      ref_idx=1.5))
    return spheres

# --- Camera parameters ---
def get_camera_data(window_width, window_height):
    """
    Camera settings:
      - lookfrom: camera position
      - lookat: target point
      - vup: upward vector
      - vfov: vertical field of view (degrees)
    """
    lookfrom = np.array([13.0, 2.0, 3.0], dtype=np.float32)
    lookat   = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    vup      = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    vfov     = 30.0
    aspect_ratio = window_width / window_height
    aperture = 0.0
    focus_dist = 10.0

    theta = np.radians(vfov)
    h = np.tan(theta / 2.0)
    viewport_height = 2.0 * h
    viewport_width  = aspect_ratio * viewport_height

    w = (lookfrom - lookat)
    w = w / np.linalg.norm(w)
    u = np.cross(vup, w)
    u = u / np.linalg.norm(u)
    v = np.cross(w, u)

    origin = lookfrom
    horizontal = focus_dist * viewport_width * u
    vertical   = focus_dist * viewport_height * v
    lower_left_corner = origin - horizontal/2.0 - vertical/2.0 - focus_dist * w

    return {
        "origin": origin,
        "horizontal": horizontal,
        "vertical": vertical,
        "lower_left_corner": lower_left_corner
    }

def main():
    # Initialize GLFW
    if not glfw.init():
        print("Could not initialize GLFW")
        sys.exit(1)

    window_width, window_height = 1000, 800
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    window = glfw.create_window(window_width, window_height, "GLSL Raytracer", None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)
    glfw.make_context_current(window)

    # Load shader sources from files
    with open("vertex_shader.glsl", "r") as f:
        vertex_src = f.read()
    with open("fragment_shader.glsl", "r") as f:
        fragment_src = f.read()

    program = create_program(vertex_src, fragment_src)
    gl.glUseProgram(program)

    quad_vertices = np.array([
         # positions (x, y)
         -1.0, -1.0,
          1.0, -1.0,
         -1.0,  1.0,
         -1.0,  1.0,
          1.0, -1.0,
          1.0,  1.0,
    ], dtype=np.float32)

    vao = gl.glGenVertexArrays(1)
    vbo = gl.glGenBuffers(1)

    gl.glBindVertexArray(vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, gl.GL_STATIC_DRAW)
    pos_attrib = gl.glGetAttribLocation(program, "aPos")
    gl.glEnableVertexAttribArray(pos_attrib)
    gl.glVertexAttribPointer(pos_attrib, 2, gl.GL_FLOAT, gl.GL_FALSE, 2 * quad_vertices.itemsize, gl.ctypes.c_void_p(0))
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

    # Pass camera parameters to the shader
    cam = get_camera_data(window_width, window_height)
    loc_origin     = gl.glGetUniformLocation(program, "uCameraOrigin")
    loc_llc        = gl.glGetUniformLocation(program, "uLowerLeftCorner")
    loc_horizontal = gl.glGetUniformLocation(program, "uHorizontal")
    loc_vertical   = gl.glGetUniformLocation(program, "uVertical")

    gl.glUniform3fv(loc_origin,     1, cam["origin"])
    gl.glUniform3fv(loc_llc,        1, cam["lower_left_corner"])
    gl.glUniform3fv(loc_horizontal, 1, cam["horizontal"])
    gl.glUniform3fv(loc_vertical,   1, cam["vertical"])

    # Build the random scene
    spheres = build_scene()
    num_spheres = len(spheres)

    # Set our new maximum spheres count (here we allow up to 128)
    MAX_SPHERES = 128
    if num_spheres > MAX_SPHERES:
        print(f"Truncating sphere list from {num_spheres} to {MAX_SPHERES}")
        spheres = spheres[:MAX_SPHERES]
        num_spheres = MAX_SPHERES

    loc_numSpheres = gl.glGetUniformLocation(program, "uNumSpheres")
    gl.glUniform1i(loc_numSpheres, num_spheres)

    # Prepare arrays for uniform data
    centers = []
    radii   = []
    matTypes= []
    albedos = []
    fuzzes  = []
    refidx  = []

    for s in spheres:
        centers.extend([s.center[0], s.center[1], s.center[2]])
        radii.append(s.radius)
        matTypes.append(s.materialType)
        albedos.extend([s.albedo[0], s.albedo[1], s.albedo[2]])
        fuzzes.append(s.fuzz)
        refidx.append(s.ref_idx)

    centers = np.array(centers, dtype=np.float32)
    radii   = np.array(radii,   dtype=np.float32)
    matTypes= np.array(matTypes, dtype=np.int32)
    albedos = np.array(albedos,  dtype=np.float32)
    fuzzes  = np.array(fuzzes,   dtype=np.float32)
    refidx  = np.array(refidx,   dtype=np.float32)

    loc_center  = gl.glGetUniformLocation(program, "uSphereCenter")
    loc_radius  = gl.glGetUniformLocation(program, "uSphereRadius")
    loc_matType = gl.glGetUniformLocation(program, "uMaterialType")
    loc_albedo  = gl.glGetUniformLocation(program, "uSphereAlbedo")
    loc_fuzz    = gl.glGetUniformLocation(program, "uSphereFuzz")
    loc_refidx  = gl.glGetUniformLocation(program, "uSphereRefIdx")

    gl.glUniform3fv(loc_center,  num_spheres, centers)
    gl.glUniform1fv(loc_radius,  num_spheres, radii)
    gl.glUniform1iv(loc_matType, num_spheres, matTypes)
    gl.glUniform3fv(loc_albedo,  num_spheres, albedos)
    gl.glUniform1fv(loc_fuzz,    num_spheres, fuzzes)
    gl.glUniform1fv(loc_refidx,  num_spheres, refidx)

    # Seed for random number generation
    loc_seed = gl.glGetUniformLocation(program, "uSeed")
    gl.glUniform1f(loc_seed, time.time() % 1000)

    # Main render loop
    while not glfw.window_should_close(window):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glUseProgram(program)
        gl.glBindVertexArray(vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == '__main__':
    main()
