from lib.files import parse_manage_args


def test_arguments_true():
    args = parse_manage_args(["_", "f", "l", "q"])

    assert args.force
    assert args.log
    assert args.quick


def test_arguments_false():
    args = parse_manage_args(["_"])

    assert not args.force
    assert not args.log
    assert not args.quick
