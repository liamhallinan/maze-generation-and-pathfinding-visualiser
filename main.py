import pygame
import sys
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import * 
from tkinter.ttk import *
import random
from settings import *
import time

class Grid:
    def __init__(self, rows, columns, grid_size):
        self.rows = rows
        self.columns = columns
        self.grid_size = grid_size
        self.grid = [[0] * columns for _ in range(rows)] # initalises grid, setting all cells to 0 (empty)
        self.start_node_pos = None
        self.end_node_pos = None
        self.path = None

    def reset(self):
        self.grid = [[0] * self.columns for _ in range(self.rows)] # resets grid, setting all cells to 0 (empty)
        self.start_node_pos = self.end_node_pos = None
        self.path = None
        maze_solver.node_pos = None

    def reset_explored_nodes(self):
        # resets explored nodes, so grid is ready to be searched again
        for row in range(self.rows):
            for column in range(self.columns):
                if self.grid[row][column] == 3: # 3 represents a explored node
                    self.grid[row][column] = 0

    def randomise_walls(self, probability_of_wall=0.1):
        # gives each cell in the grid a probability_of_wall chance of becoming a wall node
        for row in range(self.rows):
            for column in range(self.columns):
                if self.grid[row][column] not in [1, 2] and random.random() < probability_of_wall:
                    self.grid[row][column] = -1 # -1 represents a wall node

    def get_neighbours(self, node):
        #gets the neighbouring cells of a node
        row, column = node
        neighbours = []

        for change_in_row, change_in_column in [(-1, 0), (1, 0), (0, -1), (0, 1)]: 
            new_row, new_column = row + change_in_row, column + change_in_column
            # checks if new position is within grid bounds, and not a wall, if so it's added to neighbours
            if 0 <= new_row < self.rows and 0 <= new_column < self.columns and self.grid[new_row][new_column] != -1:
                neighbours.append((new_row, new_column))

        #print(neighbours)
        return neighbours

