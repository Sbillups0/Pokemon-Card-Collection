CREATE TABLE decks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    deck_name TEXT NOT NULL,
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE deck_cards (
    id SERIAL PRIMARY KEY,
    deck_id INTEGER NOT NULL,
    card_name TEXT NOT NULL,
    CONSTRAINT fk_deck_id FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);


-- Make sure card names are unique
ALTER TABLE cards
ADD CONSTRAINT cards_name_unique UNIQUE (name);

-- Now create the foreign key
ALTER TABLE deck_cards
ADD CONSTRAINT fk_deck_cards_card
FOREIGN KEY (card_name) REFERENCES cards(name) ON DELETE CASCADE;


-- Remove duplicates, keeping only one of each (deck_id, card_name)
DELETE FROM deck_cards a
USING deck_cards b
WHERE a.ctid < b.ctid
  AND a.deck_id = b.deck_id
  AND a.card_name = b.card_name;


-- Run these one by one:

ALTER TABLE deck_cards DROP CONSTRAINT IF EXISTS deck_cards_pkey;
ALTER TABLE deck_cards DROP COLUMN IF EXISTS id;
ALTER TABLE deck_cards ADD PRIMARY KEY (deck_id, card_name);
ALTER TABLE deck_cards ADD CONSTRAINT fk_deck_cards_deck
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE;
ALTER TABLE deck_cards ADD CONSTRAINT fk_deck_cards_caard
    FOREIGN KEY (card_name) REFERENCES cards(name) ON DELETE CASCADE;

