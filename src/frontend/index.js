function addToLocalStorageArray(key, newElement) {
    const existingArray = JSON.parse(localStorage.getItem(key)) || [];
    existingArray.push(newElement);
    localStorage.setItem(key, JSON.stringify(existingArray));
    return existingArray;
}

function removeFromLocalStorageArray(key, toRemove) {
    const existingArray = JSON.parse(localStorage.getItem(key)) || [];
    localStorage.setItem(key, JSON.stringify(existingArray.filter(elem => elem != toRemove)));
}

function getLocalStorageArray(key) {
    return JSON.parse(localStorage.getItem(key)) || [];
}

function showPendingRequests() {
		const list = document.getElementById('pending-requests');
		list.innerHTML = '';
		const elements = getLocalStorageArray("pending-requests");
		if (elements.length > 0) {
				elements.forEach(request => {
						const li = document.createElement('li');
						li.textContent = request;
						list.appendChild(li);
				});
		} else {
				const li = document.createElement('li');
				li.textContent = "No pending requests";
				list.appendChild(li);
		}
}

function showMsg(el, text, ok) {
  el.hidden = false;
  el.className = 'msg ' + (ok ? 'ok' : 'err');
  el.textContent = text;
  try {
    json = JSON.parse(str);
    el.textContent = json['detail'][0]['msg'];
  } catch (e) {
    el.textContent = text;
  }
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

showPendingRequests();
window.addEventListener('DOMContentLoaded', () => {
  // Create Request form
  const crForm = document.getElementById('create-request-form');
  const crMsg = document.getElementById('cr-msg');
  crForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    crMsg.hidden = true;
    const url = document.getElementById('cr-url').value.trim();
    const chapters = Number(document.getElementById('cr-chapters').value);
    const file_extension = document.getElementById('cr-ext').value;
    try {
      const req_id = await postJson('/requests', { url, chapters, file_extension });
      addToLocalStorageArray("pending-requests", req_id);
      showPendingRequests();
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
      if (ct.includes('application/zip')) {
        const blob = await res.blob();
        removeFromLocalStorageArray("pending-requests", req_id);
	      showPendingRequests();
        downloadBlob(blob, 'Result.zip');
        showMsg(dlMsg, 'Download started for Result.zip', true);
      } else {
        const text = await res.text();
	      if (text != "Request is not completed yet") {
			      removeFromLocalStorageArray("pending-requests", req_id);
			      showPendingRequests();
	      }
	      if (!res.ok) {
	        throw new Error(text || ('HTTP ' + res.status));
	      }
        showMsg(dlMsg, text, true);
      }
    } catch (err) {
      showMsg(dlMsg, err.message, false);
    }
  });
});
