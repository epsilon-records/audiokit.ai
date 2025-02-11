import ast
from pathlib import Path
from typing import List

from pydantic import BaseModel


class AudioFunction(BaseModel):
    name: str
    file_path: str
    line_number: int
    parameters: List[str]
    docstring: str | None
    calls_audio_kit: bool


class CodeAnalysisRequest(BaseModel):
    repo_path: str
    file_patterns: List[str] = ["*.py"]


class CodeAnalysisResponse(BaseModel):
    audio_functions: List[AudioFunction]
    total_audio_calls: int
    files_analyzed: int


class AudioKitAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.audio_functions = []
        self.current_file = ""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Check if function uses AudioKit
        uses_audio_kit = self._check_for_audio_kit(node)

        if uses_audio_kit:
            self.audio_functions.append(
                AudioFunction(
                    name=node.name,
                    file_path=self.current_file,
                    line_number=node.lineno,
                    parameters=[arg.arg for arg in node.args.args],
                    docstring=ast.get_docstring(node),
                    calls_audio_kit=True,
                ),
            )
        self.generic_visit(node)

    def _check_for_audio_kit(self, node: ast.FunctionDef) -> bool:
        """Check if function uses AudioKit related calls"""
        audio_keywords = {
            "AudioKit",
            "playSound",
            "processAudio",
            "AudioEngine",
            "AudioBuffer",
            "AudioFile",
            "AudioPlayer",
        }

        code = ast.dump(node)
        return any(keyword in code for keyword in audio_keywords)


async def analyze_code(request: CodeAnalysisRequest) -> CodeAnalysisResponse:
    """Analyze repository for audio-related code patterns"""
    repo_path = Path(request.repo_path)
    analyzer = AudioKitAnalyzer()
    files_analyzed = 0

    for pattern in request.file_patterns:
        for file_path in repo_path.rglob(pattern):
            try:
                with open(file_path) as f:
                    code = f.read()

                analyzer.current_file = str(file_path)
                tree = ast.parse(code)
                analyzer.visit(tree)
                files_analyzed += 1

            except (SyntaxError, UnicodeDecodeError):
                continue

    return CodeAnalysisResponse(
        audio_functions=analyzer.audio_functions,
        total_audio_calls=len(analyzer.audio_functions),
        files_analyzed=files_analyzed,
    )
