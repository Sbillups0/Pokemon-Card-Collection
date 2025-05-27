# Code Review Comments and Updates

## `battle.py`

### Review Comment
- `.one()` can raise an exception if no result is found before checking for deck existence.
- **Suggestion**: Use `.fetchone()` instead and check if the result is `None` before accessing the value.

### battle.py has been update for the above review comment

## catalog.py

### Review comments
- In catalog.py, I would suggest in create_catalog to add either a warning log or raise an exception if the catalog returns empty.
- In create_catalog, I would suggest adding an ORDER BY for this query: SELECT name, price FROM packs to return the packs that are expected with that call and in an order that is pre-determined. **

### catalog.py has been updated for the above review comments 

## collection.py

### Review comments

- In collection.py, in two different routes, you use the function name get_collection, which may cause an error or lead to confusion when distinguishing between functions. I recommend changing one of these function names to be more descriptive for their respective routes.
- I also think that both routes using get_collection should be @router.get instead of @router.post because they are read-only.

### collection.py has been updated for the above review comments 

## decks.py

### Review comments
In decks.py, you raise an exception like this: if not check_user_exists(user_id):
raise HTTPException(status_code=404, detail="User not found")
This is redundant because check_user_exists already raises an exception on its own, so it can be called just like this: check_user_exists(user_id)

Also in create_deck, you have this query: 
```
connection.execute(
sqlalchemy.text("""
INSERT INTO deck_cards (deck_id, card_name)
VALUES (:deck_id, :card_name)
RETURNING id
"""),
```
but id is never used. You can either use id for something later, or you don't need to return it.

### collection.py has been updated for the above review comments 

## cards.py

### Review comments
- In cards.py, in the sell_card_by_name function, instead of using the design of if owned.quantity == req.quantity: DELETE else: UPDATE, I would combine it into one query of UPDATE... RETURNING, which seems to make it clearer and more readable.
- There is duplicated code in cards.py and packs.py. This can be rewritten as a function that both can call individually.

     In cards.py
  ```
    def check_user_exists(user_id: int):
        with db.engine.connect() as conn:
            result = conn.execute(
                sqlalchemy.text("SELECT id FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="User not found")
  ```
  - Also move up where you check if the user exists or not in sell by card name before checking their quantity; The not enough cards exception might be caused by the user not existing/bad input
  - In cards.py, the sell_card_by_name endpoint allows selling cards that are currently in decks. This could lead to invalid decks where users have decks containing cards they no longer own. The endpoint should either prevent selling cards that are in decks or remove the cards from decks when sold.
  - In sell by card name, it might be helpful to tell the user how many of that card they own in the exception itself since they can’t see the printed outputs
  - In both sell card by name and get card by name when raising the error for card not found, it would be good to also include a sentence about how the name should be formatted (capitalized) because passing in the card name with all lowercase letters means that no card_id is returned
  

### cards.py has been updated for the above review comments 

### Review comments not accepted
- Along similar lines in cards.py] rename the endpoint for sell_card_by_name from /users/{user_id}/sell/{card_name}to /sell/{user_id}/{card_name}

  This will not be RESTful. We are grouping all actions that are user centric under users. Changing this as per review comments will move away from this understanding

- Not all database transactions are atomic. For example, sell_card_by_name in cards.py checks collection, updates or deletes from collection, and then updates the user's coins all in different transactions when they should be within the same transaction. That way if one fails they all get rolled back instead of having an inconsistent change of state.

  All transaction are performed using db.engine.begin(). This ensures that whenever a database transaction is started it happens in the same transaction.

## display.py

### Review comments
- In display.py, in the first query, you should also filter by user_id, and use this: WHERE ca.name = :card_name AND co.user_id = :user_id. This makes it so that each user can only get their own collection.

### display.py has been updated for the above review comments 

### Review comments not accepted
- In display.py, there's no validation to prevent displaying the same card multiple times. A user could add the same card to their display multiple times. This doesn't make sense from a user interface perspective. The endpoint should check if a card is already being displayed before adding it again.
- In the case where a user’s display is both full and they’re adding a card that is already in display it would be more useful to know that that card is already in the display than that their display is full so consider switching the ordering of the http exceptions

     This is already taken care in the below code segment
  
    ```
    if len(in_collection) == 0:
        raise HTTPException(status_code=404, detail="Card not in user's collection")
    elif len(current_display) == 4:
        raise HTTPException(status_code=403, detail="User's display is full")
    elif card_name in current_display:
        raise HTTPException(status_code=403, detail="Card is already in user's display")
    ```

## packs.py

