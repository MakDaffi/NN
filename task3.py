import argparse
import json
import numpy as np
from lxml import etree as ET


class Node:
    def __init__(self, node, parents=[], children=[]) -> None:
        self.node = node
        self.from_nodes = parents.copy()
        self.to_nodes = children.copy()


class Graph:
    def __init__(self, nodes, edges, nodes_to_func) -> None:
        edges.sort(key=lambda a: a[2])
        self.nodes = nodes
        self.edges = edges
        self.nodes_to_func = nodes_to_func
        parents = {i: [] for i in self.nodes}
        children = {i: [] for i in self.nodes}
        for edge in edges:
            children[edge[0]].append(edge[1])
            parents[edge[1]].append(edge[0])
        self.graph = {node: Node(node, parents[node], children[node]) for node in nodes}

    def has_cycle(self):
        path = set()

        def visit(node):
            path.add(node)
            for neighbour in self.graph[node].to_nodes:
                if neighbour in path or visit(neighbour):
                    return True
            path.remove(node)
            return False

        for node in self.nodes:
            if visit(node):
                return True
        return False

    def _cur_node_linear_interpretation(self, cur_node):
        if self.has_cycle():
            raise "В графе присутствует цикл!"
        ans = []
        for node in self.graph[cur_node].to_nodes:
            cur_expression = []
            if not self.graph[node].to_nodes:
                cur_expression.append(self.nodes_to_func[node])
                ans.append(cur_expression)
            else:
                cur_expression.append(self.nodes_to_func[node])
                tmp = self._cur_node_linear_interpretation(node)
                if tmp:
                    if len(tmp) > 1:
                        cur_expression.append(tmp)
                    else:
                        cur_expression.append(tmp[0])
                ans.append(cur_expression)
        return ans

    def get_linear_interpretation(self):
        ans = []
        for node in self.nodes:
            cur_expression = []
            if not self.graph[node].from_nodes:
                cur_expression.append(self.nodes_to_func[node])
                tmp = self._cur_node_linear_interpretation(node)
                if tmp:
                    cur_expression.append(tmp)
                ans.append(cur_expression)
        return ans


def _calc(expression):
    if expression[0] == "+":
        return _calc(expression[1][0]) + _calc(expression[1][1])
    elif expression[0] == "*":
        return _calc(expression[1][0]) * _calc(expression[1][1])
    elif expression[0] == "exp":
        return np.exp(_calc(expression[1]))
    else:
        return int(expression[0])


def calculate(expression):
    ans = []
    for e in expression:
        ans.append(_calc(e))
    return ans


def parse_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    nodes = []
    for vertex in root.findall("vertex"):
        nodes.append(vertex.text)
    edges = []
    for arc in root.findall("arc"):
        v1 = arc.find("from").text
        v2 = arc.find("to").text
        order = int(arc.find("order").text)
        edges.append((v1, v2, order))
    return nodes, edges


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help="path/to/input/xml/file")
    parser.add_argument("--nodes_to_func_file", help="path/to/nodes_to_func/json/file")
    parser.add_argument("--output_file", help="path/to/output/txt/file")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    if args.input_file is None:
        raise "Не введен входной файл!"
    if args.nodes_to_func_file is None:
        raise "Не введен файл с отображением вершин в функции!"
    if args.output_file is None:
        raise "Не введен выходной файл!"
    try:
        nodes, edges = parse_xml(args.input_file)
        with open(args.nodes_to_func_file) as f:
            nodes_to_func = json.load(f)
    except:
        raise "Ошибка чтения файла!"
    try:
        graph = Graph(nodes, edges, nodes_to_func)
    except:
        raise "Ошибка при создании графа!"
    ans = graph.get_linear_interpretation()
    with open(args.output_file, "w") as f:
        json.dump(calculate(ans), f)
