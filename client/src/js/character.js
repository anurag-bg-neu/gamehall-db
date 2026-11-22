const detail = document.getElementById("detail");
const statusEl = document.getElementById("detail-status");

const avatarUrl = (seed) =>
  `https://api.dicebear.com/7.x/adventurer/svg?seed=${encodeURIComponent(seed)}&backgroundColor=1a1e26`;

const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};

const renderCharacter = (c) => {
  const card = el("article", "fighter-card");

  const portrait = el("div", "fighter-portrait");
  const img = el("img");
  img.src = avatarUrl(c.avatar_seed);
  img.alt = `${c.name} portrait`;
  portrait.append(img);

  const info = el("div", "fighter-info");
  const powerRow = el("div", "fighter-power-row");
  const track = el("div", "power-bar-track");
  const fill = el("div", "power-bar-fill");
  fill.style.width = `${c.power}%`;
  track.append(fill);
  powerRow.append(
    el("span", "fighter-power-label", "POWER"),
    track,
    el("span", "power-bar-value", String(c.power))
  );

  info.append(
    el("div", "fighter-badge", c.game),
    el("h1", null, c.name),
    el("p", "fighter-role", c.role),
    powerRow,
    el("p", "fighter-desc", c.description),
    el("p", "fighter-id", `Database ID #${c.id} · slug: ${c.slug}`)
  );

  card.append(portrait, info);
  return card;
};

const loadCharacter = async () => {
  const slug = decodeURIComponent(window.location.pathname.split("/").pop());

  try {
    const response = await fetch(`/api/characters/${encodeURIComponent(slug)}`);
    if (response.status === 404) {
      window.location.replace("/404");
      return;
    }
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const character = await response.json();
    document.title = `${character.name} - GameHall`;
    statusEl.remove();
    detail.replaceChildren(renderCharacter(character));
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Could not load this fighter. Is the server connected to the database?";
  }
};

loadCharacter();
