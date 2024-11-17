# FAQ

## What is `pip install ptah`

https://pypi.org/project/ptah/

Not to be confused with
[Ptah project](https://github.com/ptahproject/ptah/)

## zsh compinit: insecure files

https://stackoverflow.com/a/22753363

``` bash
compaudit | xargs chmod g-w
compaudit | xargs sudo chown root
```
