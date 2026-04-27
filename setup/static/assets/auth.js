/* ============================================================
   MUSILAB — auth.js
   Login & Register page interactions
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  initFormAnimations();
  initPasswordToggles();
  initFormValidation();
  initFormSubmit();
});

/* ─── FORM ENTRANCE ANIMATION ───────────────────────────── */
function initFormAnimations() {
  if (typeof gsap === 'undefined') return;

  const wrap = document.querySelector('.auth-form-wrap');
  if (!wrap) return;

  const elements = [
    wrap.querySelector('.auth-form-title'),
    wrap.querySelector('.auth-form-subtitle'),
    ...wrap.querySelectorAll('.form-group, .form-row, .form-divider, [type=submit], .btn-secondary'),
  ].filter(Boolean);

  gsap.fromTo(elements,
    { opacity: 0, y: 28 },
    { opacity: 1, y: 0, duration: 0.7, stagger: 0.08, ease: 'power3.out', delay: 0.2 }
  );

  const visual = document.querySelector('.auth-visual-content');
  if (visual) {
    gsap.fromTo(visual,
      { opacity: 0, x: -30 },
      { opacity: 1, x: 0, duration: 0.9, ease: 'power3.out', delay: 0.1 }
    );
  }
}

/* ─── PASSWORD TOGGLES ──────────────────────────────────── */
function initPasswordToggles() {
  document.querySelectorAll('.pw-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const wrap  = btn.closest('.pw-wrap');
      const input = wrap.querySelector('input');
      if (!input) return;
      const visible = input.type === 'text';
      input.type  = visible ? 'password' : 'text';
      btn.textContent = visible ? '👁' : '🙈';
    });
  });
}

/* ─── INLINE VALIDATION ─────────────────────────────────── */
function initFormValidation() {
  const inputs = document.querySelectorAll('.form-input');
  inputs.forEach(input => {
    input.addEventListener('blur', () => validateInput(input));
    input.addEventListener('input', () => {
      if (input.classList.contains('invalid')) validateInput(input);
    });
  });
}

function validateInput(input) {
  const val = input.value.trim();
  let ok = true;

  if (input.type === 'email') {
    ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
  } else if (input.type === 'password') {
    ok = val.length >= 8;
    const hint = input.closest('.form-group')?.querySelector('.form-hint');
    if (hint) hint.textContent = val.length > 0 && val.length < 8
      ? `Mínimo 8 caracteres (${val.length}/8)`
      : 'Mínimo 8 caracteres.';
  } else if (input.id === 'confirm_password') {
    const pw = document.getElementById('password');
    ok = pw && val === pw.value && val.length > 0;
    const hint = input.closest('.form-group')?.querySelector('.form-hint');
    if (hint) hint.textContent = 'As senhas não coincidem.';
  } else {
    ok = val.length >= 2;
  }

  if (val === '') {
    input.classList.remove('valid', 'invalid');
    return;
  }
  input.classList.toggle('valid',   ok);
  input.classList.toggle('invalid', !ok);
}

/* ─── FORM SUBMIT ───────────────────────────────────────── */
function initFormSubmit() {
  const loginForm    = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');

  if (loginForm) {
    loginForm.addEventListener('submit', e => {
      e.preventDefault();
      const inputs = loginForm.querySelectorAll('.form-input');
      let allValid = true;
      inputs.forEach(inp => { validateInput(inp); if (inp.classList.contains('invalid')) allValid = false; });
      if (!allValid) return shakeForm(loginForm);
      submitFlow(loginForm.querySelector('.form-submit'), 'dashboard.html');
    });
  }

  if (registerForm) {
    registerForm.addEventListener('submit', e => {
      e.preventDefault();
      const inputs = registerForm.querySelectorAll('.form-input');
      let allValid = true;
      inputs.forEach(inp => { validateInput(inp); if (inp.classList.contains('invalid') || inp.value.trim() === '') allValid = false; });
      const terms = registerForm.querySelector('#terms');
      if (terms && !terms.checked) {
        allValid = false;
        terms.style.outline = '2px solid var(--error)';
        setTimeout(() => { terms.style.outline = ''; }, 2500);
      }
      if (!allValid) return shakeForm(registerForm);
      submitFlow(registerForm.querySelector('.form-submit'), 'dashboard.html');
    });
  }
}

function submitFlow(btn, redirect) {
  if (!btn) return;
  const text = btn.querySelector('.submit-text');
  const icon = btn.querySelector('.submit-icon');
  if (text) text.textContent = 'Carregando…';
  if (icon) icon.textContent = '⏳';
  btn.disabled = true;
  btn.style.opacity = '0.75';

  setTimeout(() => {
    window.location.href = redirect;
  }, 1200);
}

function shakeForm(form) {
  if (typeof gsap === 'undefined') return;
  gsap.to(form, {
    x: [-8, 8, -6, 6, -3, 3, 0],
    duration: 0.55,
    ease: 'none',
  });
}
