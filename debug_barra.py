import pickletools
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(r"C:\Users\lzx\Desktop\研一下\量化\Project")
barra_path = PROJECT_ROOT / "data_1800" / "stock1000" / "data" / "barra" / "style" / "Beta.pkl"

print("Analyzing Barra Beta pickle...")
all_blobs = []
for op, arg, _ in pickletools.genops(barra_path.read_bytes()):
    if op.name in {"BYTEARRAY8", "BINBYTES"} and isinstance(arg, (bytes, bytearray)):
        all_blobs.append((op.name, len(arg)))

print(f"Total blobs: {len(all_blobs)}")
for i, (name, size) in enumerate(all_blobs[:10]):
    print(f"  Blob {i}: {name}, size={size}")

# Check if there are any large blobs
large_blobs = [b for b in all_blobs if b[1] > 100000]
print(f"\nLarge blobs (>100KB): {len(large_blobs)}")
for i, (name, size) in enumerate(large_blobs[:5]):
    print(f"  {name}: {size} bytes, {size//8} float64 values")

# Try reading directly
all_bytes = []
for op, arg, _ in pickletools.genops(barra_path.read_bytes()):
    if op.name in {"BYTEARRAY8", "BINBYTES"} and isinstance(arg, (bytes, bytearray)):
        all_bytes.append(bytes(arg))

if len(all_bytes) >= 2:
    print("\nTrying to parse as Barra format...")
    values_blob = all_bytes[0]
    dates_blob = all_bytes[1]
    print(f"Values blob: {len(values_blob)} bytes = {len(values_blob)//8} float64")
    print(f"Dates blob: {len(dates_blob)} bytes = {len(dates_blob)//8} int64")

    n_dates = len(dates_blob) // 8
    n_cols = (len(values_blob) // 8) // n_dates
    print(f"Inferred: {n_dates} dates x {n_cols} stocks")
