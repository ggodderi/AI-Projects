from space_invaders.core import GameState, Invader

gs=GameState(width=200,height=200)
gs.player.y=160
gs.invaders=[Invader(gs.player.x, gs.player.y-50)]
b=gs.player_shoot()
print('start invaders:', [(i.x,i.y,i.alive) for i in gs.invaders], 'bullet', (b.x,b.y,b.alive))
for i in range(20):
    gs.update()
    print(f'after {i+1}: invaders:', [(inv.x,inv.y,inv.alive) for inv in gs.invaders], 'b alive', b.alive, 'score', gs.score, 'level', gs.level)
print('final invaders', [(inv.x,inv.y,inv.alive) for inv in gs.invaders])
