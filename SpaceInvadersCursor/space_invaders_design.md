# Product requirements

1 - Create a game very similar to the legacy space invaders game.
2 - The graphics for the invaders and the shooter to look authentic
3 - There is to be sound with each shot and each hit.
4 - When a bullet hits an invader, the bullet stops.  One bullet cannot kill more than one invader.
5 - If the invaders hit the shooter, or the shooter's level, the game is over.
6 - This game is to be written in python using whichever graphics library you feel is best.
7 - Make the sure the game is performant - the sound and drawing should not slow down the game.
8 - Also allow up to 5 bullets to be in the air at a time.
9 - Please make sure there is a score that is displayed.
10 - Please make sure there is a game over screen when the invaders hit the ground or the shooter.
11 - Ask the user if they want to play again.
12 - Once a set of invaders are cleared, a new set with more invaders appears and is faster than the previous one.  This continues until the game is over or 12 levels are reached, which ever happens first.
13 - For each set of invaders, as the number of invaders left in the level decreases, the speed of the remaining invaders speeds up slightly.
14 - User Multi-threading to ensure the system is performant.
15 - There is a total of 170 bullets that can be used per level.  Once the bullets are used up, the shooting stops and the invaders are allowed to reach the ground.
16 - The number of bullets remaining for this level should be seen on the Heads Up Display.
17 - The shooter will look like a tank.
18 - The invaders will look like spiders trying to invade.
19 - The invaders will periodically drop a bomb on the shooter.  If the bomb hits the shooter, the shooter will the shooter will blow up and the game will end.
20 - If the bullet from the shooter hits the bomb from the invader, the bomb will explode and stop dropping.
21 - The width of the shooter will be no more than the width of the invaders.