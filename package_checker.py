import pkgutil
import inspect
import importlib
import importlib.metadata


def get_package_info(module_name: str):
    candidates = [
        module_name,
        module_name.split('.')[0],
        module_name.replace('.', '-'),
        module_name.split('.')[0].replace('_', '-'),
    ]
    for name in candidates:
        try:
            meta = importlib.metadata.metadata(name)
            return {
                "package":       meta["Name"],
                "version":       meta["Version"],
                "summary":       meta.get("Summary", "N/A"),
                "author":        meta.get("Author", meta.get("Author-email", "N/A")),
                "license":       meta.get("License", "N/A"),
                "home_page":     meta.get("Home-page", meta.get("Project-URL", "N/A")),
                "requires_python": meta.get("Requires-Python", "N/A"),
            }
        except importlib.metadata.PackageNotFoundError:
            continue
    return None


def explore_class(mod, class_name: str):
    cls = getattr(mod, class_name, None)
    if cls is None:
        print(f"\n## Class '{class_name}' not found in module.\n")
        return

    print(f"\n{'='*60}")
    print(f"CLASS: {class_name}")
    print(f"{'='*60}")

    # Docstring
    if cls.__doc__:
        print(f"\n## DOCSTRING:\n   {cls.__doc__.strip()[:400]}")

    # MRO (inheritance chain)
    mro = [c.__name__ for c in cls.__mro__ if c.__name__ != 'object']
    print(f"\n## INHERITANCE: {' -> '.join(mro)}")

    # __init__ signature
    try:
        init_sig = inspect.signature(cls.__init__)
        print(f"\n##  CONSTRUCTOR:\n   {class_name}{init_sig}")
    except (ValueError, TypeError):
        print(f"\n##  CONSTRUCTOR: (unable to inspect)")

    # Methods
    methods = [
        (name, obj)
        for name, obj in inspect.getmembers(cls, predicate=inspect.isfunction)
        if not name.startswith('_')
    ]
    # Include dunder methods that are useful
    useful_dunders = ['__init__', '__call__', '__enter__', '__exit__', '__aenter__', '__aexit__']
    dunder_methods = [
        (name, obj)
        for name, obj in inspect.getmembers(cls, predicate=inspect.isfunction)
        if name in useful_dunders and name != '__init__'
    ]

    if methods:
        print(f"\n## METHODS ({len(methods)}):")
        for name, obj in methods:
            try:
                sig = str(inspect.signature(obj))
                sig = sig if len(sig) < 60 else sig[:57] + "..."
            except (ValueError, TypeError):
                sig = "(...)"
            doc = (obj.__doc__ or "").strip().split('\n')[0][:50]
            print(f"   - {name}{sig}")
            if doc:
                print(f"     └─ {doc}")

    if dunder_methods:
        print(f"\n##  SPECIAL METHODS:")
        for name, obj in dunder_methods:
            try:
                sig = str(inspect.signature(obj))
            except (ValueError, TypeError):
                sig = "(...)"
            print(f"   - {name}{sig}")

    # Class attributes / properties
    props = [
        (name, obj)
        for name, obj in inspect.getmembers(cls)
        if isinstance(obj, property) and not name.startswith('_')
    ]
    if props:
        print(f"\n## PROPERTIES ({len(props)}):")
        for name, obj in props:
            doc = (obj.__doc__ or "").strip().split('\n')[0][:60]
            print(f"   - {name:<40} {doc}")

    print(f"\n{'='*60}\n")


def explore_module(module_name: str):
    try:
        mod = importlib.import_module(module_name)
    except ModuleNotFoundError:
        print(f"\n## Module '{module_name}' not found.\n")
        return None

    print(f"\n{'='*60}")
    print(f"MODULE: {module_name}")
    print(f"{'='*60}")

    info = get_package_info(module_name)
    if info:
        print(f"\n## PACKAGE INFO:")
        print(f"   Package        : {info['package']}")
        print(f"   Version        : {info['version']}")
        print(f"   Summary        : {info['summary']}")
        print(f"   Author         : {info['author']}")
        print(f"   License        : {info['license']}")
        print(f"   Home Page      : {info['home_page']}")
        print(f"   Requires Python: {info['requires_python']}")

    print(f"\n## FILE INFO:")
    print(f"   Path : {getattr(mod, '__file__', 'built-in')}")

    if mod.__doc__:
        print(f"\n## DOCSTRING:\n   {mod.__doc__.strip()[:300]}")

    if hasattr(mod, '__path__'):
        submodules = [m.name for m in pkgutil.iter_modules(mod.__path__)]
        if submodules:
            print(f"\n## SUBMODULES ({len(submodules)}):")
            for s in submodules:
                print(f"   - {s}")

    classes = [
        (name, obj)
        for name, obj in inspect.getmembers(mod, inspect.isclass)
        if not name.startswith('_')
    ]
    if classes:
        print(f"\n## CLASSES ({len(classes)}):")
        for name, obj in classes:
            doc = (obj.__doc__ or "").strip().split('\n')[0][:60]
            print(f"   - {name:<40} {doc}")

    functions = [
        (name, obj)
        for name, obj in inspect.getmembers(mod, inspect.isfunction)
        if not name.startswith('_')
    ]
    if functions:
        print(f"\n## FUNCTIONS ({len(functions)}):")
        for name, obj in functions:
            try:
                sig = str(inspect.signature(obj))
                sig = sig if len(sig) < 60 else sig[:57] + "..."
            except (ValueError, TypeError):
                sig = "(...)"
            print(f"   - {name}{sig}")

    others = [
        name for name in dir(mod)
        if not name.startswith('_')
        and not inspect.isclass(getattr(mod, name))
        and not inspect.isfunction(getattr(mod, name))
        and not inspect.ismodule(getattr(mod, name))
    ]
    if others:
        print(f"\n## CONSTANTS / OTHER ({len(others)}):")
        for name in others:
            val = str(getattr(mod, name))
            val = val if len(val) < 60 else val[:57] + "..."
            print(f"   - {name:<40} = {val}")

    print(f"\n{'='*60}\n")
    return mod


if __name__ == "__main__":
    print("\n🔍 Module & Class Explorer")
    print("   Commands:")
    print("   - type a module name     e.g. a2a.client")
    print("   - type module::ClassName e.g. a2a.client::ClientFactory")
    print("   - type 'q' to quit\n")

    current_mod = None

    while True:
        try:
            user_input = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDone!")
            break

        if not user_input:
            continue
        if user_input.lower() == 'q':
            print("Done!")
            break

        # Check if user wants to drill into a class: module::ClassName
        if '::' in user_input:
            parts = user_input.split('::', 1)
            module_name, class_name = parts[0].strip(), parts[1].strip()
            mod = explore_module(module_name)
            if mod:
                explore_class(mod, class_name)
        else:
            current_mod = explore_module(user_input)