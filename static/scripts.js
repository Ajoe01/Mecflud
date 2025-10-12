/* =========================================================
   scripts.js — Enviar todo al final (validación estricta)
   ========================================================= */

(() => {
  'use strict';
  const form = document.getElementById('all-quiz-form');
  if (!form || !Array.isArray(window.QUIZ)) return;

  // Limpia marcas de error visual
  function clearMarks() {
    document.querySelectorAll('.exercise-card.missing')
      .forEach(el => el.classList.remove('missing'));
  }

  // Marca como faltante una tarjeta y hace scroll
  function markMissing(id) {
    const card = document.getElementById(`qcard-${id}`);
    if (card) {
      card.classList.add('missing');
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  form.addEventListener('submit', (e) => {
    clearMarks();

    // Verificación dura: TODAS respondidas
    const missing = [];
    for (const q of window.QUIZ) {
      const checked = form.querySelector(`input[name="q-${q.id}"]:checked`);
      if (!checked) missing.push(q.id);
    }

    if (missing.length > 0) {
      e.preventDefault();
      // Marca y enfoca la primera que falte
      markMissing(missing[0]);
      alert(`Faltan ${missing.length} pregunta(s) por responder.`);
    }
  });
})();
// Guardar progreso local del quiz
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('all-quiz-form');
  if (!form) return;

  // Cargar respuestas guardadas
  for (let el of form.elements) {
    if (el.name && localStorage.getItem(el.name)) {
      el.checked = localStorage.getItem(el.name) === el.value;
    }
  }

  // Guardar cada cambio
  form.addEventListener('change', e => {
    if (e.target.name) {
      localStorage.setItem(e.target.name, e.target.value);
    }
  });

  // Al enviar, limpiar almacenamiento
  form.addEventListener('submit', () => localStorage.clear());
});
// Validación de faltantes antes de enviar (además del backend)
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('all-quiz-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    // Nombres tipo q<ID>
    const questions = new Set();
    for (const el of form.elements) {
      if (el.name && /^q\d+$/.test(el.name)) {
        questions.add(el.name);
      }
    }
    let missing = [];
    for (const q of questions) {
      const checked = form.querySelector(`input[name="${q}"]:checked`);
      if (!checked) missing.push(q.replace(/^q/, ''));
    }
    if (missing.length > 0) {
      e.preventDefault();
      alert(`Tienes ${missing.length} pregunta(s) sin responder: ${missing.join(', ')}. Complétalas antes de enviar.`);
    }
  });
});

// Ocultar enlace 'Preguntas' en la navegación si el servidor indica lock_Q o has_attempt
document.addEventListener('DOMContentLoaded', () => {
  // Intentar obtener flags del servidor
  fetch('/api/nav_flags', { credentials: 'same-origin' })
    .then(r => {
      if (!r.ok) throw new Error('no-json');
      return r.json();
    })
    .then(data => {
      const hide = (data.lock_Q === 1) || Boolean(data.has_attempt);
      if (!hide) return;

      // Buscar enlaces que apunten a /exercises o cuyo texto sea 'Preguntas'
      const navLinks = Array.from(document.querySelectorAll('a'));
      for (const a of navLinks) {
        try {
          const href = a.getAttribute('href') || '';
          const txt = (a.textContent || '').trim().toLowerCase();
          if (href.endsWith('/exercises') || txt === 'preguntas') {
            // Ocultar el elemento de lista padre si existe, si no, ocultar el enlace
            const li = a.closest('li');
            if (li) li.style.display = 'none';
            else a.style.display = 'none';
          }
        } catch (e) {
          // ignora
        }
      }
    })
    .catch(() => {
      // Si falla la petición no hacemos nada
    });
});
