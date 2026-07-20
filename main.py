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

def get_sent_members_list():
    if not os.path.exists(SENT_MEMBERS_FILE):
        return []
    with open(SENT_MEMBERS_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

async def sender_worker(message_text, guild):
    global is_running
    while is_running and not queue.empty():
        member = await queue.get()
        try:
            await member.send(message_text)
            save_sent_member(str(member.id))
            await asyncio.sleep(random.randint(5, 10))
        except:
            pass
        queue.task_done()
    is_running = False

class DMModal(discord.ui.Modal, title='نظام الإرسال الاحترافي'):
    message_input = discord.ui.TextInput(label='نص الرسالة', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        global is_running
        is_running = True
        sent_list = set(get_sent_members_list())
        count = 0
        
        for member in interaction.guild.members:
            if not member.bot and str(member.id) not in sent_list:
                await queue.put(member)
                count += 1
        
        await interaction.response.send_message(f"✅ تم إضافة {count} عضو للطابور، سيبدأ الإرسال الآن.", ephemeral=True)
        bot.loop.create_task(sender_worker(self.message_input.value, interaction.guild))

@bot.tree.command(name="send_dm", description="إرسال رسالة بنظام الطابور")
async def send_dm(interaction: discord.Interaction):
    await interaction.response.send_modal(DMModal())

@bot.tree.command(name="status", description="معرفة إحصائيات الإرسال")
async def status(interaction: discord.Interaction):
    sent_list = get_sent_members_list()
    count = len(sent_list)
    
    recent_ids = sent_list[-10:]
    names = []
    for uid in recent_ids:
        member = interaction.guild.get_member(int(uid))
        names.append(member.name if member else f"ID: {uid}")

    members_text = "\n".join(names) if names else "لا يوجد إرسال بعد"
    await interaction.response.send_message(
        f"📊 **إحصائيات البوت:**\n"
        f"إجمالي من تم الإرسال لهم: {count}\n\n"
        f"آخر 10 يوزرات تم الإرسال لهم:\n{members_text}", 
        ephemeral=True
    )

@bot.tree.command(name="stop", description="إيقاف عملية الإرسال")
async def stop(interaction: discord.Interaction):
    global is_running
    is_running = False
    await interaction.response.send_message("🛑 تم إيقاف عملية الإرسال.")

@bot.event
async def on_ready():
    await bot.tree.sync()
    
    # 🟣 استخدم رابط Twitch لكي يظهر زر (Watch) تماماً مثل الصورة الثانية
    stream_activity = discord.Streaming(
        name="N W | H P IRAQ", 
        url="https://www.twitch.tv/Right"
    )
    await bot.change_presence(activity=stream_activity)
    
    print(f'البوت {bot.user} جاهز للعمل وتم تفعيل زر المشاهدة.')

bot.run(os.getenv('TOKEN'))
