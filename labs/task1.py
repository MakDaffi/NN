import argparse
from lxml import etree as ET


class Node:
    def __init__(self, node, parents=[], children=[]) -> None:
        self.node = node
        self.from_nodes = parents.copy()
        self.to_nodes = children.copy()


class Graph:
    def __init__(self, nodes, edges) -> None:
        edges.sort(key=lambda a: a[2])
        self.nodes = nodes
        self.edges = edges
        parents = {i: [] for i in self.nodes}
        children = {i: [] for i in self.nodes}
        for edge in edges:
            children[edge[0]].append(edge[1])
            parents[edge[1]].append(edge[0])
        self.graph = {node: Node(node, parents[node], children[node]) for node in nodes}


def write_xml(graph, filepath):
    tree = ET.Element("graph")
    for v in graph.nodes:
        ET.SubElement(tree, "vertex").text = v
    for edge in graph.edges:
        arc = ET.SubElement(tree, "arc")
        ET.SubElement(arc, "from").text = edge[0]
        ET.SubElement(arc, "to").text = edge[1]
        ET.SubElement(arc, "order").text = edge[2]
    tree = ET.ElementTree(tree)
    tree.write(filepath, pretty_print=True, encoding="utf-8")


def parse_txt(filepath):
    with open(filepath, "r") as f:
        contents = f.read()
    edges = contents[1:-1].split(sep="), (")
    nodes = []
    for i in range(len(edges)):
        edge = edges[i].split(sep=", ")
        try:
            int(edge[2])
        except:
            raise f"Порядок ребра {edge[0]}:{edge[1]} не является числом!"
        edges[i] = edge
        nodes.append(edge[0])
        nodes.append(edge[1])
    nodes = list(set(nodes))
    return nodes, edges


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help="path/to/input/text/file")
    parser.add_argument("--output_file", help="path/to/output/xml/file")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    if args.input_file is None:
        raise "Не введен входной файл!"
    if args.output_file is None:
        raise "Не введен выходной файл!"
    try:
        nodes, edges = parse_txt(args.input_file)
    except:
        raise "Ошибка чтения файла!"
    try:
        graph = Graph(nodes, edges)
    except:
        raise "Ошибка при создании графа!"
    try:
        write_xml(graph, args.output_file)
    except:
        raise "Ошибка записи в файл!"
