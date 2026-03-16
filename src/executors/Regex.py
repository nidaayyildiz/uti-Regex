import os
import sys
import re
from typing import Any, Iterable, List, Optional, Tuple, Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../"))

from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.Regex.src.utils.RegexEngine import RegexEngine
from components.Regex.src.utils.response import build_response_regex
from components.Regex.src.models.PackageModel import PackageModel


class Regex(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        # Some initialization payloads may contain partial configs/inputs.
        # Don't fail package initialization on strict model validation.
        try:
            self.request.model = PackageModel(**(self.request.data))
        except Exception:
            self.request.model = None
        self.pattern = self.request.get_param("configPattern")
        self.configFlagsMode = self.request.get_param("configFlagsMode")
        #  Request.get_param() returns `value` for dependentDropdownlist when inner field is option/textInput.
        # In our schema ConfigFlagsEnabled.value is "enable" (not "configFlagsEnabled"), so accept both.
        if self.configFlagsMode in {"configFlagsEnabled", "enable", True, "True"}:
            self.flags = self.request.get_param("configFlags")
            # Normalize to list for RegexEngine._build_flags()
            if self.flags is not None and not isinstance(self.flags, list):
                self.flags = [self.flags]
        else:
            self.flags = None
        self.max_split = self.request.get_param("configMaxSplit") 
        self.replacement = self.request.get_param("configReplacement") 
        self.method = self.request.get_param("configMethod")

        self.input_data = self.request.get_param("inputData")
        self.key_input_mode = self.request.get_param("configKeyInputMode")
        key_enabled = self.key_input_mode in {"keyInputEnabled", "enable", True, "True"}
        self.key_input = self.request.get_param("configKeyInput") if key_enabled else None
        self.key_inputs = [t.strip() for t in self.key_input.split(',')] if self.key_input else []

        self.outputData = None
        self.branchstop = False

    @staticmethod
    def _is_int_str(value: str) -> bool:
        try:
            int(value)
            return True
        except Exception:
            return False

    @classmethod
    def _iter_keypath_targets(
        cls, root: Any, parts: List[str]
    ) -> Iterable[Tuple[Union[dict, list], Union[str, int], Any]]:
        """
        Yield (container, key/index, value) for each target addressed by parts.

        Supports:
        - dict traversal by key
        - list traversal either by numeric index (e.g. "items.0.name")
          or by mapping to all elements when a non-numeric part is requested
          (e.g. "items.name" applies to each element in items if it's a list).
        """
        if not parts:
            return

        def _walk(node: Any, i: int) -> Iterable[Tuple[Union[dict, list], Union[str, int], Any]]:
            if i >= len(parts):
                return

            part = parts[i]
            is_last = i == (len(parts) - 1)

            if isinstance(node, dict):
                if part not in node:
                    return
                if is_last:
                    yield (node, part, node.get(part))
                    return
                yield from _walk(node.get(part), i + 1)
                return

            if isinstance(node, list):
                if cls._is_int_str(part):
                    idx = int(part)
                    if idx < 0 or idx >= len(node):
                        return
                    if is_last:
                        yield (node, idx, node[idx])
                        return
                    yield from _walk(node[idx], i + 1)
                    return

                # Non-numeric key: apply to all list elements
                for elem in node:
                    if is_last:
                        # Can't set a dict key on a list directly; last part must resolve within elem.
                        # So for "listKey" without further nesting, this yields nothing by design.
                        continue
                    yield from _walk(elem, i)
                return

            # Unsupported node type
            return

        yield from _walk(root, 0)

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}

    def _resolve_method_name(self) -> str:
        """
        Extract raw method name from configMethod.
        Config may be a Pydantic model or a primitive string.
        """
        value = self.method
        if hasattr(value, "value"):
            value = getattr(value, "value")
        if isinstance(value, str):
            return value
        return ""

    def process(self):
        """
        Execute the selected Regex method via RegexEngine.
        Handles errors via flow.stop() and branch stop when no match.
        """
        method_name = self._resolve_method_name()
        if not method_name:
            # Invalid configuration – stop the entire flow
            self.flow.stop(package_uID=self.uID)
            self.outputData = {"error": "Invalid regex method configuration"}
            return

        try:
            engine = RegexEngine(
                pattern=self.pattern or "",
                flags=self.flags ,
                max_split=self.max_split,
                replacement=self.replacement or "",
            )

            engine_method = getattr(engine, method_name, None)
            if engine_method is None:
                self.flow.stop(package_uID=self.uID)
                self.outputData = {"error": f"Unsupported regex method: {method_name}"}
                return

            is_mutation = method_name in {"sub", "subn"}
            data = self.input_data
            
            if self.key_inputs:
                items_to_process = data if isinstance(data, list) else [data]
                if is_mutation:
                    for item in items_to_process:
                        for key_path in self.key_inputs:
                            parts = [p for p in key_path.split(".") if p != ""]
                            for container, key, value in self._iter_keypath_targets(item, parts):
                                target_val = "" if value is None else str(value)
                                mutated = engine_method(target_val)
                                new_val = mutated["value"] if isinstance(mutated, dict) and "value" in mutated else mutated
                                try:
                                    container[key] = new_val  # type: ignore[index]
                                except Exception:
                                    # If the container is immutable/unexpected, skip silently
                                    pass
                    result = data
                else:
                    result = []
                    for item in items_to_process:
                        for key_path in self.key_inputs:
                            parts = [p for p in key_path.split(".") if p != ""]
                            for _container, _key, value in self._iter_keypath_targets(item, parts):
                                target_val = "" if value is None else str(value)
                                result.append(engine_method(target_val))
            else:
                if isinstance(data, list):
                    # Handle lists of primivites if no keys are provided
                    result = engine_method(data)
                else:
                    result = engine_method(str(data) if not isinstance(data, str) and not isinstance(data, dict) else data)

            # If no match or empty result for match/search/fullmatch/finditer/findall,
            # stop only this branch as specified in the requirements.
            if method_name in {
                "match",
                "search",
                "fullmatch",
                "findall",
                "finditer",
            }:
                is_empty = result is None
                if isinstance(result, list) and len(result) == 0:
                    is_empty = True
                if isinstance(result, dict) and len(result.keys()) == 0:
                    is_empty = True

                if is_empty:
                    self.branchstop = True

            self.outputData = result
        except re.error as exc:
            # Regex compilation or execution error – stop the entire flow
            self.flow.stop(package_uID=self.uID)
            self.outputData = {"error": str(exc)}

    def run(self):
        self.process()
        package_model = build_response_regex(context=self)
        return package_model


if "__main__" == __name__:
    Executor(sys.argv[1]).run()

