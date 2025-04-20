API Specification
1. Get Pack Catalog
   - Returns a catalog list of currently offered packs. Includes information related to quantity, name, and cost.
2. Get Collection
   - Returns a list of the user's card collection based on their provided user_id. (Along with associated information, like total cost)
   - If extra information is included in the proper structure, it returns a subset of the user's collection. (Type: Water Pokemon)
3. Get Card
   - Returns information related to the card_name passed into the endpoint. (Type, Cost, Quantity, etc)
4. Display/Put Card
   - Adds a card to the user's display if they have space and have it in their collection.
5. Sell All Cards
   - Sells entire collection, adding coins to the user's inventory
   - Additional information passed can be used to sell below a certain price threshold. (Sell_All_Cards(100) -> Sell all cards less than 100 coins)
6. Sell Card
   - Sells an individual card based on the provided card_name, adding coins to the user's inventory. (As long as the user has one in their collection)
7. Create Deck
   - Creates a deck based on the provided list of card_names, adding it to user's deck collection. (Must include at 5 cards in a deck)
8. View Decks
   - Returns a list of the user's current decks. (Users may have no more than 3 decks total)
9. Open/Get Card Pack
   - Returns a list of 5 cards, adding them to the user's collection and subtracting the pack's coin cost. The cards are pulled randomly based on the provided pack_name.
10. Battle
   - As long as the user provides a valid deck_name, a text message describing the battle is returned. The user may gain gold based on the results of the battle. (Higher deck value = Better odds)


