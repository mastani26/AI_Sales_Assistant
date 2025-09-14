export const API_BASE = import.meta?.env?.VITE_API_BASE || "http://127.0.0.1:8000";

export async function postJSON(path, payload){
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function postForm(path, formData){
  const res = await fetch(`${API_BASE}${path}`, { method: 'POST', body: formData });
  return res.json();
}

export async function getJSON(path){
  const res = await fetch(`${API_BASE}${path}`);
  return res.json();
}
