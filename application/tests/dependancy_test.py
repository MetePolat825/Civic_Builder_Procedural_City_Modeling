def check_dependencies(required_packages):
    import pkg_resources  # part of setuptools
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = [pkg for pkg in required_packages if pkg not in installed_packages]
    if missing_packages:
        raise ImportError(f"Missing packages: {', '.join(missing_packages)}")
