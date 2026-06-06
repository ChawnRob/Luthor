import os

import matplotlib

matplotlib.use("Agg")

from luthor.active_learning.loop import ActiveLearningLoop
from luthor.config import get_config


def main():
    config = get_config()
    os.makedirs(config.visualization.output_dir, exist_ok=True)

    print("--- Luthor Active Learning (JEPA SLM skeleton) ---")
    print(
        "Uncertainty sampling via predictor variance + dummy oracle "
        f"({config.active_learning.num_rounds} rounds)"
    )

    loop = ActiveLearningLoop(config)
    results = loop.run()

    final_loss = results[-1].mean_loss if results else 0.0
    print(f"\nActive learning complete. Final mean loss: {final_loss:.6f}")


if __name__ == "__main__":
    main()
