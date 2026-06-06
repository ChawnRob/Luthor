# Subquadratic JEPA Predictor

Luthor can replace the default mean-pooled attention block with a **linear attention** predictor for long context histories.

## Architecture

The module lives in `src/luthor/jepa_model/linear_attention.py`:

| Class | Role |
|-------|------|
| `LinearAttention` | Performer-style kernel attention, O(N d²) in sequence length |
| `SubquadraticPredictor` | Drop-in predictor using linear attention over latent, action, and history tokens |

### Feature map

Positive feature maps approximate softmax attention without materializing an N×N matrix:

- `elu+1` (default): φ(x) = ELU(x) + 1
- `relu`: φ(x) = ReLU(x) + ε

### Token layout

1. Latent state token
2. Action token
3. Optional context token **or** context sequence `(seq_len, dim)`

The latent token attends to all tokens via linear attention, then an MLP head predicts the next latent.

## Configuration

`params.yaml`:

```yaml
predictor:
  predictor_type: linear_attention   # mlp | linear_attention | mamba (future)
  hidden_dim: 64
  num_layers: 2
  dropout: 0.1
  linear_attention_dim_head: 16
  linear_attention_heads: 4
  feature_map: elu+1
```

Environment override:

```bash
export LUTHOR_PREDICTOR_TYPE=linear_attention
```

Default remains `mlp` so existing demos and tests stay unchanged.

## Activation

```bash
# One-off benchmark
python3 scripts/benchmark_subq.py --seq-lengths 10 50 200

# Training with linear attention
LUTHOR_PREDICTOR_TYPE=linear_attention make active
```

## Benchmark script

`scripts/benchmark_subq.py` compares:

- `predictor_type: mlp` (standard `MultiheadAttention` + mean pool)
- `predictor_type: linear_attention`

on synthetic history sequences. It reports per-forward latency and peak memory.

Example output:

```
seq_len | mlp_s | linear_s | speedup | memory_ratio
     10 | 0.000120 | 0.000095 | 1.26x | 1.10x
     50 | 0.000410 | 0.000180 | 2.28x | 1.85x
    200 | 0.002100 | 0.000520 | 4.04x | 3.40x
```

Ratios grow with sequence length because quadratic attention scales as O(N²) while linear attention scales as O(N).

## API compatibility

- `WorldModel.predict(latent, action, context=...)` unchanged
- Same MSE JEPA training loss
- `predict_with_uncertainty()` supported via MC dropout
- Encoder, planner, and active-learning loops require no changes

## When to use

| Scenario | Recommendation |
|----------|----------------|
| Short context (≤ 8 steps) | `mlp` (default) |
| Long memory / history (50–200+ steps) | `linear_attention` |
| Future state-space models | `mamba` (planned) |

## Tests

```bash
python3 -m unittest tests.test_linear_attention tests.test_subquadratic_predictor -v
```

- Shape and gradient checks for `LinearAttention`
- Scaling comparison vs standard attention
- World-model integration and loss decrease

## Implementation notes

- No extra dependencies beyond PyTorch
- `build_predictor()` in `predictor.py` selects the implementation
- `WorldModel` calls `build_predictor()` automatically from `PredictorConfig.predictor_type`
- Mamba support can be added later behind the same `predictor_type` switch
