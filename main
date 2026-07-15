import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

is_running = False
sent_count = 0
SENT_MEMBERS_FILE = "sent_members.txt"

# دالة لحفظ الـ ID الذي تم الإرسال له
def save_sent_member(member_id):
    try:
        with open(SENT_MEMBERS_FILE, "a") as f:
            f.write(str(member_id) + "\n")
    except Exception as e:
        print(f"Error saving to file: {e}")

# دالة لجلب قائمة الـ IDs التي تم الإرسال لها مسبقاً
def get_sent_members():
    if not os.path.exists(SENT_MEMBERS_FILE):
        return set()
    with open(SENT_MEMBERS_FILE, "r") as f:
        return set(line.strip() for line in f)

class DMModal(discord.ui.Modal, title='إرسال رسالة جماعية'):
    message_input = discord.ui.TextInput(
        label='اكتب الرسالة هنا',
        style=discord.TextStyle.paragraph,
        placeholder='...أدخل نص الرسالة التي تريد إرسالها للأعضاء...',
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        global is_running, sent_count
        is_running = True
        sent_count = 0
        await interaction.response.send_message("✅ بدأت عملية الإرسال في الخلفية.", ephemeral=True)

        sent_list = get_sent_members()
        members = [m for m in interaction.guild.members if not m.bot]

        for member in members:
            if not is_running: break
            
            # التخطي الذكي: إذا أرسلنا له مسبقاً، لا نكرر
            if str(member.id) in sent_list:
                continue 
            
            try:
                await member.send(f"{member.mention}\n\n{self.message_input.value}")
                save_sent_member(member.id) # حفظ العضو بعد الإرسال
                sent_count += 1
                
                # وقت انتظار عشوائي آمن (بين 5 و 10 دقائق = 300 إلى 600 ثانية)
                wait_time = random.randint(300, 600)
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                print(f"حدث خطأ مع {member.name}: {e}")
                continue
        
        is_running = False
        await interaction.followup.send("🏁 انتهت عملية الإرسال.")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'البوت {bot.user} جاهز مع السلاش كوماند')

@bot.tree.command(name="send_dm", description="فتح استمارة إرسال رسالة خاصة للجميع")
async def send_dm(interaction: discord.Interaction):
    await interaction.response.send_modal(DMModal())

@bot.tree.command(name="status", description="معرفة عدد الرسائل المرسلة")
async def status(interaction: discord.Interaction):
    await interaction.response.send_message(f"تم إرسال الرسالة إلى {sent_count} عضو حتى الآن.", ephemeral=True)

@bot.tree.command(name="stop", description="إيقاف عملية الإرسال الحالية")
async def stop(interaction: discord.Interaction):
    global is_running
    is_running = False
    await interaction.response.send_message("🛑 تم إيقاف العملية.")

bot.run(os.getenv('TOKEN'))
