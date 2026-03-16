import re
from typing import Any, Dict, List, Optional, Union


class RegexEngine:
    def __init__(
        self,
        pattern: str,
        flags: Optional[List[Any]] = None,
        max_split: int = 0,
        replacement: str = "",
    ) -> None:

        self.pattern = pattern or ""
        self.flags_value = self._build_flags(flags or [])
        self.max_split = max_split or 0
        self.replacement = replacement or ""
        self._regex = re.compile(self.pattern, self.flags_value)

    def _build_flags(self, flags: List[Any]) -> int:

        flag_map = {
            "A": re.ASCII,
            "ASCII": re.ASCII,
            "I": re.IGNORECASE,
            "IGNORECASE": re.IGNORECASE,
            "M": re.MULTILINE,
            "MULTILINE": re.MULTILINE,
            "S": re.DOTALL,
            "DOTALL": re.DOTALL,
            "X": re.VERBOSE,
            "VERBOSE": re.VERBOSE,
        }

        mask = 0
        for item in flags:
            code = None

            # Config object with `name` or `value`
            if hasattr(item, "name"):
                code = getattr(item, "name")
            elif hasattr(item, "value"):
                code = getattr(item, "value")
            else:
                code = item

            if isinstance(code, str):
                key = code.upper()
                if key in flag_map:
                    mask |= flag_map[key]

        return mask


    def _serialize_match(self, match: Optional[re.Match]) -> Optional[Dict[str, Any]]:
        if match is None:
            return None

        has_named = bool(self._regex.groupindex)
        base: Dict[str, Any] = {
            "value": match.group(0),
            "span": {"start": match.start(), "end": match.end()},
        }

        if has_named:
            base["groups"] = match.groupdict()
        else:
            # Exclude group 0 which is the full match
            groups = [match.group(i) for i in range(1, len(match.groups()) + 1)]
            base["groups"] = groups

        # lastgroup information is useful for tokenization-style use cases
        base["lastGroup"] = match.lastgroup
        return base

    def _apply_to_input(
        self,
        input_data: Union[str, List[str], Dict[str, Any]],
        fn,
    ) -> Union[dict, list, None]:

        if isinstance(input_data, str):
            return fn(input_data)

        if isinstance(input_data, list):
            return [fn(item) for item in input_data]

        if isinstance(input_data, dict):
            return {key: fn(value) for key, value in input_data.items()}

        # Unsupported type
        return None


    def match(self, input_data: Union[str, List[str], Dict[str, Any]]) -> Any:
        def _op(text: Any) -> Optional[Dict[str, Any]]:
            text = "" if text is None else str(text)
            m = self._regex.match(text)
            return self._serialize_match(m)

        return self._apply_to_input(input_data, _op)

    def search(self, input_data: Union[str, List[str], Dict[str, Any]]) -> Any:
        def _op(text: Any) -> Optional[Dict[str, Any]]:
            text = "" if text is None else str(text)
            m = self._regex.search(text)
            return self._serialize_match(m)

        return self._apply_to_input(input_data, _op)

    def fullmatch(self, input_data: Union[str, List[str], Dict[str, Any]]) -> Any:
        def _op(text: Any) -> Optional[Dict[str, Any]]:
            text = "" if text is None else str(text)
            m = self._regex.fullmatch(text)
            return self._serialize_match(m)

        return self._apply_to_input(input_data, _op)

    def finditer(self, input_data: Union[str, List[str], Dict[str, Any]]) -> Any:
        def _op(text: Any) -> List[Dict[str, Any]]:
            text = "" if text is None else str(text)
            return [self._serialize_match(m) for m in self._regex.finditer(text) if m]

        return self._apply_to_input(input_data, _op)

    def findall(self, input_data: Union[str, List[str], Dict[str, Any]]) -> Any:
        """
        Implemented via finditer so that we can always return
        structured items (value, span, groups, lastGroup).
        """
        return self.finditer(input_data)

    def split(self, input_data: Union[str, List[str], Dict[str, Any]]) -> Any:
        def _op(text: Any) -> List[str]:
            text = "" if text is None else str(text)
            return self._regex.split(text, maxsplit=self.max_split or 0)

        return self._apply_to_input(input_data, _op)

    def sub(self, input_data: Union[str, List[str], Dict[str, Any]]) -> Any:
        def _op(text: Any) -> str:
            text = "" if text is None else str(text)
            return self._regex.sub(self.replacement, text)

        return self._apply_to_input(input_data, _op)

    def subn(self, input_data: Union[str, List[str], Dict[str, Any]]) -> Any:
        def _op(text: Any) -> Dict[str, Any]:
            text = "" if text is None else str(text)
            result, count = self._regex.subn(self.replacement, text)
            return {"value": result, "count": count}

        return self._apply_to_input(input_data, _op)

