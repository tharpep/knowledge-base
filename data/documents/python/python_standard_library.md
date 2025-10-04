# The Python Standard Library

## Overview

This library reference manual describes the standard library that is distributed with Python. It also describes some of the optional components that are commonly included in Python distributions.

Python's standard library is very extensive, offering a wide range of facilities as indicated by the long table of contents listed below. The library contains built-in modules (written in C) that provide access to system functionality such as file I/O that would otherwise be inaccessible to Python programmers, as well as modules written in Python that provide standardized solutions for many problems that occur in everyday programming.

Some of these modules are explicitly designed to encourage and enhance the portability of Python programs by abstracting away platform-specifics into platform-neutral APIs.

The Python installers for the Windows platform usually include the entire standard library and often also include many additional components. For Unix-like operating systems Python is normally provided as a collection of packages, so it may be necessary to use the packaging tools provided with the operating system to obtain some or all of the optional components.

## Built-in Functions

The Python interpreter has a number of functions and types built into it that are always available. They are listed here in alphabetical order.

### abs(x)
Return the absolute value of a number. The argument may be an integer, a floating point number, or an object implementing `__abs__()`. If the argument is a complex number, its magnitude is returned.

### all(iterable)
Return `True` if all elements of the iterable are true (or if the iterable is empty). Equivalent to:

```python
def all(iterable):
    for element in iterable:
        if not element:
            return False
    return True
```

### any(iterable)
Return `True` if any element of the iterable is true. If the iterable is empty, return `False`. Equivalent to:

```python
def any(iterable):
    for element in iterable:
        if element:
            return True
    return False
```

### bin(x)
Convert an integer number to a binary string prefixed with "0b". The result is a valid Python expression. If x is not a Python int object, it has to define an `__index__()` method that returns an integer.

### bool([x])
Return a Boolean value, i.e. one of `True` or `False`. x is converted using the standard truth testing procedure. If x is false or omitted, this returns `False`; otherwise it returns `True`. The bool class is a subclass of int.

### bytearray([source[, encoding[, errors]]])
Return a new array of bytes. The bytearray class is a mutable sequence of integers in the range 0 <= x < 256. It has most of the usual methods of mutable sequences, described in Mutable Sequence Types, as well as most methods that the bytes type has.

### bytes([source[, encoding[, errors]]])
Return a new "bytes" object, which is an immutable sequence of integers in the range 0 <= x < 256. bytes is an immutable version of bytearray – it has the same non-mutating methods and the same indexing and slicing behavior.

### callable(object)
Return `True` if the object argument appears callable, `False` if not. If this returns `True`, it is still possible that a call fails, but if it returns `False`, calling object will never succeed. Note that classes are callable (calling a class returns a new instance); instances are callable if their class has a `__call__()` method.

### chr(i)
Return the string representing a character whose Unicode code point is the integer i. For example, `chr(97)` returns the string 'a', while `chr(8364)` returns the string '€'. This is the inverse of `ord()`.

### classmethod(function)
Return a class method for function.

A class method receives the class as implicit first argument, just like an instance method receives the instance. To declare a class method, use this idiom:

```python
class C:
    @classmethod
    def f(cls, arg1, arg2, ...): ...
```

The `@classmethod` form is a function decorator – see the description of function definitions in Function definitions for details.

### compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1)
Compile the source into a code or AST object. Code objects can be executed by `exec()` or `eval()`. source can either be a normal string, a byte string, or an AST object. Refer to the ast module documentation for information on how to work with AST objects.

### complex([real[, imag]])
Return a complex number with the value real + imag*1j or convert a string or number to a complex number. If the first parameter is a string, it will be interpreted as a complex number and the function must be called without a second parameter. The second parameter can never be a string. Each argument may be any numeric type (including complex). If imag is omitted, it defaults to zero and the function serves as a numeric conversion function like `int()` and `float()`. If both arguments are omitted, returns 0j.

### delattr(object, name)
This is a relative of `setattr()`. The arguments are an object and a string. The string must be the name of one of the object's attributes. The function deletes the named attribute, provided the object allows it. For example, `delattr(x, 'foobar')` is equivalent to `del x.foobar`.

### dict(**kwarg)
### dict(mapping, **kwarg)
### dict(iterable, **kwarg)
Create a new dictionary. The dict object is the dictionary class. See dict and Mapping Types — dict for documentation about this class.

### dir([object])
Without arguments, return the list of names in the current local scope. With an argument, attempt to return a list of valid attributes for that object.

