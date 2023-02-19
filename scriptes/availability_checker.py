from pythonping import ping


def ping_website(args) -> list[int, float]:
    id_, url, _, count, timeout = args  # noqa
    try:
        response = ping(url, size=16, count=count, timeout=timeout)
    except RuntimeError:
        return [id_, timeout * 1000]
    return [id_, response.rtt_avg_ms]
