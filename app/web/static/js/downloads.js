async function postJson(url, payload) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload || {}),
  });
  return await resp.json();
}

async function bindActionButtons() {
  document.querySelectorAll('.retry-btn').forEach(btn => {
    btn.onclick = async () => {
      const taskId = btn.dataset.taskId;
      const data = await postJson(`/api/downloads/${taskId}/retry`, { reset_retry_count: false });
      alert(data.message || 'done');
      window.location.reload();
    };
  });

  document.querySelectorAll('.cancel-btn').forEach(btn => {
    btn.onclick = async () => {
      const taskId = btn.dataset.taskId;
      const data = await postJson(`/api/downloads/${taskId}/cancel`, { reason: 'cancelled from panel' });
      alert(data.message || 'done');
      window.location.reload();
    };
  });
}

async function autoRefresh() {
  const checkbox = document.getElementById('auto-refresh');
  if (!checkbox || !checkbox.checked) return;
  window.location.reload();
}

bindActionButtons();
setInterval(autoRefresh, 8000);
