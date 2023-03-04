from argparse import ArgumentParser
from pathlib import Path
import shutil


def main():
    parser, args = parse_args()
    indir = Path(args.indir).resolve()
    outdir = Path(args.outdir).resolve()

    # Error checking
    if not indir.exists():
        parser.error(f"Input directory does not exist: '{indir}'")
    if not indir.is_dir():
        parser.error(f"Input path is not a valid directory: '{indir}'")
    if outdir.exists() and not outdir.is_dir():
        parser.error(f"Output path exists but is not a valid directory: {outdir}")
    if indir == outdir:
        parser.error(f"Input and output directories are the same")
    try:
        outdir.mkdir(exist_ok=True, parents=args.parents)
    except OSError as err:
        parser.error(f"Could not make output directory (did you mean to specify '-p'?):\n -> {err}")

    # Flatten!
    n_files, n_bytes = flatten_dir(indir, outdir, args.recurse_max, args.verbose, args.force_overwrite)
    print(f"Copied {n_files} files ({format_bytes(n_bytes)})")


def parse_args():
    parser = ArgumentParser("flatdir")
    parser.add_argument("indir", help="directory to flatten")
    parser.add_argument("outdir", help="output directory")
    parser.add_argument("--recurse_max", '-r', default=1, type=int, metavar="N", help="max number of recursions (default 1)")
    parser.add_argument("--verbose", "-v", action="store_true", help="print verbose output")
    parser.add_argument("--parents", "-p", action="store_true", help="create parents of output directory, if necessary")
    parser.add_argument("--force_overwrite", "-f", action="store_true", help="overwrite any duplicates in the destination directory")
    return parser, parser.parse_args()


def format_bytes(n_bytes: int) -> str:
    for prefix in ["", "kilo", "mega", "giga", "tera"]:
        if n_bytes < 1e3:
            break
        n_bytes /= 1e3
    return f"{n_bytes:.2f} {prefix}bytes"


def flatten_dir(indir: Path, outdir: Path, recursions_left: int, verbose: bool, overwrite: bool) -> tuple[int, int]:
    """
    flatten_dir
    Copies all files from `indir` to `outdir`.

    Parameters
    ---
    * `indir` - The directory from which to copy files.
    * `outdir` - The output directory.
    * `recursions_left` - The depth of subdirectories to recurse.
      If less than zero, does nothing.
    * `verbose` - Whether to print a confirmation of every copied file.
    * `overwrite` - Whether to overwrite duplicates in `outdir`.

    Returns
    ---
    A tuple `(n_files, n_bytes)`, where:
    * `n_files` is the total number of files copied.
    * `n_bytes` is the total number of bytes copied.
    """
    if recursions_left < 0 or indir == outdir:
        return 0, 0
    
    n_files = 0
    n_bytes = 0
    for path in indir.iterdir():
        # Recurse subdirectory
        if path.is_dir():
            sub_files, sub_bytes = flatten_dir(path, outdir, recursions_left - 1, verbose, overwrite)
            n_files += sub_files
            n_bytes += sub_bytes
        # Copy file
        elif path.is_file():
            outfile = outdir / path.name
            if outfile.exists() and not overwrite:
                continue
            if verbose:
                print(f"Copying '{outfile}'")
            shutil.copy(path, outfile)
            n_files += 1
            n_bytes += path.stat().st_size

    return n_files, n_bytes


if __name__ == "__main__":
    main()
