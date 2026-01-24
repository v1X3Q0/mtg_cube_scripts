# End to end Cube guide

This end to end cube guide isn't perfect, in fact its purely a stream of conscious for how I build cubes. Nothing in it is by any means standardized, but it allows me to put thousands of cards to good use.

## Caching a scryfall database

To cache a scryfall database, you simply need to execute the following code in a python shell, then you have your scryfall database.

```python
import scrython
```

This database created is in the form of a json file list, which is nifty to have for iterating all cards but slow.

### Dictifying scrython cache for speed

This part takes approximately 30 minutes to an hour, so you better be ready to be patient.

The point of this part is that when you are searching the scrython database to find all instances of your card, its a lengthy process and takes approximately 15 minutes to resolve across a local database of 3000 cards. This being cause the linear search against the whole scrython database has `O(N)` complexity. Dictifying the database into a json dictionary drops that complexity to `O(1)`, making it so that the most time consuming operation that has to happen is opening and loading the 3 gig file.

**NOTE:** There is still a linear sweep employed in this, under the occasion where you have 2 faced cards, or cards where the name on the card is just a themed variant, like `E Honda` or `Kefka Palazzo`.

## Scanning to build the personal database

For the first steps, you have to scan cards. I like to separate scanned cards into primarily 2 separate denominations, though not stored this way, which are those that were purchased randomly(boosters, bundles, cases, or just acquired in bulk) and those that were acquired as singles, or with the intent to use that card. This is handy for us to determine what our ratios are for creatures/noncreatures, rares/commons and the like. If you went out and bought a ton of rares for a set, that would skew the balance, and you may get a cube that has no balance, or doesn't utilize the mechanics of the sets the way their designers intended.

The next way that we split the cards that we scan is by set. This holds a bit of obviousness, but we separate by set because a log of mechanics for cards can easily be classified by their set.

So I scan all of my March of Machine cards into a single CSV file, and for my particular repo of cards I also scan all March of Machine commander cards with set code MOC, and all MUL cards into that same CSV. You can further declassify them at will, after all MUL and MOM have some similarities but MUL has no battles, or usage of the convoke mechanic, but it was my hope to keep cards that came in the same set or play boosters together to similate a sealed draft as much as possible. 

**NOTE:** For some sets this may not work, like for instance Lost Cavers of Ixalan came with Modern Horizons 2 cards, those you can keep in that same CSV or separate into a new one named MH2.csv.

There is no perfect rule, but it is important that you follow some sort of structure while putting your cards away/setting up your database. The best you can do is make sure each card is cataloged by their set in your database and stored to match. That matters most for how we use those databases.

## Variant 1, the easy way to just create a cube of sets

Now that you have all of your cards organized, we populate a giant conglomerate file containing all of the files at once. Then in a two step process, we narrow down the cards we use for the next step by picking some sets for our theme.

For instance, lets say I wanna do a Innistrad cube with some Duskmourn in it. Innistrad sets include Shadows of Innistad `soi`, Eldritch Moon `emn` Innistrad: Crimson Vow `vow`, Midnight Innistrad `mid`, Innistrad `isd` and Innistrad Remastered `inr`. Keep in mind that these sets also have commander variants (`voc` and `mic`) that you can dig into as well, which is good cause commander decks both utilize the theme while also providing cards that are useful for deckbuilding (for instance, `sol ring` keeps appearing in commander decks even though its not in many main prints.) Keep in mind that we may have to do some manual tinkering to remove cards that focus on Commander stuff that we don't want, this drafting strategy is namely for building standard draft decks after all. If you want to keep commanders in more power to you.

So adding Duskmourn to that list we have a bountiful, diverse yet themed list to choose from. Our command line for building our card list will then be something like the following:

```bash
$> python3 dup_sets.py mycardlist.csv all_cards_01182026.dict.json \
 --dictified --outfile dskexperiment.csv --force_main soi emn dsk \
 dsc vow voc mid mic isd inr
100%|██████████████████████████████| 3994/3994 [00:01<00:00, 2810.86it/s]
had 389, now have 485
wrote to file inorganic.dskexperiment1.csv
```

Wow! From 389 cards in our cardlist to 385, we can expect a lot of possibilities there when creating cubes! And to assist you, the cards that are found that are variants from other sets will just be put onto the maybeboard for now, meaning that they will be optional for later. But you have a sum total of your cards in the file `inorganic.dskexperiment1.csv`.

### Narrowing down

Next, we wil bring that list down to an acceptable number. Defaults are picked out for each draft size in increments of 45, 45 being the standard size per player to open 3 packs of 15 each.

Our python script for balancing is named `cardrand.py`, and we are going to use it and an argument it requires `--bell` to indicate that we are going to utilize the cards provided and force out the randomness to hope that we have a favorable balance of CMC 2 and 3 cards.

```bash
python3 cardrand.py --bell --cardlist_csv inorganic.dskexperiment1.csv \
 --cube_count 360
```

**NOTE:** The `--bell` isn't perfect, but it tries to setup a ratio for each color based on what you provide it and go from there. If you only provided it with creatures than only creatures are going to be used. if you gave it a ton of rares of one type, it will only utilize the amount of rares allotted per that ratio to balance the other creature/noncreature card types.

But voila! You have a 1.0 for a cube! If you didn't have a lot of multicolor cards, you can change your count of single color cards using the `--owcolor` flag. For example. in a 360 card cube I expect to use 50 cards per color, you can overwrite this to be 55 by declaring `--owcolor 55` in the command line.

Import it into cube cobra and proceed!
