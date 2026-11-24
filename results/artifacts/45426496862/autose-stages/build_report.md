### compile: ok
```

```
### import: ok
```
4.9.0

```
### mypy: FAILED
```
tinydb/table.py:475: error: Implicit return in function which does not return  [empty-body]
tinydb/table.py:477: error: Name "get" already defined on line 475  [no-redef]
tinydb/table.py:594: error: Unexpected keyword argument "doc_id" for "get" of "Table"  [call-arg]
tinydb/table.py:598: error: Too many arguments for "get" of "Table"  [call-arg]
Found 4 errors in 1 file (checked 10 source files)

```