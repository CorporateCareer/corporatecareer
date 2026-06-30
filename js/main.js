/* CareerMap.nl — Main JS */

// ── Navbar scroll effect ──────────────────────
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
}, { passive: true });

// ── Mobile hamburger menu ─────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');

hamburger.addEventListener('click', () => {
  const open = hamburger.classList.toggle('active');
  navLinks.classList.toggle('open', open);
  document.body.style.overflow = open ? 'hidden' : '';
  hamburger.setAttribute('aria-expanded', open);
  const lang = window.CURRENT_LANG || 'en';
  const openLabel  = (typeof TRANSLATIONS !== 'undefined' && TRANSLATIONS[lang]) ? TRANSLATIONS[lang]['nav.hamburger.open']  : 'Open menu';
  const closeLabel = (typeof TRANSLATIONS !== 'undefined' && TRANSLATIONS[lang]) ? TRANSLATIONS[lang]['nav.hamburger.close'] : 'Close menu';
  hamburger.setAttribute('aria-label', open ? closeLabel : openLabel);
});

// Close menu when a link is clicked
navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    hamburger.classList.remove('active');
    navLinks.classList.remove('open');
    document.body.style.overflow = '';
    hamburger.setAttribute('aria-expanded', 'false');
    const lang = window.CURRENT_LANG || 'en';
    const openLabel = (typeof TRANSLATIONS !== 'undefined' && TRANSLATIONS[lang]) ? TRANSLATIONS[lang]['nav.hamburger.open'] : 'Open menu';
    hamburger.setAttribute('aria-label', openLabel);
  });
});

// Close menu on Escape key
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && navLinks.classList.contains('open')) {
    hamburger.classList.remove('active');
    navLinks.classList.remove('open');
    document.body.style.overflow = '';
  }
});

// ── Scroll-triggered fade-up animations ──────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.12,
  rootMargin: '0px 0px -40px 0px'
});

document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

// ── Email form ────────────────────────────────
const form = document.getElementById('ctaForm');

form.addEventListener('submit', e => {
  e.preventDefault();

  const input = form.querySelector('input[type="email"]');
  const btn   = form.querySelector('button[type="submit"]');
  const email = input.value.trim();

  if (!email) return;

  // Simulated success state
  const lang = window.CURRENT_LANG || 'en';
  const successText = (typeof TRANSLATIONS !== 'undefined' && TRANSLATIONS[lang])
    ? TRANSLATIONS[lang]['cta.success'] : 'Sent!';
  const resetText = (typeof TRANSLATIONS !== 'undefined' && TRANSLATIONS[lang])
    ? TRANSLATIONS[lang]['cta.btn'] : 'Get Free Roadmap';

  btn.disabled = true;
  btn.textContent = successText;
  btn.style.cssText = 'background:#22c55e; box-shadow: 0 4px 20px rgba(34,197,94,0.4)';
  input.value = '';

  setTimeout(() => {
    btn.disabled = false;
    btn.textContent = resetText;
    btn.style.cssText = '';
  }, 3500);
});

// ── Smooth active highlight for career cards ──
document.querySelectorAll('.career-card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    document.querySelectorAll('.career-card').forEach(c => {
      if (c !== card) c.style.opacity = '0.80';
    });
  });

  card.addEventListener('mouseleave', () => {
    document.querySelectorAll('.career-card').forEach(c => {
      c.style.opacity = '';
    });
  });
});
