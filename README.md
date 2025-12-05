# Poe2-Discord-RED-BOT-cogs
Just A few commands For the game Path of exile 2 and use Red-BOT From github


# Path of Exile 2 Bot Cog

A comprehensive Discord bot cog for Path of Exile 2 information, utilities, and community features. This cog provides wiki searches, price checking, build management, crafting calculators, and automated news feeds.

## Features

- **Wiki & Information**: Search the PoE2 wiki, get current league info, and access guides
- **Trade & Economy**: Live price checking from poe.ninja, currency conversion, and market analysis
- **Build Management**: Save, share, and manage Path of Exile 2 builds with Path of Building integration
- **Crafting Tools**: Cost calculators, probability calculators, and crafting guides
- **Automated News**: RSS feed integration for official PoE2 news updates
- **Currency Calculator**: Advanced currency conversion and bulk value calculations

## Commands

### Main Commands

#### `/poe2 wiki <query>`
Search the Path of Exile 2 wiki for any term.
- **Usage**: `[p]poe2 wiki "Lightning Arrow"`
- **Example**: `[p]poe2 wiki "Passive Tree"`
- **Returns**: Direct link to the wiki page with the search term

#### `/poe2 league`
Get information about the current PoE2 league status.
- **Usage**: `[p]poe2 league`
- **Returns**: Current league information and early access status

#### `/poe2 guides`
Access a curated list of useful PoE2 resources and guides.
- **Usage**: `[p]poe2 guides`
- **Returns**: Links to official resources, community sites, and tools

#### `/poe2 passive`
Get the direct link to the PoE2 passive skill tree.
- **Usage**: `[p]poe2 passive`
- **Returns**: Link to the official passive tree planner

#### `/poe2 gems <gem_name>`
Search for information about specific skill gems.
- **Usage**: `[p]poe2 gems "Freezing Pulse"`
- **Returns**: Wiki link for the specified skill gem

### Trade & Economy Commands

#### `/poe2 price <league> <item_name>`
Check current market prices for items using poe.ninja data.
- **Usage**: `[p]poe2 price "Standard" "Divine Orb"`
- **Parameters**:
  - `league`: League name (e.g., Standard, Hardcore)
  - `item_name`: Name of the item to check
- **Returns**: Current price in Chaos Orbs with 7-day trend data

#### `/poe2 currency [league]`
Get top currency exchange rates for a specific league.
- **Usage**: `[p]poe2 currency Standard`
- **Parameters**:
  - `league` (optional): League name, defaults to "Standard"
- **Returns**: Top 10 most valuable currencies with their Chaos values

### Build Management Commands

#### `/poe2 build save <build_name> <build_info>`
Save a build to the server's build database.
- **Usage**: `[p]poe2 build save "My Ranger Build" Class: Ranger, Main Skill: Lightning Arrow, PoB: pastebin.com/abc123`
- **Parameters**:
  - `build_name`: Unique name for your build
  - `build_info`: Detailed build information (class, skills, gear, PoB code, etc.)
- **Features**: Automatically saves author, timestamp, and build details

#### `/poe2 build get <build_name>`
Retrieve a saved build from the database.
- **Usage**: `[p]poe2 build get "My Ranger Build"`
- **Returns**: Embed with build details, author, and creation date

#### `/poe2 build list`
Display all saved builds in the server.
- **Usage**: `[p]poe2 build list`
- **Returns**: List of up to 25 most recent builds with author and preview

#### `/poe2 build delete <build_name>`
Delete a saved build (author or admin only).
- **Usage**: `[p]poe2 build delete "My Ranger Build"`
- **Permissions**: Build author or users with Manage Messages permission

#### `/poe2 build pob [pob_code]`
Share a Path of Building build code or link.
- **Usage**: `[p]poe2 build pob pastebin.com/abc123`
- **Parameters**:
  - `pob_code` (optional): PoB code or pastebin link
- **Returns**: Formatted embed with import instructions

### Crafting Calculator Commands

#### `/poe2 craft calc <num_attempts> <cost_per_attempt>`
Calculate total crafting costs and conversions.
- **Usage**: `[p]poe2 craft calc 100 5.5`
- **Parameters**:
  - `num_attempts`: Number of crafting attempts
  - `cost_per_attempt`: Cost per attempt in Chaos Orbs
