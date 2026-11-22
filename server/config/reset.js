const { pool } = require("./database");
const characters = require("../data/characters");

const createTableQuery = `
  DROP TABLE IF EXISTS characters;

  CREATE TABLE characters (
    id          SERIAL PRIMARY KEY,
    slug        VARCHAR(100) NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    game        VARCHAR(100) NOT NULL,
    role        VARCHAR(100) NOT NULL,
    power       INTEGER      NOT NULL CHECK (power BETWEEN 0 AND 100),
    description TEXT         NOT NULL,
    avatar_seed VARCHAR(100) NOT NULL
  );
`;

const insertQuery = `
  INSERT INTO characters (slug, name, game, role, power, description, avatar_seed)
  VALUES ($1, $2, $3, $4, $5, $6, $7)
`;

const reset = async () => {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query(createTableQuery);
    console.log("🎮 characters table created");

    for (const c of characters) {
      await client.query(insertQuery, [
        c.slug, c.name, c.game, c.role, c.power, c.description, c.avatarSeed,
      ]);
      console.log(`✅ seeded ${c.name}`);
    }

    await client.query("COMMIT");
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  } finally {
    client.release();
    await pool.end();
  }
};

reset().catch((err) => {
  console.error("⚠️ reset failed:", err.message);
  process.exitCode = 1;
});
