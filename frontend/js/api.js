const CARD_CONTAINER_ID = "card-container";
const components = {};

// Utility: load an external HTML template and cache it
async function loadComponent(path) {
  if (components[path]) return components[path];
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load component ${path}`);
  const html = await res.text();
  const temp = document.createElement("div");
  temp.innerHTML = html.trim();
  const templateEl = temp.querySelector("template");
  if (!templateEl) throw new Error(`No <template> found in ${path}`);
  components[path] = templateEl;
  return templateEl;
}

// Render loader while waiting for API
async function showLoader() {
  const container = document.getElementById(CARD_CONTAINER_ID);
  container.innerHTML = "";
  const loaderTpl = await loadComponent("/components/Loader.html");
  const node = loaderTpl.content.cloneNode(true);
  container.appendChild(node);
}

// Display generated quote card
async function showQuoteCard(imgUrl) {
  const container = document.getElementById(CARD_CONTAINER_ID);
  container.innerHTML = "";
  const cardTpl = await loadComponent("/components/QuoteCard.html");
  const node = cardTpl.content.cloneNode(true);
  const img = node.querySelector("img");
  img.src = imgUrl;
  img.alt = "Generated quote";
  container.appendChild(node);
}

function handleError(err) {
  alert(err.message || err);
  const container = document.getElementById(CARD_CONTAINER_ID);
  container.innerHTML = "";
}

async function handleGenerate(evt) {
  evt.preventDefault();
  const input = document.getElementById("topic-input");
  const topic = input.value.trim();

  try {
    await showLoader();

    let url = "/api/quote";
    if (topic) {
      url += `?topic=${encodeURIComponent(topic)}`;
    }
    const resp = await fetch(url);
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(text);
    }
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    await showQuoteCard(data.img_url);
  } catch (err) {
    handleError(err);
  }
}

function init() {
  const form = document.getElementById("generate-form");
  form.addEventListener("submit", handleGenerate);
}

document.addEventListener("DOMContentLoaded", init); 