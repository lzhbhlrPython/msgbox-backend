# msgbox
![msgbox](https://socialify.git.ci/lzhbhlrPython/msgbox/image?description=1&font=KoHo&forks=1&issues=1&name=1&owner=1&pattern=Charlie%20Brown&pulls=1&stargazers=1&theme=Light)

[online demo](https://msgbox.nomoneyer.top)

你需要创建一个`api/config.py`在使用之前.

```python
config = {
    "redis": {
        "ip": "redis_server",
        "port": 'port:int',
        "password": "your_password_of_redis",
        "db": 'db_num:int'
    }, "control": {
        "clear_db": "clear_db_password",
        "find_all_data": "find_all_password",
        "ban_ip": "unban_ip_pwd",
    }, "ip_blacklist": [
        "ip banned forever "
    ]
}
```

## Develop

```bash
vercel dev
```

## Preview

```bash
vercel
```

## Production

```bash
vercel --prod
```

## Msgbox Team全体成员

@lzhbhlrpython, @calvinweb, @3swordman