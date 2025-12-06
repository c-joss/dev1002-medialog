# Feedback Log

## Brando — User–Review Connector

**Feedback received:**  
Brando pointed out that it looked like there should be a line from **User → Review** in the ERD, as the cardinality wasn’t shown.

**Action taken:**  
I updated the ERD to include the correct **1 User → Many Reviews** relationship, so the diagram now matches the intended data model and the relationship summary table.

**Reflection:**  
This was a helpful catch, and the change was straightforward to apply. Everything in the ERD is now accurate and complete for this relationship.

---

## Amelia — Junction Tables & Problem Statement

**Feedback received:**

- The junction tables (`item_creator` and `item_tag`) shouldn’t have optional connectors on their foreign keys. Even though tags/creators for an item are optional, both foreign keys in the junction tables are required to form the composite primary key.
- Including a brief description or problem statement outlining the purpose of the database (e.g. favourite TV shows, movies, albums, multiple media types, etc.) would help with conceptualisation.

**Action taken:**

I reviewed all junction-table relationships to ensure they correctly represent the intended many-to-many structure. Each junction table already shows a mandatory “1” at the item, tag, and creator ends, and an optional many at the junction-table ends. This is the correct modelling pattern:

- Each junction record must link to exactly one parent (Item/Tag/Creator).
- Each parent entity may have zero or many related junction records.
  Because this behaviour was already represented accurately, no changes were needed to the cardinality.
  I will also add a short problem statement to describe the purpose of the MediaLog database.

**Reflection:**  
Reviewing the junction-table relationships confirmed they were already structured appropriately for many-to-many modelling. The suggestion to add a problem statement was helpful for improving the clarity of the documentation.
