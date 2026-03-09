import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Базовая настройка логирования для приложения и воркеров."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

