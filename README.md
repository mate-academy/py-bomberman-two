# Bomberman pygame application day 2

- Read [the guideline](https://github.com/mate-academy/py-task-guideline/blob/main/README.md) before start
- [Pygame primer](https://realpython.com/pygame-a-primer/#sprite-groups)
- [Pygame sprites and groups](https://kidscancode.org/blog/2016/08/pygame_1-2_working-with-sprites/)

You already have player that can move and plant a bomb.
Now you have to implement such features:
- Bomb should explode in few seconds after the planting.
- In the explosion, bomb generates fire for 5 cells in 
four directions. Fire exists for a small amount of 
time. Fire cannot spread over the wall.
- Enemies should be generated out of bounds with period
of one second. Add an event for this. Enemies should try
to overtake the player. Enemy should not walk over
the walls.
- If player or any enemy touch the fire - he dies 
immediately.
- Initially player should have 100 health points. If any
enemy touches the player - it dies and player's health is
reduced by 10.
- If player's health less than or equal to zero - player 
dies.
- If player dies, the game is over.

Example:

![Example2](https://user-images.githubusercontent.com/80070761/153884714-8fac9c58-b7c4-4bc2-9c38-e1c698d9eba1.gif)
