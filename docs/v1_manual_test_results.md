# Manual Testing yay

## Pack Collecting Example Flow

Lina is a new player who just started her journey. She's excited to begin collecting and wants to start by purchasing some beginner-friendly packs to build her inventory.
Lina begins by calling `GET /packs/catalog` to see what kinds of packs are available. She sees options like Grass_Pack and Water_Pack, both priced at 20 coins each.

- She registers as a user with a username `POST /users/register/user_lina`
- She decides to buy one of each, so she calls: `POST /packs/users/lina/purchase_pack/Jungle/1`, `POST /packs/users/lina/purchase_pack/Basic/1`
- To make sure the purchases went through, she calls: `GET /inventory/lina/audit`

Lina is ready to start opening packs and seeing what surprises await her inside!

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
"name": "Basic",
"price": 25
},
{
"name": "Jungle",
"price": 50
},
{
"name": "Fossil",
"price": 100
},
{
"name": "Team Rocket",
"price": 200
}
]
```

### Register Username

1. Curl statement called.

```bash
curl -X 'POST' \
  'https://pokemon-card-collection-kek1.onrender.com/users/users/register/{username}' \
  -H 'accept: application/json' \
  -H 'access_token: 123456789' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "user_lina"
}'
```

2. Response

```
{
  "user_id": 1
}
```

### Buy packs

1. Buy Basic Pack
   
   ```bash
   curl -X 'POST' \
   'https://pokemon-card-collection-kek1.onrender.com/packs/users/4/purchase_packs/Basic/1' \
   -H 'accept: */*' \
   -H 'access_token: 123456789' \
   -d ''
   ```
1a. Response

```
{
  "pack": "Basic",
  "total_spent": 25
}
```
2. Buy Jungle Pack
  ```bash
  curl -X 'POST' \
'https://pokemon-card-collection-kek1.onrender.com/packs/users/4/purchase_packs/Jungle/1' \
-H 'accept: */*' \
-H 'access_token: 123456789' \
-d ''
````

2a. Response

```
{
  "pack": "Jungle",
  "total_spent": 50
}
```

### Make Sure Purchase Went Through

1. Curl statement called.

```bash
curl -X 'GET' \
  'https://pokemon-card-collection-kek1.onrender.com/inventory/4/audit' \
  -H 'accept: application/json' \
  -H 'access_token: 123456789'
```

2. Response

```
{
  "packs": [
    {
      "pack": {
        "name": "Basic",
        "price": 25
      },
      "quantity": 1
    },
    {
      "pack": {
        "name": "Jungle",
        "price": 50
      },
      "quantity": 1
    }
  ]
}
```
