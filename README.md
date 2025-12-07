# MediaLog API

MediaLog is a small REST API I built using Flask and PostgreSQL so I could learn how to design a relational database and expose it through simple JSON endpoints. It lets a user store items in a personal collection and add categories, tags, creators, and their own reviews. The whole project focuses on the backend, including the database structure, the data relationships, and the CRUD routes.

---

## Live Deployment

Production URL:

```text
https://medialog-api.onrender.com/
```

The API is deployed on Render using a managed PostgreSQL database.

Insomnia files are included in `docs/insomnia` so the routes can be tested easily.

---

## Problem Statement

Collectors and hobbyists often store information about their media items in spreadsheets, notes, or simple lists. These methods make it difficult to organise items, apply multiple tags, track creators, record reviews, or filter a growing collection. The MediaLog database is designed to provide a structured way to manage items, categories, creators, tags, and user-generated reviews. By modelling these relationships properly, the system supports flexible organisation and easier retrieval of information while ensuring data consistency as the collection grows.

---

## Database System Choice

I chose PostgreSQL because my data has clear relationships. One user can have many items, and items can have many tags and creators. A relational database made this easier because I could use foreign keys and junction tables instead of storing lists inside a single field. SQLAlchemy helped a lot since it let me work in Python without writing raw SQL all the time.

### Why relational?

MediaLog has well-defined relationships, such as:

- 1 User → Many Items
- 1 Category → Many Items
- Many Items ↔ Many Tags
- Many Items ↔ Many Creators
- 1 User → Many Reviews

These are all natural fits for a relational model. Using PostgreSQL let me model this with foreign keys, join tables and simple unique constraints so things like tag names and creator names only exist once, and the links between tables handle the many-to-many parts. This reduces duplication and avoids inconsistencies.

### Non-relational databases

A document database like MongoDB stores nested objects inside each record. With this kind of data, tags and creators would be repeated inside every item document. If a tag changed, every item using it would need to be updated, which risks inconsistency. A relational model avoids that by storing shared values once and connecting them through junction tables.

SQLite is also relational, but it wasn’t ideal for deployment because I wanted to use the same database locally and in the cloud.

### Why PostgreSQL specifically

PostgreSQL provides:

- ACID guarantees
- strong data integrity
- reliable migrations
- good support through SQLAlchemy

It gave me a good balance between normalisation, data consistency and cloud support, without changing databases between development and deployment.

---

## Entity Relationship Diagram (ERD)

A full ERD is included in:

[Full ERD PDF](docs/medialogERD.pdf)

![ERD Diagram](docs/images/ERD.jpg)

The database was normalised from UNF to 3NF to remove repeating groups, eliminate partial and transitive dependencies, and then multi-valued attributes were moved into their own junction tables to avoid duplication and follow Fourth Normal Form (4NF) design principles.

I normalised the database step-by-step. First, I removed repeating groups by splitting multi-valued fields like tags and creators into separate rows so each value was stored on its own (UNF → 1NF). Then, I created separate tables for each main entity (`User`, `Category`, `Item`, `Tag`, `Creator`, `Review`) so that every column depended on the full key of that table instead of mixing different kinds of data together (1NF → 2NF).

Next, I cleaned up transitive dependencies by moving shared information, such as category names and user details, into their own tables and linking them with foreign keys (2NF → 3NF). Finally, I handled the two independent many-to-many relationships (items to tags and items to creators) using their own junction tables with constraints to avoid duplicated relationships. This removes multi-valued dependencies and follows the design principles of Fourth Normal Form (4NF) in a practical way.

### Normalisation Summary

| Normalisation Step | Key Action                                                                   | Why It Matters                                                                                     |
| ------------------ | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| UNF → 1NF          | Split repeating tag/creator lists into separate atomic rows                  | Ensures each cell holds a single value (atomic attributes).                                        |
| 1NF → 2NF          | Separated data into User, Category, Tag, Creator, Item, and Review tables    | Eliminates partial dependencies; each non-key depends on the whole key of its table.               |
| 2NF → 3NF          | Removed transitive dependencies via dedicated parent tables (User, Category) | Confirms all non-key attributes depend only on the primary key and not on other non-key fields.    |
| 3NF → 4NF (design) | Used `item_tags` and `item_creators` junction tables for multi-valued sets   | Resolves multi-valued dependencies and avoids repeating tags/creators per item (4NF-style design). |

---

## API Routes (CRUD)

Below are the main CRUD routes.

---

### Users

| Method | Route         | Description |
| ------ | ------------- | ----------- |
| POST   | `/users`      | Create user |
| GET    | `/users`      | List users  |
| GET    | `/users/<id>` | Get user    |
| POST   | `/login`      | User login  |

---

### Items

| Method | Route         | Description |
| ------ | ------------- | ----------- |
| POST   | `/items`      | Create item |
| GET    | `/items`      | List items  |
| GET    | `/items/<id>` | Get item    |
| PATCH  | `/items/<id>` | Update item |
| DELETE | `/items/<id>` | Delete item |

---

### Reviews

| Method | Route                 | Description   |
| ------ | --------------------- | ------------- |
| POST   | `/reviews`            | Create review |
| GET    | `/reviews`            | List reviews  |
| GET    | `/items/<id>/reviews` | Item reviews  |

---

### Tags

| Method | Route              | Description         |
| ------ | ------------------ | ------------------- |
| GET    | `/tags`            | List tags           |
| POST   | `/tags`            | Create tag          |
| POST   | `/items/<id>/tags` | Assign tags to item |

