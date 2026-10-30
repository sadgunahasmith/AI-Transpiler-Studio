import time
import sys
import os
import json

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.compiler.pipeline import CompilerPipeline
from app.ai.corrector import AICorrector

def benchmark_lang(lang, target, num_lines=1000):
    lines = []
    if lang == 'python':
        lines.append('def main():')
        for i in range(num_lines // 2):
            lines.append(f'    x{i} = {i}')
            lines.append(f'    print(x{i})')
        lines.append('if __name__ == "__main__":\n    main()')
    elif lang == 'javascript':
        lines.append('function main() {')
        for i in range(num_lines // 2):
            lines.append(f'    let x{i} = {i};')
            lines.append(f'    console.log(x{i});')
        lines.append('}\nmain();')
    elif lang == 'c':
        lines.append('#include <stdio.h>\nint main() {')
        for i in range(num_lines // 2):
            lines.append(f'    int x{i} = {i};')
            lines.append(f'    printf("%d", x{i});')
        lines.append('    return 0;\n}')
    elif lang == 'java':
        lines.append('public class Main {\n    public static void main(String[] args) {')
        for i in range(num_lines // 2):
            lines.append(f'        int x{i} = {i};')
            lines.append(f'        System.out.println(x{i});')
        lines.append('    }\n}')

    code = '\n'.join(lines)
    p = CompilerPipeline()
    t0 = time.perf_counter()
    res = p.run_full_pipeline(lang, target, code, optimize=True)
    json_bytes = json.dumps(res).encode('utf-8')
    t1 = time.perf_counter()
    print(f"[{lang.upper()} -> {target.upper()}] Lines: {len(lines)}, Time: {t1-t0:.3f}s, Payload: {len(json_bytes)//1024} KB, Success: {res['success']}")

if __name__ == '__main__':
    benchmark_lang('c', 'python', 1000)
    benchmark_lang('python', 'javascript', 1000)
    benchmark_lang('javascript', 'python', 1000)
    benchmark_lang('java', 'python', 1000)