class Interface:
    def __init__(self, grid, max_grid_height, max_grid_width):
        self.grid = grid
        self.max_grid_height = max_grid_height 
        self.max_grid_width = max_grid_width
        self.max_grid_dimension = max(MAX_GRID_WIDTH, MAX_GRID_HEIGHT)
        self.grid_size = min(max_grid_width // grid.columns, max_grid_height // grid.rows)
        self.width = grid.columns * self.grid_size  
        self.height = grid.rows * self.grid_size 
        self.placing_start = False
        self.placing_end = False
        self.placing_wall = False
        self.path = None

        # initialize button coordinates
        self.reset_button_rect = pygame.Rect(10, self.height + 10, 100, 30)
        self.randomise_button_rect = pygame.Rect(self.reset_button_rect.right + 10, self.height +10, 220, 30)
        self.generate_maze_button_rect = pygame.Rect(self.randomise_button_rect.right + 10, self.height + 10, 200, 30)
        self.info_button_rect = pygame.Rect(self.generate_maze_button_rect.right + 50, self.height +10, 50, 30)
        self.bfs_button_rect = pygame.Rect(550,200,75,50)
        self.dijkstra_button_rect = pygame.Rect(550, 300, 100, 50)
        self.solve_button_rect = pygame.Rect(550, 400, 100, 50)

        pygame.init()
        self.window = pygame.display.set_mode((self.height + 230, self.width + 50), 0,0)
        pygame.display.set_caption("Maze generation and pathfinding visualiser")

    def draw_grid(self):
        # colours cell depending on what type of node it is
        for row in range(self.grid.rows):
            for column in range(self.grid.columns):
                colour = WHITE
                if self.grid.grid[row][column] == 1:
                    colour = START_COLOUR
                elif self.grid.grid[row][column] == 2:
                    colour = END_COLOUR
                elif self.grid.grid[row][column] == -1:
                    colour = WALL_COLOUR
                elif self.grid.grid[row][column] == 3:
                    colour = PREV_EXPLORED_COLOUR
                elif self.grid.grid[row][column] == 4:
                    colour = CURRENT_EXPLORED_COLOUR
                elif self.grid.grid[row][column] == 5:
                    colour = USER_CONTROLLED_COLOUR

                pygame.draw.rect(self.window, colour, (column * self.grid_size, row * self.grid_size, self.grid_size, self.grid_size))

        # draws horizontal + vertical grid lines
        for i in range(0, self.grid.rows):
            pygame.draw.line(self.window, BLACK, (0, i * self.grid_size), (self.width, i * self.grid_size))
        for j in range(0, self.grid.columns):
            pygame.draw.line(self.window, BLACK, (j * self.grid_size, 0), (j * self.grid_size, self.height))

    # method to draw all buttons on interface
    def draw_buttons(self, reset_button_rect, bfs_button_rect, randomise_walls_button_rect, info_button_rect, dijkstra_button_rect, generate_maze_button_rect, solve_button_rect, font):
        # checks if the mouse is over the buttons (to add 'hovering' effect)
        reset_hovered = reset_button_rect.collidepoint(pygame.mouse.get_pos())
        bfs_hovered = bfs_button_rect.collidepoint(pygame.mouse.get_pos())
        dijkstra_hovered = dijkstra_button_rect.collidepoint(pygame.mouse.get_pos())
        randomise_hovered = randomise_walls_button_rect.collidepoint(pygame.mouse.get_pos())
        info_hovered = info_button_rect.collidepoint(pygame.mouse.get_pos())
        generate_maze_hovered = generate_maze_button_rect.collidepoint(pygame.mouse.get_pos())
        solve_hovered = solve_button_rect.collidepoint(pygame.mouse.get_pos())

        # each button is drawn below

        pygame.draw.rect(self.window, (191, 191, 191) if reset_hovered else (211, 211, 211), reset_button_rect)
        reset_text = font.render("Reset", True, BLACK)
        self.window.blit(reset_text, (reset_button_rect.x + 10, reset_button_rect.y + 5)) 

        pygame.draw.rect(self.window, (191, 191, 191) if bfs_hovered else (211, 211, 211), bfs_button_rect)
        bfs_text = font.render("BFS", True, BLACK)
        self.window.blit(bfs_text, (bfs_button_rect.x + 10, bfs_button_rect.y + 5))

        pygame.draw.rect(self.window, (191, 191, 191) if dijkstra_hovered else (211, 211, 211), dijkstra_button_rect)
        dijkstra_text = font.render("Dijkstra", True, BLACK)
        self.window.blit(dijkstra_text, (dijkstra_button_rect.x + 10, dijkstra_button_rect.y + 5))

        pygame.draw.rect(self.window, (191, 191, 191) if randomise_hovered else (211, 211, 211), randomise_walls_button_rect)
        randomise_walls_text = font.render("Randomise Walls", True, BLACK)
        self.window.blit(randomise_walls_text, (randomise_walls_button_rect.x + 10, randomise_walls_button_rect.y + 5))

        pygame.draw.rect(self.window, (191, 191, 191) if info_hovered else (211, 211, 211), info_button_rect)
        info_text = font.render("?", True, BLACK)
        self.window.blit(info_text, (info_button_rect.x + 15, info_button_rect.y + 5))

        pygame.draw.rect(self.window, (191, 191, 191) if generate_maze_hovered else (211, 211, 211), generate_maze_button_rect)
        generate_maze_text = font.render("Generate maze", True, BLACK)
        self.window.blit(generate_maze_text, (generate_maze_button_rect.x +10, generate_maze_button_rect.y +5))

        pygame.draw.rect(self.window, (191, 191, 191) if solve_hovered else (211, 211, 211), solve_button_rect)
        solve_text = font.render("Solve", True, BLACK)
        self.window.blit(solve_text, (solve_button_rect.x +10, solve_button_rect.y +5))

    def draw_grid_lines(self):
        # draws horizontal and vertical grid lines
        for i in range(1, self.grid.rows +1):
            pygame.draw.line(self.window, BLACK, (0, i * self.grid_size), (self.width, i * self.grid_size))
        for j in range(1, self.grid.columns +1):
            pygame.draw.line(self.window, BLACK, (j * self.grid_size, 0), (j * self.grid_size, self.height))

    def handle_button_clicks(self, event):
        global path  
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.reset_button_rect.collidepoint(event.pos):
                # reset button clicked
                self.grid.reset()
                path = None  
                maze_solver.stop_timer()
                maze_solver.reset()
            elif self.bfs_button_rect.collidepoint(event.pos) and self.grid.start_node_pos and self.grid.end_node_pos:
                # bfs button clicked
                path = pathfinding.bfs(self.grid, self.grid.start_node_pos, self.grid.end_node_pos, self.window)
                if path is None:
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showerror("Error", "No solution to the maze")
                    # if no solution display error message - tkinter
                    root.destroy()
            elif self.dijkstra_button_rect.collidepoint(event.pos) and self.grid.start_node_pos and self.grid.end_node_pos:
                # dijkstra button clicked
                path = pathfinding.dijkstra(self.grid, self.grid.start_node_pos, self.grid.end_node_pos, self.window)
                if path is None:
                    # if no solution display error message - tkinter
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showerror("Error", "No solution to the maze")
                    root.destroy()
            elif self.randomise_button_rect.collidepoint(event.pos):
                # randomise button clicked
                self.grid.randomise_walls()
            elif self.info_button_rect.collidepoint(event.pos):
                # info button clicked
                self.info_button()
            elif self.generate_maze_button_rect.collidepoint(event.pos):
                # maze button clicked
                maze_generator.initiate_maze(self.grid)
            elif self.solve_button_rect.collidepoint(pygame.mouse.get_pos()) and self.grid.start_node_pos and self.grid.end_node_pos:
                # solve button clicked
                maze_solver.start_timer()

    def handle_mouse_events(self):
        # handles user-grid interaction with mouse
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        #mouse_y = pygame.mouse.get_pos()
        row, column = mouse_y // self.grid_size, mouse_x // self.grid_size

        if mouse_buttons[0] and not self.placing_end:
            if 0 <= row < self.grid.rows and 0 <= column < self.grid.columns and self.grid.grid[row][column] == 0:
                if self.grid.start_node_pos is None:
                    self.grid.grid[row][column] = 1  # start node
                    self.placing_start = True
                    self.grid.start_node_pos = (row, column)

        elif mouse_buttons[2] and not self.placing_start and not self.placing_end:
            if 0 <= row < self.grid.rows and 0 <= column < self.grid.columns and self.grid.grid[row][column] == 0:
                if self.grid.end_node_pos is None:
                    self.grid.grid[row][column] = 2  # end node
                    self.placing_end = True
                    self.grid.end_node_pos = (row, column)

        elif mouse_buttons[1]:
            if 0 <= row < self.grid.rows and 0 <= column < self.grid.columns:
                self.grid.grid[row][column] = -1  # wall
                self.drawing_wall = True

        elif not any(mouse_buttons):
            self.placing_start = self.placing_end = self.drawing_wall = False

    
    def draw_path(self, path):
        # draws path if it exists
        #print(path)
        if path:
            for node in path[1:-1]:
                row, column = node
                pygame.draw.rect(self.window, BLUE, (column * self.grid_size, row * self.grid_size, self.grid_size, self.grid_size))
                self.draw_grid_lines()  # Draw grid lines

    def draw_start_end_nodes(self):
        # draws start/end nodes
        if self.grid.start_node_pos:
            row, column = self.grid.start_node_pos
            pygame.draw.rect(self.window, START_COLOUR, (column * self.grid_size, row * self.grid_size, self.grid_size, self.grid_size))

        if self.grid.end_node_pos:
            row, column = self.grid.end_node_pos
            pygame.draw.rect(self.window, END_COLOUR, (column * self.grid_size, row * self.grid_size, self.grid_size, self.grid_size))

        self.draw_grid_lines() 

    # tkinter window acting as a help/ information window guide
    def info_button(self):
        root = tk.Tk()
        root.title("Information")
        root.geometry("720x800")
        
        tabControl = ttk.Notebook(root)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)
        
        tabControl.add(tab1, text='How to use')
        tabControl.add(tab2, text='Breadth-First Search')
        tabControl.add(tab3, text="Dijkstra's Algorithm")
        tabControl.pack(expand=1, fill="both")

        
        ttk.Label(tab1, text="Mouse interaction", font="Calibri 20 bold italic").grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(tab1, text="Left click", font="Calibri 16 bold").grid(row=1, column=0, padx=10, pady=10)
        ttk.Label(tab1, text="   Place start node", font="Calibri 11").grid(row=1, column=1, padx=1, pady=10)

        ttk.Label(tab1, text="Right click", font="Calibri 16 bold").grid(row=2, column=0, padx=10, pady=1)
        ttk.Label(tab1, text="   Place end node", font="Calibri 11").grid(row=2, column=1, padx=1, pady=1)

        ttk.Label(tab1, text="Scroll wheel click", font="Calibri 16 bold").grid(row=3, column=0, padx=10, pady=1)
        ttk.Label(tab1, text="   Place wall node", font="Calibri 11").grid(row=3, column=1, padx=1, pady=1)

        ttk.Label(tab1, text="Button interaction", font="Calibri 20 bold italic").grid(row=4, column=0, padx=10, pady=1)

        ttk.Label(tab1, text="Reset", font="Calibri 16 bold").grid(row=5, column=0, padx=10, pady=1)
        ttk.Label(tab1, text="   Resets grid", font="Calibri 11").grid(row=5, column=1, padx=1, pady=1)

        ttk.Label(tab1, text="Randomise walls", font="Calibri 16 bold").grid(row=6, column=0, padx=10, pady=1)
        ttk.Label(tab1, text="    Gives all empty nodes a certain probablity of becoming a wall node", font="Calibri 11").grid(row=6, column=1, padx=1, pady=1)

        ttk.Label(tab1, text="Generate maze", font="Calibri 16 bold").grid(row=7, column=0, padx=10, pady=1)
        ttk.Label(tab1, text="    Generates a random maze", font="Calibri 11").grid(row=7, column=1, padx=1, pady=1)

        ttk.Label(tab1, text="BFS", font="Calibri 16 bold").grid(row=8, column=0, padx=10, pady=1)
        ttk.Label(tab1, text="    Perform a Breadth-First-Search on grid", font="Calibri 11").grid(row=8, column=1, padx=1, pady=1)

        ttk.Label(tab1, text="Dijkstra", font="Calibri 16 bold").grid(row=9, column=0, padx=10, pady=1)
        ttk.Label(tab1, text="    Perform Dijkstra's Algorithm on grid", font="Calibri 11").grid(row=9, column=1, padx=1, pady=1)

        ttk.Label(tab1, text="Solve", font="Calibri 16 bold").grid(row=10, column=0, padx=10, pady=1)
        ttk.Label(tab1, text="    Initiates a timer, user can attempt to solve the grid by using the arrow keys", font="Calibri 11").grid(row=10, column=1, padx=1, pady=1)

        ''' https://www.geeksforgeeks.org/python-add-image-on-a-tkinter-button/ '''

        bfs_photo = PhotoImage(file = r"C:\Users\Liam\Desktop\nea_code\BFS_image.png") 
        bfs_title = ttk.Label(tab2, text = "Breadth-First Search", font="Calibri 11 bold")
        bfs_title.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        bfs_image = Label(tab2, image=bfs_photo)
        bfs_image.grid(row=1, column=0, sticky="nw", padx=10, pady=10)
        bfs_text = ttk.Label(tab2, text="""The Breadth-First Search algorithm works by starting at the root of the graph, 
        visitng all nodes on the current depth level, before moving to the next depth level.""", font="Calibri 12")
        '''https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/'''
        bfs_text.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        ttk.Label(tab2, text="Pseudocode", font="Calibri 11 bold").grid(row=3, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="Input: s as the source node", font="Calibri 8").grid(row=4, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text=" ", font="Calibri 8").grid(row=5, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="BFS (G, s)", font="Calibri 8").grid(row=6, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="let Q be queue.", font="Calibri 8").grid(row=7, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="Q.enqueue( s )", font="Calibri 8").grid(row=8, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text=" ", font="Calibri 8").grid(row=9, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="mark s as visited", font="Calibri 8").grid(row=10, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="while ( Q is not empty)", font="Calibri 8").grid(row=8, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="v = Q.dequeue( )", font="Calibri 8").grid(row=11, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text=" ", font="Calibri 8").grid(row=12, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="for all neighbours w of v in Graph G", font="Calibri 8").grid(row=13, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="if w is not visited", font="Calibri 8").grid(row=14, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="Q.enqueue( w )", font="Calibri 8").grid(row=15, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab2, text="mark w as visited", font="Calibri 8").grid(row=16, column=0, sticky="w", padx=10, pady=(5, 0))
       
        dijkstra_photo = PhotoImage(file = r"C:\Users\Liam\Desktop\nea_code\dijkstra_image.png") 
        dijkstra_title = ttk.Label(tab3, text = "Dijktra's algorithm", font="Calibri 11 bold")
        dijkstra_title.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        dijkstra_image = Label(tab3, image=dijkstra_photo)
        dijkstra_image.grid(row=1, column=0, sticky="nw", padx=10, pady=10)
        dijkstra_text = ttk.Label(tab3, text="""Dijkstra's algorithm finds the shortest path from the start node to all other nodes in a graph by using the 
     weights of edges to find a path that minimises the total distance between start node and all other nodes.""", font="Calibri 12")
        dijkstra_text.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        '''https://www.freecodecamp.org/news/dijkstras-shortest-path-algorithm-visual-introduction/#:~:text=Dijkstra's%20Algorithm%20finds%20the%20shortest,node%20and%20all%20other%20nodes.'''

        ttk.Label(tab3, text="Pseudocode", font="Calibri 11 bold").grid(row=3, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="function Dijkstra(Graph, source):", font="Calibri 8").grid(row=4, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="  for each vertex v in Graph.Vertices:", font="Calibri 8").grid(row=5, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="      dist[v] = INFINITY", font="Calibri 8").grid(row=6, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="          prev[v] = UNDEFINED", font="Calibri 8").grid(row=7, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="          add v to Q", font="Calibri 8").grid(row=8, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="  dist[source] = 0", font="Calibri 8").grid(row=9, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="", font="Calibri 8").grid(row=10, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="  while Q is not empty:", font="Calibri 8").grid(row=8, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="      u = vertex in Q with min dist[u]", font="Calibri 8").grid(row=11, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="      remove u from Q", font="Calibri 8").grid(row=12, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="", font="Calibri 8").grid(row=13, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="      for each neighbor v of u still in Q:", font="Calibri 8").grid(row=14, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="          alt = dist[u] + Graph.Edges(u, v)", font="Calibri 8").grid(row=15, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="          if alt < dist[v]:", font="Calibri 8").grid(row=16, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="              dist[v] = alt", font="Calibri 8").grid(row=17, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="              prev[v] = u", font="Calibri 8").grid(row=18, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="", font="Calibri 8").grid(row=19, column=0, sticky="w", padx=10, pady=(5, 0))
        ttk.Label(tab3, text="  return dist[], prev[]", font="Calibri 8").grid(row=20, column=0, sticky="w", padx=10, pady=(5, 0))

        root.mainloop() 

