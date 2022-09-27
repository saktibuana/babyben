import time
import os

from datetime import datetime
from apscheduler.schedulers.asyncio  import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import nextcord
from nextcord.ext import commands
from nextcord.utils import get
import config

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def main():
    # allows privledged intents for monitoring members joining, roles editing, and role assignments
    # these need to be enabled in the developer portal as well
    intents = nextcord.Intents.default()

    # To enable guild intents:
    intents.guilds = True

    # To enable member intents:
    intents.members = True

    # Set bot's custom status
    activity = nextcord.Activity( type=nextcord.ActivityType.watching, name=f"You 👀")

    # ids
    progate_nextLevel_guild_id = 927864766070919168 # discord id of server progate next level
    general_channel_id = 927864767236964386 # discord channel general id of progate next level
    statistic_channel_id = 946373024758771723 # discord channel statistic id of progate next level
    perkenalan_channel_id = 930734847348080651 # discord channel perkenalan id of progate next level
    botCommand_channel_id = 928501038812647444 # discord channel bot-command id of progate next level
    exceptions = {
        "tomohiro": 489975393982480396,
        "birdie": 698384707477569596,
        "norman": 750946264463573034,
        "gurudomba": 698427506461507644,
        "aqshal": 810524921528451074,
        "mufti#0372": 517356388796858384,
        "mufti#4778": 928137058281742366,
        "sakti#8603": 699235804941254656,
        "sakti#4937": 928198372316311572
    }

    bot = commands.Bot(
        commands.when_mentioned_or(config.BOT_PREFIX),
        intents=intents,
        activity=activity,
    )

    # Get the modules of all cogs whose directory structure is cogs/<module_name>/cog.py
    for folder in os.listdir("cogs"):
        if os.path.exists(os.path.join("cogs", folder, "cog.py")):
            bot.load_extension(f"cogs.{folder}.cog")

    @bot.event
    async def on_ready():
        # when discord is connected
        themessage = f"{bot.user.name} has connected to Discord!"
        # prompt to the terminal to initiate
        print(themessage)
        await infoTotal()

        # scheduled to be posted every 9 am and 6pm
        scheduler = AsyncIOScheduler()
        scheduler.add_job(infoTotal, CronTrigger(hour="9,18", minute="00", second="0"))
        scheduler.start()

    @bot.event
    async def on_message(message):
        guild = message.guild
        channel = message.channel

         # check if the command is sent thru bot-commands channel or not
        if channel.id != botCommand_channel_id:
            return ''

        # beginning of .total
        if message.content.startswith('.total'):
            await infoTotal()
        # end of .total

        # beginning of .getalljoined
        if message.content.startswith('.getalljoined'):
            #sheets init
            print(f"Importing .env configuration...")

            # If modifying these scopes, delete the file token.pickle.
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            VERIFICATION_SPREADSHEET_ID = config.VERIFICATION_SPREADSHEET_ID
            TAB_DISCORD_RANGE = config.TAB_DISCORD_RANGE

            print("Initializing Google Authentication...")

            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()

            #bots
            thebot = get(guild.members, id=bot.user.id)

            valuesToWrite = [
                [ "id","username","role"],
            ]

            exceptUserIDs = [v for v in exceptions.values()]

            for member in guild.members:
                if member.bot == False and member.id not in exceptUserIDs:
                    state = ""
                    for x in member.roles:
                        if (x.name == "Verified") or (x.name == "Expired") or (x.name == "Unverified"):
                            state += x.name
                            rowValuesToWrite = [f"{member.id}", f"{member.name}#{member.discriminator}", f"{state}"]
                            valuesToWrite.append(rowValuesToWrite)

            #clear the `discord` sheet first
            result1 = sheet.values().clear(spreadsheetId=VERIFICATION_SPREADSHEET_ID, range=TAB_DISCORD_RANGE)
            result1.execute()

            #fill the `discord` sheet with updated value
            body = { 'values': valuesToWrite }
            result2 = sheet.values().update(spreadsheetId=VERIFICATION_SPREADSHEET_ID, range=TAB_DISCORD_RANGE, valueInputOption='USER_ENTERED', body=body).execute()

            await channel.send(f"Sesuai perintah kak <@{message.author.id}> :point_up:, {thebot.nick} (<@{thebot.id}>) sudah mengirimkan daftar peserta server ini {guild.name}!")
        # end of .getalljoined

        #beginning of .setrolebyid
        if message.content.startswith('.setrolebyid'):
            commands = message.content.split()
            target_user_id = int(commands[1])
            target_role_name = str(commands[2])
            target_user = get(guild.members, id=target_user_id)
            channel_perkenalan = get(guild.channels, id=perkenalan_channel_id)
            target_role = get(guild.roles, name=f"{target_role_name}")

            #clear all three statuses
            for role in guild.roles:
                if (role.name.lower() == "verified") or (role.name.lower() == "unverified") or (role.name.lower() == "expired"):
                    await target_user.remove_roles(role)
            #set the determined status
            for role in guild.roles:
                if (role == target_role):
                    await target_user.add_roles(role)
                    await channel.send(f"Sesuai perintah kak <@{message.author.id}> :point_up:, Ben sudah mengubah role {target_user.mention} menjadi {target_role.name}!")

            if(target_role.name.lower() == "verified"):
                congraz_message = f"Selamat ya kak {target_user.mention}! Akun nya sudah terverifikasi!"
                congraz_message += f"\nYang belum kenalan, ditunggu {channel_perkenalan.mention} nyaa"
                congraz_message += f"\nIni adalah pesan otomatis yang dikirim oleh bot. Jika ada pertanyaan silahkan bertanya pada Admin di channel #general yaa"
                await target_user.send(congraz_message)
                
            if(target_role.name.lower() == "expired"):
                bye_message = f"Kakak {target_user.mention}, mohon maaf :pray: kupon progate Anda telah expired!"
                bye_message += f"\nAyo kak, segera claim kupon Progate Plus melalui https://linktr.ee/progateid"
                bye_message += f"\nJangan lupa juga kak, setelahnya mengisi formulir (https://forms.gle/7RftSs16fcEDq5j57), makasih ya kak :pray: "
                bye_message += f"\nIni adalah pesan otomatis yang dikirim oleh bot. Jika ada pertanyaan silahkan bertanya pada Admin di channel #general yaa"

                await target_user.send(bye_message)
        #end of .setrolebyid

    # beginning of infoTotal
    async def infoTotal():
        await bot.wait_until_ready()
        guild = bot.get_guild(progate_nextLevel_guild_id)
        totalnow = guild.member_count
        channel = get(guild.channels, id=statistic_channel_id) #statistic
        promptMessage  = f"\n :alarm_clock: {time.strftime('%d %B %Y')} {time.strftime('%H:%M:%S')} :alarm_clock:"
        promptMessage  += f"\n Komunitas Server **{guild.name}**"
        promptMessage  += f"\n Total Pengguna :arrow_right:  {totalnow-len(exceptions)} pengguna. :arrow_heading_down:"
        user_verified_count = 0
        user_unverified_count = 0
        user_expired_count = 0
        statisticMessage = ""

        for member in guild.members:
            amember = get(guild.members, id=member.id)
            for x in amember.roles:
                if (x.name == "Verified"):
                    user_verified_count += 1
                if (x.name == "Unverified"):
                    user_unverified_count += 1
                if (x.name == "Expired"):
                    user_expired_count += 1

        statisticMessage += f"\n > \t {user_unverified_count} \t Unverified"
        statisticMessage += f"\n > \t {user_verified_count} \t Verified"
        statisticMessage += f"\n > \t {user_expired_count} \t Expired"

        promptMessage += statisticMessage
        await channel.send(promptMessage)
        
    # end of infoTotal

    # Run Discord bot
    bot.run(config.DISCORD_TOKEN)

if __name__ == "__main__":
    main()