### Review comments
- Packs.py: In the queries, you are using lists of dictionaries: [{"pack_name": pack_name}] and [{"user_id": user_id, "card_name": chosen_card}], the lists aren't needed, you can just make them plain dictionaries; {"pack_name": pack_name} and {"user_id": user_id, "card_name": chosen_card}.
- Packs.py: If owned packs is None, you should raise an exception as well. Change this: if owned_packs < pack_quantity: raise HTTPException(...) to if owned_packs is None or owned_packs < pack_quantity: raise HTTPException(...)
- Packs.py: I would switch your for loop structure. You currently have: for i in range(pack_quantity): with db.engine.begin() as connection. I would switch it to: with db.engine.begin() as connection: for i in range(pack_quantity). This change in order would have the for loop inside the single db connection, making it so that a new connection isn't opened every iteration of the for loop.
- In open packs you can simplify the first query if you just store the result of check_pack_exists in a variable since that function returns an id if the pack exists
- Consider moving everything under opening packs for number of packs opened to be in the same transaction as everything else so that if something fails in this part it’ll also rollback the updates to quantity inventory
- If you save the pack id, in your query that returns packs you can instead just use the pack id instead of the name (the query from lines 92-99 in packs.py)
- In purchase packs you should check if the user exists earlier in the transaction (before getting pack data) so if the user doesn’t exist you’re not doing other queries from the database
-
 ```
def check_user_exists(user_id: int):
    with db.engine.connect() as conn:
        user = conn.execute(
            sqlalchemy.text("SELECT id FROM users WHERE id = :id"),
            {"id": user_id}
        ).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
```
In packs.py you have a for loop with the database connection inside of it. If I'm not mistaken this is much worse than having the for loop inside the database connection block.

```
for i in range(pack_quantity):
    with db.engine.begin() as connection:
        packs = connection.execute(...)
```
There is a possible race condition in the open_packs function. I believe the problem can occur in the following scenario:
Two requests come in at about the same time.

### packs.py has been updated for the above review comments

## user.py

### Review comments
- In register user on line 31 the column for username is capitalizes as ‘Username’ which might be causing problems when registering a user that already exists. When trying to register with a username that exists a 500 internal server error occurs instead of raising the http exception that the username exists

### user.py has been updated for the above review comments

## inventory.py

### Review comments
- I think that the Get Inventory endpoint should also return how many coins I have. It was hard to know how many coins I had when testing locally.
- In get_inventory it’s probably best if you check if the user exists or not (When I passed in a larger user_id (30) because my user_id was 12 it just returned an empty catalog; if the user doesn’t exist it would be nice to return a message saying that the user doesn’t exist)
- The Get Inventory endpoint should return the user's coin balance. Currently, there's no easy way to check how many coins you have, which makes it difficult to plan purchases or know when you can afford packs. As of right now I just have to trial and error my way through it.

### inventory.py has been updated for the above review comments




- 




  


















It would be good to have a check for if it is a valid type or not in get_collection in collection.py

In get collection it would be useful to have some kind of formatting function for the type that is passed in. When I try to look for the ‘normal’ cards I own I get an empty string but when I look for cards of type “Normal” I can see the cards. It would be useful to include a message on the formatting of the type and then also run a formatter function on what is passed in as well

In creating deck when you check if a deck with that name exists make sure your exception specifies that the deck name already exists since it’s not necessarily that combination of cards

There are redundant checks for invalid cards after getting deck id in create_deck in decks.py(lines 82-96 seem like a copy paste of lines 53-68 and don’t seem to serve any additional purpose)

In create decks the check for non existent cards only checks if the card doesn't exist at all in the database. It should also check for if the user owns those cards.

It would be nice if there was a check for if they already have the max amount of decks before creating a new deck instead of letting the creation of the deck go through and raising an error when trying to view the decks




I would double check the code for check_pack_exists because when I tried opening a pack that was non existent by not capitalizing the pack name it resulted in a 500 internal server error instead of raising an exception (nothing stands out from this code so I’m not sure why the exception isn’t being raised) (The code works properly for purchasing a pack, so maybe you might just need to have that piece of code in the function for check_pack_exists)


Not sure if this is intentional or not but I'm not able to view the battle and display endpoints on the render so I couldn’t test those endpoints

Didn’t seem like there was a schema for the display table in schema.sql and the alembic revisions so make sure to add that somewhere (But from the code for the endpoint I think you would just need to have a user_id and card_id column and the primary key would be the tuple of both of those values)

It would be cool to add a get display endpoint where you can pass in a username and see the cards they have in display and also an edit display endpoint

The functions in collection.py should be marked as get endpoints instead of post endpoints since nothing is being added to the database (both of them are currently shown as post endpoints)

