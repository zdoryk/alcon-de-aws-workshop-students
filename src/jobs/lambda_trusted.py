from src.utils.aws_manager import AwsManager


def main(handler=None, context=None):
    print('Starting lambda_trusted job')
    return {"status": "OK"}


if __name__ == '__main__':
    main()
