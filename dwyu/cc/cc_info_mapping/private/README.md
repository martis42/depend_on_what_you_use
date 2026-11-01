# Design Decisions

## Multi step approach for filtering

We choose this multi step approach for filtering after all information was gathered by the aspect due to technical limitations.
An aspect can receive user defined parameters via aspect attributes, but those only support 'bool', 'int' an 'string' values
'string_list' is not supported and we don't want the extra complexity of (de)serializing list information through a single string.
