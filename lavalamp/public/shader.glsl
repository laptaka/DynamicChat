uniform float u_time;
uniform vec2 u_resolution;
uniform float u_seed;
uniform vec3 u_blob_color_center;
uniform vec3 u_blob_color_edge;
uniform vec3 u_bg_color;


float rand(int i) {
    return sin(float(i) * u_seed);
}

vec4 get_blob(int i, float time) {
    float spd = .25;
    float move_range = .5;
    float x = float(i);

    vec2 center = vec2(.5, .5) + .1 * vec2(rand(i), rand(i + 42));
    center += move_range * vec2(sin(spd * time * rand(i + 2)) * rand(i + 56), -sin(spd * time) * rand(i * 9));
    
    float base_radius = .2 * abs(rand(i + 3));
    float radius = base_radius * (0.5 + 0.5 * sin(0.3 * time + rand(i + 100)));
    float aspect_ratio = 1.0 + 0.05 * sin(0.5 * time + rand(i + 4));
    
    return vec4(center.xy, radius, aspect_ratio);
}

void main() {
    
    vec3 blob_color_center = u_blob_color_center;
    vec3 blob_color_edge = u_blob_color_edge;
    
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    float aspect = u_resolution.y / u_resolution.x;
    uv.y *= aspect;

    vec3 bg_col_top = u_bg_color;
    vec3 bg_col_bottom = u_bg_color * 0.3;

    vec3 bg_col = bg_col_top * (gl_FragCoord.y / u_resolution.y) + bg_col_bottom * (2.0 - (gl_FragCoord.y / u_resolution.y));

    int num_blobs = 10;
    float thresh = 3000.0;

    float dist_sum = 0.0;
    
    for (int i = 0; i < num_blobs; i++) {
        vec4 blob = get_blob(i, u_time);
        float radius = blob.z;
        float blob_aspect = blob.w;
        vec2 center = blob.xy;
        center.y *= aspect;

        vec2 dist_to_center_vec = (center - uv) * vec2(blob_aspect, 1.0);
        float dist_to_center = max(length(dist_to_center_vec) + radius / 2.0, 0.0);

        float tmp = (dist_to_center * dist_to_center);
        dist_sum += 1.0 / (tmp * tmp);
    }

    gl_FragColor = vec4(bg_col, 1.0);

    if (dist_sum > thresh) {
        gl_FragColor = vec4(blob_color_center, 1.0);
    } else if (dist_sum > thresh * 0.5) {
        gl_FragColor = vec4(blob_color_edge, 1.0);
    }
}
