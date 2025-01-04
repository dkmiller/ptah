# FAQ

## What is `pip install ptah`

https://pypi.org/project/ptah/

Not to be confused with
[Ptah project](https://github.com/ptahproject/ptah/)

## square/go-jose: error in cryptographic primitive

If you see this message when visiting the Kubernetes dashboard, follow
[this suggestion](https://stackoverflow.com/a/60264070): explicitly sign out then retry.

## zsh compinit: insecure files

If you encounter this message after [installing completions for Zsh](../reference/cli.md), follow
[this suggestion](https://stackoverflow.com/a/22753363) and run the commands below.

``` bash
compaudit | xargs chmod g-w
compaudit | xargs sudo chown root
```