class Pathfinding:
    def __init__(self):
        self.path = None

    def bfs(self, grid, start, end, window, animation_delay=5):
        queue = [start] # queue initialised 
        visited = [] # list to track visited nodes
        came_from = {} # dictionary to store parent nodes, used to reconstruct path

        while queue:
            current_node = queue.pop(0)

            # if current node is end node, reconstruct path and return
            if current_node == end:
                grid.reset_explored_nodes()
                return self.reconstruct_path(start, end, came_from)

            # explore neighbours of current node
            for neighbour in grid.get_neighbours(current_node):
                if neighbour not in visited: # add neighbour to queue and mark visited
                    queue.append(neighbour)
                    visited.append(neighbour)
                    came_from[neighbour] = current_node # parent node stored to reconrcut path
                    if neighbour != start and neighbour != end:
                        grid.grid[neighbour[0]][neighbour[1]] = 3
                    pygame.time.delay(animation_delay)
                    window.fill(WHITE)
                    interface.draw_grid()
                    pygame.display.flip()

        return None

    # boilerplate code to reconstruct path from end node to start node
    def reconstruct_path(self, start, end, came_from):
        path = [end]
        current_node = end

        while current_node != start:
            current_node = came_from[current_node]
            path.append(current_node)

        return path[::-1]  # reverses path to get it from start to end

    def dijkstra(self, grid, start, end, window, animation_delay=5):
        self.dists = {}
        self.prev_nodes = {}

        # nested loops to popilated dictionaries
        for row in range(grid.rows):
            for column in range(grid.columns):
                self.dists[(row, column)] = float('inf')
                self.prev_nodes[(row, column)] = None

        self.dists[start] = 0

        # 2d array to keep track of visited nodes
        visited = [[0] * grid.columns for _ in range(grid.rows)]
        while True:
            # gets  node with  smallest distance among unvisited nodes
            min_dist_node = None
            min_dist = float('inf')
            for node, dist in self.dists.items():
                row, column = node
                if visited[row][column] == 0 and dist < min_dist:
                    min_dist = dist
                    min_dist_node = node

            if min_dist_node is None:
                # all reachable nodes have been visited
                break

            row, column = min_dist_node
            visited[row][column] = 1  # node has been visited

            if min_dist_node == end:
                grid.reset_explored_nodes()
                return self.reconstruct_path(start, end, self.prev_nodes)

            for neighbour in grid.get_neighbours(min_dist_node):
                # calculate  distance to neighbour thru current node
                dist = self.dists[min_dist_node] + 1 

                if dist < self.dists[neighbour]:
                    self.dists[neighbour] = dist
                    self.prev_nodes[neighbour] = min_dist_node
                    if neighbour != start and neighbour != end:
                        grid.grid[neighbour[0]][neighbour[1]] = 3
                    pygame.time.delay(animation_delay)
                    window.fill(WHITE)
                    interface.draw_grid()
                    pygame.display.flip()

