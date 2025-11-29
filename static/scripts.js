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

  // Al enviar: marcar sesión como bloqueada para este quiz (no limpiar localStorage)
  form.addEventListener('submit', (e) => {
    try {
      // Marcar bloqueo sólo para este quiz (usa el id del form si existe)
      const key = `quiz_blocked_${form.id || 'all'}`;
      sessionStorage.setItem(key, '1');
    } catch (err) {
      // si falla sessionStorage, no impedimos el envío
    }
    // permitir que el formulario siga su flujo normal (ir a resultados)
  });
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

// Manejo de bloqueo de respuestas en la sesión: al cargar la página deshabilitar inputs si está bloqueado
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('all-quiz-form');
  if (!form) return;

  const key = `quiz_blocked_${form.id || 'all'}`;
  if (sessionStorage.getItem(key) === '1') {
    // Deshabilitar todos los controles del formulario para que no se puedan cambiar
    for (const el of form.elements) {
      try {
        if (el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA' || el instanceof HTMLElement) {
          el.disabled = true;
        }
      } catch (e) {
        // ignore
      }
    }

    // Mostrar un aviso arriba del formulario indicando que las respuestas están bloqueadas
    const banner = document.createElement('div');
    banner.className = 'quiz-blocked-banner';
    banner.textContent = 'Respuestas bloqueadas. Puedes verlas pero no modificarlas.';
    banner.style.cssText = 'background:#fff3cd;border:1px solid #ffe08a;padding:10px;margin-bottom:10px;border-radius:4px;color:#856404;font-weight:600;';
    form.parentNode && form.parentNode.insertBefore(banner, form);
  }
});
