import sqlalchemy
import os
import dotenv
from faker import Faker
import random
import numpy as np
from src.api import auth
from src import database as db
from src.api import packs

def generate_a_bajillion_users():
    num_users = 100000
    fake = Faker()
    Faker.seed(0)

    with db.engine.begin() as conn:
        all_cards = conn.execute(sqlalchemy.text("""
            SELECT cards.name, cards.price FROM cards
            ORDER BY cards.price ASC;
            """)).all()

        print("creating fake users...")
        for i in range(num_users):
            #create 1 user
            username = fake.user_name()
            rand_coins = abs(int(np.random.normal(loc=100, scale=20)))
            user_id = conn.execute(sqlalchemy.text("""
            INSERT INTO users (username, coins) VALUES (:username, :coins) RETURNING id;
            """), {"username": username, "coins": rand_coins}).scalar_one()
            
            #create 10 cards in the collection of the new user
            for i in range(10):
                chosen_card = packs.weighted_random_choice(all_cards)
                conn.execute(sqlalchemy.text("""
                INSERT INTO collection (user_id, card_id, quantity) 
                VALUES (:user_id, :card_id, 1)
                ON CONFLICT (user_id, card_id)
                DO UPDATE SET quantity = quantity + 1;
                """), {"user_id": user_id, "card_id": chosen_card})

            #create 1 deck for each user if they have enough unique cards
            cards_owned = conn.execute(sqlalchemy.text("""
                SELECT col.card_id, cards.card_name FROM collection AS col
                JOIN cards on cards.id = col.card_id
                WHERE col.user_id = :user_id
                """),
                {"user_id": user_id}).all()
            
            card_names = [card.card_name for card in cards_owned]
            if (len(cards_owned) >= 5):
                rand_deck = random.choices(card_names, k=5)
                deck_name = '_'.join(fake.words())
                deck_id = conn.execute(sqlalchemy.text("""
                INSERT INTO decks (user_id, deck_name) VALUES (:user_id, :deck_name) RETURNING id;
                """), {"user_id": user_id, "deck_name": rand_coins}).scalar_one()
                
                for card_name in rand_deck:
                    conn.execute(sqlalchemy.text("""
                    INSERT INTO deck_cards (deck_id, card_name) VALUES (:deck_id, :card_name);
                    """), {"deck_id": deck_id, "card_name": card_name})

            #give each user 1 pack in inventory
            all_packs = conn.execute(sqlalchemy.text("SELECT id FROM packs")).scalars().all()
            rand_pack = random.choice(all_packs)
            conn.execute(sqlalchemy.text("""
            INSERT INTO inventory (user_id, pack_id, quantity) VALUES (:user_id, :pack_id, 1);
            """), {"user_id": user_id, "pack_id": rand_pack})

            #insert 0-4 cards into the user's display
            if (len(cards_owned) < 5):
                display_num = np.random.randint(0, len(cards_owned))
            else:
                display_num = np.random.randint(0, 5)
            
            while (display_num > 0):
                try:
                    display_card = random.choice(cards_owned)
                    conn.execute(sqlalchemy.text("""
                        INSERT INTO display (user_id, card_id) 
                        VALUES (:user, :card_id);
                        """), {"user_id": user_id, "card_id": display_card})
                    display_num -= 1
                except sqlalchemy.exc.IntegrityError:
                    continue
    