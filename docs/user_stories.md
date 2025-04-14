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
