I created a simple snake project, where the head is yellow annd the body is green for easier visibility. 
I also created an RL AI that plays the game, although it isn't doing as well as a human player.
So, I improved on it by ditching the Q-Learning and instead, using A* & Perturbated Hamiltonian cycles to ensure it doesn't die while still getting the apple as quickly as possible.

Snake1:
Standard 4-arrow key playstyle of the game Snake.

Snake2:
Unique rotational 2 arrow-key playstyle of the game Snake.

Q-Learning AI Files:-

SnakeAI:
Contains Q-Learning methods and attributes that is used to predict rewards of future states.

AI_Environment:
Q-Learning AI Environment that runs the training epochs & the snake itself. Based on the file SnakeAI.

avg_reward_500k_epochs:
PNG file that tracks the reward of the Q-Learning AI that it projects throughout it's training. Sadly, it seems to stagnate after some time, making it only work for snake lengths up to 20 or so.


A* + Hamiltonian Cycle Files:-

Hamiltonian_Test:
Involves snake_algo_ai file. It generates a Hamiltonian cycle where it goes through every 25x25 cell in the 1000x500 pixel grid only once and loops back to the beginning. This is mainly to test if the Hamiltonian cycle is generating properly.

snake_algo_ai:
The first A* + Perturb algorithm combination. It insists that the snake takes the path of A* first, then once it has exhausted the possible paths of A*, go to perturbated Hamiltonian cycle. If that is also runnning on empty, then move to the final part which is pure Hamiltonian cycle. Although it dies, it does provide a valiant effort that truimphs above the Q-Learning AI. Going to lengths beyond 100. 

algo_environment_1:
The environment for snake_algo_ai.

snake_algo_additional:
Added extra features on top of snake_algo_ai to make it unique. Such as a flood check, a longer path that is safe in case if the Snake ever ended up in a bad situation, checking for safe squares, etc. These all combined to make an AI that very nearly beat the game, but it got stuck in the last few apples where it felt the need to loop as there was no other "safe" path it saw and got stuck. Performance wise, beats the snake_algo_ai by a long shot and goes up to 3 squares remaining to clear before dying or looping. But completion wise, it doesn't even get anywhere.

algo_environment_2:
The environment for snake_algo_additional.

snake_algo_additional2:
Removed some features such as the long path and instead tried to adopt an 'A* "safe" shortcuts on cycles based on head and tail position' approach where it will start with A* but as the Snake gets longer, the shortcuts it takes from the cycle move to more safer alternatives, essentially adapting to the board. However, it had the opposite problem to snake_algo_additional. Dying earlier. Since it thinks that the A* path from the head to tail based on a cycle is the safest without realizing obstacles that may trap the Snake or just make it loop itself. Essentially, while trying to unwind itself, it only creates a way to make the path worse. Performance wise, doesn't do as well as snake_algo_additional as it doesn't even get to lengths 150+ without dying. Completion wise, completely luck based as it hopes that the cycle shortcuts are actually not trapping itself between the head and tail. 

algo_environment_3:
The environment for snake_algo_additional2.

snake_algo_additional3:
The potentially final version of the A* + Perturb algorithm combination. It uses the base as Perturbated Hamiltonian cycle that gets close to the apple without dying and only then it uses A* to create it's own shortcuts without ruining the cycle, which is the reverse/converse of snake_algo_additional2, where the cycles are based on the head and tail position and the A* path the snake follows. I started with simple Hamiltonian, but as it progressed, it got better and better and finding apples within or outside of its cycle. It can complete the entire board faster than snake_algo_additional2 or snake_algo_ai as well. Maybe not as good or fast as snake_algo_additional, but gosh, it massively bolsters the survivability of the Snake. From not dying to doing shortcuts while not dying or looping, I managed to create a self-sustaining Snake AI that can create and find shortcuts based on cycles that were already made, starting from the base Hamiltonian cycle all the way to the A*+Perturb hybrid.

algo_environment_4:
Th environment for snake_algo_additional3.





