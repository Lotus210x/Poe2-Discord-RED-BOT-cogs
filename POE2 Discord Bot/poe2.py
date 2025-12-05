import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.chat_formatting import box, pagify
import aiohttp
import asyncio
from typing import Optional, Dict, List
from datetime import datetime
import json
import re
from xml.etree import ElementTree as ET

class PathOfExile2(commands.Cog):
    """A comprehensive cog for Path of Exile 2 information and utilities"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "notification_channel": None,
            "news_feed_channel": None,
            "tracked_leagues": [],
            "last_news_check": None,
            "saved_builds": {}
        }
        default_user = {
            "favorite_builds": []
        }
        self.config.register_guild(**default_guild)
        self.config.register_user(**default_user)
        self.session = None
        
        # News feed check task
        self.news_task = None
        self.bot.loop.create_task(self.initialize())
    
    async def initialize(self):
        """Initialize the cog"""
        await self.bot.wait_until_ready()
        self.session = aiohttp.ClientSession()
        self.news_task = self.bot.loop.create_task(self.check_news_feed())
    
    def cog_unload(self):
        if self.news_task:
            self.news_task.cancel()
        if self.session:
            self.bot.loop.create_task(self.session.close())
    
    # ============ NEWS FEED ============
    
    async def check_news_feed(self):
        """Background task to check for new PoE2 news"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                all_guilds = await self.config.all_guilds()
                for guild_id, settings in all_guilds.items():
                    channel_id = settings.get("news_feed_channel")
                    if not channel_id:
                        continue
                    
                    guild = self.bot.get_guild(guild_id)
                    if not guild:
                        continue
                    
                    channel = guild.get_channel(channel_id)
                    if not channel:
                        continue
                    
                    # Check official PoE news RSS
                    await self.fetch_and_post_news(guild, channel)
                
                # Check every 30 minutes
                await asyncio.sleep(1800)
            except Exception as e:
                print(f"Error in news feed check: {e}")
                await asyncio.sleep(1800)
    
    async def fetch_and_post_news(self, guild, channel):
        """Fetch news from RSS feed and post new items"""
        try:
            if not self.session:
                return
                
            # Parse the official PoE news feed
            async with self.session.get("https://www.pathofexile.com/news/rss") as resp:
                if resp.status != 200:
                    return
                
                xml_content = await resp.text()
                root = ET.fromstring(xml_content)
                
                last_check = await self.config.guild(guild).last_news_check()
                last_check_time = datetime.fromisoformat(last_check) if last_check else datetime.min
                
                new_items = []
                
                # Parse RSS feed
                for item in root.findall('.//item')[:5]:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    desc_elem = item.find('description')
                    pub_elem = item.find('pubDate')
                    
                    if title_elem is None or link_elem is None:
                        continue
                    
                    title = title_elem.text
                    link = link_elem.text
                    description = desc_elem.text if desc_elem is not None else ""
                    pub_date = pub_elem.text if pub_elem is not None else ""
                    
                    # Parse publication date (simplified)
                    try:
                        # RSS pubDate format: "Wed, 04 Dec 2024 12:00:00 +0000"
                        date_parts = pub_date.split()
                        if len(date_parts) >= 4:
                            # Simple check - just compare the raw string for now
                            if pub_date > str(last_check_time):
                                new_items.append({
                                    'title': title,
                                    'link': link,
                                    'description': description,
                                    'pub_date': pub_date
                                })
                    except:
                        pass
                
                # Post new items
                for item in reversed(new_items):
                    # Filter for PoE2 related news
                    if "path of exile 2" in item['title'].lower() or "poe2" in item['title'].lower():
                        # Clean HTML from description
                        clean_desc = re.sub('<[^<]+?>', '', item['description'])
                        clean_desc = clean_desc[:500] + "..." if len(clean_desc) > 500 else clean_desc
                        
                        embed = discord.Embed(
                            title=item['title'],
                            url=item['link'],
                            description=clean_desc,
                            color=discord.Color.gold()
                        )
                        embed.set_footer(text="Path of Exile 2 News")
                        await channel.send(embed=embed)
                
                # Update last check time
                await self.config.guild(guild).last_news_check.set(datetime.now().isoformat())
                
        except Exception as e:
            print(f"Error fetching news: {e}")
    
    @commands.hybrid_group(name="poe2")
    async def poe2(self, ctx):
        """Path of Exile 2 commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    # ============ WIKI & BASIC INFO ============
    
    @poe2.command(name="wiki")
    @discord.app_commands.describe(query="Search query for the PoE2 wiki")
    async def wiki_search(self, ctx, *, query: str):
        """Search the Path of Exile 2 wiki"""
        wiki_url = f"https://www.poewiki.net/wiki/{query.replace(' ', '_')}"
        
        embed = discord.Embed(
            title=f"PoE2 Wiki: {query}",
            description=f"[Click here to view on wiki]({wiki_url})",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Path of Exile 2 Wiki")
        
        await ctx.send(embed=embed)
    
    @poe2.command(name="league")
    @discord.app_commands.describe()
    async def current_league(self, ctx):
        """Get information about the current PoE2 league"""
        embed = discord.Embed(
            title="Path of Exile 2 - Current Status",
            description="Path of Exile 2 is currently in Early Access",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Early Access Info",
            value="PoE2 is available for Early Access supporters",
            inline=False
        )
        embed.set_footer(text="Visit pathofexile.com for more info")
        
        await ctx.send(embed=embed)
    
    @poe2.command(name="guides")
    @discord.app_commands.describe()
    async def guides(self, ctx):
        """Get links to useful PoE2 guides and resources"""
        embed = discord.Embed(
            title="Path of Exile 2 - Guides & Resources",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="Official Resources",
            value="[Official Website](https://www.pathofexile.com/poe2)\n"
                  "[PoE2 Wiki](https://www.poewiki.net/)",
            inline=False
        )
        embed.add_field(
            name="Community",
            value="[Reddit: r/PathOfExile2](https://reddit.com/r/pathofexile2)\n"
                  "[Official Forums](https://www.pathofexile.com/forum)",
            inline=False
        )
        embed.add_field(
            name="Tools",
            value="[Path of Building](https://pathofbuilding.community/)\n"
                  "[poe.ninja Builds](https://poe.ninja/poe2/builds)\n"
                  "[Trade Site](https://www.pathofexile.com/trade2/search)",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    # ============ TRADE API & PRICING ============
    
    @poe2.command(name="price")
    @discord.app_commands.describe(league="League name (e.g., Standard, Hardcore)", item_name="Name of the item to check")
    async def check_price(self, ctx, league: str, *, item_name: str):
        """Check item prices from poe.ninja
        
        Example: [p]poe2 price "Standard" "Divine Orb"
        """
        if not self.session:
            await ctx.send("Session not initialized. Please try again in a moment.")
            return
            
        try:
            async with ctx.typing():
                # Try currency first
                url = f"https://poe.ninja/api/data/currencyoverview?league={league}&type=Currency"
                async with self.session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Search for the item
                        for item in data.get('lines', []):
                            if item_name.lower() in item['currencyTypeName'].lower():
                                chaos_value = item.get('chaosEquivalent', 'N/A')
                                
                                embed = discord.Embed(
                                    title=f"💰 {item['currencyTypeName']}",
                                    color=discord.Color.gold()
                                )
                                embed.add_field(
                                    name="Chaos Value",
                                    value=f"{chaos_value} Chaos Orbs",
                                    inline=False
                                )
                                
                                # Add sparkline data if available
                                sparkline = item.get('receiveSparkLine', {})
                                change = sparkline.get('totalChange', 0)
                                if change != 0:
                                    trend = "📈" if change > 0 else "📉"
                                    embed.add_field(
                                        name="7-Day Change",
                                        value=f"{trend} {change:.2f}%",
                                        inline=True
                                    )
                                
                                embed.set_footer(text=f"League: {league} | Data from poe.ninja")
                                await ctx.send(embed=embed)
                                return
                
                # If not found in currency, try items
                await ctx.send(f"Could not find pricing for `{item_name}` in league `{league}`. "
                              f"Try checking: https://poe.ninja/poe2/builds or the trade site.")
                              
        except Exception as e:
            await ctx.send(f"Error fetching price data: {str(e)}")
    
    @poe2.command(name="currency")
    @discord.app_commands.describe(league="League name (default: Standard)")
    async def currency_rates(self, ctx, league: str = "Standard"):
        """Get top currency exchange rates
        
        Example: [p]poe2 currency Standard
        """
        if not self.session:
            await ctx.send("Session not initialized. Please try again in a moment.")
            return
            
        try:
            async with ctx.typing():
                url = f"https://poe.ninja/api/data/currencyoverview?league={league}&type=Currency"
                async with self.session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        embed = discord.Embed(
                            title=f"💱 Currency Rates - {league}",
                            color=discord.Color.gold(),
                            description="Top currency values in Chaos Orbs"
                        )
                        
                        # Get top currencies
                        lines = sorted(data.get('lines', []), 
                                     key=lambda x: x.get('chaosEquivalent', 0), 
                                     reverse=True)[:10]
                        
                        for item in lines:
                            name = item['currencyTypeName']
                            value = item.get('chaosEquivalent', 'N/A')
                            embed.add_field(
                                name=name,
                                value=f"{value} Chaos",
                                inline=True
                            )
                        
                        embed.set_footer(text="Data from poe.ninja")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f"Could not fetch currency data for league: {league}")
                        
        except Exception as e:
            await ctx.send(f"Error fetching currency data: {str(e)}")
    
    # ============ BUILD DATABASE ============
    
    @commands.hybrid_group(name="build", invoke_without_command=True)
    async def build(self, ctx):
        """Build management commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @build.command(name="save")
    @discord.app_commands.describe(build_name="Name for your build", build_info="Build details (class, skills, PoB code, etc.)")
    async def build_save(self, ctx, build_name: str, *, build_info: str):
        """Save a build to the server database
        
        Example: [p]poe2 build save "My Ranger Build" Class: Ranger, Main Skill: Lightning Arrow, PoB: pastebin.com/abc123
        """
        async with self.config.guild(ctx.guild).saved_builds() as builds:
            if build_name in builds:
                await ctx.send(f"Build `{build_name}` already exists! Use a different name or delete the old one first.")
                return
            
            builds[build_name] = {
                "info": build_info,
                "author": str(ctx.author),
                "author_id": ctx.author.id,
                "created": datetime.now().isoformat()
            }
        
        await ctx.send(f"✅ Build `{build_name}` has been saved to the server database!")
    
    @build.command(name="get")
    @discord.app_commands.describe(build_name="Name of the build to retrieve")
    async def build_get(self, ctx, *, build_name: str):
        """Retrieve a saved build from the database
        
        Example: [p]poe2 build get "My Ranger Build"
        """
        builds = await self.config.guild(ctx.guild).saved_builds()
        
        if build_name not in builds:
            await ctx.send(f"Build `{build_name}` not found in database.")
            return
        
        build_data = builds[build_name]
        
        embed = discord.Embed(
            title=f"🏹 {build_name}",
            description=build_data['info'],
            color=discord.Color.blue()
        )
        embed.add_field(name="Author", value=build_data['author'], inline=True)
        embed.add_field(name="Created", value=build_data['created'][:10], inline=True)
        
        await ctx.send(embed=embed)
    
    @build.command(name="list")
    @discord.app_commands.describe()
    async def build_list(self, ctx):
        """List all saved builds in the server"""
        builds = await self.config.guild(ctx.guild).saved_builds()
        
        if not builds:
            await ctx.send("No builds saved yet! Use `[p]poe2 build save` to add one.")
            return
        
        embed = discord.Embed(
            title="📚 Saved Builds",
            color=discord.Color.green()
        )
        
        for name, data in list(builds.items())[:25]:  # Limit to 25 for embed limits
            embed.add_field(
                name=name,
                value=f"By: {data['author']}\n{data['info'][:50]}...",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @build.command(name="delete")
    @discord.app_commands.describe(build_name="Name of the build to delete")
    async def build_delete(self, ctx, *, build_name: str):
        """Delete a saved build (author or admin only)"""
        builds = await self.config.guild(ctx.guild).saved_builds()
        
        if build_name not in builds:
            await ctx.send(f"Build `{build_name}` not found.")
            return
        
        # Check if user is author or has manage_messages permission
        build_data = builds[build_name]
        if build_data['author_id'] != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You can only delete your own builds (or you need Manage Messages permission).")
            return
        
        async with self.config.guild(ctx.guild).saved_builds() as builds:
            del builds[build_name]
        
        await ctx.send(f"🗑️ Build `{build_name}` has been deleted.")
    
    @build.command(name="pob")
    @discord.app_commands.describe(pob_code="Path of Building code or pastebin link")
    async def build_pob(self, ctx, pob_code: Optional[str] = None):
        """Share a Path of Building build code"""
        if not pob_code:
            await ctx.send(
                "Please provide a Path of Building (PoB) code or pastebin link!\n"
                "Usage: `[p]poe2 build pob <pastebin_url_or_code>`"
            )
            return
        
        embed = discord.Embed(
            title="📊 Path of Building Build",
            description=f"**Code/Link:** {pob_code}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="How to Import",
            value="1. Open Path of Building\n2. Click 'Import/Export Build'\n3. Paste the code or URL",
            inline=False
        )
        embed.set_footer(text="Shared by " + str(ctx.author))
        
        await ctx.send(embed=embed)
    
    # ============ CRAFTING HELPER ============
    
    @commands.hybrid_group(name="craft", invoke_without_command=True)
    async def craft(self, ctx):
        """Crafting helper commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @craft.command(name="calc")
    @discord.app_commands.describe(num_attempts="Number of crafting attempts", cost_per_attempt="Cost per attempt in chaos orbs")
    async def craft_calc(self, ctx, num_attempts: int, cost_per_attempt: float):
        """Calculate crafting costs
        
        Example: [p]poe2 craft calc 100 5.5
        (100 attempts at 5.5 chaos each)
        """
        if num_attempts <= 0 or cost_per_attempt <= 0:
            await ctx.send("Please provide positive numbers!")
            return
        
        total_cost = num_attempts * cost_per_attempt
        
        embed = discord.Embed(
            title="🔨 Crafting Cost Calculator",
            color=discord.Color.orange()
        )
        embed.add_field(name="Attempts", value=f"{num_attempts:,}", inline=True)
        embed.add_field(name="Cost per Attempt", value=f"{cost_per_attempt} Chaos", inline=True)
        embed.add_field(name="Total Cost", value=f"{total_cost:,.2f} Chaos", inline=False)
        
        # Add Divine Orb conversion (assuming ~180 chaos per divine as placeholder)
        divine_cost = total_cost / 180
        embed.add_field(name="In Divine Orbs", value=f"≈ {divine_cost:.2f} Divine", inline=True)
        
        await ctx.send(embed=embed)
    
    @craft.command(name="odds")
    @discord.app_commands.describe(success_chance="Success chance percentage (0-100)", attempts="Number of attempts")
    async def craft_odds(self, ctx, success_chance: float, attempts: int):
        """Calculate probability of success
        
        Example: [p]poe2 craft odds 5.0 100
        (5% chance per attempt, 100 attempts)
        """
        if success_chance <= 0 or success_chance > 100:
            await ctx.send("Success chance must be between 0 and 100!")
            return
        
        if attempts <= 0:
            await ctx.send("Attempts must be positive!")
            return
        
        # Convert to decimal
        chance = success_chance / 100
        
        # Probability of at least one success
        prob_at_least_one = 1 - ((1 - chance) ** attempts)
        
        # Expected number of attempts for first success
        expected_attempts = 1 / chance
        
        embed = discord.Embed(
            title="🎲 Crafting Probability Calculator",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="Success Chance per Attempt",
            value=f"{success_chance}%",
            inline=True
        )
        embed.add_field(
            name="Number of Attempts",
            value=f"{attempts:,}",
            inline=True
        )
        embed.add_field(
            name="Chance of At Least 1 Success",
            value=f"{prob_at_least_one * 100:.2f}%",
            inline=False
        )
        embed.add_field(
            name="Expected Attempts for Success",
            value=f"{expected_attempts:.1f} attempts",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @craft.command(name="guide")
    @discord.app_commands.describe()
    async def craft_guide(self, ctx):
        """Get links to crafting guides"""
        embed = discord.Embed(
            title="🔨 Crafting Guides & Resources",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="Official Resources",
            value="[PoE2 Wiki - Crafting](https://www.poewiki.net/wiki/Crafting)\n"
                  "[Item Mods Database](https://www.poewiki.net/wiki/Modifiers)",
            inline=False
        )
        embed.add_field(
            name="Community Guides",
            value="Check [Reddit](https://reddit.com/r/pathofexile2) for community crafting guides",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    # ============ NEWS FEED MANAGEMENT ============
    
    @poe2.command(name="setnews")
    @checks.admin_or_permissions(manage_guild=True)
    @discord.app_commands.describe(channel="Channel to post PoE2 news updates")
    async def set_news_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel for PoE2 news updates (Admin only)"""
        await self.config.guild(ctx.guild).news_feed_channel.set(channel.id)
        await ctx.send(f"✅ PoE2 news will be posted to {channel.mention}")
    
    @poe2.command(name="unsetnews")
    @checks.admin_or_permissions(manage_guild=True)
    @discord.app_commands.describe()
    async def unset_news_channel(self, ctx):
        """Disable PoE2 news updates (Admin only)"""
        await self.config.guild(ctx.guild).news_feed_channel.set(None)
        await ctx.send("✅ PoE2 news updates disabled")
    
    # ============ CURRENCY CALCULATOR ============
    
    @commands.hybrid_group(name="calc", invoke_without_command=True)
    async def calc(self, ctx):
        """Currency calculator commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @calc.command(name="convert")
    @discord.app_commands.describe(amount="Amount to convert", from_currency="Source currency name", to_currency="Target currency name", league="League name (default: Standard)")
    async def currency_convert(self, ctx, amount: float, from_currency: str, to_currency: str, league: str = "Standard"):
        """Convert between currencies using live rates
        
        Example: [p]poe2 calc convert 100 "Divine Orb" "Chaos Orb" Standard
        """
        if not self.session:
            await ctx.send("Session not initialized. Please try again in a moment.")
            return
        
        try:
            async with ctx.typing():
                url = f"https://poe.ninja/api/data/currencyoverview?league={league}&type=Currency"
                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send(f"Could not fetch currency data for league: {league}")
                        return
                    
                    data = await resp.json()
                    lines = data.get('lines', [])
                    
                    # Find the currencies
                    from_rate = None
                    to_rate = None
                    from_name = None
                    to_name = None
                    
                    for item in lines:
                        name = item['currencyTypeName'].lower()
                        if from_currency.lower() in name:
                            from_rate = item.get('chaosEquivalent', 0)
                            from_name = item['currencyTypeName']
                        if to_currency.lower() in name:
                            to_rate = item.get('chaosEquivalent', 0)
                            to_name = item['currencyTypeName']
                    
                    if from_rate is None:
                        await ctx.send(f"Could not find currency: {from_currency}")
                        return
                    if to_rate is None:
                        await ctx.send(f"Could not find currency: {to_currency}")
                        return
                    
                    # Convert
                    chaos_value = amount * from_rate
                    result = chaos_value / to_rate if to_rate > 0 else 0
                    
                    embed = discord.Embed(
                        title="💱 Currency Conversion",
                        color=discord.Color.blue()
                    )
                    embed.add_field(
                        name="From",
                        value=f"{amount:,.2f} {from_name}",
                        inline=True
                    )
                    embed.add_field(
                        name="To",
                        value=f"{result:,.2f} {to_name}",
                        inline=True
                    )
                    embed.add_field(
                        name="Via Chaos",
                        value=f"{chaos_value:,.2f} Chaos Orbs",
                        inline=False
                    )
                    embed.set_footer(text=f"League: {league} | Rates from poe.ninja")
                    
                    await ctx.send(embed=embed)
                    
        except Exception as e:
            await ctx.send(f"Error converting currency: {str(e)}")
    
    @calc.command(name="worth")
    @discord.app_commands.describe(amount="Amount of currency", currency_name="Currency name", league="League name (default: Standard)")
    async def currency_worth(self, ctx, amount: float, currency_name: str, league: str = "Standard"):
        """Calculate how much a currency stack is worth in chaos and divines
        
        Example: [p]poe2 calc worth 500 "Chaos Orb" Standard
        """
        if not self.session:
            await ctx.send("Session not initialized. Please try again in a moment.")
            return
        
        try:
            async with ctx.typing():
                url = f"https://poe.ninja/api/data/currencyoverview?league={league}&type=Currency"
                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send(f"Could not fetch currency data for league: {league}")
                        return
                    
                    data = await resp.json()
                    lines = data.get('lines', [])
                    
                    # Find the currency
                    currency_rate = None
                    currency_full_name = None
                    divine_rate = None
                    
                    for item in lines:
                        name = item['currencyTypeName'].lower()
                        if currency_name.lower() in name:
                            currency_rate = item.get('chaosEquivalent', 0)
                            currency_full_name = item['currencyTypeName']
                        if "divine orb" in name:
                            divine_rate = item.get('chaosEquivalent', 1)
                    
                    if currency_rate is None:
                        await ctx.send(f"Could not find currency: {currency_name}")
                        return
                    
                    # Calculate worth
                    chaos_worth = amount * currency_rate
                    divine_worth = chaos_worth / divine_rate if divine_rate > 0 else 0
                    
                    embed = discord.Embed(
                        title=f"💰 Stack Value: {amount:,.0f} {currency_full_name}",
                        color=discord.Color.gold()
                    )
                    embed.add_field(
                        name="Worth in Chaos Orbs",
                        value=f"{chaos_worth:,.2f} Chaos",
                        inline=False
                    )
                    embed.add_field(
                        name="Worth in Divine Orbs",
                        value=f"{divine_worth:,.2f} Divine",
                        inline=False
                    )
                    embed.set_footer(text=f"League: {league} | Rates from poe.ninja")
                    
                    await ctx.send(embed=embed)
                    
        except Exception as e:
            await ctx.send(f"Error calculating worth: {str(e)}")
    
    @calc.command(name="ratio")
    @discord.app_commands.describe(currency1="First currency name", currency2="Second currency name", league="League name (default: Standard)")
    async def currency_ratio(self, ctx, currency1: str, currency2: str, league: str = "Standard"):
        """Get the exchange ratio between two currencies
        
        Example: [p]poe2 calc ratio "Divine Orb" "Chaos Orb" Standard
        """
        if not self.session:
            await ctx.send("Session not initialized. Please try again in a moment.")
            return
        
        try:
            async with ctx.typing():
                url = f"https://poe.ninja/api/data/currencyoverview?league={league}&type=Currency"
                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send(f"Could not fetch currency data for league: {league}")
                        return
                    
                    data = await resp.json()
                    lines = data.get('lines', [])
                    
                    # Find currencies
                    rate1 = None
                    rate2 = None
                    name1 = None
                    name2 = None
                    
                    for item in lines:
                        name = item['currencyTypeName'].lower()
                        if currency1.lower() in name:
                            rate1 = item.get('chaosEquivalent', 0)
                            name1 = item['currencyTypeName']
                        if currency2.lower() in name:
                            rate2 = item.get('chaosEquivalent', 0)
                            name2 = item['currencyTypeName']
                    
                    if rate1 is None:
                        await ctx.send(f"Could not find currency: {currency1}")
                        return
                    if rate2 is None:
                        await ctx.send(f"Could not find currency: {currency2}")
                        return
                    
                    # Calculate ratios
                    ratio_1_to_2 = rate1 / rate2 if rate2 > 0 else 0
                    ratio_2_to_1 = rate2 / rate1 if rate1 > 0 else 0
                    
                    embed = discord.Embed(
                        title="📊 Currency Exchange Ratio",
                        color=discord.Color.purple()
                    )
                    embed.add_field(
                        name=f"1 {name1} =",
                        value=f"{ratio_1_to_2:,.2f} {name2}",
                        inline=False
                    )
                    embed.add_field(
                        name=f"1 {name2} =",
                        value=f"{ratio_2_to_1:,.4f} {name1}",
                        inline=False
                    )
                    embed.add_field(
                        name="Chaos Values",
                        value=f"{name1}: {rate1:,.2f}c\n{name2}: {rate2:,.2f}c",
                        inline=False
                    )
                    embed.set_footer(text=f"League: {league} | Rates from poe.ninja")
                    
                    await ctx.send(embed=embed)
                    
        except Exception as e:
            await ctx.send(f"Error calculating ratio: {str(e)}")
    
    @calc.command(name="bulk", with_app_command=False)
    async def bulk_calculator(self, ctx, *items_and_amounts):
        """Calculate total value of multiple currency stacks
        
        Example: [p]poe2 calc bulk 10 divine 500 chaos 50 exalted Standard
        Format: amount1 currency1 amount2 currency2 ... league
        """
        if len(items_and_amounts) < 3:
            await ctx.send("Usage: `[p]poe2 calc bulk <amount1> <currency1> <amount2> <currency2> ... <league>`\n"
                          "Example: `[p]poe2 calc bulk 10 divine 500 chaos Standard`")
            return
        
        # Last item is the league
        league = items_and_amounts[-1]
        items = items_and_amounts[:-1]
        
        # Parse items (amount, currency pairs)
        if len(items) % 2 != 0:
            await ctx.send("Please provide pairs of amount and currency name!")
            return
        
        if not self.session:
            await ctx.send("Session not initialized. Please try again in a moment.")
            return
        
        try:
            async with ctx.typing():
                url = f"https://poe.ninja/api/data/currencyoverview?league={league}&type=Currency"
                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send(f"Could not fetch currency data for league: {league}")
                        return
                    
                    data = await resp.json()
                    lines = data.get('lines', [])
                    
                    total_chaos = 0
                    items_found = []
                    divine_rate = 1
                    
                    # Get divine rate
                    for item in lines:
                        if "divine orb" in item['currencyTypeName'].lower():
                            divine_rate = item.get('chaosEquivalent', 1)
                            break
                    
                    # Process each currency pair
                    for i in range(0, len(items), 2):
                        try:
                            amount = float(items[i])
                            currency = items[i + 1]
                            
                            # Find currency rate
                            found = False
                            for item in lines:
                                if currency.lower() in item['currencyTypeName'].lower():
                                    rate = item.get('chaosEquivalent', 0)
                                    value = amount * rate
                                    total_chaos += value
                                    items_found.append({
                                        'name': item['currencyTypeName'],
                                        'amount': amount,
                                        'value': value
                                    })
                                    found = True
                                    break
                            
                            if not found:
                                await ctx.send(f"Warning: Could not find currency '{currency}'")
                        except ValueError:
                            await ctx.send(f"Invalid amount: {items[i]}")
                            return
                    
                    if not items_found:
                        await ctx.send("No valid currencies found!")
                        return
                    
                    # Create embed
                    embed = discord.Embed(
                        title="💼 Bulk Currency Calculator",
                        color=discord.Color.blue()
                    )
                    
                    for item in items_found:
                        embed.add_field(
                            name=f"{item['amount']:,.0f} {item['name']}",
                            value=f"{item['value']:,.2f} Chaos",
                            inline=True
                        )
                    
                    embed.add_field(
                        name="━━━━━━━━━━━━━━━",
                        value="** **",
                        inline=False
                    )
                    embed.add_field(
                        name="💰 Total Value",
                        value=f"**{total_chaos:,.2f} Chaos Orbs**\n"
                              f"**{(total_chaos / divine_rate):,.2f} Divine Orbs**",
                        inline=False
                    )
                    embed.set_footer(text=f"League: {league} | Rates from poe.ninja")
                    
                    await ctx.send(embed=embed)
                    
        except Exception as e:
            await ctx.send(f"Error calculating bulk value: {str(e)}")
    
    # ============ ADDITIONAL COMMANDS ============
    
    @poe2.command(name="passive")
    @discord.app_commands.describe()
    async def passive_tree(self, ctx):
        """Get the link to the passive skill tree"""
        embed = discord.Embed(
            title="Path of Exile 2 - Passive Tree",
            description="[View the Passive Skill Tree](https://www.pathofexile.com/passive-skill-tree/poe2)",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @poe2.command(name="gems")
    @discord.app_commands.describe(gem_name="Name of the skill gem to search")
    async def skill_gems(self, ctx, *, gem_name: str):
        """Search for skill gem information"""
        wiki_url = f"https://www.poewiki.net/wiki/{gem_name.replace(' ', '_')}"
        
        embed = discord.Embed(
            title=f"💎 Skill Gem: {gem_name}",
            description=f"[View gem details on wiki]({wiki_url})",
            color=discord.Color.teal()
        )
        embed.set_footer(text="Path of Exile 2 - Skill Gems")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PathOfExile2(bot))