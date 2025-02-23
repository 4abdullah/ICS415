#version 330 core

out vec4 FragColor;
in vec2 TexCoords;

// Camera uniforms
uniform vec3 uCameraOrigin;
uniform vec3 uLowerLeftCorner;
uniform vec3 uHorizontal;
uniform vec3 uVertical;

// Scene uniforms (increased array sizes for more spheres)
uniform int uNumSpheres;
uniform vec3 uSphereCenter[128];
uniform float uSphereRadius[128];
uniform int   uMaterialType[128];  // 0 = Lambertian, 1 = Metal, 2 = Dielectric
uniform vec3  uSphereAlbedo[128];
uniform float uSphereFuzz[128];
uniform float uSphereRefIdx[128];

// Random seed
uniform float uSeed;

const int MAX_DEPTH = 50;
const int SAMPLES = 25;  // Adjust this for anti-aliasing (more samples = less noise)

// -----------------------------------------------------------------------------
// Pseudo-random generator
float rand(vec2 co)
{
    highp float a = 12.9898;
    highp float b = 78.233;
    highp float c = 43758.5453;
    highp float dt = dot(co, vec2(a, b));
    return fract(sin(dt + uSeed) * c);
}

// Return a random point inside a unit sphere
vec3 random_in_unit_sphere(vec2 seed)
{
    vec3 p;
    do {
        p = 2.0 * vec3(rand(seed + vec2(1.0,0.0)),
                       rand(seed + vec2(0.0,1.0)),
                       rand(seed + vec2(1.0,1.0))) - vec3(1.0);
        seed += vec2(1.0);
    } while(dot(p, p) >= 1.0);
    return p;
}

// -----------------------------------------------------------------------------
vec3 reflect_vec(vec3 v, vec3 n)
{
    return v - 2.0 * dot(v, n) * n;
}

bool refract_vec(vec3 v, vec3 n, float ni_over_nt, out vec3 refracted)
{
    float dt = dot(v, n);
    float discriminant = 1.0 - ni_over_nt * ni_over_nt * (1.0 - dt * dt);
    if(discriminant > 0.0) {
        refracted = ni_over_nt * (v - n * dt) - n * sqrt(discriminant);
        return true;
    }
    return false;
}

float schlick(float cosine, float ref_idx)
{
    float r0 = (1.0 - ref_idx) / (1.0 + ref_idx);
    r0 = r0 * r0;
    return r0 + (1.0 - r0) * pow((1.0 - cosine), 5.0);
}

struct Ray {
    vec3 origin;
    vec3 direction;
};

Ray make_ray(vec3 o, vec3 d)
{
    Ray r;
    r.origin = o;
    r.direction = d;
    return r;
}

Ray get_ray(float s, float t)
{
    Ray r;
    r.origin = uCameraOrigin;
    r.direction = normalize(uLowerLeftCorner + s * uHorizontal + t * uVertical - uCameraOrigin);
    return r;
}

struct HitRecord {
    float t;
    vec3 p;
    vec3 normal;
    int material;
    vec3 albedo;
    float fuzz;
    float ref_idx;
    bool front_face;
};

void set_face_normal(in Ray r, in vec3 outward_normal, inout HitRecord rec)
{
    rec.front_face = dot(r.direction, outward_normal) < 0.0;
    rec.normal = rec.front_face ? outward_normal : -outward_normal;
}

bool hit_sphere(Ray r, int i, float t_min, float t_max, out HitRecord rec)
{
    vec3 oc = r.origin - uSphereCenter[i];
    float a = dot(r.direction, r.direction);
    float half_b = dot(oc, r.direction);
    float c = dot(oc, oc) - uSphereRadius[i] * uSphereRadius[i];
    float discriminant = half_b * half_b - a * c;
    if(discriminant < 0.0)
        return false;

    float sqrtd = sqrt(discriminant);
    float root = (-half_b - sqrtd) / a;
    if(root < t_min || root > t_max) {
        root = (-half_b + sqrtd) / a;
        if(root < t_min || root > t_max)
            return false;
    }

    rec.t = root;
    rec.p = r.origin + rec.t * r.direction;
    vec3 outward_normal = (rec.p - uSphereCenter[i]) / uSphereRadius[i];
    set_face_normal(r, outward_normal, rec);
    rec.material = uMaterialType[i];
    rec.albedo   = uSphereAlbedo[i];
    rec.fuzz     = uSphereFuzz[i];
    rec.ref_idx  = uSphereRefIdx[i];
    return true;
}