class MazeGenerator:
    def initiate_maze(self, grid):
        # set all cells to walls
        for row in range(grid.rows):
            for column in range(grid.columns):
                grid.grid[row][column] = -1

        #print(grid.grid)
        
        #  recursive backtracking to generate maze
        def generate_maze(row, column):
            grid.grid[row][column] = 0  # mark the current cell as empty
            
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)] 
            random.shuffle(directions)
            
            # explore each direction from current cell
            for change_in_row, change_in_column in directions:
                n_row, n_column = row + change_in_row, column + change_in_column
                #hecks if new position is within grid bounds and unvisited
                if (0 <= n_row < grid.rows) and (0 <= n_column < grid.columns) and (grid.grid[n_row][n_column] == -1):
                    # carve passage between current cell and unvisited neighbour
                    wall_row = (row + n_row) // 2
                    wall_column = (column + n_column) // 2
                    grid.grid[wall_row][wall_column] = 0 
                    # recursion
                    generate_maze(n_row, n_column)
        # maze generation always starts from top left corner
        generate_maze(0, 0)
          
class MazeSolver:
    def __init__(self, start_node_pos):
        self.start_time = None
        self.font = pygame.font.Font(None, 36)
        self.timer_rect = pygame.Rect(550, 100, 150, 50)
        self.timer_running = False
        self.node_pos = start_node_pos
        self.initial_node_pos_set = False
        self.elapsed_time = 0 
        self.should_draw_timer = False

    def reset(self):
        self.start_time = None
        self.timer_running = False
        self.node_pos = None
        self.initial_node_pos_set = False
        self.elapsed_time = 0
        self.should_draw_timer = False

    def start_timer(self):
        self.start_time = time.time()  
        self.timer_running = True  
        self.should_draw_timer = True

    def stop_timer(self):
        self.timer_running = False  
        if self.start_time: 
            self.elapsed_time = time.time() - self.start_time

    def get_elapsed_time(self):
        if self.timer_running:
            return time.time() - self.start_time
        else:
            return self.elapsed_time  

    def draw_timer(self, window):
        if self.should_draw_timer:
            elapsed_time = self.get_elapsed_time()
            timer_text = self.font.render("Time: {:.2f}".format(elapsed_time), True, BLACK)
            window.blit(timer_text, (self.timer_rect.x, self.timer_rect.y))

    def user_movement(self, grid, window):
        # Handle user-controlled movement using arrow key
        if not self.initial_node_pos_set:
            self.node_pos = grid.start_node_pos
            self.initial_node_pos_set = True

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1

        new_x = self.node_pos[1] + dx
        new_y = self.node_pos[0] + dy

        if 0 <= new_x < grid.columns and 0 <= new_y < grid.rows and grid.grid[new_y][new_x] != -1:
            # move node to the new position
            grid.grid[self.node_pos[0]][self.node_pos[1]] = 0
            self.node_pos = (new_y, new_x)
            grid.grid[new_y][new_x] = 5  # 5 on grid represesnts user controlled node
            pygame.time.delay(100)  # delay so node is easier to control for user
            window.fill(WHITE)
            interface.draw_grid()
            pygame.display.flip()

        # checks if user controlled node is at end node, if so end timer
        if self.node_pos == grid.end_node_pos:
            self.stop_timer()


