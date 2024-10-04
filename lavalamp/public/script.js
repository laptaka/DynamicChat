async function loadShader(url) {
  const response = await fetch(url);
  return await response.text();
}



// Initialize the scene, camera, and renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
let renderer;

const canvas = document.createElement('canvas');
const context = canvas.getContext('webgl2');
renderer = new THREE.WebGLRenderer({
  alpha: true,
  antialias: true,
  stencilBuffer: true,
  canvas: canvas,
  context: context
});

renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);


let r = 245
let g = 230
let b = 99

let bg_r = 54
let bg_g = 53
let bg_b = 55

let blob_color_center = new THREE.Vector3(r / 256.0, g / 256.0, b / 256.0);
let blob_color_edge = new THREE.Vector3(Math.max(r - 20, 0) / 256.0, Math.max(g - 20, 0) / 256.0, Math.max(b - 20, 0) / 256.0);
let bg_color = new THREE.Vector3(bg_r / 256.0, bg_g / 256.0, bg_b / 256.0);

console.log(renderer.capabilities.isWebGL2)

// Load the shader and create the material
loadShader('shader.glsl').then(fragmentShader => {
  const geometry = new THREE.PlaneGeometry(2, 2);
  const uniforms = {
    u_time: { value: 1.0 },
    u_resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
    u_seed: { value: Math.random() * (100.0) },
    u_blob_color_center: { value: blob_color_center },
    u_blob_color_edge: { value: blob_color_edge },
    u_bg_color: { value: bg_color }
  };

  const material = new THREE.ShaderMaterial({
    vertexShader: `
            void main() {
                gl_Position = vec4(position, 1.0);
            }
        `,
    fragmentShader: fragmentShader,
    uniforms: uniforms
  });

  const plane = new THREE.Mesh(geometry, material);
  scene.add(plane);

  camera.position.z = 1;

  let speedFactor = 0.004; // Default speed factor
  
  function animate() {
    requestAnimationFrame(animate);
    uniforms.u_time.value = (uniforms.u_time.value + speedFactor) % 1000; // Keep u_time within a range
    renderer.render(scene, camera);
  }
  animate();
  
  window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
    uniforms.u_resolution.value.set(window.innerWidth, window.innerHeight);
  });
  
  const ws = new WebSocket('ws://localhost:3000');

  let currentTrack = null;

  function updateColors() {
    blob_color_center.set(r / 256.0, g / 256.0, b / 256.0);
    blob_color_edge.set(Math.max(r - 20, 0) / 256.0, Math.max(g - 20, 0) / 256.0, Math.max(b - 20, 0) / 256.0);
    uniforms.u_blob_color_center.value = blob_color_center;
    uniforms.u_blob_color_edge.value = blob_color_edge;
    uniforms.u_bg_color.value = bg_color;
  }

  function animateColorChange(startColor, endColor, startBgColor, endBgColor, duration) {
    const startTime = performance.now();
    
    function step(currentTime) {
      const elapsedTime = currentTime - startTime;
      const progress = Math.min(elapsedTime / duration, 1);
      
      r = Math.round(startColor[0] + (endColor[0] - startColor[0]) * progress);
      g = Math.round(startColor[1] + (endColor[1] - startColor[1]) * progress);
      b = Math.round(startColor[2] + (endColor[2] - startColor[2]) * progress);
      
      bg_r = Math.round(startBgColor[0] + (endBgColor[0] - startBgColor[0]) * progress);
      bg_g = Math.round(startBgColor[1] + (endBgColor[1] - startBgColor[1]) * progress);
      bg_b = Math.round(startBgColor[2] + (endBgColor[2] - startBgColor[2]) * progress);
      
      bg_color.set(bg_r / 256.0, bg_g / 256.0, bg_b / 256.0);
      
      updateColors();
      
      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }
    
    requestAnimationFrame(step);
  }

  ws.onmessage = (event) => {
    event.data.text().then(data => {
      const trackInfo = JSON.parse(data);
      console.log(trackInfo);
      
      currentTrack = trackInfo;
      const newBgColor = trackInfo.dominant_color || [245, 230, 99];
      const newBlobColor = trackInfo.complementary_color || [54, 53, 55];
      const energy = trackInfo.energy / 150 || 0.004;
      speedFactor = energy;

      if (Array.isArray(newBgColor) && newBgColor.length === 3 && Array.isArray(newBlobColor) && newBlobColor.length === 3) {
        animateColorChange([r, g, b], newBlobColor, [bg_r, bg_g, bg_b], newBgColor, 5000);
      } else {
        console.error("Invalid color format:", newBgColor, newBlobColor);
      }
    });
  };
});