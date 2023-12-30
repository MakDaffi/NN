import numpy as np
import argparse
import copy
import json


def np_converter(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    

class ActivationFunctions:
    def __init__(self):
        pass

    @classmethod
    def linear(self, X, w):
        return np.sum(X * w, axis=1)

    @classmethod
    def sigmoid(self, X, w):
        return 1 / (1 + np.exp(-np.sum(X * w, axis=1)))

    @classmethod
    def softmax(self, X, **kwargs):
        return np.exp(X) / np.sum(np.exp(X))

    @classmethod
    def argmax(self, X, **kwargs):
        return np.argmax(X)
    


class Layer:
    def __init__(self, weights, activation_func, name="layer"):
        self.weights = weights
        self.activation_func_name = activation_func
        self.activation_func = getattr(ActivationFunctions, activation_func)
        self.name = name

    def calc(self, X):
        return self.activation_func(X, w=self.weights)

    def get_layer_name(self):
        return self.name + "." + self.activation_func_name


class NeuralNetwork:
    def __init__(self, weights, layer_names):
        self.layers = [
            Layer(
                weights[i],
                layer_names[i].split(sep=".")[1],
                layer_names[i].split(sep=".")[0],
            )
            for i in range(len(weights))
        ]

    def forward(self, X, verbose=False):
        Y = copy.deepcopy(X)
        for layer in self.layers:
            Y = layer.calc(Y)
            if verbose:
                print(f"Результаты вычисления слоя {layer.get_layer_name()}\n{Y}")
        return Y


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights_file", help="path/to/json/file/with/weights")
    parser.add_argument("--input_file", help="path/to/input/text/file")
    parser.add_argument("--output_file", help="path/to/output/txt/file")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    if args.input_file is None:
        raise "Не введен входной файл!"
    if args.weights_file is None:
        raise "Не введен файл с весами!"
    if args.output_file is None:
        raise "Не введен выходной файл!"
    try:
        with open(args.input_file, "r") as f:
            content = f.read()
        X = np.array(list(map(float, content.split(sep=", "))))
    except:
        raise "Ошибка во время парсинг входного файла!"
    try:
        with open(args.weights_file) as f:
            content = json.load(f)
        layer_names = []
        layer_weights = []
        for i in content:
            layer_names.append(i)
            layer_weights.append(content[i])
    except:
        raise "Ошибка во время парсинг файла с весами!"
    nn = NeuralNetwork(layer_weights, layer_names)
    Y = nn.forward(X)
    try:
        with open(args.output_file, "w") as f:
            json.dump({"Y":Y}, f, default=np_converter)
    except:
        raise "Ошибка во время записи выходного файла!"
