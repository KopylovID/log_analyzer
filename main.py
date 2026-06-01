from src.app import Config
import argparse


def main():

    parser = argparse.ArgumentParser(description="Анализатор журналов NGNIX")
    parser.add_argument("-e", "--env-file", type=str, help='Путь к .env файлу', default='.env')
    args = parser.parse_args()

    Config.load(env_file=args.env_file)

if __name__ == "__main__":

    main()
