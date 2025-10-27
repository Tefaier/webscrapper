function showMsg(el, text, ok) {
  el.hidden = false;
  el.className = 'msg ' + (ok ? 'ok' : 'err');
  el.textContent = text;
}

async function postJson(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const text = await res.text();
  if (!res.ok) throw new Error(text || ('HTTP ' + res.status));
  return text;
}

function downloadBlob(blob, filename) {
  const a = document.createElement('a');
  const url = URL.createObjectURL(blob);
  a.style = "display: none";
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

window.addEventListener('DOMContentLoaded', () => {
  // Create Request form
  const crForm = document.getElementById('create-request-form');
  const crMsg = document.getElementById('cr-msg');
  crForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    crMsg.hidden = true;
    const url = document.getElementById('cr-url').value.trim();
    const chapters = Number(document.getElementById('cr-chapters').value);
    try {
      const req_id = await postJson('/requests', { url, chapters });
      showMsg(crMsg, 'Request created. Request ID: ' + req_id + '\nDo not lose it since it will be later required to download result.', true);
    } catch (err) {
      showMsg(crMsg, err.message, false);
    }
  });

  // Add Website form
  const awForm = document.getElementById('add-website-form');
  const awMsg = document.getElementById('aw-msg');
  awForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    awMsg.hidden = true;
    const url = document.getElementById('aw-url').value.trim();
    try {
      const msg = await postJson('/add-website', { url });
      showMsg(awMsg, msg, true);
    } catch (err) {
      showMsg(awMsg, err.message, false);
    }
  });

  // Download Result form
  const dlForm = document.getElementById('download-form');
  const dlMsg = document.getElementById('dl-msg');
  dlForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    dlMsg.hidden = true;
    const req_id = document.getElementById('dl-rid').value.trim();
    try {
      const res = await fetch('/download?req_id=' + encodeURIComponent(req_id), {
        method: 'GET'
      });
      const ct = res.headers.get('content-type') || '';
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || ('HTTP ' + res.status));
      }
      if (ct.includes('application/zip')) {
        const blob = await res.blob();
        downloadBlob(blob, 'Result.zip');
        showMsg(dlMsg, 'Download started for Result.zip', true);
      } else {
        const text = await res.text();
        showMsg(dlMsg, text, true);
      }
    } catch (err) {
      showMsg(dlMsg, err.message, false);
    }
  });
});
