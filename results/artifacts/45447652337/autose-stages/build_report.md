### compile: ok
```

```
### import: ok
```
4.9.0

```
### mypy: FAILED
```
tinydb/table.py:202: error: Argument 1 to "_update_table" of "Table" has incompatible type "Callable[[dict[int, Mapping[Any, Any]]], list[None]]"; expected "Callable[[dict[int, Mapping[Any, Any]]], None]"  [arg-type]
tinydb/table.py:203: error: "__setitem__" of "dict" does not return a value (it only ever returns None)  [func-returns-value]
tinydb/table.py:244: error: Implicit return in function which does not return  [empty-body]
tinydb/table.py:246: error: Name "get" already defined on line 244  [no-redef]
tinydb/table.py:363: error: Unexpected keyword argument "doc_id" for "get" of "Table"  [call-arg]
tinydb/table.py:367: error: Too many arguments for "get" of "Table"  [call-arg]
Found 6 errors in 1 file (checked 10 source files)

```