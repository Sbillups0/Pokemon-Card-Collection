User Stories and Exceptions

1: As a professional card collector, I want to display my favorite cards, so that everyone can see my awesome collection. (Displaying Cards)

- Exceptions:
  - The user tries to display a card not in their collection (Or an invalid card name)
    - The request will return an error, and ask for a different card to display.
  - The user's display is full
    - The request will return an error, and tell them they must remove a card first.

2: As an uber-intelligent finance-bro, the only thing I care about are the coins in my account. I want to be able to sell all of my cards at once and skyrocket the amount of coins I have. (Sell All Cards)

- Exceptions:
  - The user has no cards to sell. (Empty collection)
    - The request will return an error, and tell the user their collection is empty.

3: As any professional Pokemon trainer such as myself would know, the only way to make a deck is to prioritize a particular type. Therefore, I want to sort my collection of cards for only water-type Pokemon. (View Collection)

- Exceptions:
  - The user has no water-type pokemon in their collections (Returns an empty list)
    - Displays a message informing the user that they have no Pokemon of that type.
  - The user enters a "type" that does not exist
    - The request will return an error, and tell the user that the requested type does not exist.

4: As a budget-conscious trainer, I want to buy card packs using my PokéCoins so that I can expand my collection without going broke. (Buy Card Packs)

- Exceptions:
  - The user tries to buy a pack but does not have enough coins.
    - The request will return an error and inform the user that they do not have sufficient coins.
  - The user tries to buy a non-existent or unavailable pack.
    - The request will return an error and let the user know that the requested pack does not exist.

5: As a curious collector, I want to view the details of a specific card, so that I can learn more about its type, stats, and rarity. (View Card Details)

- Exceptions:
  - The user requests a card that does not exist in the database.
    - The request will return an error and prompt the user to check the card name.
  - The user does not specify a card name.
    - The request will return an error asking the user to provide a valid card name.

6: As a tactical battler, I want to create a custom deck from the cards in my collection so that I can prepare for future matches. (Create Deck)

- Exceptions:
  - The user tries to add a card they do not own to their deck.
    - The request will return an error and notify the user that the card is not in their collection.
  - The user tries to add more cards than the allowed deck size.
    - The request will return an error and tell the user to remove cards before adding new ones.

7: As an irresponsible whale, I want to buy one type of pack continuously until I can get the card I want. (Buy certain pack until obtained card)

- Exceptions:
  - The user tries to buy a pack but does not have enough coins.
    - The request will return an error and inform the user that they do not have sufficient coins.

8: As a collaborative collector, I want to trade a card to my friend in exchange for one of their cards which I want. (Trade with friend)

- Exceptions:
  - The user puts up a card for trade that they do not own.
    - The request will return an error and notify the user that the card is not in their collection.
  - The user tries to trade with a user that does not exist.
    - The request will return an error and inform the user that the specified user does not exist.
  - The user tries to trade with a user that is not on their friends list.
    - The request will return an error and inform the user that they are not friends with the specified user.
  - The user has no cards to trade. (Empty collection)
    - The request will return an error, and tell the user their collection is empty.

9: As a wily merchant, I want to understand the value of my collection. Therefore, I want to know the rarity and market price of all my cards together. (View collection value)

- Exceptions:
  - The user has no cards to view. (Empty list)
    - Displays a message informing the user that they have no cards to view.

10: As someone who is currently broke, I need the most money I can get, but I don't want to give up the little cards that I have. So I want to sell only my most expensive card. (Sell individual Card)

- Exceptions:
  - The card is not in the user's collection (Empty list)
    - Displays a message informing the user to try another card.

11: As a professional battler, I only want to fight to make money. (Battle)

- Exceptions:
  - The user has no valid deck (Empty list)
    - Displays a message informing the user that they must have a full deck to battle.

12: As an avid art collector, I only care about my most expensive cards. Nothing below 1000 Pokecoins will suffice. Therefore, I want to sell all of my cards below a certain Pokecoin threshold. (Sell All Cards Less Than X)

- Exceptions:
  - The user has no cards to sell. (Empty list)
    - Displays a message informing the user that they have no cards to sell.
