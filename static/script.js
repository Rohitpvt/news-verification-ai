// Tab functionality
const tabs = document.querySelectorAll('.tab-button');
tabs.forEach(t => t.addEventListener('click', function() {
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  tabs.forEach(b => b.classList.remove('active'));
  const id = this.getAttribute('data-tab');
  if (id) document.getElementById(id).classList.add('active');
  this.classList.add('active');
}));

// Text verification
const textForm = document.getElementById('textForm');
if (textForm) {
  textForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = document.getElementById('textInput').value.trim();
    if (!text) return alert('Enter claim');
    try {
      const r = await fetch('/api/verify-text', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({claim: text})});
      const d = await r.json();
      showResults(d, 'text');
    } catch(e) { alert(e.message); }
  });
}

// Image verification
const imgForm = document.getElementById('imageForm');
if (imgForm) {
  imgForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = document.getElementById('imageInput').files[0];
    if (!file) return alert('Select file');
    const fd = new FormData(); fd.append('image', file);
    try {
      const r = await fetch('/api/verify-image', {method: 'POST', body: fd});
      const d = await r.json();
      showResults(d, 'image');
    } catch(e) { alert(e.message); }
  });
}

function showResults(d, t) {
  const div = document.getElementById(t + 'Results');
  if (!div) return;
  div.innerHTML = '';
  if (d.error) { div.innerHTML = '<p style="color:red"><b>Error:</b> ' + d.error + '</p>'; return; }
  if (t === 'image' && d.extracted_text) div.innerHTML = '<p><b>Text:</b> ' + d.extracted_text + '</p>';
  if (d.results) {
    d.results.forEach(r => {
      const h = '<div class="result-item"><b>' + (r.source || 'Result') + '</b><p>' + (r.coverage || r.verdict || 'No info') + '</p></div>';
      div.innerHTML += h;
    });
  }
  div.style.display = 'block';
}

window.addEventListener('DOMContentLoaded', () => { if (tabs.length) tabs[0].click(); });