import callbacks  # noqa
from app import app, get_df, server  # noqa
from layouts import layout_server


def main():
    url = (
        "https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188"
        "/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv"
    )
    get_df(url)
    app.layout = layout_server()
    app.run_server()


if __name__ == "__main__":
    main()
