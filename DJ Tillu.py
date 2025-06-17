import discord
from discord.ext import commands
from discord import FFmpegOpusAudio
import yt_dlp
import asyncio
import os

os.environ["PATH"] += os.pathsep + r"C:\Users\Admin\Documents\FFMPEG\bin"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch',
    'noplaylist': True,
    'extract_flat': False,
    'forceurl': True
}

class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []

    @commands.command()
    async def play(self, ctx, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("Voice Chat ki po raa labbey!!!!")
        if not ctx.voice_client:
            await voice_channel.connect()

        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(search, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                url = info['url']
                title = info['title']
                self.queue.append((url, title))
                await ctx.send(f'Taruvati Paata:**{title}**')

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            try:
                print(f"[PLAY] {title}")
                print(f"[STREAM URL] {url}")
                source = await FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(
                    source,
                    after=lambda e: self.client.loop.create_task(self.play_next(ctx))
                )
                await ctx.send(f'Ee chakkati gaanam mee kosam **{title}**')
            except Exception as e:
                print(f"[FFmpeg ERROR] {e}")
                await ctx.send("Sairaaaam ee paataki battai paddade ayyayyooooo 💀")
        else:
            await ctx.send("List Khaali bhAAi!!!!")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send('Lepesa 👍')

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("OK aapina 👍")
        else:
            await ctx.send("Paata yeda undi raa neeku pause cheyyaniki")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("OK malla pettina 👍")
        else:
            await ctx.send("Paata aapakunda malli resume antav em raa howla")


client = commands.Bot(command_prefix="Tillu mowa ", intents=intents)

async def main():
    await client.add_cog(MusicBot(client))
    await client.start('MTM4NDIyMzUxMTk3MDU4MjY3MQ.GsC5yY.H1-j8QTQJttkalBDqDKoonKoNyc6Gq4_1Gqmz0')

asyncio.run(main())
