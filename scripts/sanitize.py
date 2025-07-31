def text(text: str) -> str:
    if isinstance(text, str):
        return (
            text.replace('\\', '\\\\')
                .replace('"', "'")
                .replace('\n', '\\n')
                .replace('\t', '\\t')
        )
    return text

def variables(variables: dict) -> dict:
    return {
        key: text(value) if isinstance(value, str) else value
        for key, value in variables.items()
    }