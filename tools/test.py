import pkgutil
import importlib
import howlitbe
import tired.logging
import os


os.environ["HWL_TEST_LB22_TOPO"] = "1"  # To run topology generation test


def check_function_in_module(module_name, function_name):
    checked = set()

    try:
        # Import the specified module
        module = importlib.import_module(module_name)
    except ImportError:
        print(f"Module '{module_name}' not found.")
        return

    # Function to traverse packages and check for the function
    def traverse_packages(package):
        nonlocal checked
        for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            # Prevent double checking
            if modname in checked:
                continue
            checked = checked.union({modname})

            if ispkg:
                # Recursive call for sub-packages
                sub_package = importlib.import_module(modname)
                traverse_packages(sub_package)
            else:
                # Import the module and check for the function
                mod = importlib.import_module(modname)
                # Flush global variables
                mod = importlib.reload(mod)
                for attribute in dir(mod):
                    if attribute.startswith("test") and callable(getattr(mod, attribute)):
                        print("Testing", f'"{modname}.{attribute}"')
                        getattr(mod, attribute)()

    # Start traversing from the main module
    traverse_packages(module)

# Example usage
tired.logging.set_level(tired.logging.DEBUG)
check_function_in_module('howlitbe', 'test')
print("SUCCESS! No test has triggered an assert")
