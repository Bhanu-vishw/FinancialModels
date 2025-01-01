from pathlib import Path
import shutil

package_path = Path(__file__).parent.resolve()
shutil.make_archive("backtestlib", "zip", package_path)
