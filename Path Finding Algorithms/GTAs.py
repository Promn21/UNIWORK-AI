import pygame
from collections import  deque
import heapq

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Graph Traversal Visualization")
font = pygame.font.SysFont("Arial", 20)

##### Graph Tree #####
# Node Position
nodes = {
    'A': (100, 200),
    'B': (200, 300),
    'C': (300, 200),
    'D': (400, 300),
    'E': (500, 250),
    'F': (450, 200),
    'G': (700, 300),
    'H': (650, 150)
}

# Edges and Weights 
edges = {
    'A': [('B', 1), ('C', 4)],
    'B': [('D', 1), ('E', 5)],
    'C': [('F', 1)],
    'D': [('G', 1)],
    'E': [('H', 3)],
    'F': [('H', 2)],
    'G': [('H', 4)]
}

def draw_node(name, color):
    x, y = nodes[name]
    pygame.draw.circle(screen, color, (x, y), 20)
    text = font.render(name, True, (0, 0, 0))
    screen.blit(text, (x - 10, y - 10))

def draw_edge(start, end, color, weight):
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]
    pygame.draw.line(screen, color, (x1, y1), (x2, y2), 2)
    
    # midpoint of the edge to display the weight
    mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
    weight_text = font.render(str(weight), True, (255, 255, 255)) 
    screen.blit(weight_text, (mid_x - 10, mid_y - 10))

visited_dfs = set()

def dfs(node):
    global visited_dfs  
    visited_dfs = set()  # reset visited
    
    def dfs_visit(node):
        if node in visited_dfs:
            return
        visited_dfs.add(node)
        
        draw_node(node, 'Orange')
        pygame.display.update()
        pygame.time.delay(500)
        
        for neighbor, weight in edges.get(node, []):
            draw_edge(node, neighbor, 'Orange', weight)
            dfs_visit(neighbor)
            draw_edge(node, neighbor, 'Gray', weight)  
        
        draw_node(node, 'Gray')
        pygame.display.update()
        pygame.time.delay(500)
    
    dfs_visit(node)

def bfs(start):
    queue = deque([start])
    visited_bfs = set([start])
    
    # queue feed (kill feed)
    queue_feed = []  
    max_feed_length = 5  

    while queue:
        node = queue.popleft()
        
        draw_node(node, 'Orange')
        pygame.display.update()
        pygame.time.delay(500)
        
        queue_feed.append((f"Processing: {node}", (255, 165, 0)))  
        
        for neighbor, weight in edges.get(node, []):
            if neighbor not in visited_bfs:
                visited_bfs.add(neighbor)
                queue.append(neighbor)
                draw_edge(node, neighbor, 'Orange', weight)
                
                # add to queue feed 
                queue_feed.append((f"Enqueued: {neighbor}", (135, 206, 250)))  
                if len(queue_feed) > max_feed_length:
                    queue_feed.pop(0) 
        
        draw_node(node, 'Gray')
        pygame.display.update()
        pygame.time.delay(500)
        
        queue_feed.append((f"Visited: {node}", (128, 128, 128)))  
        if len(queue_feed) > max_feed_length:
            queue_feed.pop(0)
        
        # queue feed on the screen with color coding
        y_offset = height - 0 - max_feed_length * 50
        screen.fill((50, 55, 50), (10, y_offset, 300, max_feed_length * 50)) 
        for i, (entry_text, color) in enumerate(queue_feed):
            feed_text = font.render(entry_text, True, color)
            screen.blit(feed_text, (10, y_offset + i * 20))
        
        pygame.display.update()


def dijkstra(start, end):
    dist = {node: float('inf') for node in nodes}
    dist[start] = 0
    pq = [(0, start)]
    visited_dijkstra = set()
    
    while pq:
        current_dist, node = heapq.heappop(pq)
        if node in visited_dijkstra:
            continue
        visited_dijkstra.add(node)
        
        draw_node(node, 'Orange')
        pygame.display.update()
        pygame.time.delay(500)
        
        for neighbor, weight in edges.get(node, []):
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
                draw_edge(node, neighbor, 'Orange', weight) 
        
        draw_node(node, 'Gray')
        pygame.display.update()
        pygame.time.delay(500)
        
        pygame.draw.rect(screen, (50, 55, 50), (10, height - 30, width, 30))
        
        # dist array
        dist_text = "Dist: " + ", ".join(f"{n}:{dist[n]}" for n in dist)
        dist_surface = font.render(dist_text, True, (255, 255, 255))  
        screen.blit(dist_surface, (10, height - 30))
        pygame.display.update()

def main():
    running = True
    while running:
        screen.fill((50, 55, 50))  
        # draw all nodes and edges initially in default colors
        for start, neighbors in edges.items():
            for neighbor, weight in neighbors:
                draw_edge(start, neighbor, (255, 255, 255), weight)  # draw edges with weights
        for node in nodes:
            draw_node(node, 'Skyblue')
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # 1 DFS
                    dfs('A')
                elif event.key == pygame.K_2:  # 2 BFS
                    bfs('A')
                elif event.key == pygame.K_3:  # 3 Dijkstra's
                    dijkstra('A', 'H')
        
        pygame.display.flip()
    pygame.quit()

main()
