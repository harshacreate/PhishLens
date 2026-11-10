"""Print held-out metrics for the synthetic URL feature generator."""

import json

from phishlens.model import PhishModel


def main():
    model = PhishModel.train(seed=0)
    result = model.evaluate(seed=1)
    print(json.dumps({"dataset": "synthetic generated URL features",
                      "train_seed": 0, "evaluation_seed": 51, **result}, indent=2))


if __name__ == "__main__":
    main()
