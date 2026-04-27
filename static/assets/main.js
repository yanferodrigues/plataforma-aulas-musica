/* ============================================================
   HARMONIA — main.js
   Three.js wave grid + GSAP ScrollTrigger + Cursor + Lenis
   ============================================================ */

/* ─── 1. PRELOADER ─────────────────────────────────────── */
window.addEventListener('DOMContentLoaded', () => {
  const preloader = document.getElementById('preloader');
  if (!preloader) return;

  setTimeout(() => {
    preloader.classList.add('done');
    document.body.style.overflow = '';
    initAll();
  }, 2000);
});

document.body.style.overflow = 'hidden';

/* ─── 2. INIT ALL ──────────────────────────────────────── */
function initAll() {
  initLenis();
  initCursor();
  initNavScroll();
  initHeroThree();
  initHeroGSAP();
  initScrollAnimations();
  initCounters();
}

/* ─── 3. SMOOTH SCROLL (removido — scroll nativo) ──────── */
function initLenis() {}

/* ─── 4. CUSTOM CURSOR ─────────────────────────────────── */
function initCursor() {
  const dot  = document.querySelector('.cursor-dot');
  const ring = document.querySelector('.cursor-ring');
  if (!dot || !ring) return;

  let mx = -200, my = -200;
  let rx = -200, ry = -200;

  document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });

  (function trackRing() {
    rx += (mx - rx) * 0.11;
    ry += (my - ry) * 0.11;
    dot.style.transform  = `translate(${mx}px, ${my}px) translate(-50%,-50%)`;
    ring.style.transform = `translate(${rx}px, ${ry}px) translate(-50%,-50%)`;
    requestAnimationFrame(trackRing);
  })();

  document.querySelectorAll('a, button, [data-hover]').forEach(el => {
    el.addEventListener('mouseenter', () => { dot.classList.add('hovered'); ring.classList.add('hovered'); });
    el.addEventListener('mouseleave', () => { dot.classList.remove('hovered'); ring.classList.remove('hovered'); });
  });

  document.addEventListener('mousedown', () => { dot.classList.add('clicking'); ring.classList.add('clicking'); });
  document.addEventListener('mouseup',   () => { dot.classList.remove('clicking'); ring.classList.remove('clicking'); });
}

/* ─── 5. NAV SCROLL STATE ──────────────────────────────── */
function initNavScroll() {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 60);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ─── 6. THREE.JS HERO WAVE ────────────────────────────── */
function initHeroThree() {
  const canvas = document.getElementById('hero-canvas');
  if (!canvas || typeof THREE === 'undefined') return;

  /* Scene */
  const scene    = new THREE.Scene();
  const W        = window.innerWidth;
  const H        = window.innerHeight;
  const camera   = new THREE.PerspectiveCamera(55, W / H, 0.1, 1000);
  camera.position.set(0, 14, 20);
  camera.lookAt(0, 0, -2);

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setSize(W, H);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  /* Particle grid — reduzida e discreta */
  const COLS = 55, ROWS = 18;
  const TOTAL = COLS * ROWS;
  const positions = new Float32Array(TOTAL * 3);
  const scales    = new Float32Array(TOTAL);
  const phases    = new Float32Array(TOTAL);

  for (let i = 0; i < COLS; i++) {
    for (let j = 0; j < ROWS; j++) {
      const idx = (i * ROWS + j);
      positions[idx * 3 + 0] = (i / (COLS - 1) - 0.5) * 40;
      positions[idx * 3 + 1] = 0;
      positions[idx * 3 + 2] = (j / (ROWS - 1) - 0.5) * 14;
      scales[idx]  = 0.25 + Math.random() * 0.45;
      phases[idx]  = Math.random() * Math.PI * 2;
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('aScale',   new THREE.BufferAttribute(scales, 1));
  geo.setAttribute('aPhase',   new THREE.BufferAttribute(phases, 1));

  /* Shaders */
  const vertexShader = /* glsl */`
    attribute float aScale;
    attribute float aPhase;
    uniform float uTime;
    uniform vec2  uMouse;
    varying float vY;

    void main() {
      vec3 pos = position;

      float wave =
        sin(pos.x * 0.30 + uTime * 0.55) * 0.9 +
        cos(pos.z * 0.42 + uTime * 0.38) * 0.55 +
        sin((pos.x + pos.z) * 0.15 + uTime * 0.28) * 0.35;

      pos.y = wave + aPhase * 0.18;

      /* Mouse elevation — mais suave */
      float dx = pos.x - uMouse.x;
      float dz = pos.z - uMouse.y;
      float md = sqrt(dx*dx + dz*dz);
      pos.y += max(0.0, 4.0 - md) * 0.35;

      vY = (pos.y + 2.5) / 5.0;

      vec4 mvp = modelViewMatrix * vec4(pos, 1.0);
      gl_PointSize = aScale * 2.2 * (260.0 / -mvp.z);
      gl_Position  = projectionMatrix * mvp;
    }
  `;

  const fragmentShader = /* glsl */`
    uniform vec3 uColorA;
    uniform vec3 uColorB;
    varying float vY;

    void main() {
      vec2  c    = gl_PointCoord - 0.5;
      float dist = length(c);
      if (dist > 0.5) discard;

      float alpha = pow(1.0 - dist * 2.0, 2.8) * 0.45;
      vec3  col   = mix(uColorA, uColorB, clamp(vY, 0.0, 1.0));
      gl_FragColor = vec4(col, alpha);
    }
  `;

  const mat = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime:   { value: 0 },
      uMouse:  { value: new THREE.Vector2(0, 0) },
      uColorA: { value: new THREE.Color('#5828C8') },
      uColorB: { value: new THREE.Color('#9068E8') },
    },
    transparent: true,
    depthWrite: false,
    blending: THREE.NormalBlending,
  });

  const particles = new THREE.Points(geo, mat);
  scene.add(particles);

  /* Mouse tracking */
  const mouse = new THREE.Vector2();
  window.addEventListener('mousemove', e => {
    const nx =  (e.clientX / window.innerWidth  - 0.5) * 42;
    const ny = -(e.clientY / window.innerHeight - 0.5) * 18;
    mouse.set(nx, ny);
  });

  /* Resize */
  window.addEventListener('resize', () => {
    const w = window.innerWidth, h = window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });

  /* Animate */
  const clock = new THREE.Clock();
  (function loop() {
    requestAnimationFrame(loop);
    const t = clock.getElapsedTime();
    mat.uniforms.uTime.value  = t;
    mat.uniforms.uMouse.value.lerp(mouse, 0.04);
    renderer.render(scene, camera);
  })();
}

