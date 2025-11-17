from typing import Type, Dict, Any
import inspect


class BaseBuilder:
    """
    Used to create instances of classes

    Requires prior call to register (instance name, class) and configure (instance name, constructor parameters)

    In constructor parameters defaults can be omitted, other instances can be references by $name
    """

    def __init__(self):
        self._registry = {}
        self._config = {}
        self._created = {}
        self._creating = set()

    def register(self, name: str, cls: Type):
        self._registry[name] = cls

    def configure(self, config: Dict[str, Any]):
        self._config = config

    def add_config(self, name: str, params: Dict[str, Any]):
        self._config[name] = params

    def create(self, name: str, **kwargs):
        if name in self._creating:
            raise RuntimeError(f"Circular dependency detected: {name}")
        if name not in self._registry:
            raise ValueError(f"Service {name} not registered")
        if name in self._created:
            return self._created[name]

        self._creating.add(name)
        cls = self._registry[name]
        service_config = self._config.get(name, {})

        # Merge provided kwargs with config
        merged_kwargs = {**service_config, **kwargs}

        # Analyze constructor parameters
        sig = inspect.signature(cls.__init__)
        params = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            if param_name in merged_kwargs:
                params[param_name] = self._determine_value(merged_kwargs[param_name])
            elif param.default != param.empty:
                params[param_name] = param.default
            else:
                raise ValueError(f"Missing required parameter: {param_name}")

        self._creating.remove(name)
        self._created[name] = cls(**params)
        return self._created[name]

    def _determine_value(self, value):
        if isinstance(value, str) and value.startswith("$"):
            return self.create(value[1:])
        elif isinstance(value, list):
            return [self._determine_value(val) for val in value]
        elif isinstance(value, dict):
            return {key: self._determine_value(val) for key, val in value.items()}
        else:
            return value
