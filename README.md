# WEB103 Project 2 - *GameHall*

Submitted by: **Anurag Bheemappa Gnanamurthy**

About this web app: **GameHall is a listicle web app showcasing iconic video game characters, now served from a Render PostgreSQL database. Each character has a name, game, role, power rating, description, and avatar. The frontend is plain HTML, CSS, and JavaScript that fetches the roster from an Express API backed by Postgres. Users can browse the roster, search it by name, game, or role, and open a dedicated detail page for each character.**

Time spent: **X** hours

## Required Features

The following **required** functionality is completed:

<!-- Make sure to check off completed functionality below -->
- [x] **The web app uses only HTML, CSS, and JavaScript without a frontend framework**
- [x] **The web app is connected to a PostgreSQL database, with an appropriately structured database table for the list items**
  - [ ] **NOTE: Your walkthrough added to the README must include a view of your Render dashboard demonstrating that your Postgres database is available**
  - [ ]  **NOTE: Your walkthrough added to the README must include a demonstration of your table contents. Use the psql command 'SELECT * FROM tablename;' to display your table contents.**


The following **optional** features are implemented:

- [x] The user can search for items by a specific attribute

The following **additional** features are implemented:

- [x] Search lets the user choose which attribute to search (name, game, or role), and matching is case-insensitive and partial (`ILIKE`)
- [x] Detail pages for unknown characters return a real HTTP 404 page (checked against the database)
- [x] REST API: `GET /api/characters`, `GET /api/characters?search=…&field=…`, `GET /api/characters/:slug`
- [x] One-command database reset and seed script (`npm run reset`) that runs in a transaction
- [x] Arcade character-select theme with a responsive card grid, styled with Picocss

## Video Walkthrough

Here's a walkthrough of implemented required features:

<img src='http://i.imgur.com/link/to/your/gif/file.gif' title='Video Walkthrough' width='' alt='Video Walkthrough' />

<!-- Replace this with whatever GIF tool you used! -->
GIF created with ...  GIF tool here
<!-- Recommended tools:
[Kap](https://getkap.co/) for macOS
[ScreenToGif](https://www.screentogif.com/) for Windows
[peek](https://github.com/phw/peek) for Linux. -->

## Notes

This refactors the Unit 1 GameHall app. EJS server rendering was replaced with static HTML pages. Those pages load their data from a JSON API with vanilla JavaScript (`fetch` plus DOM APIs, with no `innerHTML`). The data now lives in PostgreSQL.

**Project structure**

```
client/            # frontend: static HTML, CSS, vanilla JS
  index.html       # roster + search
  character.html   # detail view (/characters/:slug)
  404.html
  src/css/style.css
  src/js/characters.js, src/js/character.js
server/            # backend: Express + pg
  server.js
  config/database.js   # pg Pool (DATABASE_URL, SSL for Render)
  config/reset.js      # creates + seeds the characters table
  controllers/characters.js
  routes/characters.js
  data/characters.js   # seed data
```

**Table schema**

```sql
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
```

**Running locally**

1. Create a free PostgreSQL instance on [Render](https://render.com) and copy its **External Database URL**.
2. `cp .env.example .env` and paste the URL into `DATABASE_URL`.
3. `npm install`
4. `npm run reset` creates the table and seeds it.
5. `npm start`, then open http://localhost:3001

All queries are parameterized. The searchable column is checked against an allowlist, so user input never reaches the SQL text.

## License

Copyright 2026 Anurag Bheemappa Gnanamurthy

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

> http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
