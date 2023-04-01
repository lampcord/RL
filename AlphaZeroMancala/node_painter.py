import time

import pygame
import sys

pygame.init()

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []
        self.pos = None
        self.selected = False
        self.action = None

    def add_child(self, child, action):
        child.action = action
        self.children.append(child)

    def render_node(self, screen, font):
        if self.selected:
            node_color = (0, 255, 0)
            text_color = (0, 0, 0)
        else:
            node_color = (0, 128, 0)
            text_color = (255, 255, 255)
        pygame.draw.circle(screen, node_color, self.pos, 20)
        text = font.render(self.value, True, text_color)
        text_rect = text.get_rect(center=self.pos)
        screen.blit(text, text_rect)

    def get_path_label(self):
        return str(self.action)
def draw_node(screen, node, font):
    node.render_node(screen, font)

def draw_label(screen, font, label, start_pos, end_pos):
    mid_x = (start_pos[0] + end_pos[0]) // 2
    mid_y = (start_pos[1] + end_pos[1]) // 2
    text = font.render(label, True, (0, 0, 255))
    text_rect = text.get_rect(center=(mid_x, mid_y))
    screen.blit(text, text_rect)

def draw_tree(screen, node, font):
    for i, child in enumerate(node.children):
        pygame.draw.line(screen, (192, 192, 192), node.pos, child.pos, 2)
        draw_label(screen, font, child.get_path_label(), node.pos, child.pos)
        draw_node(screen, child, font)
        draw_tree(screen, child, font)

def calculate_positions(node, x, y, level_width, stagger):
    node.pos = (x, y)
    child_y = y + 300
    num_children = len(node.children)
    child_x_space = level_width // (num_children + 1)
    for i, child in enumerate(node.children):
        child_x = x - level_width // 2 + (i + 1) * child_x_space
        calculate_positions(child, child_x, child_y + 50 * stagger, child_x_space, stagger)
        stagger = (stagger + 1) % 3

def find_closest_node(node, pos, max_distance, best_node=None, best_dist=None):
    distance = (node.pos[0] - pos[0]) * (node.pos[0] - pos[0]) + (node.pos[1] - pos[1]) * (node.pos[1] - pos[1])
    if distance < max_distance * max_distance:
        if not best_node or distance < best_dist:
            best_node = node
            best_dist = distance
    for child in node.children:
        best_node, best_dist = find_closest_node(child, pos, max_distance, best_node, best_dist)
    return best_node, best_dist
def main():
    screen = pygame.display.set_mode((1900, 1000))
    pygame.display.set_caption("Tree Diagram")
    font = pygame.font.Font(None, 24)

    root = TreeNode("Root")


    for x in range(9):
        child = TreeNode(f"C {x}")
        root.add_child(child, x + 1)

        for y in range(8):
            grandchild = TreeNode(f"G {y}")
            child.add_child(grandchild, y + 1)

    calculate_positions(root, 950, 50, 2000, 0)

    running = True
    click_coordinates = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_coordinates = event.pos
                print(f"Mouse clicked at {click_coordinates}")

        screen.fill((255, 255, 255))
        draw_node(screen, root, font)
        draw_tree(screen, root, font)

        if click_coordinates:
            best_node, best_dist = find_closest_node(root, click_coordinates, 50)
            label = str(best_node.value) if best_node is not None else "None"
            if best_node:
                best_node.selected = not best_node.selected
            text = font.render(f"Mouse clicked at {click_coordinates} {label}", True, (0, 0, 0))
            screen.blit(text, (10, 10))
            click_coordinates = None

        pygame.display.flip()
        time.sleep(.1)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
