import src


def run_thingsboard_backend(
    config: src.types.Config,
    logger: src.utils.Logger,
) -> None:
    assert config.backend is not None
    assert config.backend.provider == "thingsboard"

    # TODO