### divmod(a, b)
Take two (non complex) numbers as arguments and return a pair of numbers consisting of their quotient and remainder when using integer division. With mixed operand types, the rules for binary arithmetic operators apply. For integers, the result is the same as `(a // b, a % b)`. For floating point numbers the result is `(q, a % b)`, where q is usually `math.floor(a / b)` but may be 1 less than that.

### enumerate(iterable, start=0)
Return an enumerate object. iterable must be a sequence, an iterator, or some other object which supports iteration. The `__next__()` method of the iterator returned by `enumerate()` returns a tuple containing a count (from start which defaults to 0) and the values obtained from iterating over iterable.

### eval(expression, globals=None, locals=None)
The arguments are a string and optional globals and locals. If provided, globals must be a dictionary. If provided, locals can be any mapping object.

The expression argument is parsed and evaluated as a Python expression (technically speaking, a condition list) using the globals and locals dictionaries as global and local namespace.

### exec(object[, globals[, locals]])
This function supports dynamic execution of Python code. object must be either a string or a code object. If it is a string, the string is parsed as a suite of Python statements which is then executed (unless a syntax error occurs).

### filter(function, iterable)
Construct an iterator from those elements of iterable for which function returns true. iterable may be either a sequence, a container which supports iteration, or an iterator. If function is None, the identity function is assumed, that is, all elements of iterable that are false are removed.

### float([x])
Return a floating point number constructed from a number or string x.

If the argument is a string, it should contain a decimal number, optionally preceded by a sign, and optionally embedded in whitespace. The optional sign may be '+' or '-'; a '+' sign has no effect on the value produced.

### format(value[, format_spec])
Convert a value to a "formatted" representation, as controlled by format_spec. The interpretation of format_spec will depend on the type of the value argument, however there is a standard formatting syntax that is used by most built-in types: Format Specification Mini-Language.

### frozenset([iterable])
Return a new frozenset object, optionally with elements taken from iterable. frozenset is a built-in class. See frozenset and Set Types — set, frozenset for documentation about this class.

### getattr(object, name[, default])
Return the value of the named attribute of object. name must be a string. If the string is the name of one of the object's attributes, the result is the value of that attribute. For example, `getattr(x, 'foobar')` is equivalent to `x.foobar`. If the named attribute does not exist, default is returned if provided, otherwise AttributeError is raised.

### globals()
Return a dictionary representing the current global symbol table. This is always the dictionary of the current module (inside a function or method, this is the module where it is defined, not the module from which it is called).

### hasattr(object, name)
The arguments are an object and a string. The result is `True` if the string is the name of one of the object's attributes, `False` if not. (This is implemented by calling `getattr(object, name)` and seeing whether it raises an AttributeError or not.)

### hash(object)
Return the hash value of the object (if it has one). Hash values are integers. They are used to quickly compare dictionary keys during a dictionary lookup. Numeric values that compare equal have the same hash value (even if they are of different types, as is the case for 1 and 1.0).

### help([object])
Invoke the built-in help system. (This function is intended for interactive use.) If no argument is given, the interactive help system starts on the interpreter console. If the argument is a string, then the string is looked up as the name of a module, function, class, method, keyword, or documentation topic, and a help page is printed on the console.

### hex(x)
Convert an integer number to a lowercase hexadecimal string prefixed with "0x". If x is not a Python int object, it has to define an `__index__()` method that returns an integer.

### id(object)
Return the "identity" of an object. This is an integer which is guaranteed to be unique and constant for this object during its lifetime. Two objects with non-overlapping lifetimes may have the same `id()` value.

### input([prompt])
If the prompt argument is present, it is written to standard output without a trailing newline. The function then reads a line from input, converts it to a string (stripping a trailing newline), and returns that.

### int([x])
### int(x, base=10)
Return an integer object constructed from a number or string x, or return 0 if no arguments are given.

### isinstance(object, classinfo)
Return `True` if the object argument is an instance of the classinfo argument, or of a (direct, indirect or virtual) subclass thereof. If object is not an object of the given type, the function always returns `False`.

### issubclass(class, classinfo)
Return `True` if class is a subclass of classinfo (direct, indirect or virtual). A class is considered a subclass of itself. classinfo may be a tuple of class objects, in which case every entry in classinfo will be checked.

### iter(object[, sentinel])
Return an iterator object. The first argument is interpreted very differently depending on the presence of the second argument. Without a second argument, object must be a collection object which supports the iteration protocol (the `__iter__()` method), or it must support the sequence protocol (the `__getitem__()` method with integer arguments starting at 0).

