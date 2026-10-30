// Accès au moteur MasqueIA, avec une interface proche de fetch() :
// - dans l'extension : via le service worker, seul à joindre le moteur local
// - page servie par le serveur Flask de développement : requête HTTP sur la même origine

const IN_EXTENSION = typeof chrome !== 'undefined' && !!chrome.runtime?.id;

async function apiFetch(path, options = {}) {
  if (!IN_EXTENSION) return fetch(`/api${path}`, options);

  const reply = await chrome.runtime.sendMessage({
    action: 'api',
    method: options.method || 'GET',
    path,
    body: options.body ? JSON.parse(options.body) : undefined
  });
  if (!reply || reply.transportError) {
    throw new Error(reply?.transportError || 'Moteur MasqueIA indisponible');
  }
  return { ok: reply.status < 400, status: reply.status, json: async () => reply.body };
}
