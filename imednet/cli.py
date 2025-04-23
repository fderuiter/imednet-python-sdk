import typer

app = typer.Typer()


@app.command()
def hello(name: str = "World"):
    """Says hello"""
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
