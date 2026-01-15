from graphic.gui import create_app


def main():
    app, main_window = create_app()
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main() 