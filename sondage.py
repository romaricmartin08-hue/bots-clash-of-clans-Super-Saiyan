import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class SondageGuerreView(discord.ui.View):
    def __init__(self, log_messages: list):
        super().__init__(timeout=None)
        self.log_messages = log_messages
        self.participants = {}

    async def enregistrer_choix(self, interaction: discord.Interaction, choix: str, message_ephemeral: str):
        user = interaction.user
        salon_origine = interaction.channel.name
        role_principal = "Membre"
        if len(user.roles) > 1:
            role_principal = user.roles[-1].name

        self.participants[user.id] = f"• {user.mention} ({user.name}) — *{role_principal}* ➔ **{choix}**"
        await interaction.response.send_message(message_ephemeral, ephemeral=True)

        liste_texte = "\n".join(self.participants.values())
        nouveau_contenu = (
            f"⚔️ **Sondage Guerre en cours**\n"
            f"• **Salon concerné :** #{salon_origine}\n\n"
            f"**Total des réponses ({len(self.participants)}) :**\n"
            f"{liste_texte}"
        )

        for msg in self.log_messages:
            try:
                await msg.edit(content=nouveau_contenu)
            except discord.HTTPException:
                pass

    @discord.ui.button(label="Oui", style=discord.ButtonStyle.success, custom_id="sondage_oui")
    async def bouton_oui(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.enregistrer_choix(interaction, "Oui", "✅ C'est noté ! Ta participation est enregistrée pour la guerre. Bonne chance pour la guerre ! 🛡️")

    @discord.ui.button(label="Non", style=discord.ButtonStyle.danger, custom_id="sondage_non")
    async def bouton_non(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.enregistrer_choix(interaction, "Non", "❌ C'est noté, tu es indiqué comme absent pour cette guerre.")

    @discord.ui.button(label="Tous mes comptes", style=discord.ButtonStyle.primary, custom_id="sondage_tous_comptes")
    async def bouton_tous_comptes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.enregistrer_choix(interaction, "Tous mes comptes", "⚔️ C'est noté ! Tous tes comptes participeront à la guerre. Bonne chance pour la guerre !")

    @discord.ui.button(label="Un seul de mes comptes", style=discord.ButtonStyle.secondary, custom_id="sondage_un_compte")
    async def bouton_un_compte(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.enregistrer_choix(interaction, "Un seul de mes comptes", "📌 C'est pris en compte ! Pense à préciser dans le tchat quel compte tu souhaites engager pour cette guerre.")

@bot.event
async def on_ready():
    print(f"Le bot de sondage GDC est prêt et connecté en tant que {bot.user} !")

@bot.command()
@commands.has_any_role("Chefs", "Chefs Adjoints")
async def sondage(ctx):
    sondage_channel = discord.utils.get(ctx.guild.text_channels, name="sondage")
    annonce_channel = discord.utils.get(ctx.guild.text_channels, name="annonces-légion-de-l-ouest")
    
    if not sondage_channel or not annonce_channel:
        await ctx.send("❌ Erreur : Impossible de trouver le salon `sondage` ou `annonces-légion-de-l-ouest`.", ephemeral=True)
        return

    texte_initial = (
        f"⚔️ **Sondage Guerre en cours**\n"
        f"• **Salon concerné :** #{ctx.channel.name}\n\n"
        f"**Total des réponses (0) :**\n"
        f"*Aucune réponse pour l'instant...*"
    )

    log_msg_chefs = await sondage_channel.send(texte_initial)
    log_msg_annonces = await annonce_channel.send(texte_initial)

    vue = SondageGuerreView([log_msg_chefs, log_msg_annonces])
    await ctx.send(
        "🏰 **PRÉPARATION DE GUERRE DE CLAN** 🏰\n\n"
        "Qui souhaite participer à la prochaine guerre ? Merci de cliquer sur l'option qui correspond à votre situation ci-dessous :", 
        view=vue
    )
    
    await ctx.send("✅ Le sondage de guerre a bien été publié !", ephemeral=True)

@sondage.error
async def sondage_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("❌ Désolé, cette commande est réservée aux Chefs et Chefs Adjoints.", ephemeral=True)

token = os.environ.get("DISCORD_TOKEN")
bot.run(token)