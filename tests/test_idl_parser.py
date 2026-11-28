import pytest
from lark import UnexpectedInput

from polyglue.parser import parse_idl


def test_declarations_and_source_spans():
    source = '''module example;
import domain.User;
import domain.{User, UserStatus};
import domain as model;
import domain.User as DomainUser;
const MaxUsers: int32 = 100;
enum State { Idle = 0, Running = 1 }
flags Permission { Read = 1, Write = 2, ReadWrite = 3 }
variant Response { Success: User; Failure: string; NotFound; }
/// A filter.
record Filter { name: optional<string> = null; limit: int32 = MaxUsers; }
private record Page<T> { items: list<T>; }
async callback Changed(value: User): void;
@platform.apple(ios: "17.0", macos: "14.0")
interface Store {
    async find(id: int64): optional<User>;
    async find(filter: Filter): list<User>;
    async observe(@ownership("retained") listener: Changed): void;
}
public interface ExtendedStore : Store {
    static async create(): ExtendedStore;
    async page(): Page<User>;
}
specialize common.Page<domain.User> as UserPage;
'''
    tree = parse_idl(source)
    assert len(list(tree.find_data("import_group"))) == 1
    assert len(list(tree.find_data("import_alias"))) == 2
    assert len(list(tree.find_data("import_segment"))) == 2
    assert len(list(tree.find_data("method"))) == 5
    assert len(list(tree.find_data("static_modifier"))) == 1
    assert len(list(tree.find_data("variant_case"))) == 3
    assert len(list(tree.find_data("generic_parameters"))) == 1
    assert len(list(tree.find_data("specialization"))) == 1
    field = next(tree.find_data("field"))
    assert field.meta.line == 11
    assert source[field.meta.start_pos:field.meta.end_pos] == "name: optional<string> = null;"
    docs = list(tree.scan_values(lambda node: getattr(node, "type", None) == "DOC"))
    assert [str(doc) for doc in docs] == ["/// A filter."]


def test_literals_preserve_exact_tokens():
    source = r'''module values;
// ignored comment
/* ignored block */
const Max: uint64 = 18446744073709551615;
const Real: float64 = -1.5e+3;
const Text: string = "a\n\u0000\uD83D\uDE00";
const Items: list<int32> = [1, -2, 3];
const Mapping: map<string, bool> = {"a": true, "b": false};
'''
    tree = parse_idl(source)
    assert "18446744073709551615" in [str(node.children[0]) for node in tree.find_data("integer_literal")]
    assert str(next(tree.find_data("float_literal")).children[0]) == "-1.5e+3"
    assert len(list(tree.find_data("map_entry"))) == 2
    assert len(list(tree.find_data("sequence_literal"))) == 1


@pytest.mark.parametrize("source", [
    "record User {}",
    "module a; import b.*;",
    "module a; import b;",
    "module a; record string {}",
    "module a; record Café {}",
    "module a; interface A { async static create(): A; }",
    "module a; interface A : B, C {}",
    "module a; interface A { m<T>(): T; }",
    "module a; variant V { A = 1; }",
    "module a; const N: int32 = 1 + 2;",
    r'module a; const S: string = "\x41";',
    "module a; record A { x: int32;",
])
def test_invalid_syntax(source):
    with pytest.raises(UnexpectedInput):
        parse_idl(source)


@pytest.mark.parametrize("source", [r'module a; const S: string = "\uD800";', 'module a; const S: string = "\ud800";'])
def test_invalid_unicode(source):
    with pytest.raises(UnicodeEncodeError):
        parse_idl(source)


@pytest.mark.parametrize("options", [{"max_bytes": 0}, {"max_depth": 0}])
def test_invalid_limits(options):
    with pytest.raises(ValueError, match="positive"):
        parse_idl("module a;", **options)


def test_utf8_byte_limit():
    source = 'module a; const S: string = "é";'
    assert parse_idl(source, max_bytes=len(source.encode("utf-8")))
    with pytest.raises(ValueError, match="byte limit"):
        parse_idl(source, max_bytes=len(source))
    with pytest.raises(ValueError, match="byte limit"):
        parse_idl(source, max_bytes=1)


def test_nesting_limit_and_unmatched_delimiter():
    source = "module a; record A { value: list<int32>; }"
    assert parse_idl(source, max_depth=2)
    with pytest.raises(ValueError, match="nesting limit"):
        parse_idl(source, max_depth=1)
    with pytest.raises(ValueError, match="Unmatched closing delimiter"):
        parse_idl("module a; }")
