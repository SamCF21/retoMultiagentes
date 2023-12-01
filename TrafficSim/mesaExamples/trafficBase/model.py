from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json

import requests
import json


class CityModel(Model):
    """
    Creates a model based on a city map.

    Args:
        N: Number of agents in the simulation
    """

    def __init__(self, N):
        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("/Users/VMM/Desktop/repos/retoGr-ficas-pruebas-/TrafficSim/mesaExamples/trafficBase/city_files/mapDictionary.json"))

        self.traffic_lights = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open("/Users/VMM/Desktop/repos/retoGr-ficas-pruebas-/TrafficSim/mesaExamples/trafficBase/city_files/2023_base.txt") as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0]) - 1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus=False)
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}",
                            self,
                            False if col == "S" else True,
                            int(dataDictionary[col]),
                        )
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)

        self.num_agents = N
        self.running = True
        self.steps=0
        self.num_cars_arrived = 0
    
    def set_destination(self):
        destinations= []
        for agent in self.schedule.agents:
            if isinstance(agent, Destination):
                destinations.append(agent.pos)
        return self.random.choice(destinations)
    
    def remove_car(self, car):
        """
        Removes the car from the model.

        Args:
            car: The car to be removed.
        """
        self.schedule.remove(car)
        self.grid.remove_agent(car)
    

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()

        print(self.schedule.steps)
        if self.schedule.steps % 100 == 0:

            url = "http://52.1.3.19:8585/api/"
            endpoint = "attempts"

            data = {
            "year" : 2023,
            "classroom" : 302,
            "name" : "Equipo 12 - Sam y Vale",
            "num_cars": self.num_cars_arrived
            }

            headers = {
            "Content-Type": "application/json"
            }

            response = requests.post(url+endpoint, data=json.dumps(data), headers=headers)

            print("Request " + "successful" if response.status_code == 200 else "failed", "Status code:", response.status_code)
            print("Responses:", response.json())

        # Create a new Car agent at each corner every 10 steps
        if self.schedule.steps % 10 == 0 or self.schedule.steps == 1:
            corners = [(0, 0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1),]
            for corner in corners:
                new_agent = Car(self.num_agents + 1, self, corner, self.set_destination())
                new_agent.get_path()
                
                self.grid.place_agent(new_agent, corner)
                self.schedule.add(new_agent)
                self.num_agents += 1