# setting position of pygame window - https://stackoverflow.com/questions/4135928/pygame-display-position
x = 80
y = 250
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

# initialise objects
grid = Grid(GRID_ROWS, GRID_COLUMNS, GRID_SIZE)
interface = Interface(grid, MAX_GRID_WIDTH, MAX_GRID_HEIGHT)
pathfinding = Pathfinding()
maze_generator = MazeGenerator()
maze_solver = MazeSolver(grid.start_node_pos)


'''
testing pathfinding attributes
assert pathfinding.path is None, "Path attribute is not initialized to None"
print("Pathfinding initialised successfully")
'''


'''
testing mazesolver attributes
assert maze_solver.start_time is None, "Start_time attribute is not initialized to None"
print("Start_time initialised successfully")
assert maze_solver.timer_running is False, "Timer_running attribute is not initialized to False"
print("Timer_running initialised successfully")
assert maze_solver.node_pos is grid.start_node_pos, "Node_pos attribute is not initialized to start_node_pos"
print("Node_pos initialised successfully")
assert maze_solver.initial_node_pos_set is False, "initial_node_pos_set attribute is not initialized to False"
print("initial_node_pos_set initialised successfully")
assert maze_solver.elapsed_time is 0, "elapsed_time attribute is not initialized to 0"
print("elapsed_time initialised successfully")
assert maze_solver.should_draw_timer is False, "should_draw_timer attribute is not initialized to False"
print("should_draw_timer initialised successfully")


#testing grid attributes
assert grid.rows is GRID_ROWS, "rows attribute is not initialized to GRID_ROWS"
print("rows initialised successfully")
assert grid.columns is GRID_COLUMNS, "columns attribute is not initialized to GRID_COLUMNS"
print("columns initialised successfully")
assert grid.grid_size is GRID_SIZE, "grid_size attribute is not initialized to GRID_SIZE"
print("grid_size initialised successfully")
assert grid.start_node_pos is None, "start_node_pos attribute is not initialized to None"
print("start_node_pos initialised successfully")
assert grid.end_node_pos is None, "end_node_pos attribute is not initialized to None"
print("end_node_pos initialised successfully")
assert grid.path is None, "path attribute is not initialized to None"
print("path initialised successfully")
'''

