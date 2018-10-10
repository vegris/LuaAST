import argparse
from pathlib import Path

import pygraphviz as pgv

from grammar import parser, Node


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("code", type=Path, help="Lua code to parse.")
    argparser.add_argument("out_file", type=Path, help="Output .png file.")
    args = argparser.parse_args()

    with open(args.code) as file:
        result = parser.parse(file.read())

    ast_graph = pgv.AGraph()

    # Замыкаем так сказатб
    def draw_node(parent_node, cur_node):
        if isinstance(cur_node, Node):
            ast_graph.add_node(id(parent_node), label=parent_node.leaf)
            ast_graph.add_node(id(cur_node), label=cur_node.leaf)
            ast_graph.add_edge(id(parent_node), id(cur_node))
            for child in cur_node.children:
                draw_node(cur_node, child)
        elif isinstance(cur_node, list):
            for node in cur_node:
                draw_node(parent_node, node)
        else:
            ast_graph.add_node(id(parent_node), label=parent_node.leaf)
            ast_graph.add_node(id(cur_node), label=cur_node)
            ast_graph.add_edge(id(parent_node), id(cur_node))

    for block in result:
        draw_node(Node(leaf="Statements",), block)

    ast_graph.draw(str(args.out_file), prog="dot")


if __name__ == '__main__':
    main()
