require("./config/dotenv");
const express = require("express");
const path = require("path");
const charactersRouter = require("./routes/characters");
const { getCharacterBySlug } = require("./controllers/characters");

const app = express();
const PORT = process.env.PORT || 3000;
const CLIENT_DIR = path.join(__dirname, "../client");

app.use("/src", express.static(path.join(CLIENT_DIR, "src")));

app.use("/api/characters", charactersRouter);

app.get("/", (req, res) => {
  res.sendFile(path.join(CLIENT_DIR, "index.html"));
});

// Check the database before serving the detail page so unknown slugs get a real 404.
app.get("/characters/:slug", async (req, res, next) => {
  try {
    const character = await getCharacterBySlug(req.params.slug);
    if (!character) return next();
    res.sendFile(path.join(CLIENT_DIR, "character.html"));
  } catch (err) {
    next(err);
  }
});

app.use((req, res) => {
  res.status(404).sendFile(path.join(CLIENT_DIR, "404.html"));
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("Something went wrong. Check the server logs.");
});

app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});
