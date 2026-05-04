"""CSV loading helpers."""

from pathlib import Path
import pandas as pd
from backend.utils.logger import get_logger
from backend.utils.config import settings

logger = get_logger(__name__)


def load_csv(file_path: Path, nrows: int | None = None) -> pd.DataFrame:
    """Read a CSV with basic error handling."""
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    logger.info("loading_csv", file_path=str(file_path), nrows=nrows)
    df = pd.read_csv(file_path, nrows=nrows)
    logger.info("csv_loaded", rows=len(df), columns=len(df.columns))
    return df


def load_training_data(
    data_dir: Path | None = None,
    nrows: int | None = None
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the three training CSVs (train, weather, farm)."""
    data_dir = data_dir or settings.abs_data_dir
    
    # Look for CSVs in data directory (flexible naming)
    train_data_path = _find_file(data_dir, ["train_data", "train_data-"])
    train_weather_path = _find_file(data_dir, ["train_weather", "train_weather-"])
    farm_data_path = _find_file(data_dir, ["farm_data", "farm_data-"])
    
    train_data = load_csv(train_data_path, nrows=nrows)
    train_weather = load_csv(train_weather_path, nrows=nrows)
    farm_data = load_csv(farm_data_path, nrows=nrows)
    
    logger.info(
        "all_training_data_loaded",
        train_rows=len(train_data),
        weather_rows=len(train_weather),
        farm_rows=len(farm_data)
    )
    
    return train_data, train_weather, farm_data


def _find_file(data_dir: Path, prefixes: list[str]) -> Path:
    """Glob for a CSV whose name starts with one of the given prefixes."""
    for f in data_dir.rglob("*.csv"):
        for prefix in prefixes:
            if f.stem.startswith(prefix) or prefix in f.stem:
                return f
    raise FileNotFoundError(
        f"Could not find CSV with prefixes {prefixes} in {data_dir}"
    )


def load_uploaded_csv(file_content: bytes) -> pd.DataFrame:
    """Parse raw bytes as CSV (for file uploads)."""
    from io import BytesIO
    df = pd.read_csv(BytesIO(file_content))
    logger.info("uploaded_csv_loaded", rows=len(df), columns=list(df.columns))
    return df
