/* ============================================================
   MUSILAB — dashboard.js
   Dashboard animations, progress bars, sidebar toggle
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  initProgressBars();
  initCardEntrance();
  initSidebarMobile();
  initSearch();
});

/* ─── PROGRESS BARS ─────────────────────────────────────── */
function initProgressBars() {
  /* Animate all [data-width] bars on load */
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar = entry.target;
        const target = bar.dataset.width || '0%';
        setTimeout(() => { bar.style.width = target; }, 200);
        observer.unobserve(bar);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.pbar-fill').forEach(bar => observer.observe(bar));
}

/* ─── CARD ENTRANCE ─────────────────────────────────────── */
function initCardEntrance() {
  if (typeof gsap === 'undefined') return;

  const cards = document.querySelectorAll('.db-mod-card');
  if (!cards.length) return;

  gsap.fromTo(cards,
    { opacity: 0, y: 40, scale: 0.97 },
    {
      opacity: 1, y: 0, scale: 1,
      duration: 0.7, stagger: 0.1, ease: 'power3.out', delay: 0.3,
    }
  );

  const continueCard = document.querySelector('.continue-card');
  if (continueCard) {
    gsap.fromTo(continueCard,
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out', delay: 0.1 }
    );
  }

  const topbarTitle = document.querySelector('.db-topbar-title');
  if (topbarTitle) {
    gsap.fromTo(topbarTitle,
      { opacity: 0, x: -20 },
      { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out', delay: 0.05 }
    );
  }
}

/* ─── SIDEBAR MOBILE TOGGLE ─────────────────────────────── */
function initSidebarMobile() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  /* Create hamburger button if viewport is mobile */
  if (window.innerWidth <= 1100) {
    const btn = document.createElement('button');
    btn.innerHTML = '☰';
    btn.setAttribute('aria-label', 'Abrir menu');
    Object.assign(btn.style, {
      position: 'fixed', top: '14px', left: '14px',
      zIndex: '200', background: 'var(--glass)',
      border: '1px solid var(--glass-border)', borderRadius: '8px',
      width: '42px', height: '42px', fontSize: '18px',
      color: 'var(--text-primary)', cursor: 'pointer',
      backdropFilter: 'blur(12px)',
    });
    document.body.appendChild(btn);

    const overlay = document.createElement('div');
    Object.assign(overlay.style, {
      position: 'fixed', inset: '0', background: 'rgba(0,0,0,0.5)',
      zIndex: '99', display: 'none', backdropFilter: 'blur(4px)',
    });
    document.body.appendChild(overlay);

    btn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay.style.display = sidebar.classList.contains('open') ? 'block' : 'none';
    });
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.style.display = 'none';
    });
  }
}

/* ─── SEARCH ────────────────────────────────────────────── */
function initSearch() {
  const input = document.querySelector('.db-search input');
  if (!input) return;

  input.addEventListener('input', () => {
    const query = input.value.toLowerCase().trim();
    document.querySelectorAll('.db-mod-card').forEach(card => {
      const title = card.querySelector('.db-mod-title')?.textContent.toLowerCase() || '';
      const desc  = card.querySelector('.db-mod-desc')?.textContent.toLowerCase()  || '';
      const match = !query || title.includes(query) || desc.includes(query);
      card.style.opacity  = match ? '1' : '0.25';
      card.style.transform = match ? '' : 'scale(0.97)';
    });
  });
}