### len(s)
Return the length (the number of items) of an object. The argument may be a sequence (such as a string, bytes, tuple, list or range) or a collection (such as a dictionary, set, or frozen set).

### list([iterable])
Rather than being a function, list is actually a mutable sequence type, as documented in Lists and Sequence Types — list, tuple, range.

### locals()
Update and return a dictionary representing the current local symbol table. Free variables are returned by `locals()` when it is called in function blocks, but not in class blocks.

### map(function, iterable, ...)
Return an iterator that applies function to every item of iterable, yielding the results. If additional iterable arguments are passed, function must take that many arguments and is applied to the items from all iterables in parallel.

### max(iterable, *[, key, default])
### max(arg1, arg2, *args[, key])
Return the largest item in an iterable or the largest of two or more arguments.

### min(iterable, *[, key, default])
### min(arg1, arg2, *args[, key])
Return the smallest item in an iterable or the smallest of two or more arguments.

### next(iterator[, default])
Retrieve the next item from the iterator by calling its `__next__()` method. If default is given, it is returned if the iterator is exhausted, otherwise StopIteration is raised.

### object()
Return a new featureless object. object is a base for all classes. It has the methods that are common to all instances of Python classes.

### oct(x)
Convert an integer number to an octal string prefixed with "0o". The result is a valid Python expression. If x is not a Python int object, it has to define an `__index__()` method that returns an integer.

### open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
Open file and return a corresponding file object. If the file cannot be opened, an OSError is raised.

### ord(c)
Given a string representing one Unicode character, return an integer representing the Unicode code point of that character. For example, `ord('a')` returns the integer 97 and `ord('€')` (Euro sign) returns 8364. This is the inverse of `chr()`.

### pow(base, exp[, mod])
Return base to the power exp; if mod is present, return base to the power exp, modulo mod (computed more efficiently than `pow(base, exp) % mod`). The two-argument form `pow(base, exp)` is equivalent to using the power operator: `base**exp`.

### print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)
Print objects to the text stream file, separated by sep and followed by end. sep, end, file and flush, if present, must be given as keyword arguments.

### property(fget=None, fset=None, fdel=None, doc=None)
Return a property attribute.

### range(stop)
### range(start, stop[, step])
Rather than being a function, range is actually an immutable sequence type, as documented in Ranges and Sequence Types — list, tuple, range.

### repr(object)
Return a string containing a printable representation of an object. For many types, this function makes an attempt to return a string that would yield an object with the same value when passed to `eval()`, otherwise the representation is a string enclosed in angle brackets that contains the name of the type of the object together with additional information often including the name and address of the object.

### reversed(seq)
Return a reverse iterator. seq must be an object which has a `__reversed__()` method or supports the sequence protocol (the `__getitem__()` method with integer arguments starting at 0).

### round(number[, ndigits])
Return number rounded to ndigits precision after the decimal point. If ndigits is omitted or is None, it returns the nearest integer to its input.

### set([iterable])
Return a new set object, optionally with elements taken from iterable. set is a built-in class. See set and Set Types — set, frozenset for documentation about this class.

### setattr(object, name, value)
This is the counterpart of `getattr()`. The arguments are an object, a string and an arbitrary value. The string may name an existing attribute or a new attribute. The function assigns the value to the attribute, provided the object allows it.

### slice(stop)
### slice(start, stop[, step])
Return a slice object representing the set of indices specified by range(start, stop, step). The start and step arguments default to None.

### sorted(iterable, *, key=None, reverse=False)
Return a new sorted list from the items in iterable.

### str(object='')
### str(object=b'', encoding='utf-8', errors='strict')
Return a str version of object.

### sum(iterable, /, start=0)
Sums start and the items of an iterable from left to right and returns the total. The iterable's items are normally numbers, and the start value is not allowed to be a string.

### super([type[, object-or-type]])
Return a proxy object that delegates method calls to a parent or sibling class of type. This is useful for accessing inherited methods that have been overridden in a class.

### tuple([iterable])
Rather than being a function, tuple is actually an immutable sequence type, as documented in Tuples and Sequence Types — list, tuple, range.

### type(object)
### type(name, bases, dict)
With one argument, return the type of an object. The return value is a type object and generally the same object as returned by `object.__class__`.

### vars([object])
Return the `__dict__` attribute for a module, class, instance, or any other object with a `__dict__` attribute.

### zip(*iterables)
Make an iterator that aggregates elements from each of the iterables.

### __import__(name, globals=None, locals=None, fromlist=(), level=0)
This is an advanced function that is not needed in everyday Python programming, unlike `importlib.import_module()`.
