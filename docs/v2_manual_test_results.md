
## Collector Example Flow
Misty, a dedicated water Pokemon card collector, isn't interested in battling. Instead, she is looking very hard and closely for new cards to grow collection. Especially, the "Prismatic Evolution" pack. She's hoping to pull rare evolutions of classic Pokémon to expand her collection and display her favorites.

First, Misty request a catalog to see the latest packs available in the catalog by calling `GET /packs/catalog`. She sees in the catalog, there is Shrouded Fable, Surging Sparks, Paldean Fates, or Crown Zenith.

Misty decides to buy the Paldean Fates pack, open the pack, and display her favorite cards. To do so she:

- starts by calling `POST /users/misty_id/purchase_pack/Paldean Fates`
- then Misty decides to open her new exciting pack, by calling `POST /users/misty_id/open_pack/Paldean Fates/1`
- she decides to view her collection making another call `GET /users/misty_id/collection`
= finally she shows off her favorite pull - Prismatic Umbreon by calling `POST /users/misty_id/display/Prismatic_Umbreon`

## Testing results

### Catalog

1. Curl statement called.

```bash
curl -X 'GET' \
  'https://pokemon-card-collection-kek1.onrender.com/catalog/' \
  -H 'accept: application/json'
```

2. Response

```
[
  {
    "name": "Shrouded Fable",
    "price": 25
  },
  {
    "name": "Surging Sparks",
    "price": 50
  },
  {
    "name": "Paldean Fates",
    "price": 100
  },
  {
    "name": "Crown Zenith",
    "price": 200
  }
]
```

### Purchase Pack

1. Curl statement called.

```bash
curl -X 'POST' \
  'https://pokemon-card-collection.onrender.com/packs/users/3/purchase_packs/Paldean%20Fates/1' \
  -H 'accept: application/json' \
  -H 'access_token: 123456789' \
  -d ''
```

2. Response

```
{
  "pack": "Paldean Fates",
  "total_spent": 100
}
```

### Open Pack

1. Curl statement called.

```bash
curl -X 'POST' \
  'https://pokemon-card-collection.onrender.com/packs/users/3/open_packs/Paldean%20Fates/1' \
  -H 'accept: application/json' \
  -H 'access_token: 123456789' \
  -d ''
```

2. Response

```
[
  {
    "name": "Paldean Fates #1",
    "cards": [
      "Dragonair",
      "Jynx",
      "Chikorita",
      "Smoochum",
      "Porygon"
    ]
  }
]
```
### Get Collection

1. Curl statement called.

```bash
curl -X 'POST' \
  'https://pokemon-card-collection.onrender.com/collection/3/get' \
  -H 'accept: application/json' \
  -H 'access_token: 123456789' \
  -d ''
```

2. Response

```
[
  {
    "Card": {
      "type": "Dragon",
      "name": "Dragonair",
      "price": 40
    },
    "Quantity": 1
  },
  {
    "Card": {
      "type": "Grass",
      "name": "Chikorita",
      "price": 20
    },
    "Quantity": 1
  },
  {
    "Card": {
      "type": "Ice",
      "name": "Smoochum",
      "price": 30
    },
    "Quantity": 1
  },
  {
    "Card": {
      "type": "Ice",
      "name": "Jynx",
      "price": 50
    },
    "Quantity": 1
  },
  {
    "Card": {
      "type": "Normal",
      "name": "Porygon",
      "price": 20
    },
    "Quantity": 1
  }
]
```
### Display


## Selling and Expanding Collection Example Flow

AZ, an out of touch player wants to get back in the game. He doesn't have any collection. He wants to start a collection by getting some valuable and newer cards for his collection. He has some old cards, which he doesn't want any more and wants to sell it. AZ does the following:

- He gets the card details by calling `GET /collection/AZ-id/get`. AZ views his collection and decide what cards to sell. He sees the list of cards as - .
- He decides to sell - "". He calls `POST /users/az/sell/"Flygon"` to sell his "Flygon" card.
- He decides to buy the pack - "Paldean Fates" by calling `POST /users/az/purchase_pack/"Paldean Fates"` with the money he got by selling "Flygon" card
- He opens the pack to see the card details by calling `POST /packs/users/misty_id/open_pack/"Paldean Fates"/1`
- He calls `GET /packs/catalog/"Paldean Fates"/"Armarouge"` as he is new to the game and wanted to know more details about Armarouge card
- He puts the card for display by calling `POST /users/az/display/"Armarouge` to let everyone know that he is ready for the game
- He continues researching and expanding further

## Testing results

### GetCard

1. Curl statement called.

```bash
curl -X 'GET' \
  'https://pokemon-card-collection-kek1.onrender.com/catalog/' \
  -H 'accept: application/json'
```

2. Response

```
[
  {
    "name": "Shrouded Fable",
    "price": 25
  },
  {
    "name": "Surging Sparks",
    "price": 50
  },
  {
    "name": "Paldean Fates",
    "price": 100
  },
  {
    "name": "Crown Zenith",
    "price": 200
  }
]
```
### SellCard

1. Curl statement called.

```bash
curl -X 'GET' \
  'https://pokemon-card-collection-kek1.onrender.com/catalog/' \
  -H 'accept: application/json'
```

2. Response

```
[
  {
    "name": "Shrouded Fable",
    "price": 25
  },
  {
    "name": "Surging Sparks",
    "price": 50
  },
  {
    "name": "Paldean Fates",
    "price": 100
  },
  {
    "name": "Crown Zenith",
    "price": 200
  }
]
```

### Purchase Pack
1. Curl statement called.

```bash
curl -X 'GET' \
  'https://pokemon-card-collection-kek1.onrender.com/catalog/' \
  -H 'accept: application/json'
```

2. Response

```
[
  {
    "name": "Shrouded Fable",
    "price": 25
  },
  {
    "name": "Surging Sparks",
    "price": 50
  },
  {
    "name": "Paldean Fates",
    "price": 100
  },
  {
    "name": "Crown Zenith",
    "price": 200
  }
]
```

### OpenPack
1. Curl statement called.

```bash
curl -X 'GET' \
  'https://pokemon-card-collection-kek1.onrender.com/catalog/' \
  -H 'accept: application/json'
```

2. Response

```
[
  {
    "name": "Shrouded Fable",
    "price": 25
  },
  {
    "name": "Surging Sparks",
    "price": 50
  },
  {
    "name": "Paldean Fates",
    "price": 100
  },
  {
    "name": "Crown Zenith",
    "price": 200
  }
]
```

### GetCard
1. Curl statement called.

```bash
curl -X 'GET' \
  'https://pokemon-card-collection-kek1.onrender.com/catalog/' \
  -H 'accept: application/json'
```

2. Response

```
[
  {
    "name": "Shrouded Fable",
    "price": 25
  },
  {
    "name": "Surging Sparks",
    "price": 50
  },
  {
    "name": "Paldean Fates",
    "price": 100
  },
  {
    "name": "Crown Zenith",
    "price": 200
  }
]
```

### Display Card

