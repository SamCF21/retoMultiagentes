from mesa import Agent
import heapq

def heuristic(a, b):
    """
    Calculates the Manhattan distance between two points.
    Args:
        a: First point
        b: Second point
    Returns:
        Manhattan distance between the two points
    """
    #
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(graph, start, goal, free_way):
    """
    A* search algorithm.
    Args:
        graph: The graph where the search will be performed
        start: Starting point
        goal: Goal point
        path: Path to be followed
    Returns:
        The path to be followed
    """

    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while frontier:
        #take the current node with the minimum cost
        current = heapq.heappop(frontier)[1]

        if current == goal:
            break
        
        for next in graph.get_neighborhood(current, moore=False, include_center=False):
            if not free_way(current, next):
                continue

            new_cost = cost_so_far[current] + 1
            
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                heapq.heappush(frontier, (priority, next))
                came_from[next] = current
    
    path = {}
    current = goal
    while current != start:
        if current in came_from:
            previous = came_from[current]
            path[previous] = current
            current = previous
        else:
            return {}
        
    return path

class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, start, end):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

        self.end = end
        self.start = start
        self.path = None
        
    
    def get_path(self):
        self.path = self.find_path()

    
    def check_path(self, current, next, road_direction):
        dx = next[0] - current[0] # Change in x
        dy = next[1] - current[1] # Change in y

        if road_direction == "Right":
            return dx != -1 
        elif road_direction == "Left": 
            return dx != 1 
        elif road_direction == "Up": 
            return dy != -1 
        elif road_direction == "Down": 
            return dy != 1 
        return False 
    #function to find the path from the start to the end
    def find_path(self):
        if self.end:
            def free_way(current,next):
                content = self.model.grid.get_cell_list_contents([next])
                if any(isinstance(agent, Obstacle) for agent in content):
                    return False
                

                #see if there is a road in the next cell
                if any(isinstance(agent, (Road, Traffic_Light, Destination)) for agent in content):
                    #check if the agent is a road
                    road_agent= [agent for agent in content if isinstance(agent, Road)]
                    if road_agent:
                        road_agent = road_agent[0]
                        #check if the road is in the right direction
                        return self.check_path(current, next, road_agent.direction)
                    return True
                return False
            return a_star_search(self.model.grid, self.start, self.end, free_way)
        return None

    def object_orientation(self, current, next):
        """
       To see the direction the agent should face after moving.
        """
        dx = next[0] - current[0] # Change in x
        dy = next[1] - current[1] # Change in y
        if dx == 1: # If the agent moved right,
            return "Right"
        elif dx == -1: 
            return "Left"
        elif dy == -1: 
            return "Up"
        elif dy == 1: 
            return "Down"
        else: 
            return None

    def move(self):
            """ 
            Determines if the agent can move in the direction that was chosen
            """
            if self.path and self.pos in self.path: # If the path is set and the current position is in the path,
                if isinstance(self.model.grid[self.path.get(self.pos)[0]][self.path.get(self.pos)[1]], list):
                    # Itera sobre los agentes en la lista

                    for agent_in_cell in self.model.grid[self.path.get(self.pos)[0]][self.path.get(self.pos)[1]]:
                        if type(agent_in_cell) == Car:
                            next_pos = self.pos
                        elif type(agent_in_cell) == Traffic_Light:
                            if agent_in_cell.state == False:
                                next_pos = self.pos
                            else:
                                next_pos = self.path.get(self.pos) # Get the next position
                        else:
                            next_pos = self.path.get(self.pos) # Get the next position
                
                if next_pos is not None: 
                    # Move the agent to the next position
                    self.model.grid.move_agent(self, next_pos) 
                    # Change the direction of the agent
                    self.direction = self.object_orientation(self.pos, next_pos) 
                    if next_pos == self.end: 
                        print(f"Car {self.unique_id} reached destination {self.end}") 
                        self.model.num_cars_arrived += 1 # Increment the number of cars that reached their destination
                        self.model.remove_car(self)
                else: 
                    print("No valid next position found.")

                """ if road_agent:
                # Move the car based on the direction of the road agent
                if road_agent.direction == "Left":
                    self.model.grid.move_agent(self, (x - 1, y))
                elif road_agent.direction == "Right":
                    self.model.grid.move_agent(self, (x + 1, y))
                elif road_agent.direction == "Up":
                    self.model.grid.move_agent(self, (x, y + 1))
                elif road_agent.direction == "Down":
                    self.model.grid.move_agent(self, (x, y - 1)) """

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.move()

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction