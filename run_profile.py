from time import perf_counter

from app.models import seed, query_post_v3, query_post_v2


def run():
    start = perf_counter()
    # posts = query_post_v2(1)
    posts = query_post_v3(1)

    end = perf_counter()
    print(f"took: {(end - start)*1000}ms")


if __name__ == "__main__":
    run()