---

### Creators

| Method | Route                  | Description             |
| ------ | ---------------------- | ----------------------- |
| GET    | `/creators`            | List creators           |
| POST   | `/creators`            | Create creator          |
| POST   | `/items/<id>/creators` | Assign creators to item |

---

### Example Response

Example: GET `/items/2`

```json
{
  "id": 2,
  "title": "The Wheel of Time",
  "category_id": 2,
  "user_id": 1,
  "image_url": "https://example.com/wheel-of-time.jpg",
  "tags": ["Fantasy", "Adventure"],
  "creators": ["Robert Jordan"]
}
```

---

## Validation & DRY Principles

Keeping validation and session commits in helpers prevents repeated logic across routes and makes the API easier to maintain.

The API uses centralised helper functions to ensure clean validation:

- `get_json_or_error()`
  Handles invalid JSON input.

- `require_fields()`
  Ensures no required fields are empty.

- `require_positive_int()`
  Validates ID fields.

- `parse_optional_rating()`
  Validates rating range (1–5).

- `commit_session()`
  Manages DB commits and rollbacks.

### Global error handlers

- `404` — invalid route

- `500` — server error

Errors always return structured JSON:

```json
{
  "errors": ["Message here"]
}
```

### DRY Principles

Repeated logic is centralised using:

- input validation helpers
- session commit helper
- model → dict converters

This removes duplication and keeps endpoints clean and readable.

---

## Seed Data

Seed script: `seed.py`

It creates:

- 2 users
- 2 categories
- 2 items
- 4 tags
- 2 creators
- 2 reviews

This gives enough data to test all CRUD routes in Insomnia.

Run locally:

```bash
python seed.py
```

---

## Running the Project Locally

### Requirements

- Python 3.9+
- PostgreSQL
- Virtual environment

### 1. Clone the Repository

```bash
git clone git@github.com:c-joss/dev1002-medialog.git
cd dev1002-medialog
```

### 2. Create a Virtual Environment

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\activate
```

You should now see `(venv)` before your prompt.

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- Flask
- SQLAlchemy
- Flask-Migrate
- Psycopg2 (PostgreSQL driver)
- Other libraries used by the project

### 4. Install PostgreSQL

If you don’t already have PostgreSQL installed:

#### macOS (Homebrew)

```bash
brew install postgresql
brew services start postgresql
```

#### Ubuntu / Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

#### Windows

Download and install from:
https://www.postgresql.org/download/windows/

### 5. Create a Local Database

After installing PostgreSQL:

#### macOS / Linux

```bash
psql postgres
CREATE DATABASE medialog;
\q
```

#### Windows (PowerShell)

```powershell
psql -U postgres
CREATE DATABASE medialog;
\q
```

_Note: If your PostgreSQL username is different, replace postgres accordingly._

### 6. Configure Environment Variables

Create a `.env` file in the project root:

```ini
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/medialog
FLASK_APP=server.app
FLASK_ENV=development
```

_Tip: Use your actual database username/password._

On Windows PowerShell, you may prefer:

```powershell
$env:DATABASE_URL="postgresql://postgres:yourpassword@localhost:5432/medialog"
$env:FLASK_APP="server.app"
$env:FLASK_ENV="development"
```

### 7. Create Database Tables

This creates all tables defined in `models.py` using SQLAlchemy directly:

```bash
python init_db.py
```

or on Windows PowerShell:

```powershell
python .\init_db.py
```

### 8. Seed Initial Test Data

This inserts categories, items, tags, creators, and reviews so you can immediately test routes.

```bash
python -m server.seed
```

or on Windows:

```powershell
python .\seed.py
```

You should see output like:

```nginx
Database seeded successfully
```

### 9. Run the Server

```bash
flask run
```

The API will be available at:

```text
http://127.0.0.1:5000/
```

You should see:

```csharp
 * Running on http://127.0.0.1:5000/
```

---

### Testing with Insomnia

Insomnia test files are included in `docs/insomnia`

You can import the collection:

1. Open Insomnia
2. Click Import
3. Select Import Data > From File
4. Choose the .json file in docs/insomnia/

Two sets of tests are provided:

- Local tests (http://127.0.0.1:5000)
- Render tests (cloud endpoint)

This includes automated requests for:

- Users
- Items
- Reviews
- Tags
- Creators

Each request shows both:

- route
- example response

---

## Deployment

The production database uses the same structure and migrations as the local environment, which keeps the schema consistent across development and deployment.

- PostgreSQL database service on Render
- `DATABASE_URL` environment variable
- `flask db upgrade` for running migrations
- same models and Alembic history used locally and in production

---

## Tools Used

- Python + Flask
- SQLAlchemy
- Flask-Migrate
- PostgreSQL
- Render
- Insomnia for testing

---

## Feedback & Response

Feedback was gathered from two peers.

### Brando — User–Review Link

**Feedback**: Missing cardinality line from User → Review in ERD.

**Action**: Updated ERD to include the correct 1-to-many relationship.

### Amelia — Junction Tables & Problem Statement

**Feedback**: Check junction table connectors and add a problem statement.

**Action**: Confirmed correct M2M modelling and added the problem statement to the ERD/README.

Full log:

`docs/feedbacklog.md`

## Reflection

This project helped me practise normalising the data and using join tables in a real design. I also learned how to build a simple Flask API and deploy it online with PostgreSQL, instead of only running it locally, which made the whole workflow feel more practical.
