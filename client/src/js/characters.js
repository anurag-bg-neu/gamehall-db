const grid = document.getElementById("roster-grid");
const statusEl = document.getElementById("roster-status");
const form = document.getElementById("search-form");
const fieldSelect = document.getElementById("search-field");
const searchInput = document.getElementById("search-input");

const avatarUrl = (seed) =>
  `https://api.dicebear.com/7.x/adventurer/svg?seed=${encodeURIComponent(seed)}&backgroundColor=1a1e26`;

const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};

const renderCard = (character) => {
  const card = el("a", "card");
  card.href = `/characters/${encodeURIComponent(character.slug)}`;

  const imgWrap = el("div", "card-img-wrap");
  const img = el("img", "card-img");
  img.src = avatarUrl(character.avatar_seed);
  img.alt = `${character.name} portrait`;
  const nameplate = el("div", "card-nameplate");
  nameplate.append(el("h3", null, character.name));
  imgWrap.append(img, nameplate);

  const meta = el("div", "card-meta");
  const line = el("div");
  line.append(el("span", "game", character.game), ` · ${character.role}`);

  const power = el("div", "power-bar");
  const track = el("div", "power-bar-track");
  const fill = el("div", "power-bar-fill");
  fill.style.width = `${character.power}%`;
  track.append(fill);
  power.append(track, el("span", "power-bar-value", String(character.power)));

  meta.append(line, power);
  card.append(imgWrap, meta);
  return card;
};

const loadCharacters = async (search = "", field = "name") => {
  statusEl.textContent = "Loading roster...";
  const params = new URLSearchParams();
  if (search) {
    params.set("search", search);
    params.set("field", field);
  }

  try {
    const response = await fetch(`/api/characters?${params}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const characters = await response.json();

    grid.replaceChildren(...characters.map(renderCard));
    if (characters.length === 0) {
      statusEl.textContent = `No fighters match "${search}" in ${field}.`;
    } else {
      statusEl.textContent = search
        ? `${characters.length} fighter(s) found for "${search}" in ${field}.`
        : `${characters.length} fighters loaded.`;
    }
  } catch (err) {
    console.error(err);
    grid.replaceChildren();
    statusEl.textContent = "Could not load the roster. Is the server connected to the database?";
  }
};

form.addEventListener("submit", (event) => {
  event.preventDefault();
  loadCharacters(searchInput.value.trim(), fieldSelect.value);
});

// Clearing the search box (including the native "x" button) restores the full list.
searchInput.addEventListener("search", () => {
  if (!searchInput.value) loadCharacters();
});

loadCharacters();
