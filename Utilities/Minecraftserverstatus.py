from discord.ext import commands
from mcstatus import JavaServer

@commands.command(name='mcserver')
async def mcserver(ctx, ip: str):
    try:

        server = JavaServer(ip, 25565)
        
        status = server.status() 
        
        await ctx.send(
            f"The server has {status.players.online} player(s) online and replied in {status.latency:.2f} ms."
        )
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
