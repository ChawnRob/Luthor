"""
Luthor Configuration Module

Centralized configuration management for Luthor WM.
Loads configuration from environment variables and provides sensible defaults.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class EncoderConfig:
    """Encoder configuration."""
    latent_dim: int = 128
    hidden_dim: int = 256
    num_layers: int = 2
    dropout: float = 0.1


@dataclass
class PredictorConfig:
    """Predictor configuration."""
    hidden_dim: int = 256
    num_layers: int = 3
    dropout: float = 0.1
    use_attention: bool = True
    predictor_type: str = "mlp"
    linear_attention_dim_head: int = 32
    linear_attention_heads: int = 4
    feature_map: str = "elu+1"


@dataclass
class PlannerConfig:
    """Planner configuration."""
    horizon: int = 10
    num_samples: int = 100
    learning_rate: float = 0.001
    num_iterations: int = 100


@dataclass
class VisualizationConfig:
    """Visualization configuration."""
    enabled: bool = True
    output_dir: str = "./outputs"
    save_plots: bool = True
    show_plots: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    log_file: Optional[str] = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class InventoryConfig:
    """Inventory management environment configuration."""
    num_products: int = 3
    holding_cost: float = 0.5
    stockout_cost: float = 10.0
    lead_time: int = 2
    demand_mean: list[float] = field(default_factory=lambda: [10.0, 20.0, 15.0])
    demand_std: list[float] = field(default_factory=lambda: [2.0, 5.0, 3.0])
    max_steps: int = 50
    max_order: float = 40.0
    demand_distribution: str = "normal"
    service_level_target: float = 0.9
    initial_stock: list[float] | None = None


@dataclass
class GridWorldConfig:
    """GridWorld environment configuration."""
    state_dim: int = 2
    action_dim: int = 2
    grid_size: int = 10
    noise_std: float = 0.1
    goal: list[float] = field(default_factory=lambda: [8.0, 8.0])
    goal_tolerance: float = 0.5
    max_steps: int = 50
    obstacles: list[list[int]] = field(default_factory=list)


@dataclass
class EnvironmentConfig:
    """Top-level environment selector."""
    type: str = "gridworld"
    inventory: InventoryConfig = field(default_factory=InventoryConfig)


@dataclass
class GeneralizationConfig:
    """Train/test scenario split for generalization benchmarks."""
    train_scenarios: list[int] = field(default_factory=lambda: [0, 1, 2, 3])
    test_scenarios: list[int] = field(default_factory=lambda: [4, 5])
    max_steps: int = 30
    train_steps_per_scenario: int = 20


@dataclass
class ActiveLearningConfig:
    """Active learning loop configuration (JEPA SLM skeleton)."""
    num_rounds: int = 10
    pool_size: int = 32
    query_batch_size: int = 8
    mc_samples: int = 10
    train_steps_per_round: int = 5
    input_dim: int = 2
    action_dim: int = 2
    human_in_loop: bool = False
    use_mock_human: bool = True


@dataclass
class ABTestingConfig:
    """A/B testing configuration for model variants."""
    enabled: bool = False
    models: dict[str, str] = field(
        default_factory=lambda: {
            "default": "models/jepa_model.pth",
            "candidate": "models/jepa_model_v2.pth",
        }
    )


@dataclass
class MCPConnectorConfig:
    """Single MCP connector configuration."""
    enabled: bool = False
    url: str = ""
    api_key: str = ""
    token: str = ""
    site_id: str = ""
    model: str = "tiny"
    device: str = "cpu"
    allowed_domains: list[str] = field(
        default_factory=lambda: ["youtube.com", "youtu.be", "vimeo.com"]
    )
    download_dir: str = "./data/downloads"
    max_downloads_per_user: int = 10
    event_type_id: str = ""


@dataclass
class QuotaTierLimits:
    """Per-tier usage limits (freemium)."""
    max_api_calls_per_day: int = 50
    max_complex_tasks_per_month: int = 5
    max_storage_mb: int = 10


@dataclass
class QuotasConfig:
    """Quota limits by subscription tier."""
    free: QuotaTierLimits = field(default_factory=QuotaTierLimits)
    pro: QuotaTierLimits = field(
        default_factory=lambda: QuotaTierLimits(
            max_api_calls_per_day=10000,
            max_complex_tasks_per_month=1000,
            max_storage_mb=1024,
        )
    )

    def limits_for(self, tier: str) -> QuotaTierLimits:
        if tier == "pro":
            return self.pro
        return self.free


@dataclass
class MCPConfig:
    """MCP tool integration configuration."""
    enabled: bool = True
    tools: dict[str, MCPConnectorConfig] = field(
        default_factory=lambda: {
            "n8n": MCPConnectorConfig(),
            "penpot": MCPConnectorConfig(),
            "appflowy": MCPConnectorConfig(),
            "plausible": MCPConnectorConfig(),
            "whisper": MCPConnectorConfig(enabled=False, model="tiny", device="cpu"),
            "ytdlp": MCPConnectorConfig(
                enabled=False,
                download_dir="./data/downloads",
                max_downloads_per_user=10,
            ),
            "fooocus": MCPConnectorConfig(),
            "calcom": MCPConnectorConfig(),
        }
    )


@dataclass
class MemoryConfig:
    """Context compression (GRU memory) configuration."""
    use_context_compression: bool = False
    history_length: int = 8
    gru_hidden_dim: int = 64
    gru_num_layers: int = 1
    compress_source: str = "observation"


@dataclass
class LuthorConfig:
    """Main Luthor configuration."""
    encoder: EncoderConfig
    predictor: PredictorConfig
    planner: PlannerConfig
    visualization: VisualizationConfig
    logging: LoggingConfig
    active_learning: ActiveLearningConfig
    memory: MemoryConfig
    ab_testing: ABTestingConfig
    environment: EnvironmentConfig
    gridworld: GridWorldConfig
    generalization: GeneralizationConfig
    mcp: MCPConfig = field(default_factory=MCPConfig)
    quotas: QuotasConfig = field(default_factory=QuotasConfig)
    prompt_version: str = "v1"
    seed: int = 42
    debug: bool = False

    @staticmethod
    def from_params(params: dict) -> "LuthorConfig":
        visualization = params.get("visualization", {})
        logging_cfg = params.get("logging", {})

        memory_cfg = params.get("memory", {})
        ab_cfg = params.get("ab_testing", {})
        ab_models = ab_cfg.get("models", {})
        env_cfg = params.get("environment", {})
        inventory_cfg = env_cfg.get("inventory", {})
        grid_cfg = params.get("gridworld", {})
        gen_cfg = params.get("generalization", {})
        quotas_cfg = params.get("quotas", {})
        quotas = QuotasConfig(
            free=QuotaTierLimits(**quotas_cfg.get("free", {})) if quotas_cfg.get("free") else QuotaTierLimits(),
            pro=QuotaTierLimits(**quotas_cfg.get("pro", {})) if quotas_cfg.get("pro") else QuotasConfig().pro,
        )

        mcp_cfg = params.get("mcp", {})
        mcp_tools = mcp_cfg.get("tools", {})

        def _connector(name: str) -> MCPConnectorConfig:
            raw = mcp_tools.get(name, {})
            return MCPConnectorConfig(
                enabled=bool(raw.get("enabled", False)),
                url=str(raw.get("url", "")),
                api_key=str(raw.get("api_key", "")),
                token=str(raw.get("token", "")),
                site_id=str(raw.get("site_id", "")),
                model=str(raw.get("model", "tiny")),
                device=str(raw.get("device", "cpu")),
                allowed_domains=list(
                    raw.get("allowed_domains", ["youtube.com", "youtu.be", "vimeo.com"])
                ),
                download_dir=str(raw.get("download_dir", "./data/downloads")),
                max_downloads_per_user=int(raw.get("max_downloads_per_user", 10)),
                event_type_id=str(raw.get("event_type_id", "")),
            )

        environment = EnvironmentConfig(
            type=str(env_cfg.get("type", "gridworld")),
            inventory=InventoryConfig(**inventory_cfg) if inventory_cfg else InventoryConfig(),
        )
        gridworld = GridWorldConfig(**grid_cfg) if grid_cfg else GridWorldConfig()
        generalization = GeneralizationConfig(**gen_cfg) if gen_cfg else GeneralizationConfig()

        active_learning = ActiveLearningConfig(**params["active_learning"])
        if environment.type == "inventory":
            inv = environment.inventory
            active_learning.input_dim = inv.num_products * 3
            active_learning.action_dim = inv.num_products

        return LuthorConfig(
            encoder=EncoderConfig(**params["encoder"]),
            predictor=PredictorConfig(**params["predictor"]),
            planner=PlannerConfig(**params["planner"]),
            visualization=VisualizationConfig(**visualization),
            logging=LoggingConfig(**logging_cfg),
            active_learning=active_learning,
            memory=MemoryConfig(**memory_cfg),
            ab_testing=ABTestingConfig(
                enabled=bool(ab_cfg.get("enabled", False)),
                models={
                    "default": ab_models.get("default", "models/jepa_model.pth"),
                    "candidate": ab_models.get("candidate", "models/jepa_model_v2.pth"),
                },
            ),
            environment=environment,
            gridworld=gridworld,
            generalization=generalization,
            quotas=quotas,
            mcp=MCPConfig(
                enabled=bool(mcp_cfg.get("enabled", True)),
                tools={
                    "n8n": _connector("n8n"),
                    "penpot": _connector("penpot"),
                    "appflowy": _connector("appflowy"),
                    "plausible": _connector("plausible"),
                    "whisper": _connector("whisper"),
                    "ytdlp": _connector("ytdlp"),
                    "fooocus": _connector("fooocus"),
                    "calcom": _connector("calcom"),
                },
            ),
            prompt_version=str(params.get("prompt_version", "v1")),
            seed=int(params.get("seed", 42)),
            debug=params.get("debug", False),
        )

    @staticmethod
    def from_env() -> "LuthorConfig":
        """Load configuration from environment variables."""
        return LuthorConfig(
            encoder=EncoderConfig(
                latent_dim=int(os.getenv("LUTHOR_ENCODER_LATENT_DIM", "128")),
                hidden_dim=int(os.getenv("LUTHOR_ENCODER_HIDDEN_DIM", "256")),
                num_layers=int(os.getenv("LUTHOR_ENCODER_NUM_LAYERS", "2")),
                dropout=float(os.getenv("LUTHOR_ENCODER_DROPOUT", "0.1")),
            ),
            predictor=PredictorConfig(
                hidden_dim=int(os.getenv("LUTHOR_PREDICTOR_HIDDEN_DIM", "256")),
                num_layers=int(os.getenv("LUTHOR_PREDICTOR_LAYERS", "3")),
                dropout=float(os.getenv("LUTHOR_PREDICTOR_DROPOUT", "0.1")),
                use_attention=os.getenv("LUTHOR_PREDICTOR_USE_ATTENTION", "true").lower() == "true",
                predictor_type=os.getenv("LUTHOR_PREDICTOR_TYPE", "mlp"),
                linear_attention_dim_head=int(os.getenv("LUTHOR_LINEAR_ATTENTION_DIM_HEAD", "32")),
                linear_attention_heads=int(os.getenv("LUTHOR_LINEAR_ATTENTION_HEADS", "4")),
                feature_map=os.getenv("LUTHOR_LINEAR_ATTENTION_FEATURE_MAP", "elu+1"),
            ),
            planner=PlannerConfig(
                horizon=int(os.getenv("LUTHOR_PLANNER_HORIZON", "10")),
                num_samples=int(os.getenv("LUTHOR_PLANNER_NUM_SAMPLES", "100")),
                learning_rate=float(os.getenv("LUTHOR_PLANNER_LR", "0.001")),
                num_iterations=int(os.getenv("LUTHOR_PLANNER_ITERATIONS", "100")),
            ),
            visualization=VisualizationConfig(
                enabled=os.getenv("LUTHOR_VISUALIZATION_ENABLED", "true").lower() == "true",
                output_dir=os.getenv("LUTHOR_VISUALIZATION_OUTPUT_DIR", "./outputs"),
                save_plots=os.getenv("LUTHOR_VISUALIZATION_SAVE_PLOTS", "true").lower() == "true",
                show_plots=os.getenv("LUTHOR_VISUALIZATION_SHOW_PLOTS", "false").lower() == "true",
            ),
            logging=LoggingConfig(
                level=os.getenv("LUTHOR_LOG_LEVEL", "INFO"),
                log_file=os.getenv("LUTHOR_LOG_FILE"),
                format=os.getenv(
                    "LUTHOR_LOG_FORMAT",
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                ),
            ),
            active_learning=ActiveLearningConfig(
                num_rounds=int(os.getenv("LUTHOR_AL_ROUNDS", "10")),
                pool_size=int(os.getenv("LUTHOR_AL_POOL_SIZE", "32")),
                query_batch_size=int(os.getenv("LUTHOR_AL_QUERY_BATCH", "8")),
                mc_samples=int(os.getenv("LUTHOR_AL_MC_SAMPLES", "10")),
                train_steps_per_round=int(os.getenv("LUTHOR_AL_TRAIN_STEPS", "5")),
                input_dim=int(os.getenv("LUTHOR_AL_INPUT_DIM", "2")),
                action_dim=int(os.getenv("LUTHOR_AL_ACTION_DIM", "2")),
                human_in_loop=os.getenv("LUTHOR_HUMAN_IN_LOOP", "false").lower() == "true",
                use_mock_human=os.getenv("LUTHOR_USE_MOCK_HUMAN", "true").lower() == "true",
            ),
            environment=EnvironmentConfig(),
            gridworld=GridWorldConfig(),
            generalization=GeneralizationConfig(),
            seed=int(os.getenv("LUTHOR_SEED", "42")),
            ab_testing=ABTestingConfig(
                enabled=os.getenv("LUTHOR_AB_TESTING_ENABLED", "false").lower() == "true",
                models={
                    "default": os.getenv("LUTHOR_AB_MODEL_DEFAULT", "models/jepa_model.pth"),
                    "candidate": os.getenv("LUTHOR_AB_MODEL_CANDIDATE", "models/jepa_model_v2.pth"),
                },
            ),
            prompt_version=os.getenv("LUTHOR_PROMPT_VERSION", "v1"),
            memory=MemoryConfig(
                use_context_compression=os.getenv(
                    "LUTHOR_USE_CONTEXT_COMPRESSION", "false"
                ).lower()
                == "true",
                history_length=int(os.getenv("LUTHOR_HISTORY_LENGTH", "8")),
                gru_hidden_dim=int(os.getenv("LUTHOR_GRU_HIDDEN_DIM", "64")),
                gru_num_layers=int(os.getenv("LUTHOR_GRU_NUM_LAYERS", "1")),
                compress_source=os.getenv("LUTHOR_COMPRESS_SOURCE", "observation"),
            ),
            mcp=_mcp_config_from_env(),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "encoder": {
                "latent_dim": self.encoder.latent_dim,
                "hidden_dim": self.encoder.hidden_dim,
                "num_layers": self.encoder.num_layers,
                "dropout": self.encoder.dropout,
            },
            "predictor": {
                "hidden_dim": self.predictor.hidden_dim,
                "num_layers": self.predictor.num_layers,
                "dropout": self.predictor.dropout,
                "use_attention": self.predictor.use_attention,
                "predictor_type": self.predictor.predictor_type,
                "linear_attention_dim_head": self.predictor.linear_attention_dim_head,
                "linear_attention_heads": self.predictor.linear_attention_heads,
                "feature_map": self.predictor.feature_map,
            },
            "planner": {
                "horizon": self.planner.horizon,
                "num_samples": self.planner.num_samples,
                "learning_rate": self.planner.learning_rate,
                "num_iterations": self.planner.num_iterations,
            },
            "visualization": {
                "enabled": self.visualization.enabled,
                "output_dir": self.visualization.output_dir,
                "save_plots": self.visualization.save_plots,
                "show_plots": self.visualization.show_plots,
            },
            "logging": {
                "level": self.logging.level,
                "log_file": self.logging.log_file,
                "format": self.logging.format,
            },
            "active_learning": {
                "num_rounds": self.active_learning.num_rounds,
                "pool_size": self.active_learning.pool_size,
                "query_batch_size": self.active_learning.query_batch_size,
                "mc_samples": self.active_learning.mc_samples,
                "train_steps_per_round": self.active_learning.train_steps_per_round,
                "input_dim": self.active_learning.input_dim,
                "action_dim": self.active_learning.action_dim,
                "human_in_loop": self.active_learning.human_in_loop,
                "use_mock_human": self.active_learning.use_mock_human,
            },
            "environment": {
                "type": self.environment.type,
                "inventory": self.environment.inventory.__dict__,
            },
            "gridworld": self.gridworld.__dict__,
            "generalization": self.generalization.__dict__,
            "seed": self.seed,
            "ab_testing": {
                "enabled": self.ab_testing.enabled,
                "models": self.ab_testing.models,
            },
            "prompt_version": self.prompt_version,
            "memory": {
                "use_context_compression": self.memory.use_context_compression,
                "history_length": self.memory.history_length,
                "gru_hidden_dim": self.memory.gru_hidden_dim,
                "gru_num_layers": self.memory.gru_num_layers,
                "compress_source": self.memory.compress_source,
            },
            "mcp": {
                "enabled": self.mcp.enabled,
                "tools": {
                    name: {
                        "enabled": connector.enabled,
                        "url": connector.url,
                        "api_key": connector.api_key,
                        "token": connector.token,
                        "site_id": connector.site_id,
                    }
                    for name, connector in self.mcp.tools.items()
                },
            },
            "debug": self.debug,
        }


def _parse_connector_from_params(raw: dict[str, Any]) -> MCPConnectorConfig:
    return MCPConnectorConfig(
        enabled=bool(raw.get("enabled", False)),
        url=str(raw.get("url", "")),
        api_key=str(raw.get("api_key", "")),
        token=str(raw.get("token", "")),
        site_id=str(raw.get("site_id", "")),
        model=str(raw.get("model", "tiny")),
        device=str(raw.get("device", "cpu")),
        allowed_domains=list(
            raw.get("allowed_domains", ["youtube.com", "youtu.be", "vimeo.com"])
        ),
        download_dir=str(raw.get("download_dir", "./data/downloads")),
        max_downloads_per_user=int(raw.get("max_downloads_per_user", 10)),
        event_type_id=str(raw.get("event_type_id", "")),
    )


def _apply_mcp_env_overrides(config: LuthorConfig) -> None:
    env_flags = {
        "n8n": "LUTHOR_MCP_N8N_ENABLED",
        "penpot": "LUTHOR_MCP_PENPOT_ENABLED",
        "appflowy": "LUTHOR_MCP_APPFLOWY_ENABLED",
        "plausible": "LUTHOR_MCP_PLAUSIBLE_ENABLED",
        "whisper": "LUTHOR_MCP_WHISPER_ENABLED",
        "ytdlp": "LUTHOR_MCP_YTDLP_ENABLED",
        "fooocus": "LUTHOR_MCP_FOOOCUS_ENABLED",
        "calcom": "LUTHOR_MCP_CALCOM_ENABLED",
    }
    for name, env_key in env_flags.items():
        if os.getenv(env_key) is not None:
            config.mcp.tools[name].enabled = os.getenv(env_key, "false").lower() == "true"
    if os.getenv("LUTHOR_MCP_ENABLED") is not None:
        config.mcp.enabled = os.getenv("LUTHOR_MCP_ENABLED", "true").lower() == "true"


def _mcp_config_from_env() -> MCPConfig:
    def _connector(
        name: str,
        *,
        url_env: str,
        key_env: str | None = None,
        token_env: str | None = None,
        site_env: str | None = None,
        enabled_env: str | None = None,
    ) -> MCPConnectorConfig:
        return MCPConnectorConfig(
            enabled=os.getenv(enabled_env or f"LUTHOR_MCP_{name.upper()}_ENABLED", "false").lower()
            == "true",
            url=os.getenv(url_env, ""),
            api_key=os.getenv(key_env, "") if key_env else "",
            token=os.getenv(token_env, "") if token_env else "",
            site_id=os.getenv(site_env, "") if site_env else "",
        )

    return MCPConfig(
        enabled=os.getenv("LUTHOR_MCP_ENABLED", "true").lower() == "true",
        tools={
            "n8n": _connector("n8n", url_env="N8N_API_URL", key_env="N8N_API_KEY"),
            "penpot": _connector(
                "penpot",
                url_env="PENPOT_API_URL",
                token_env="PENPOT_ACCESS_TOKEN",
            ),
            "appflowy": _connector(
                "appflowy",
                url_env="APPFLOWY_API_URL",
                token_env="APPFLOWY_TOKEN",
            ),
            "plausible": _connector(
                "plausible",
                url_env="PLAUSIBLE_API_URL",
                token_env="PLAUSIBLE_TOKEN",
                site_env="PLAUSIBLE_SITE_ID",
            ),
            "whisper": MCPConnectorConfig(
                enabled=os.getenv("LUTHOR_MCP_WHISPER_ENABLED", "false").lower() == "true",
                model=os.getenv("WHISPER_MODEL_SIZE", "tiny"),
                device=os.getenv("WHISPER_DEVICE", "cpu"),
            ),
            "ytdlp": MCPConnectorConfig(
                enabled=os.getenv("LUTHOR_MCP_YTDLP_ENABLED", "false").lower() == "true",
                download_dir=os.getenv("YTDLP_DOWNLOAD_DIR", "./data/downloads"),
                max_downloads_per_user=int(os.getenv("YTDLP_MAX_DOWNLOADS_PER_USER", "10")),
            ),
            "fooocus": _connector(
                "fooocus",
                url_env="FOOOCUS_API_URL",
                key_env="FOOOCUS_API_KEY",
            ),
            "calcom": MCPConnectorConfig(
                enabled=os.getenv("LUTHOR_MCP_CALCOM_ENABLED", "false").lower() == "true",
                url=os.getenv("CALCOM_API_URL", ""),
                api_key=os.getenv("CALCOM_API_KEY", ""),
                event_type_id=os.getenv("CALCOM_EVENT_TYPE_ID", ""),
            ),
        },
    )


# Global configuration instance
_config: Optional[LuthorConfig] = None


def _default_params_path() -> Path | None:
    override = os.getenv("LUTHOR_PARAMS_PATH")
    if override:
        path = Path(override)
        return path if path.exists() else None

    repo_root = Path(__file__).resolve().parents[2]
    candidate = repo_root / "params.yaml"
    return candidate if candidate.exists() else None


def _merge_predictor_config(config: LuthorConfig, predictor_params: dict) -> None:
    if not predictor_params:
        return
    merged = {**config.predictor.__dict__, **predictor_params}
    allowed = PredictorConfig.__dataclass_fields__.keys()
    config.predictor = PredictorConfig(**{key: merged[key] for key in allowed})


def _merge_params_into_config(config: LuthorConfig, params: dict) -> LuthorConfig:
    config.prompt_version = str(params.get("prompt_version", config.prompt_version))
    _merge_predictor_config(config, params.get("predictor", {}))

    ab_cfg = params.get("ab_testing", {})
    if ab_cfg:
        config.ab_testing.enabled = bool(ab_cfg.get("enabled", config.ab_testing.enabled))
        models = ab_cfg.get("models", {})
        if models:
            config.ab_testing.models = {
                "default": models.get("default", config.ab_testing.models["default"]),
                "candidate": models.get("candidate", config.ab_testing.models["candidate"]),
            }

    al_cfg = params.get("active_learning", {})
    if "human_in_loop" in al_cfg:
        config.active_learning.human_in_loop = bool(al_cfg["human_in_loop"])
    if "use_mock_human" in al_cfg:
        config.active_learning.use_mock_human = bool(al_cfg["use_mock_human"])

    env_cfg = params.get("environment", {})
    if env_cfg:
        config.environment.type = str(env_cfg.get("type", config.environment.type))
        inventory_cfg = env_cfg.get("inventory", {})
        if inventory_cfg:
            merged = {**config.environment.inventory.__dict__, **inventory_cfg}
            allowed = InventoryConfig.__dataclass_fields__.keys()
            config.environment.inventory = InventoryConfig(
                **{key: merged[key] for key in allowed}
            )

    grid_cfg = params.get("gridworld", {})
    if grid_cfg:
        merged = {**config.gridworld.__dict__, **grid_cfg}
        allowed = GridWorldConfig.__dataclass_fields__.keys()
        config.gridworld = GridWorldConfig(**{key: merged[key] for key in allowed})

    gen_cfg = params.get("generalization", {})
    if gen_cfg:
        merged = {**config.generalization.__dict__, **gen_cfg}
        allowed = GeneralizationConfig.__dataclass_fields__.keys()
        config.generalization = GeneralizationConfig(**{key: merged[key] for key in allowed})

    if "seed" in params:
        config.seed = int(params["seed"])

    if config.environment.type == "inventory":
        inv = config.environment.inventory
        config.active_learning.input_dim = inv.num_products * 3
        config.active_learning.action_dim = inv.num_products

    quotas_cfg = params.get("quotas", {})
    if quotas_cfg:
        if free_cfg := quotas_cfg.get("free"):
            merged = {**config.quotas.free.__dict__, **free_cfg}
            config.quotas.free = QuotaTierLimits(
                **{k: merged[k] for k in QuotaTierLimits.__dataclass_fields__}
            )
        if pro_cfg := quotas_cfg.get("pro"):
            merged = {**config.quotas.pro.__dict__, **pro_cfg}
            config.quotas.pro = QuotaTierLimits(
                **{k: merged[k] for k in QuotaTierLimits.__dataclass_fields__}
            )

    mcp_cfg = params.get("mcp", {})
    if mcp_cfg:
        config.mcp.enabled = bool(mcp_cfg.get("enabled", config.mcp.enabled))
        tools_cfg = mcp_cfg.get("tools", {})
        for name, raw in tools_cfg.items():
            if name not in config.mcp.tools:
                config.mcp.tools[name] = _parse_connector_from_params(raw)
                continue
            connector = config.mcp.tools[name]
            parsed = _parse_connector_from_params({**connector.__dict__, **raw})
            config.mcp.tools[name] = parsed

    return config


def get_config() -> LuthorConfig:
    """Get the global Luthor configuration."""
    global _config
    if _config is None:
        _config = LuthorConfig.from_env()
        params_path = _default_params_path()
        if params_path is not None:
            from luthor.pipeline.params import load_params

            _config = _merge_params_into_config(_config, load_params(params_path))

        if os.getenv("LUTHOR_AB_TESTING_ENABLED") is not None:
            _config.ab_testing.enabled = (
                os.getenv("LUTHOR_AB_TESTING_ENABLED", "false").lower() == "true"
            )
        if os.getenv("LUTHOR_PROMPT_VERSION") is not None:
            _config.prompt_version = os.getenv("LUTHOR_PROMPT_VERSION", "v1")
        if os.getenv("LUTHOR_PREDICTOR_TYPE") is not None:
            _config.predictor.predictor_type = os.getenv("LUTHOR_PREDICTOR_TYPE", "mlp")
        _apply_mcp_env_overrides(_config)
    return _config


def reset_config():
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
