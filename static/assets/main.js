/* ============================================================
   MUSILAB — main.js
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
  initNavScroll();
  initHeroGSAP();
  initScrollAnimations();
  initCounters();
}

/* ─── 3. SMOOTH SCROLL (removido — scroll nativo) ──────── */
function initLenis() {}

/* ─── 4. NAV SCROLL STATE ──────────────────────────────── */
function initNavScroll() {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 60);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ─── 6. HERO GSAP ENTRANCE ────────────────────────────── */
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
