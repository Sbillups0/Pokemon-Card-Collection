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
