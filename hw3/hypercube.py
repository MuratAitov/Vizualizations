import json

import streamlit as st
import streamlit.components.v1 as components


def render_hw3() -> None:
    st.subheader("Interactive Hypercube Visualization")

    st.markdown(
        """
**Description:** A 4-dimensional hypercube (tesseract) projected into 3D space
using perspective projection. The tesseract has 16 vertices and 32 edges.

**Main ideas:**
- Represent a hypercube as vertices and edges in 4D space.
- Apply rotations in 4D planes (XW, YW, ZW).
- Project the rotated 4D object into 3D via perspective projection.
- Render interactively with Three.js.

**Interaction:** Use 4 rotation sliders (one per dimension) to rotate the tesseract
in different 4D planes. Drag to orbit the 3D view. Scroll to zoom.
"""
    )

    st.markdown("**4D Rotation angles**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        angle_xw = st.slider(
            "X-W rotation", min_value=0.0, max_value=6.28, value=0.0, step=0.01
        )
    with col2:
        angle_yw = st.slider(
            "Y-W rotation", min_value=0.0, max_value=6.28, value=0.0, step=0.01
        )
    with col3:
        angle_zw = st.slider(
            "Z-W rotation", min_value=0.0, max_value=6.28, value=0.0, step=0.01
        )
    with col4:
        angle_xy = st.slider(
            "X-Y rotation", min_value=0.0, max_value=6.28, value=0.0, step=0.01
        )

    col5, col6, col7 = st.columns(3)
    with col5:
        perspective_4d = st.slider(
            "4D perspective distance",
            min_value=1.5,
            max_value=5.0,
            value=2.0,
            step=0.1,
        )
    with col6:
        show_axes = st.checkbox("Show coordinate axes", value=True)
    with col7:
        color_mode = st.selectbox(
            "Color mode",
            options=["Depth (W-axis)", "Solid", "Edge rainbow"],
            index=0,
        )

    params = json.dumps(
        {
            "angleXW": angle_xw,
            "angleYW": angle_yw,
            "angleZW": angle_zw,
            "angleXY": angle_xy,
            "perspective4d": perspective_4d,
            "showAxes": show_axes,
            "colorMode": color_mode,
        }
    )

    html = _build_html(params)
    components.html(html, height=720)