#testing interface attributes
'''
assert interface.grid is grid, "grid attribute is not initialized to grid"
print("grid initialised successfully")
assert interface.max_grid_height is MAX_GRID_HEIGHT, "max_grid_height attribute is not initialized to MAX_GRID_HEIGHT"
print("max_grid_height initialised successfully")
assert interface.max_grid_width is MAX_GRID_WIDTH, "max_grid_width attribute is not initialized to MAX_GRID_WIDTH"
print("max_grid_width initialised successfully")
assert interface.placing_start is False, "placing_start attribute is not initialized to False"
print("placing_start initialised successfully")
assert interface.placing_end is False, "placing_end attribute is not initialized to False"
print("placing_end initialised successfully")
assert interface.placing_wall is False, "placing_wall attribute is not initialized to False"
print("placing_wall initialised successfully")
'''

path = None

def Main():
    while True:
        for event in pygame.event.get():
            #print(grid.grid)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            interface.handle_button_clicks(event)
        interface.handle_mouse_events()
        if maze_solver.timer_running:
                maze_solver.user_movement(grid, interface.window)
        interface.window.fill(WHITE)
        interface.draw_grid()
        interface.draw_buttons(interface.reset_button_rect, 
                       interface.bfs_button_rect, 
                       interface.randomise_button_rect, 
                       interface.info_button_rect, 
                       interface.dijkstra_button_rect,
                       interface.generate_maze_button_rect, 
                       interface.solve_button_rect, 
                       pygame.font.Font(None, 36))
        interface.draw_grid_lines()
        maze_solver.draw_timer(interface.window)
        interface.draw_path(path)
        interface.draw_start_end_nodes()
        interface.draw_grid_lines()

        #print( grid.grid)
        #grid.get_neighbours((1,1))

        '''
        # unit testing
        is_timer_running = maze_solver.timer_running
        if is_timer_running == True:
            print("Timer starts correctly")
        else:
            print("Timer not started yet")
            

            
        if maze_solver.timer_running == True:
            print("timer is currently running, if not timer does not end correctly")
        else:
            print("Timer is not currently running, timer has ended correctly, or solving has not begun")
            

        if maze_solver.timer_running == False and maze_solver.should_draw_timer == False:
            print("Timer is reset")
            '''

        pygame.display.flip()

if __name__ == "__main__":
    Main()