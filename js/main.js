/* CorporateCareer — Main JS */

// ── Scroll-triggered fade-up animations ──────
// Dit blok staat bewust bovenaan. De class js op <html> verbergt elk
// .fade-up-element tot dit de class visible toevoegt, en op de homepage zijn
// dat er 37, waaronder de h1. Zou hier iets boven staan dat een fout gooit,
// dan werd dit nooit uitgevoerd en bleef de pagina leeg. Alles hieronder is
// afgeschermd zodat een ontbrekend element op een enkele pagina de rest van
// dit bestand niet meesleurt.
(function () {
  // Het vangnet in de head haalt de class js weer weg als deze vlag bij het
  // load-event niet gezet is. Dat vangt het geval af dat dit bestand helemaal
  // niet laadt: de class js zou dan blijven staan en alles verborgen houden.
  window.__ccFade = true;

  const items = document.querySelectorAll('.fade-up');

  // Zonder IntersectionObserver is er geen manier om te weten wanneer iets in
  // beeld komt. Dan alles direct tonen: geen animatie, wel een pagina.
  if (!('IntersectionObserver' in window)) {
    items.forEach(el => el.classList.add('visible'));
    return;
  }

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

  items.forEach(el => observer.observe(el));
})();

// ── Navbar scroll effect ──────────────────────
const navbar = document.getElementById('navbar');

if (navbar) window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
}, { passive: true });

// ── Mobile hamburger menu ─────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');

if (hamburger && navLinks) {
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
}

// ── Finance dropdown submenu (mobile expand / accessible toggle) ──
document.querySelectorAll('.nav-sub-toggle').forEach(btn => {
  btn.addEventListener('click', e => {
    e.preventDefault();
    e.stopPropagation();
    const item = btn.closest('.nav-dropdown');
    if (!item) return;
    const open = item.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
});

// ── Email form ────────────────────────────────
const form = document.getElementById('ctaForm');

if (form) form.addEventListener('submit', e => {
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
