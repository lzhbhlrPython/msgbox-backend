# msgbox

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