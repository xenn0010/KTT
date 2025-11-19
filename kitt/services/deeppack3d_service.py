"""
DeepPack3D Service for KITT
Provides a clean interface to the DeepPack3D 3D bin-packing algorithm
"""

import sys
import os
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Add DeepPack3D to path
DEEPPACK_DIR = Path(__file__).parent / "deeppack3d_engine"
sys.path.insert(0, str(DEEPPACK_DIR))

try:
    # Suppress matplotlib warnings during import
    import warnings
    warnings.filterwarnings('ignore')
    from deeppack3d import deeppack3d
    DEEPPACK_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("DeepPack3D loaded successfully")
except ImportError as e:
    DEEPPACK_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"DeepPack3D not available, using mock service: {e}")
except Exception as e:
    DEEPPACK_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error(f"Error loading DeepPack3D: {e}")


class DeepPack3DService:
    """Service wrapper for DeepPack3D bin-packing algorithm"""

    def __init__(self, method: str = "bl", lookahead: int = 5, verbose: int = 0):
        """
        Initialize DeepPack3D service

        Args:
            method: Packing method - "bl" (best lookahead), "baf" (best area fit),
                   "bssf" (best short side fit), "blsf" (best long side fit),
                   "rl" (reinforcement learning)
            lookahead: Lookahead value for the algorithm (1-10)
            verbose: Verbosity level (0=silent, 1=standard, 2=detailed)
        """
        if not DEEPPACK_AVAILABLE:
            raise RuntimeError("DeepPack3D is not available. Please install dependencies.")

        self.method = method
        self.lookahead = lookahead
        self.verbose = verbose

    def pack_items(
        self,
        items: List[Dict[str, Any]],
        container_dimensions: Tuple[float, float, float],
        max_weight: float = None
    ) -> Dict[str, Any]:
        """
        Pack items into a container using DeepPack3D

        Args:
            items: List of items with keys: id, width, height, depth, weight
            container_dimensions: Tuple of (width, height, depth) for container
            max_weight: Maximum weight capacity of container (optional)

        Returns:
            dict: Packing result with placements, utilization, and metrics
        """
        start_time = time.time()

        try:
            # CRITICAL: DeepPack3D has hardcoded 32×32×32 limit
            # Calculate scaling factor to fit container into 32×32×32
            max_container_dim = max(container_dimensions)
            DEEPPACK_MAX = 30  # Use 30 instead of 32 for safety margin
            scale_factor = DEEPPACK_MAX / max_container_dim if max_container_dim > DEEPPACK_MAX else 1.0

            # Scale down container and items for DeepPack3D
            scaled_container = tuple(int(d * scale_factor) for d in container_dimensions)
            scaled_items = [
                {
                    **item,
                    "width": item["width"] * scale_factor,
                    "height": item["height"] * scale_factor,
                    "depth": item["depth"] * scale_factor
                }
                for item in items
            ]

            logger.info(f"Scaling: {scale_factor:.4f}x (container {container_dimensions} → {scaled_container})")

            # Convert KITT items to DeepPack3D format (already scaled)
            deeppack_items = self._convert_items_to_deeppack_format(scaled_items)

            # Create temporary input file for DeepPack3D
            input_file = self._create_input_file(deeppack_items, container_dimensions)

            # Run Deep Pack3D algorithm
            placements = []
            bins_used = 1  # Start with bin 1
            current_bin_weight = 0.0
            current_bin_items = []

            try:
                for result in deeppack3d(
                    method=self.method,
                    lookahead=self.lookahead,
                    n_iterations=-1,  # Process all items
                    data='file',
                    path=str(input_file),
                    verbose=self.verbose
                ):
                    if result is None:
                        # New bin started (marker between bins)
                        bins_used += 1
                        current_bin_weight = 0.0
                        current_bin_items = []
                        continue

                    # Extract placement information
                    # Result format: (item_cuboid, position_tuple, size_tuple, rotation)
                    # or: (item_cuboid, position_tuple, size_tuple, split_cuboid)
                    try:
                        item_cuboid, pos_tuple, size_tuple, extra = result

                        # Extract coordinates from position tuple/cuboid
                        if hasattr(pos_tuple, 'x'):  # It's a Cuboid
                            x, y, z = pos_tuple.x, pos_tuple.y, pos_tuple.z
                        else:
                            x, y, z = pos_tuple

                        # Extract dimensions from size tuple/cuboid
                        if hasattr(size_tuple, 'width'):  # It's a Cuboid
                            w, h, d = size_tuple.width, size_tuple.height, size_tuple.depth
                        else:
                            w, h, d = size_tuple

                        # Extract item index from item_cuboid
                        if hasattr(item_cuboid, 'width'):  # It's a Cuboid (the item)
                            # Find matching item by dimensions
                            item_idx = None
                            for idx, deeppack_item in enumerate(deeppack_items):
                                if (abs(deeppack_item[0] - item_cuboid.width) < 0.01 and
                                    abs(deeppack_item[1] - item_cuboid.height) < 0.01 and
                                    abs(deeppack_item[2] - item_cuboid.depth) < 0.01):
                                    item_idx = idx
                                    break
                            if item_idx is None:
                                item_idx = len(placements)  # Fallback to placement count
                        else:
                            item_idx = item_cuboid

                        # Rotation (extra can be rotation or split cuboid)
                        rotation = int(extra) if isinstance(extra, (int, float)) else 0

                    except (ValueError, AttributeError, TypeError) as e:
                        logger.error(f"Error unpacking result tuple: {e}, result={result}")
                        import traceback
                        traceback.print_exc()
                        continue

                    if item_idx < len(items):
                        item = items[item_idx]
                        item_weight = item.get("weight", 0)

                        # Check weight constraint
                        if max_weight and current_bin_weight + item_weight > max_weight:
                            logger.warning(f"Item {item['id']} exceeds weight limit, starting new bin")
                            bins_used += 1
                            current_bin_weight = item_weight
                            current_bin_items = [item['id']]
                        else:
                            current_bin_weight += item_weight
                            current_bin_items.append(item['id'])

                        # Scale positions and dimensions back to original size
                        placements.append({
                            "item_id": item["id"],
                            "position": {
                                "x": float(x / scale_factor),
                                "y": float(y / scale_factor),
                                "z": float(z / scale_factor)
                            },
                            "dimensions": {
                                "width": float(w / scale_factor),
                                "height": float(h / scale_factor),
                                "depth": float(d / scale_factor)
                            },
                            "rotation": rotation,
                            "bin_number": bins_used,
                            "weight": item_weight
                        })

            except Exception as e:
                logger.error(f"Error during DeepPack3D execution: {e}")
                raise
            finally:
                # Clean up temporary file
                if input_file.exists():
                    input_file.unlink()

            # Calculate metrics
            computation_time_ms = int((time.time() - start_time) * 1000)
            utilization = self._calculate_utilization(placements, container_dimensions)

            result = {
                "success": True,
                "placements": placements,
                "bins_used": bins_used if bins_used > 0 else 1,
                "utilization": round(utilization, 2),
                "algorithm": f"deeppack3d-{self.method}",
                "computation_time_ms": computation_time_ms,
                "container_dimensions": {
                    "width": container_dimensions[0],
                    "height": container_dimensions[1],
                    "depth": container_dimensions[2]
                },
                "items_packed": len(placements),
                "items_requested": len(items)
            }

            logger.info(
                f"DeepPack3D completed: {len(placements)}/{len(items)} items packed, "
                f"{utilization:.2f}% utilization in {bins_used} bins"
            )

            return result

        except Exception as e:
            logger.error(f"DeepPack3D packing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "algorithm": f"deeppack3d-{self.method}",
                "computation_time_ms": int((time.time() - start_time) * 1000)
            }

    def _convert_items_to_deeppack_format(
        self,
        items: List[Dict[str, Any]]
    ) -> List[Tuple[float, float, float]]:
        """Convert KITT items to DeepPack3D format (w, h, d tuples)"""
        return [
            (
                float(item["width"]),
                float(item["height"]),
                float(item["depth"])
            )
            for item in items
        ]

    def _create_input_file(
        self,
        items: List[Tuple[float, float, float]],
        container_dimensions: Tuple[float, float, float]
    ) -> Path:
        """Create temporary input file for DeepPack3D"""
        # DeepPack3D input format:
        # Each line: item dimensions (w h d), one per line
        # NOTE: DeepPack3D uses hardcoded 32×32×32 bin size
        # Container dimensions are ignored by the algorithm

        temp_dir = Path("/tmp/kitt_deeppack3d")
        temp_dir.mkdir(exist_ok=True)

        input_file = temp_dir / f"input_{int(time.time() * 1000)}.txt"

        with open(input_file, 'w') as f:
            # Write only item dimensions (no container size)
            # Use integers to match DeepPack3D's expected format
            for w, h, d in items:
                f.write(f"{int(w)} {int(h)} {int(d)}\n")

        return input_file

    def _calculate_utilization(
        self,
        placements: List[Dict[str, Any]],
        container_dimensions: Tuple[float, float, float]
    ) -> float:
        """Calculate space utilization percentage"""
        if not placements:
            return 0.0

        # Calculate total item volume
        total_item_volume = sum(
            p["dimensions"]["width"] * p["dimensions"]["height"] * p["dimensions"]["depth"]
            for p in placements
        )

        # Calculate container volume (considering bins used)
        bins_used = max(p["bin_number"] for p in placements) if placements else 1
        container_volume = (
            container_dimensions[0] * container_dimensions[1] * container_dimensions[2]
        ) * bins_used

        return (total_item_volume / container_volume) * 100 if container_volume > 0 else 0.0