bool hit_world(Ray r, float t_min, float t_max, out HitRecord rec)
{
    bool hit_anything = false;
    float closest_so_far = t_max;
    HitRecord tempRec;
    for(int i = 0; i < uNumSpheres; i++) {
        if(hit_sphere(r, i, t_min, closest_so_far, tempRec)) {
            hit_anything = true;
            closest_so_far = tempRec.t;
            rec = tempRec;
        }
    }
    return hit_anything;
}

vec3 ray_color(Ray r, vec2 seed)
{
    vec3 attenuation = vec3(1.0);

    for(int bounce = 0; bounce < MAX_DEPTH; bounce++)
    {
        HitRecord rec;
        if(hit_world(r, 0.001, 1e8, rec))
        {
            if(rec.material == 0)
            {
                // Lambertian
                vec3 scatter_direction = rec.normal + normalize(random_in_unit_sphere(seed + vec2(float(bounce))));
                if(length(scatter_direction) < 0.001)
                    scatter_direction = rec.normal;
                r = make_ray(rec.p, normalize(scatter_direction));
                attenuation *= rec.albedo;
            }
            else if(rec.material == 1)
            {
                // Metal
                vec3 reflected = reflect_vec(normalize(r.direction), rec.normal);
                vec3 fuzz_vec = rec.fuzz * random_in_unit_sphere(seed + vec2(float(bounce)));
                r = make_ray(rec.p, normalize(reflected + fuzz_vec));
                if(dot(r.direction, rec.normal) <= 0.0)
                    return attenuation * vec3(0.0);
                attenuation *= rec.albedo;
            }
            else if(rec.material == 2)
            {
                // Dielectric
                float refraction_ratio = rec.front_face ? (1.0 / rec.ref_idx) : rec.ref_idx;
                vec3 unit_direction = normalize(r.direction);
                float cos_theta = min(dot(-unit_direction, rec.normal), 1.0);
                float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
                bool cannot_refract = (refraction_ratio * sin_theta > 1.0);
                vec3 direction;
                if(cannot_refract || schlick(cos_theta, rec.ref_idx) > rand(seed + vec2(float(bounce))))
                    direction = reflect_vec(unit_direction, rec.normal);
                else {
                    vec3 refracted;
                    if(refract_vec(unit_direction, rec.normal, refraction_ratio, refracted))
                        direction = refracted;
                    else
                        direction = reflect_vec(unit_direction, rec.normal);
                }
                r = make_ray(rec.p, normalize(direction));
                attenuation *= rec.albedo;
            }
        }
        else
        {
            // Background color gradient
            vec3 unit_direction = normalize(r.direction);
            float t = 0.5 * (unit_direction.y + 1.0);
            vec3 background = mix(vec3(1.0), vec3(0.5, 0.7, 1.0), t);
            return attenuation * background;
        }
    }
    return vec3(0.0);
}

void main()
{
    vec3 finalColor = vec3(0.0);
    for(int s = 0; s < SAMPLES; s++)
    {
        float u = TexCoords.x + (rand(TexCoords + vec2(float(s))) - 0.5) / 800.0;
        float v = TexCoords.y + (rand(TexCoords + vec2(float(s+10))) - 0.5) / 600.0;
        Ray r = get_ray(u, v);
        finalColor += ray_color(r, TexCoords + vec2(float(s)*1.234));
    }
    finalColor /= float(SAMPLES);
    finalColor = sqrt(finalColor); // Gamma correction (gamma=2.0)
    FragColor = vec4(finalColor, 1.0);
}
