API Specification
1. Get Pack Catalog
   - Returns a catalog list of currently offered packs. Includes information related to quantity, name, and cost.
   - GET /packs/catalog ---> Grass_Pack (5): 20 Coins, Water_Pack (5): 20 Coins
2. Get Collection(user_id, Type: Optional addition, if not included, will return entire collection)
   - Returns a list of the user's card collection based on their provided user_id. (Along with associated information, like total cost)
   - If extra information is included in the proper structure, it returns a subset of the user's collection. (Type: Water Pokemon)
   - GET /users/user_id/collection/Type = "Grass" ---> [Venusaur, Celibee, Rowlett]
3. Get Card(card_name)
   - Returns information related to the card_name passed into the endpoint. (Type, Cost, Pack)
   - GET /cards/card_name = "Charizard" ---> Charizard (50): Fire, Fire_Pack
4. Display/Put Card(user_id, card_name)
   - Adds a card to the user's display if they have space and have it in their collection.
   - POST /users/user_id/display/card_name
5. Sell Card(user_id, card_name, quantity)
   - Sells an individual card based on the provided card_name, adding coins to the user's inventory. (As long as the user has one in their collection)
   - POST /users/user_id/sell/card_name
6. Create/Put Deck(user_id, card_name[5], deck_name)
   - Creates a deck based on the provided list of card_names, adding it to user's deck collection. (Must include at 5 cards in a deck)
   - POST /users/user_id/create_deck/deck_name/card_name[5]
7. View/Get Decks(user_id)
   - Returns a list of the user's current decks. (Users may have no more than 3 decks total)
   - GET /users/user_id/decks ---> [Grassy, Mega Grassy, Mega Grass EX]
8. Buy Pack(user_id, pack_name)
   - Adds pack to user_id's inventory, subtracting the corresponding coin cost.
   - GET /users/user_id/purchase_pack/pack_name
9. Open Card Pack(user_id, pack_name)
   - Returns a list of 5 cards, adding them to the user's collection and subtracting the pack's coin cost. The cards are pulled randomly based on the provided pack_name.
   - POST /users/user_id/open_pack/pack_name ---> [Oddish, Rowlett, Shaymin, Snivy, Leafeon EX]
10. Battle(user_id, deck_name)
   - As long as the user provides a valid deck_name, a text message describing the battle is returned. The user may gain gold based on the results of the battle. (Higher deck value = Better odds)
   - POST /users/user_id/battle/deck_name ---> "you got demolished, sucks to suck. No gold gained"
   - POST /users/user_id/battle/deck_name ---> "Lightwork, gained 50 gold"
11. Get Inventory(user_id)
   - Returns list of packs in the user's inventory, along with their quantities.
   - GET /users/user_id/inventory ---> [Grass(5), Water(2), Fire(7)] 


