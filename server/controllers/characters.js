const { pool } = require("../config/database");

// Columns a user may search by. Anything else is rejected so the column name
// never comes from raw user input.
const SEARCHABLE_FIELDS = ["name", "game", "role"];

const getCharacters = async (req, res) => {
  const search = (req.query.search || "").trim();
  const field = req.query.field || "name";

  if (search && !SEARCHABLE_FIELDS.includes(field)) {
    return res.status(400).json({ error: `field must be one of: ${SEARCHABLE_FIELDS.join(", ")}` });
  }

  try {
    const results = search
      ? await pool.query(
          `SELECT * FROM characters WHERE ${field} ILIKE $1 ORDER BY id`,
          [`%${search}%`]
        )
      : await pool.query("SELECT * FROM characters ORDER BY id");
    res.json(results.rows);
  } catch (err) {
    console.error("getCharacters failed:", err);
    res.status(500).json({ error: "Could not load characters" });
  }
};

const getCharacterBySlug = async (slug) => {
  const results = await pool.query("SELECT * FROM characters WHERE slug = $1", [slug]);
  return results.rows[0];
};

const getCharacter = async (req, res) => {
  try {
    const character = await getCharacterBySlug(req.params.slug);
    if (!character) {
      return res.status(404).json({ error: "Character not found" });
    }
    res.json(character);
  } catch (err) {
    console.error("getCharacter failed:", err);
    res.status(500).json({ error: "Could not load character" });
  }
};

module.exports = { getCharacters, getCharacter, getCharacterBySlug };
