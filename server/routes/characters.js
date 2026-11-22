const express = require("express");
const { getCharacters, getCharacter } = require("../controllers/characters");

const router = express.Router();

router.get("/", getCharacters);
router.get("/:slug", getCharacter);

module.exports = router;
