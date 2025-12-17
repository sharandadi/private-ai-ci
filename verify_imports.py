
import importlib
import sys

def verify_imports():
    packages = [
        "numpy",
        "pandas",
        "scipy",
        "sklearn",
        "matplotlib",
        "seaborn",
        "tqdm",
        "yaml",
        "click",
        "psutil",
        "bs4",
        "aiohttp",
        "pytest",
        "cv2",
        "fastapi",
        "torch",
        "django",
    ]

    print("Verifying imports...")
    failed = []
    for package in packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} imported successfully")
        except ImportError as e:
            print(f"❌ {package} failed to import: {e}")
            failed.append(package)

    if failed:
        print(f"\nFailed to import {len(failed)} packages: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\n🎉 All packages imported successfully!")
        sys.exit(0)

if __name__ == "__main__":
    verify_imports()