/* ─── 7. HERO GSAP ENTRANCE ────────────────────────────── */
function initHeroGSAP() {
  if (typeof gsap === 'undefined') return;
  gsap.registerPlugin(ScrollTrigger);

  const eyebrow  = document.querySelector('.hero-eyebrow');
  const titleEl  = document.querySelector('.hero-title');
  const body     = document.querySelector('.hero-body');
  const ctas     = document.querySelector('.hero-ctas');

  /* Split title into chars */
  if (titleEl) {
    const rows = titleEl.querySelectorAll('.hero-title-row');
    rows.forEach(row => {
      const text = row.textContent;
      row.innerHTML = [...text].map(ch =>
        ch === ' ' ? '<span class="char" style="display:inline-block;width:.28em;">&nbsp;</span>'
                   : `<span class="char">${ch}</span>`
      ).join('');
    });
  }

  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

  if (eyebrow) tl.to(eyebrow, { opacity: 1, y: 0, duration: 0.8 }, 0.1);

  if (titleEl) {
    const chars = titleEl.querySelectorAll('.char');
    tl.to(chars, {
      opacity: 1,
      y: 0,
      duration: 1.0,
      stagger: 0.028,
      ease: 'power4.out',
    }, 0.3);
  }

  if (body) tl.to(body, { opacity: 1, y: 0, duration: 0.9, ease: 'power3.out' }, 0.7);
  if (ctas) tl.to(ctas, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }, 0.9);
}

/* ─── 8. SCROLL ANIMATIONS ─────────────────────────────── */
function initScrollAnimations() {
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

  /* Generic section reveals */
  document.querySelectorAll('.tag, .section-h2, .section-p').forEach(el => {
    gsap.fromTo(el,
      { opacity: 0, y: 40 },
      { opacity: 1, y: 0, duration: 0.9, ease: 'power3.out',
        scrollTrigger: { trigger: el, start: 'top 88%', once: true } }
    );
  });

  /* Feature cards stagger */
  const featCards = document.querySelectorAll('.feat-card');
  if (featCards.length) {
    gsap.fromTo(featCards,
      { opacity: 0, y: 60 },
      { opacity: 1, y: 0, duration: 0.9, stagger: 0.15, ease: 'power3.out',
        scrollTrigger: { trigger: '.features-grid', start: 'top 82%', once: true } }
    );
  }

  /* Module preview cards */
  const modCards = document.querySelectorAll('.mod-card');
  if (modCards.length) {
    gsap.fromTo(modCards,
      { opacity: 0, x: 60 },
      { opacity: 1, x: 0, duration: 0.8, stagger: 0.12, ease: 'power3.out',
        scrollTrigger: { trigger: '.mods-track', start: 'top 85%', once: true } }
    );
  }

  /* Stats cells */
  const statCells = document.querySelectorAll('.stat-cell');
  if (statCells.length) {
    gsap.fromTo(statCells,
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.7, stagger: 0.1, ease: 'power2.out',
        scrollTrigger: { trigger: '.stats-grid', start: 'top 84%', once: true } }
    );
  }

  /* Testimonials */
  const testiCards = document.querySelectorAll('.testi-card');
  if (testiCards.length) {
    gsap.fromTo(testiCards,
      { opacity: 0, y: 50 },
      { opacity: 1, y: 0, duration: 0.9, stagger: 0.18, ease: 'power3.out',
        scrollTrigger: { trigger: '.testimonials-grid', start: 'top 83%', once: true } }
    );
  }

  /* CTA section */
  const ctaInner = document.querySelector('.cta-inner');
  if (ctaInner) {
    gsap.fromTo(ctaInner,
      { opacity: 0, y: 50, scale: 0.97 },
      { opacity: 1, y: 0, scale: 1, duration: 1.0, ease: 'power3.out',
        scrollTrigger: { trigger: '.cta-section', start: 'top 80%', once: true } }
    );
  }

  /* Hero subtitle parallax */
  const heroBg = document.getElementById('hero-canvas');
  if (heroBg) {
    gsap.to(heroBg, {
      y: '20%',
      ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true },
    });
  }
}

/* ─── 9. COUNTER ANIMATIONS ────────────────────────────── */
function initCounters() {
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count, 10);
    const suffix = el.dataset.suffix || '';

    ScrollTrigger.create({
      trigger: el,
      start: 'top 85%',
      once: true,
      onEnter() {
        gsap.fromTo({ val: 0 }, { val: target, duration: 2, ease: 'power2.out',
          onUpdate() { el.textContent = Math.round(this.targets()[0].val).toLocaleString('pt-BR') + suffix; }
        });
      }
    });
  });
}
