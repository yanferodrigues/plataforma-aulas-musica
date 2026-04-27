/* ============================================================
   MUSILAB — lesson.js
   Lesson page: tabs, sidebar, video placeholder, cursor
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initProgressBars();
  initVideoPlaceholder();
  initLessonEntrance();
  initLessonSidebarScroll();
});

/* ─── TABS ──────────────────────────────────────────────── */
function initTabs() {
  const btns   = document.querySelectorAll('.tab-btn');
  const panels = document.querySelectorAll('.tab-panel');

  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      btns.forEach(b => b.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const panel = document.getElementById(`tab-${target}`);
      if (panel) panel.classList.add('active');
    });
  });
}

/* ─── PROGRESS BARS ─────────────────────────────────────── */
function initProgressBars() {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar = entry.target;
        setTimeout(() => { bar.style.width = bar.dataset.width || '0%'; }, 150);
        observer.unobserve(bar);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.pbar-fill').forEach(bar => observer.observe(bar));
}

/* ─── VIDEO PLACEHOLDER ─────────────────────────────────── */
function initVideoPlaceholder() {
  const playBtn = document.getElementById('play-btn');
  if (!playBtn) return;

  playBtn.addEventListener('click', () => {
    const placeholder = playBtn.closest('.video-placeholder');
    if (!placeholder) return;

    /* Pulse animation then fade */
    if (typeof gsap !== 'undefined') {
      gsap.to(playBtn, {
        scale: 1.3, opacity: 0, duration: 0.35, ease: 'power2.in',
        onComplete() {
          placeholder.style.opacity = '0';
          placeholder.style.transition = 'opacity 0.4s';
          setTimeout(() => { placeholder.style.display = 'none'; }, 400);
        }
      });
    } else {
      placeholder.style.display = 'none';
    }

    /* In a real app you'd call player.play() here */
    console.log('[MUSILAB] Video play triggered');
  });
}

/* ─── LESSON ENTRANCE ───────────────────────────────────── */
function initLessonEntrance() {
  if (typeof gsap === 'undefined') return;

  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

  tl.fromTo('.lesson-topbar', { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.5 }, 0);
  tl.fromTo('.video-wrap',    { opacity: 0, y: 30 },  { opacity: 1, y: 0, duration: 0.7 }, 0.15);
  tl.fromTo('.lesson-info',   { opacity: 0, y: 24 },  { opacity: 1, y: 0, duration: 0.6 }, 0.35);
  tl.fromTo('.tabs-bar',      { opacity: 0 },          { opacity: 1, duration: 0.5 },        0.5);
  tl.fromTo('.tab-panel.active', { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5 }, 0.6);
  tl.fromTo('.lesson-sidebar', { opacity: 0, x: 30 },  { opacity: 1, x: 0, duration: 0.7 }, 0.2);
}

/* ─── SIDEBAR ACTIVE ITEM SCROLL ─────────────────────────── */
function initLessonSidebarScroll() {
  const active = document.querySelector('.ls-item.active');
  if (active) {
    setTimeout(() => {
      active.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }, 800);
  }
}