def _build_html(params_json: str) -> str:
    return (
        """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  body { margin: 0; overflow: hidden; background: #0d1117; }
  canvas { display: block; }
  #info {
    position: absolute;
    bottom: 12px;
    left: 12px;
    color: #8b949e;
    font: 12px/1.4 Arial, sans-serif;
    background: rgba(13,17,23,0.85);
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid #30363d;
  }
  #info strong { color: #c9d1d9; }
</style>
</head>
<body>
<div id="info">
  <strong>Tesseract (4D Hypercube)</strong><br/>
  Vertices: 16 &middot; Edges: 32<br/>
  Drag to orbit &middot; Scroll to zoom
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function() {
  const PARAMS = """
        + params_json
        + """;

  // --- Hypercube geometry ---
  // 16 vertices of a unit tesseract centered at origin
  const vertices4D = [];
  for (let i = 0; i < 16; i++) {
    vertices4D.push([
      (i & 1 ? 1 : -1),
      (i & 2 ? 1 : -1),
      (i & 4 ? 1 : -1),
      (i & 8 ? 1 : -1),
    ]);
  }

  // 32 edges: connect vertices that differ in exactly one coordinate
  const edges = [];
  for (let i = 0; i < 16; i++) {
    for (let j = i + 1; j < 16; j++) {
      let diff = 0;
      for (let k = 0; k < 4; k++) {
        if (vertices4D[i][k] !== vertices4D[j][k]) diff++;
      }
      if (diff === 1) edges.push([i, j]);
    }
  }

  // --- 4D rotation matrices (applied to [x, y, z, w]) ---
  function rotate4D(v, angle, plane) {
    const [x, y, z, w] = v;
    const c = Math.cos(angle);
    const s = Math.sin(angle);
    switch (plane) {
      case 'XW': return [c * x - s * w, y, z, s * x + c * w];
      case 'YW': return [x, c * y - s * w, z, s * y + c * w];
      case 'ZW': return [x, y, c * z - s * w, s * z + c * w];
      case 'XY': return [c * x - s * y, s * x + c * y, z, w];
      case 'XZ': return [c * x - s * z, y, s * x + c * z, w];
      case 'YZ': return [x, c * y - s * z, s * y + c * z, w];
      default:   return [x, y, z, w];
    }
  }

  // Perspective projection from 4D to 3D
  function project4Dto3D(v, d) {
    const scale = d / (d - v[3]);
    return [v[0] * scale, v[1] * scale, v[2] * scale, v[3]];
  }

  // --- Three.js setup ---
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 0, 6);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setClearColor(0x0d1117);
  document.body.appendChild(renderer.domElement);

  // --- Simple orbit controls (no external dependency) ---
  let isDragging = false;
  let prevMouse = { x: 0, y: 0 };
  let orbitAngles = { theta: 0, phi: 0.3 };
  let orbitRadius = 6;

  renderer.domElement.addEventListener('mousedown', (e) => {
    isDragging = true;
    prevMouse = { x: e.clientX, y: e.clientY };
  });
  renderer.domElement.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const dx = e.clientX - prevMouse.x;
    const dy = e.clientY - prevMouse.y;
    orbitAngles.theta -= dx * 0.005;
    orbitAngles.phi = Math.max(-Math.PI / 2 + 0.1, Math.min(Math.PI / 2 - 0.1, orbitAngles.phi + dy * 0.005));
    prevMouse = { x: e.clientX, y: e.clientY };
  });
  renderer.domElement.addEventListener('mouseup', () => { isDragging = false; });
  renderer.domElement.addEventListener('mouseleave', () => { isDragging = false; });
  renderer.domElement.addEventListener('wheel', (e) => {
    orbitRadius = Math.max(2, Math.min(15, orbitRadius + e.deltaY * 0.005));
  });

  // --- Axes helper ---
  let axesHelper = null;
  if (PARAMS.showAxes) {
    axesHelper = new THREE.AxesHelper(2.5);
    scene.add(axesHelper);
  }

  // --- Vertex spheres ---
  const vertexMeshes = [];
  const vertexGeo = new THREE.SphereGeometry(0.06, 12, 12);
  for (let i = 0; i < 16; i++) {
    const mat = new THREE.MeshBasicMaterial({ color: 0x58a6ff });
    const mesh = new THREE.Mesh(vertexGeo, mat);
    scene.add(mesh);
    vertexMeshes.push(mesh);
  }

  // --- Edge lines ---
  const edgeLines = [];
  for (let i = 0; i < edges.length; i++) {
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(6);
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.LineBasicMaterial({ color: 0x58a6ff, transparent: true, opacity: 0.7 });
    const line = new THREE.Line(geo, mat);
    scene.add(line);
    edgeLines.push(line);
  }

  // --- Color helpers ---
  function wToColor(w) {
    // Map w from [-1, 1] to a blue-white-orange gradient
    const t = (w + 1) / 2; // 0..1
    const r = Math.floor(40 + t * 215);
    const g = Math.floor(80 + (1 - Math.abs(t - 0.5) * 2) * 175);
    const b = Math.floor(255 - t * 200);
    return new THREE.Color(r / 255, g / 255, b / 255);
  }

  function rainbowColor(index, total) {
    const hue = index / total;
    return new THREE.Color().setHSL(hue, 0.8, 0.6);
  }

  const solidColor = new THREE.Color(0x58a6ff);

  // --- Animation ---
  function animate() {
    requestAnimationFrame(animate);

    // Compute rotated + projected vertices using 4 independent angle sliders
    const projected = [];
    for (let i = 0; i < 16; i++) {
      let v = vertices4D[i].slice();
      v = rotate4D(v, PARAMS.angleXW, 'XW');
      v = rotate4D(v, PARAMS.angleYW, 'YW');
      v = rotate4D(v, PARAMS.angleZW, 'ZW');
      v = rotate4D(v, PARAMS.angleXY, 'XY');
      const p = project4Dto3D(v, PARAMS.perspective4d);
      projected.push(p);
    }

    // Update vertex positions and colors
    for (let i = 0; i < 16; i++) {
      const [px, py, pz, pw] = projected[i];
      vertexMeshes[i].position.set(px, py, pz);

      if (PARAMS.colorMode === 'Depth (W-axis)') {
        vertexMeshes[i].material.color = wToColor(pw);
      } else if (PARAMS.colorMode === 'Edge rainbow') {
        vertexMeshes[i].material.color = rainbowColor(i, 16);
      } else {
        vertexMeshes[i].material.color = solidColor;
      }
    }

    // Update edge positions and colors
    for (let i = 0; i < edges.length; i++) {
      const [a, b] = edges[i];
      const pa = projected[a];
      const pb = projected[b];
      const positions = edgeLines[i].geometry.attributes.position.array;
      positions[0] = pa[0]; positions[1] = pa[1]; positions[2] = pa[2];
      positions[3] = pb[0]; positions[4] = pb[1]; positions[5] = pb[2];
      edgeLines[i].geometry.attributes.position.needsUpdate = true;

      if (PARAMS.colorMode === 'Depth (W-axis)') {
        const avgW = (pa[3] + pb[3]) / 2;
        edgeLines[i].material.color = wToColor(avgW);
      } else if (PARAMS.colorMode === 'Edge rainbow') {
        edgeLines[i].material.color = rainbowColor(i, edges.length);
      } else {
        edgeLines[i].material.color = solidColor;
      }
    }

    // Update camera orbit
    camera.position.x = orbitRadius * Math.sin(orbitAngles.theta) * Math.cos(orbitAngles.phi);
    camera.position.y = orbitRadius * Math.sin(orbitAngles.phi);
    camera.position.z = orbitRadius * Math.cos(orbitAngles.theta) * Math.cos(orbitAngles.phi);
    camera.lookAt(0, 0, 0);

    renderer.render(scene, camera);
  }

  animate();

  // --- Handle resize ---
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
})();
</script>
</body>
</html>
"""
    )