- **Returns**: Total cost in Chaos and Divine Orbs

#### `/poe2 craft odds <success_chance> <attempts>`
Calculate probability of successful crafting outcomes.
- **Usage**: `[p]poe2 craft odds 5.0 100`
- **Parameters**:
  - `success_chance`: Success chance percentage (0-100)
  - `attempts`: Number of attempts
- **Returns**: Success probability, expected attempts, and statistical analysis

#### `/poe2 craft guide`
Access crafting guides and resources.
- **Usage**: `[p]poe2 craft guide`
- **Returns**: Links to official crafting resources and community guides

### Currency Calculator Commands

#### `/poe2 calc convert <amount> <from_currency> <to_currency> [league]`
Convert between different currencies using live market rates.
- **Usage**: `[p]poe2 calc convert 100 "Divine Orb" "Chaos Orb" Standard`
- **Parameters**:
  - `amount`: Amount to convert
  - `from_currency`: Source currency name
  - `to_currency`: Target currency name
  - `league` (optional): League name, defaults to "Standard"
- **Returns**: Conversion result with intermediate Chaos value

#### `/poe2 calc worth <amount> <currency_name> [league]`
Calculate the total value of a currency stack.
- **Usage**: `[p]poe2 calc worth 500 "Chaos Orb" Standard`
- **Parameters**:
  - `amount`: Amount of currency
  - `currency_name`: Currency name
  - `league` (optional): League name, defaults to "Standard"
- **Returns**: Value in both Chaos and Divine Orbs

#### `/poe2 calc ratio <currency1> <currency2> [league]`
Get the exchange ratio between two currencies.
- **Usage**: `[p]poe2 calc ratio "Divine Orb" "Chaos Orb" Standard`
- **Parameters**:
  - `currency1`: First currency name
  - `currency2`: Second currency name
  - `league` (optional): League name, defaults to "Standard"
- **Returns**: Bidirectional exchange ratios with Chaos values

#### `/poe2 calc bulk <amount1> <currency1> <amount2> <currency2> ... <league>`
Calculate total value of multiple currency stacks (text-only command).
- **Usage**: `[p]poe2 calc bulk 10 divine 500 chaos 50 exalted Standard`
- **Format**: Pairs of amount and currency name, ending with league name
- **Returns**: Individual values and total in Chaos and Divine Orbs

### News Feed Management (Admin Only)

#### `/poe2 setnews <channel>`
Set the channel for automated PoE2 news updates.
- **Usage**: `[p]poe2 setnews #poe2-news`
- **Permissions**: Admin or Manage Guild permission
- **Features**: Automatically posts PoE2 news from official RSS feed every 30 minutes

#### `/poe2 unsetnews`
Disable automated PoE2 news updates.
- **Usage**: `[p]poe2 unsetnews`
- **Permissions**: Admin or Manage Guild permission

## Configuration

The cog uses Red-DiscordBot's Config system to store:

### Guild Settings
- `notification_channel`: Channel for notifications
- `news_feed_channel`: Channel for automated news posts
- `tracked_leagues`: List of tracked leagues
- `last_news_check`: Timestamp of last news check
- `saved_builds`: Server build database

### User Settings
- `favorite_builds`: User's favorite builds list

## Data Sources

- **poe.ninja API**: Real-time currency and item pricing
- **Official PoE RSS Feed**: Automated news updates
- **PoE Wiki**: Game information and item details
- **Path of Building**: Build planning and sharing

## Requirements

- Red-DiscordBot (Red) v3.0+
- aiohttp for HTTP requests
- Discord.py with slash command support
- Internet connection for external API access

## Setup

1. Place the `poe2.py` file in your Red cogs directory
2. Load the cog: `[p]load poe2`
3. Configure news channels (optional): `[p]poe2 setnews #channel`
4. Start using the commands!

## Rate Limits

- poe.ninja API calls are made as needed with user-triggered commands
- News feed checks run every 30 minutes automatically
- All external requests include proper error handling

## Error Handling

The cog includes comprehensive error handling for:
- API failures and timeouts
- Invalid user input
- Missing permissions
- Network connectivity issues
- Invalid currency or item names

## Support

For issues or feature requests, please check the Red-DiscordBot community or the cog's repository.

---

**Note**: This cog is designed for Path of Exile 2. Some features may be limited during early access phases as APIs and data sources become available.
