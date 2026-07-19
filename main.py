import os
import discord
from discord.ext import commands
import asyncio
import random

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# طابور الإرسال
queue = asyncio.Queue()
is_running = False
SENT_MEMBERS_FILE = "sent_members.txt"

def save_sent_member(member_id):
    with open(SENT_MEMBERS_FILE, "a") as f:
        f.write(str(member_id) + "\n")

def get_sent_members():
    if not os.path.exists(SENT_MEMBERS_FILE):
        return set()
    with open(SENT_MEMBERS_FILE, "r") as f:
        return set(line.strip() for line in f)

async def sender_worker(message_text):
    global is_running
    while is_running and not queue.empty():
        member = await queue.get()
        try:
            await member.send(message_text)
            save_sent_member(str(member.id))
            # وقت انتظار بين الرسائل (احترافي وآمن)
            await asyncio.sleep(random.randint(5, 10))
        except:
            # إذا فشل الإرسال (بلوك)، البوت لا يتوقف ويستمر بذكاء
            pass
        queue.task_done()
    is_running = False

class DMModal(discord.ui.Modal, title='نظام الإرسال الاحترافي'):
    message_input = discord.ui.TextInput(label='نص الرسالة', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        global is_running
        is_running = True
        sent_list = get_sent_members()
        count = 0
        
        for member in interaction.guild.members:
            if not member.bot and str(member.id) not in sent_list:
                await queue.put(member)
                count += 1
        
        await interaction.response.send_message(f"✅ تم إضافة {count} عضو للطابور، سيبدأ الإرسال الآن.", ephemeral=True)
        bot.loop.create_task(sender_worker(self.message_input.value))

@bot.tree.command(name="send_dm", description="إرسال رسالة بنظام الطابور")
async def send_dm(interaction: discord.Interaction):
    await interaction.response.send_modal(DMModal())

@bot.tree.command(name="stop", description="إيقاف الإرسال")
async def stop(interaction: discord.Interaction):
    global is_running
    is_running = False
    await interaction.response.send_message("🛑 تم إيقاف النظام.")

bot.run(os.getenv('TOKEN'))