class MockDeepPack3DService:
    """Mock service for when DeepPack3D is not available"""

    def __init__(self, method: str = "mock", lookahead: int = 5, verbose: int = 0):
        self.method = method
        self.lookahead = lookahead
        self.verbose = verbose
        logger.warning("Using mock DeepPack3D service - install dependencies for real packing")

    def pack_items(
        self,
        items: List[Dict[str, Any]],
        container_dimensions: Tuple[float, float, float],
        max_weight: float = None
    ) -> Dict[str, Any]:
        """Mock packing - just places items in order"""
        start_time = time.time()

        placements = []
        x_offset = 0.0

        for item in items:
            placements.append({
                "item_id": item["id"],
                "position": {"x": x_offset, "y": 0.0, "z": 0.0},
                "dimensions": {
                    "width": item["width"],
                    "height": item["height"],
                    "depth": item["depth"]
                },
                "rotation": 0,
                "bin_number": 1,
                "weight": item.get("weight", 0)
            })
            x_offset += item["width"]

        # Calculate basic utilization
        total_item_volume = sum(
            item["width"] * item["height"] * item["depth"]
            for item in items
        )
        container_volume = (
            container_dimensions[0] * container_dimensions[1] * container_dimensions[2]
        )
        utilization = (total_item_volume / container_volume) * 100

        return {
            "success": True,
            "placements": placements,
            "bins_used": 1,
            "utilization": round(utilization, 2),
            "algorithm": "mock",
            "computation_time_ms": int((time.time() - start_time) * 1000),
            "container_dimensions": {
                "width": container_dimensions[0],
                "height": container_dimensions[1],
                "depth": container_dimensions[2]
            },
            "items_packed": len(items),
            "items_requested": len(items)
        }


# Factory function to get appropriate service
def get_deeppack_service(
    method: str = None,
    lookahead: int = None,
    verbose: int = 0,
    force_mock: bool = False
) -> Any:
    """
    Get DeepPack3D service (real or mock)

    Args:
        method: Packing method (defaults to env var or "bl")
        lookahead: Lookahead value (defaults to env var or 5)
        verbose: Verbosity level
        force_mock: Force use of mock service even if DeepPack3D is available

    Returns:
        DeepPack3DService or MockDeepPack3DService
    """
    # Read from environment variables if not provided
    if method is None:
        method = os.getenv("DEEPPACK3D_METHOD", "bl")
    if lookahead is None:
        lookahead = int(os.getenv("DEEPPACK3D_LOOKAHEAD", "5"))

    if DEEPPACK_AVAILABLE and not force_mock:
        return DeepPack3DService(method=method, lookahead=lookahead, verbose=verbose)
    else:
        return MockDeepPack3DService(method=method, lookahead=lookahead, verbose=verbose)
