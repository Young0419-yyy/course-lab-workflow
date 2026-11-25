"""Execute ordinary Python notebook cells without installing Jupyter packages."""

import argparse
import ast
import base64
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile


def execute(notebook_path, output_path, cwd):
    notebook = json.loads(notebook_path.read_text(encoding='utf-8-sig'))
    if notebook.get('nbformat') != 4:
        raise ValueError('Only notebook format 4 is supported')
    previous_cwd = Path.cwd()
    os.chdir(cwd)
    try:
        with tempfile.TemporaryDirectory(prefix='course-lab-notebook-') as work:
            os.environ.setdefault('MPLCONFIGDIR', work)
            os.environ['MPLBACKEND'] = 'Agg'
            plt = None
            original_show = None
            if importlib.util.find_spec('matplotlib'):
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                original_show = plt.show
            namespace = {'__name__': '__main__'}
            execution_count = 0
            try:
                for position, cell in enumerate(notebook['cells'], 1):
                    if cell['cell_type'] != 'code':
                        continue
                    execution_count += 1
                    raw_source = cell['source']
                    source = raw_source if isinstance(raw_source, str) else ''.join(raw_source)
                    if any(line.lstrip().startswith(('%', '!')) for line in source.splitlines()):
                        raise ValueError(f'Cell {position}: IPython magics and shell commands are unsupported')
                    filename = f'{notebook_path.name}:cell-{position}'
                    tree = ast.parse(source, filename=filename)
                    outputs = []
                    stdout = io.StringIO()
                    stderr = io.StringIO()

                    def flush_streams():
                        for name, stream in [('stdout', stdout), ('stderr', stderr)]:
                            value = stream.getvalue()
                            if value:
                                outputs.append({'output_type': 'stream', 'name': name, 'text': value})
                                stream.seek(0)
                                stream.truncate(0)

                    def save_figures(*args, **kwargs):
                        flush_streams()
                        for number in list(plt.get_fignums()):
                            figure = plt.figure(number)
                            buffer = io.BytesIO()
                            figure.savefig(buffer, format='png', dpi=130, bbox_inches='tight')
                            outputs.append({'output_type': 'display_data', 'metadata': {},
                                            'data': {'image/png': base64.b64encode(buffer.getvalue()).decode('ascii')}})
                            plt.close(figure)

                    if plt is not None:
                        plt.show = save_figures
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        last = tree.body[-1] if tree.body else None
                        result = None
                        if isinstance(last, ast.Expr):
                            prefix = ast.Module(body=tree.body[:-1], type_ignores=[])
                            exec(compile(prefix, filename, 'exec'), namespace)
                            result = eval(compile(ast.Expression(last.value), filename, 'eval'), namespace)
                        else:
                            exec(compile(tree, filename, 'exec'), namespace)
                        flush_streams()
                        if result is not None:
                            data = {'text/plain': repr(result)}
                            if type(result).__module__.startswith('pandas'):
                                frame = result.to_frame() if hasattr(result, 'to_frame') else result
                                if hasattr(frame, 'to_html'):
                                    data['text/html'] = frame.to_html(border=1)
                            outputs.append({'output_type': 'execute_result', 'execution_count': execution_count,
                                            'metadata': {}, 'data': data})
                        if plt is not None:
                            save_figures()
                        flush_streams()
                    cell['execution_count'] = execution_count
                    cell['outputs'] = outputs
                    print(f'Cell {position}: OK', flush=True)
            finally:
                if plt is not None:
                    plt.show = original_show
                    plt.close('all')
            metadata = notebook.setdefault('metadata', {})
            metadata.setdefault('language_info', {})['name'] = 'python'
            metadata['language_info']['version'] = '.'.join(map(str, sys.version_info[:3]))
            metadata.setdefault('kernelspec', {'display_name': 'Python 3', 'name': 'python3', 'language': 'python'})
            serialized = json.dumps(notebook, ensure_ascii=False, indent=1) + '\n'
            output_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.tmp',
                                                 dir=output_path.parent, delete=False) as target:
                    temporary_path = Path(target.name)
                    target.write(serialized)
                os.replace(temporary_path, output_path)
                temporary_path = None
            finally:
                if temporary_path is not None:
                    temporary_path.unlink(missing_ok=True)
            print(f'Saved {execution_count} executed cells: {output_path}')
    finally:
        os.chdir(previous_cwd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('notebook', type=Path)
    parser.add_argument('--output', type=Path, help='Default: update the source notebook after all cells succeed')
    parser.add_argument('--cwd', type=Path, help='Default: notebook directory')
    args = parser.parse_args()
    source = args.notebook.resolve(strict=True)
    output = args.output.resolve() if args.output else source
    cwd = args.cwd.resolve(strict=True) if args.cwd else source.parent
    execute(source, output, cwd)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    main()
