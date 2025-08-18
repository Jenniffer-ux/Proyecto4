from setuptools import setup, find_packages
setup(name="proyecto-ia-precios", version="1.1.0",
      packages=find_packages(where="src"),
      package_dir={"": "src"},
      install_requires=[r.strip() for r in open("requirements.txt").read().splitlines() if r.strip()])