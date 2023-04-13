import time

import pygame
import sys
# import TicTacToeEnv
pygame.init()


class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []
        self.pos = None
        self.selected = False
        self.action = None
        # self.env = TicTacToeEnv.TicTacToeEnv()

    def add_child(self, child, action):
        child.action = action
        self.children.append(child)

    def render_node(self, screen, font):
        # self.env.render_node(screen, self.pos)
        if self.selected:
            node_color = (0, 255, 0)
            text_color = (0, 0, 0)
        else:
            node_color = (0, 128, 0)
            text_color = (255, 255, 255)
        pygame.draw.circle(screen, node_color, self.pos, 20)
        text = font.render(self.get_value_label(), True, text_color)
        text_rect = text.get_rect(center=self.pos)
        screen.blit(text, text_rect)

    def get_value_label(self):
        return str(self.value)

    def get_path_label(self):
        return str(self.action)

class NodePainter:
    def __init__(self, node):
        self.root = node
        self.node = node
        self.screen = pygame.display.set_mode((1900, 1000))
        pygame.display.set_caption("Tree Diagram")
        self.font = pygame.font.Font(None, 24)

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None

    def paint(self, label='', selected_node=None):
        running = True
        click_coordinates = None
        while running:
            text = self.font.render(label, True, (0, 0, 0))
            calculate_positions(self.node, 950, 50, 2000, 0)
            self.screen.fill((255, 255, 255))
            self.screen.blit(text, (10, 10))
            draw_node(self.screen, self.node, selected_node, self.font)
            draw_tree(self.screen, self.node, selected_node, self.font, 3)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click_coordinates = event.pos
                    print(f"Mouse clicked at {click_coordinates}")

            if click_coordinates:
                best_node, best_dist = find_closest_node(self.node, click_coordinates, 50)
                if best_node:
                    if best_node == self.node:
                        if self.node.parent is not None:
                            self.node = self.node.parent
                    else:
                        self.node = best_node
                else:
                    running = False
                click_coordinates = None

            time.sleep(.1)



def draw_dashed_line(surface, color, start_pos, end_pos, dash_length, space_length, skip_start=3, skip_end=2):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    distance = (dx ** 2 + dy ** 2) ** 0.5
    dashes = int(distance / (dash_length + space_length)) - skip_end

    for i in range(dashes):
        start = i * (dash_length + space_length)
        end = start + dash_length
        t_start = start / distance
        t_end = end / distance

        x_start = x1 + dx * t_start
        y_start = y1 + dy * t_start
        x_end = x1 + dx * t_end
        y_end = y1 + dy * t_end

        if i < skip_start:
            continue

        pygame.draw.line(surface, color, (x_start, y_start), (x_end, y_end), 2)


def draw_node(screen, node, selected_node, font):
    node.render_node(screen, font)


def draw_label(screen, font, label, start_pos, end_pos):
    mid_x = (start_pos[0] + end_pos[0]) // 2
    mid_y = (start_pos[1] + end_pos[1]) // 2
    text = font.render(label, True, (0, 0, 255))
    text_rect = text.get_rect(center=(mid_x, mid_y))
    screen.blit(text, text_rect)


def draw_tree(screen, node, selected_node, font, max_depth=2):
    if max_depth <= 0:
        return
    for i, child in enumerate(node.children):
        draw_dashed_line(screen, (192, 192, 192), node.pos, child.pos, 5, 5)
        draw_label(screen, font, child.get_path_label(), node.pos, child.pos)
        draw_node(screen, child, selected_node, font)
        draw_tree(screen, child, selected_node, font, max_depth - 1)


def calculate_positions(node, x, y, level_width, stagger):
    node.pos = (x, y)
    child_y = y + 200
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
            label = str(best_node.get_value_label()) if best_node is not None else "None"
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