Additionally for the endpoints in collection.py you don’t need /get in the endpoint url, having /{user_id} and /{user_id}/{type} would be fine

In get collection by type it would be good to check if it is a valid type of pokemon before searching the database (You could create a new table for the different types and query that to get a type_id that you then use for the rest of the queries) (Also raising an exception if it is not a recognized type would be good instead of just returning an empty list so the user knows why they are receiving and empty list)

For get catalog, when different packs are added, I don’t see the need to limit the amount of packs you’re showing that are available since it just would return them in some arbitrary order and there is no way to check if a user would be purchasing a pack that was actually on the catalog (If you wanted to limit the amount of packs shown, I’d recommend adding an active attribute to each pack which would determine if you offer it on the catalog and also if a user can purchase it)

For deck_cards you wouldn’t need an id column -> the primary key would just be the (deck_id, card_name) tuple

It would be helpful to check for combinations of cards in a deck for create_deck, you could create a new table that stores the different card combinations a user has in a deck (Where you insert 5 card id/names and it returns a deck id for the card combination (instead of just having a deck id returned on the deck name and user id combination))(You could always have the card insertion order be in ascending card id order/alphabetical order of card names so that if they’re trying to insert the same combination of cards you catch that)

In create deck I was confused at first on how to pass in the five card names, it might be helpful if instead of taking in a list of strings you took in exactly five strings which would also help later on since you check that there is exactly five cards passed

In create deck, in addition to the check for nonexistent cards you should also be checking for if the user owns those cards, right now users can create decks with cards as long as they exist even if they don't own any cards themselves

When I look for what decks I have, it just returns the name of the deck - it would be nice to have an endpoint that allows me to see the cards are in which deck

Since there is a limit to how many decks a user can have, it would be nice to also have endpoints for users to modify or delete their current decks

It would be helpful to add an endpoint that returns all the current types of cards that exist so users know which card types they can search for

