# Bomberman pygame application day 2

- Read [the guideline](https://github.com/mate-academy/py-task-guideline/blob/main/README.md) before start
- [Pygame primer](https://realpython.com/pygame-a-primer/#sprite-groups)
- [Pygame sprites and groups](https://kidscancode.org/blog/2016/08/pygame_1-2_working-with-sprites/)

You already have a player that can move and plant a bomb.
Now you have to implement such features:
1. Bomb should explode in a few seconds after the planting.
Remove the bomb after an explosion by method `kill()`.
2. During the explosion bomb generate fire in four 
directions: left, right, up, down. Fire is usual `Sprite` with the
same size as the bomb. Fire cannot spread over the wall. In this task,
bombs are planted at the center of the line. You can
calculate coordinates of the center of a next fire and
check if it collides the wall, if it does - 
the fire stops spreading, if it
doesn't fire continues to spread. To check if sprite collides point
use `sprite.rect.collidepoint((x, y))`.
Fire exists for a small amount of time.
3. Create enemies. Enemies should be generated out of bounds within one second. 
Add an event for this. Enemies should charge the player. 
The enemy should not walk over the walls or bombs. [Events](https://realpython.com/pygame-a-primer/#custom-events)
4. If the player or any enemy touches the fire - he dies 
immediately.
5. Initially player should have 100 health points. If any
enemy touches the player - it dies and the player's health is
reduced by 10. 
6. Store the score. If the enemy dies, the score is incremented by 10 by default. 
7. If the player's health is less than or equal to zero - the player 
dies. If the player dies, the game is over.
8. Add different project properties constants to the `config.py`, such as:
`FRAMES_PER_SECOND`, `DEFAULT_PLAYER_HP`, `DEFAULT_PLAYER_SPEED`, 
`BOMB_TIMER`, `EXPLOSION_RANGE`, `BACKGROUND_COLOR`, `DEFAULT_EVENT_TIMEOUT`
etc.
9. Add an interface to the application that shows the current score, 
player's health, and speed. [Score](https://www.techwithtim.net/tutorials/game-development-with-python/pygame-tutorial/scoring-health-bars/)

Example:

![Example](https://user-images.githubusercontent.com/80070761/154238655-75a3d90e-a298-4408-a01a-0d604890334a.gif)