## Fire Deck Creation and Battle Example Flow

Timmy the witiful battler wants to prep for his pokemon battle competition by creating a fire type deck using the most powerful pokemon. She filters the card collection such that only the fire type pokemon cards are shown using Get Collection(user_id = Timmy, filter = {type: "Fire"}). Her call gives her the fire pokemon cards available: Charizard, Blaziken, Reshiram, Dragonite, and Flareon. She wants to use these pokemon to make a deck. She uses her user id along with Create Deck(deck_name = "Fire Lords", user_id = Timmy, cards = ["Charizard", "Blaziken", "Reshiram", "Dragonite", "Flareon"]). The server responds that the deck has been created and added to her account. Timmy is confident with all the strong cards in the deck and decides to go battle a user. He runs the API call Battle(user_id = Timmy, deck_name = "Fire Lords"). The server is able to process his battle request and Timmy's Fire Lords fought magnificiently and defeated the foe. The win has earned Timmy 600 Pokemon coins and a rare card reward.

## Collector Example Flow

Misty, a dedicated water Pokemon card collector, isn't interested in battling. Instead, she is looking very hard and closely for new cards to grow collection.
Especially, the **"Prismatic Evolution"** pack. She's hoping to pull rare evolutions of classic Pokémon to expand her collection and display her favorites.

First, Misty request a catalog to see the latest packs available in the catalog by calling `GET /packs/catalog`.
She sees in the catalog, there is a Prismatic Evolution (200 coins), Scarlet & Violet (150 coins), and Stellar Crown (75 coins).

Misty decides to buy the Prismatic Evolution pack, open the pack, and display her favorite cards. To do so she:

- starts by calling `POST /users/misty/purchase_pack`
- then Misty decides to open her new exciting pack, by calling `POST /users/misty/open_pack`
- she decides to view her collection making another call `GET /users/misty/collection`
- finally she shows off her favorite pull - **Prismatic Umbreon** by calling `POST /users/misty/display`

Misty is satisfied with her radiant new additions and dazzling display.