Make sure to be consistent with the naming of the endpoints (ex. If you’re going to add a /user before every /{user_id} (Decks and packs have the endpoint urls implemented as decks/users/{user_id}/… and packs/users/{user_id}/… while collection and inventory just only have user_id (ex. /inventory/{user_id}/audit))

Consider renaming the open packs endpoint from "/users/{user_id}/open_packs/{pack_name}/{pack_quantity}" to /open_packs/{user_id}/{pack_name}/{pack_quantity} (This way it’s clear that this packs.py endpoint is for when a pack is opened and the necessary information are the user id, pack name, and quantity)

Also rename the purchase packs endpoint to be /purchase_packs/{user_id}/{pack_name}/{pack_quantity} for same reasoning as above and to maintain consistency

If you only plan on allowing users to purchase packs and nothing else, you could simplify the endpoint url to just /catalog or if you will implement other kinds of purchases then make sure to rename the url so it is /catalog/packs instead of /packs/catalogs (By having packs before catalog it implies that it is a pack specific endpoint but it’s a catalog related endpoint)
Simplify the endpoint url in users.py from users/users/register to just users/register



I would add rarities to the cards or show probabilities of pulling certain cards to add an element of excitement when getting rarer cards.

After opening a pack, it would be helpful to know how many coins you have remaining instead of only listing the total amount of coins spent.

Open Packs: Once I open a pack, it was difficult to know what cards I pulled later unless I go to my collection. A log of recent pack openings could be helpful.

Get Collection: It would be nice to have the collection endpoint filter by something, this could be type, name, or price.

It would be cool to have a total estimated value of my collection as a user in order to see if I should sell, and I can build on my collection and try to get more valuable cards.

Some of the error messages, like when there is an invalid card name, are not specific. The error messages could be clearer and more targeted to each endpoint.

Were the battle endpoints supposed to be implemented? I saw that you had a battle.py, but I was not able to use it in the testing. I think that using the battle endpoints would help improve the experience.

I think that each card should have some type of quality that contributes to its fighting skills. You can add how much damage they do or what kind of attacking role they have. This would help distinguish between cards and help build a more curated deck. It would also make sense to have the cards that cost more be better at battling.

Selling one card at a time was time-consuming, especially if I opened multiple packs. I think that having an easy function to sell duplicate cards or having some kind of bulk selling would be useful.

I didn't see any way to delete decks or rename them if I wanted to. I think that it would be helpful to have some management of the decks you create.

It would be cool to see potential cards that can be pulled from each pack. It could display what cards are there and if there are cards that are more rare or less likely to be pulled.

If you want to add additional endpoints, I think that a profile that returns unopened packs, total cards, the amount of coins, and your card deck would be useful as well.



The collection endpoint could use more filtering options. Currently, we can only filter by type, but it would be useful to:

Filter by what pack they are pulled from
Filter by card name
Filter by price
Filter by the quantity of the card I have
The error messages across endpoints are inconsistent and not very detailed. For example:

When buying packs -> "Not enough coins" could include current balance
Invalid card names should specify what valid options are or specify things like the name to match the databases capitalization
It would be nice to see other users' collections or total collection value. Maybe a leaderboard or general way to inspect the collections of others.

Cards lack attributes that would make collecting more interesting:

No rarity system
No indication of card value besides price
No special attributes or abilities
No special editions (holographic, full art, etc.)
Could be a cool way to give rare versions of cards additional value too
The battle system is still in work, but as of right now it's lacking:

Cards don't have battle statistics
No way to see potential matchups
No ranking system
No battle history
Pack opening could be more engaging:

No indication of rare card probability
No preview of possible cards in each pack
No history of past pack openings
No celebration or special indication when getting rare cards
Deck management is very limited:

Can't modify existing decks
No way to delete decks
Can't rename decks
Can't see cards in a deck
The catalog endpoint should give us a way to see what cards are available in the pack and preferably the rarity of pulling a copy of the cards.

Instructions for multiple endpoints could be updated to be more clear. Like creating a deck there is nothing telling the user that a deck must have 5 cards and 5 cards only. As of right now if a user has 1 copy of a card they can make a deck with with 5 copies of it. I don't know if that is desired behavior, but deck building guidelines would help with the confusion.

User profile functionality is very limited:

No way to see total collection value
No statistics on cards owned
No history of transactions
No way to track progress (Percent of cards from pack owned)
While I don't think it's a pressing matter, the endpoint naming isn't consistent across the API:

Some use /users/{user_id}/action
Others use /action/{user_id}
Some include unnecessary words like "get"
Inconsistent use of plurals


packs/users/{user_id}/purchase_packs/{pack_name}/{pack_quantity}
There is no input validation for the quantity of packs bought. If I pass in negative number of packs it removes that many of the pack from my account, and credits me the coin price. This can work fine when used like returning an item (Like if I have 2 surging sparks packs and purchase -2 of them they get removed from my inventory and I get 2 * pack price back. Everything is the same state as before the initial purchase of the packs). However, it doesn't check how many of that pack I have, so I can input any size negative number and get essentially infinite coins. So I can purchase -10000 Crown Zenith and get 2000000 coins credited to my account. It seems like when I do this my pack count for that pack type goes negative as well. I can still exploit this by going into "pack debt" for one pack type and then opening unlimited packs of the other types.

A similar problem happens for /users/{user_id}/open_packs/{pack_name}/{pack_quantity} where I can "open" a negative number of packs and they get added to my inventory. This circumnavigates the entire coin system so the exploit above isn't even required.

There is no way to see how many coins I have
The first I noticed after registering was that I didn't know how many coins I had. I tried to buy Crown Zenith pack and was told I didn't have enough coins. I would recommend either adding an endpoint that returns user information. It could be an endpoint on its own or be returned with other information. At the very least include it in the message saying that we can't afford a pack.

/collection/{user_id}/get/{type}
I would recommend making the input case insensitive. I was confused after I opened a pack got a Vulpix and tried to check my fire type pokemon and got an empty list when I passed in 'fire'. It should be as easy as adding a lower() call to check if the input and a database entry matches.

The longer files are documented in a clear, concise manner, but the shorter ones could use a little more documentation.
For instance battle.py, collection.py, display.py could use a small documentation touch up.

There is duplicated code in cards.py and packs.py. This can be rewritten as a function that both can call individually.



# In packs.py


User has 10 packs
Request A checks quantity -> sees 10 packs, which is enough for 7
Request B checks quantity -> also sees 10 packs, which is enough for 7
Request A updates quantity -> 10 - 7 = 3 packs remaining
Request B updates quantity -> 3 - 7 = -4 packs
Not all database transactions are atomic. For example, sell_card_by_name in cards.py checks collection, updates or deletes from collection, and then updates the user's coins all in different transactions when they should be within the same transaction. That way if one fails they all get rolled back instead of having an inconsistent change of state.

This isn't too important but in packs.py the parameter dictionaries are wrapped in lists which is unecessary since we can only open one type of pack at a time.

In decks.py, the get_user_decks endpoint incorrectly returns a 404 error with message "User has too many decks (max 3)" when trying to view decks if a user has more than 3 decks. As a user I should be able to see all my decks, and not get an error unless I have a very large number of decks.

In cards.py, the sell_card_by_name endpoint allows selling cards that are currently in decks. This could lead to invalid decks where users have decks containing cards they no longer own. The endpoint should either prevent selling cards that are in decks or remove the cards from decks when sold.



