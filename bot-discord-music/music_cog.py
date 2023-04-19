import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.is_playing = False
        self.is_paused = False
        
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        #TODO complete args
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnected_streamed 1 -reconnect_delay_max 5', }
        
        self.vc = None
        
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=false) ['entries'][0]
            except Exception:
                return False
        return {'source': info['formats'[0]['url']], 'title': info['title']}
        
    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            
            m_url = self.music_queue[0][0]['source']
            
            self.music_queue.pop(0)
            
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
            
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1]['source']

                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel deepshit")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1]) 

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())     

        else: 
            self.is_playing = False
        
    @commands.command(name="play", aliases=["p", "playing"], help="Play the song you want or not, depend of your ugly face's or not")
    async def play(self, ctx, *args):
        query = " ".join(args)
        
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song, you even don't know how to c/p di***")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, voice_channel])
                
                if self.is_playing == False:
                    await self.play_music(ctx)
                    
    @commands.command(name="pause", aliases=["stop"], help="you can't stop the music, but you actually do")
    async def play(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif  self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
    
    @commands.command(name="resume", aliases=["r"], help="Et c'est parti LET'S GO !!!!")
    async def play(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            
    @commands.command(name="skip", aliases=["s"], help="This clearly means - I don't like your taste -")
    async def play(self, ctx, *args):
        if self.vc != None and self.vc:
            self.vc.stop()
            await self.vc.play_music(ctx)