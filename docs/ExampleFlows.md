## Fire Deck Creation and Battle Example Flow

Timmy the witiful battler wants to prep for his pokemon battle competition by creating a fire type deck using the most powerful pokemon.

She filters the card collection such that only the fire type pokemon cards are shown using

- GET /users/timmy/collection. Her call gives her the fire pokemon cards available: Charizard, Blaziken, Reshiram, Dragonite, and Flareon.

She wants to use these pokemon to make a deck. She uses her user id along with

- POST /users/timmy/create_deck/fire_deck/[Charizard, Blaziken, Reshiram, Dragonite, and Flareon].

The server responds that the deck has been created and added to her account. Timmy is confident with all the strong cards in the deck and decides to go battle a user. He runs the API call
-POST /users/timmy/battle/fire_deck.

The server is able to process his battle request and Timmy's Fire Lords fought magnificiently and defeated the foe. The win has earned Timmy 600 Pokemon coins and a rare card reward.

## Collector Example Flow

Misty, a dedicated water Pokemon card collector, isn't interested in battling. Instead, she is looking very hard and closely for new cards to grow collection.
Especially, the **"Prismatic Evolution"** pack. She's hoping to pull rare evolutions of classic Pokémon to expand her collection and display her favorites.

First, Misty request a catalog to see the latest packs available in the catalog by calling `GET /packs/catalog`.
She sees in the catalog, there is a Prismatic Evolution (200 coins), Scarlet & Violet (150 coins), and Stellar Crown (75 coins).

Misty decides to buy the Prismatic Evolution pack, open the pack, and display her favorite cards. To do so she:

- starts by calling `POST /users/misty_id/purchase_pack`
- then Misty decides to open her new exciting pack, by calling `POST /users/misty_id/open_pack/Pristmatic_Evolution/1`
- she decides to view her collection making another call `GET /users/misty_id/collection`
- finally she shows off her favorite pull - **Prismatic Umbreon** by calling `POST /users/misty_id/display/Prismatic_Umbreon`

Misty is satisfied with her radiant new additions and dazzling display.

## Selling and Expanding Collection Example Flow

AZ has been out of the game a while, but is looking to start building his collection again. He's interested in getting some valuable and newer cards for his collection, and he's willing to sell off some of his older cards he doesn't care that much about anymore.
AZ starts by calling `GET /packs/catalog` to see some of the available options, eventually setting his eyes on the Paldean Fates expansion. He sees that each pack is 150 coins.

- AZ calls `GET /users/az/collection` to view his collection and decide what cards to sell so he can afford the packs.
- He calls `POST /users/az/sell/"Flygon"` to sell one of his old Flygon cards.
- With the earnings from that sale, AZ calls `POST /users/az/purchase_pack/"Paldean Fates"`.
- He then calls `POST /users/misty/open_pack/"Paldean Fates:/` to open his pack.
- Since he isn't familiar with the newer cards from the pack, he calls `GET /packs/catalog/"Paldean Fates"/"Armarouge"` to learn more info about one of the cards he pulled.
- Finally, he puts the card in his display by calling `POST /users/az/display/"Armarouge` to let everyone know he's back in town.

AZ continues researching ways to improve his collection in the meantime.

## Pack Collecting Example Flow

Lina is a new player who just started her journey. She's excited to begin collecting and wants to start by purchasing some beginner-friendly packs to build her inventory.
Lina begins by calling `GET /packs/catalog` to see what kinds of packs are available. She sees options like Grass_Pack and Water_Pack, both priced at 20 coins each.

- She registers as a user with a username `POST /users/register/user_lina`
- She decides to buy one of each, so she calls: `POST /packs/users/lina/purchase_pack/Jungle/1`, `POST /packs/users/lina/purchase_pack/Basic/1`
- To make sure the purchases went through, she calls: `GET /inventory/audit`

Lina is ready to start opening packs and seeing what surprises await her inside!
