import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class ReadReceiptView(discord.ui.View):
    def __init__(self, log_messages: list):
        super().__init__(timeout=None)
        self.log_messages = log_messages
        self.deja_clique = set()
        self.participants = []

    @discord.ui.button(label="J'ai lu !", style=discord.ButtonStyle.primary, custom_id="read_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.deja_clique:
            await interaction.response.send_message("❌ Tu as déjà cliqué sur cet accusé de réception !", ephemeral=True)
            return

        self.deja_clique.add(interaction.user.id)
        await interaction.response.send_message("Merci, ton accusé de réception a bien été pris en compte ! 👍", ephemeral=True)

        user = interaction.user
        salon_origine = interaction.channel.name
        role_principal = "Membre"
        if len(user.roles) > 1:
            role_principal = user.roles[-1].name

        self.participants.append(f"• {user.mention} ({user.name}) — *{role_principal}*")
        
        liste_texte = "\n".join(self.participants)
        nouveau_contenu = (
            f"📋 **Accusé de réception en cours**\n"
            f"• **Salon concerné :** #{salon_origine}\n\n"
            f"**Personnes ayant lu ({len(self.participants)}) :**\n"
            f"{liste_texte}"
        )

        for msg in self.log_messages:
            try:
                await msg.edit(content=nouveau_contenu)
            except discord.HTTPException:
                pass

@bot.event
async def on_ready():
    print(f"Coucou ! Je suis {bot.user} et je suis réveillé pour les lectures !")

@bot.command()
@commands.has_any_role("Chefs", "Chefs Adjoints")
async def lire(ctx):
    mod_channel = discord.utils.get(ctx.guild.text_channels, name="suivi-des-lectures")
    annonce_channel = discord.utils.get(ctx.guild.text_channels, name="annonces-légion-de-l-ouest")
    
    if not mod_channel or not annonce_channel:
        await ctx.send("❌ Erreur : Impossible de trouver le salon `suivi-des-lectures` ou `annonces-légion-de-l-ouest`.", ephemeral=True)
        return

    texte_initial = (
        f"📋 **Accusé de réception en cours**\n"
        f"• **Salon concerné :** #{ctx.channel.name}\n\n"
        f"**Personnes ayant lu (0) :**\n"
        f"*Aucune pour l'instant...*"
    )

    log_msg_chefs = await mod_channel.send(texte_initial)
    log_msg_annonces = await annonce_channel.send(texte_initial)

    vue = ReadReceiptView([log_msg_chefs, log_msg_annonces])
    await ctx.send(
        "📢 **Nouveau message important !** Merci de cliquer sur le bouton ci-dessous pour confirmer que vous avez lu :", 
        view=vue
    )
    
    await ctx.send("✅ L'accusé de réception a bien été créé !", ephemeral=True)

@lire.error
async def lire_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("❌ Désolé, tu n'as pas le droit d'utiliser cette commande.", ephemeral=True)

token = os.environ.get("DISCORD_TOKEN")
bot.run(token)