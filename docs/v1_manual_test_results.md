## Manual Testing yay

## Pack Collecting Example Flow

Lina is a new player who just started her journey. She's excited to begin collecting and wants to start by purchasing some beginner-friendly packs to build her inventory.
Lina begins by calling `GET /packs/catalog` to see what kinds of packs are available. She sees options like Grass_Pack and Water_Pack, both priced at 20 coins each.

- She registers as a user with a username `POST /users/register/user_lina`
- She decides to buy one of each, so she calls: `POST /users/lina/purchase_pack/Grass_Pack`, `POST /users/lina/purchase_pack/Water_Pack`
- To make sure the purchases went through, she calls: `GET /inventory/audit`

Lina is ready to start opening packs and seeing what surprises await her inside!
