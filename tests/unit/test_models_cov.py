from __future__ import annotations

import builtins
from collections.abc import Mapping
from typing import Literal
from typing import Union

import pytest
from pydantic import BaseModel, Field
from pydantic import ValidationError

from flext_core import FlextResult
from flext_cli.constants import c
from flext_cli.models import m


def test_cli_command_branches_and_failures(monkeypatch) -> None:
    cmd = m.Cli.CliCommand(name="x", command_line="run")

    with pytest.raises(ValueError):
        cmd.execute([])
    assert cmd.with_status(c.Cli.CommandStatus.RUNNING).status == "running"
    assert cmd.with_args(["a"]).args == ["a"]
    assert cmd.update_status("done").status == "done"

    monkeypatch.setattr(
        m.Cli.CliCommand,
        "model_copy",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("copy boom")),
    )
    assert cmd.start_execution().is_failure
    assert cmd.complete_execution(0).is_failure

    assert m.Cli.CliCommand.validate_command_input(cmd).is_success
    assert m.Cli.CliCommand.validate_command_input({
        "name": "ok",
        "command_line": "x",
    }).is_success


def test_cli_session_and_result_computed_paths(monkeypatch) -> None:
    with pytest.raises(TypeError):
        m.Cli.CliSession.validate_status(123)

    with pytest.raises(ValidationError):
        m.Cli.CliSession(session_id="s", status="invalid")

    session = m.Cli.CliSession(session_id="s", status="active")
    monkeypatch.setattr(
        session,
        "_copy_with_update",
        lambda **_u: (_ for _ in ()).throw(RuntimeError("add boom")),
    )
    assert session.add_command(m.Cli.CliCommand(name="c", command_line="c")).is_failure

    result_ok = m.Cli.CommandResult(command="x", exit_code=0, stdout="")
    result_fail = m.Cli.CommandResult(command="x", exit_code=1, stderr="err")
    assert result_ok.success is True
    assert result_fail.success is False
    assert result_ok.has_output is False
    assert result_fail.has_output is True

    params = m.Cli.CliParamsConfig(verbose=True).params
    assert "verbose" in params


def test_debug_info_masking_and_option_builder_branch() -> None:
    class MappingInfo(Mapping[str, object]):
        def __init__(self, payload: dict[str, object]) -> None:
            self.payload = payload

        def __getitem__(self, key: str) -> object:
            return self.payload[key]

        def __iter__(self):
            return iter(self.payload)

        def __len__(self) -> int:
            return len(self.payload)

    info = m.Cli.DebugInfo.model_construct(
        service="svc",
        level="123",
        message="m",
        system_info=MappingInfo({"api_key": "secret"}),
        config_info=MappingInfo({"token": "abc"}),
    )
    dumped = info.dump_masked()
    assert dumped["system_info"]["api_key"] == "***MASKED***"
    assert dumped["config_info"]["token"] == "***MASKED***"

    empty_dump = m.Cli.DebugInfo.model_construct(
        service="svc",
        level="INFO",
        message="m",
        system_info=0,
        config_info=0,
    ).dump_masked()
    assert empty_dump["system_info"] == {}
    assert empty_dump["config_info"] == {}

    bad_builder = m.Cli.OptionBuilder("x", {"x": "bad"})
    with pytest.raises(TypeError):
        bad_builder.build()


def test_model_command_builder_type_resolution_helpers() -> None:
    builder = m.Cli.ModelCommandBuilder(BaseModel, lambda _m: "ok", None)

    class LiteralAlias:
        __value__ = Literal["a", "b"]

    resolved, origin = builder._resolve_type_alias(LiteralAlias)
    assert resolved is str
    assert origin is Literal

    assert builder._extract_optional_inner_type(str)[1] is False
    assert builder._extract_optional_inner_type(int | str)[0] in {int, str}
    assert builder._extract_optional_inner_type(int | None)[1] is True
    assert builder._extract_optional_inner_type(Union[Literal["x"], int])[0] is str

    assert builder.get_builtin_name(int, {"FlextCliTypes"}) == "FlextCliTypes"
    assert builder.handle_optional_type((int, type(None)), {"int"}) == (
        "str | None",
        int,
    )
    assert builder.handle_union_type(tuple(), {"int"}) == ("str", str)
    assert builder.handle_union_type((Literal["x"],), {"int"}) == (
        "str",
        Literal["x"],
    )
    union_name, union_type = builder.handle_union_type((object(),), {"int"})
    assert union_name == "str"
    assert union_type is not None

    literal_name = builder._get_type_name_for_signature(Literal["x"], {"str"})
    assert literal_name[0] == "str"
    optional_name = builder._get_type_name_for_signature(int | None, {"int"})
    assert optional_name[0] == "str"
    optional_union_name = builder._get_type_name_for_signature(
        Union[int, None], {"int"}
    )
    assert optional_union_name[0] in {"str | None", "FlextCliTypes | None"}
    union_name = builder._get_type_name_for_signature(Union[int, str], {"int"})
    assert union_name[0] in {"str", "FlextCliTypes"}

    class FakeField:
        annotation = None

    field_type, *_ = builder._process_field_metadata("x", FakeField())
    assert field_type is str

    class FakeFieldObj:
        annotation = object
        default = 7
        default_factory = None

        def is_required(self) -> bool:
            return False

    field_type_obj, *_ = builder._process_field_metadata("x", FakeFieldObj())
    assert field_type_obj is str

    annotations = {"flag": bool | None, "name": str}
    real_annotations = builder._create_real_annotations(annotations)
    assert real_annotations["flag"] is bool
    non_bool_union = builder._create_real_annotations({"value": int | str})
    assert non_bool_union["value"] == int | str


def test_model_builder_uncommon_branches(monkeypatch) -> None:
    builder = m.Cli.ModelCommandBuilder(BaseModel, lambda _m: "ok", None)

    monkeypatch.setattr("flext_cli.models.get_args", lambda *_a, **_k: ())
    monkeypatch.setattr("flext_cli.models.get_origin", lambda *_a, **_k: Union)
    assert builder._extract_optional_inner_type(int)[0] is str

    monkeypatch.setattr("flext_cli.models.get_origin", lambda *_a, **_k: Literal)
    assert builder.handle_optional_type((int, type(None)), {"x"}) == (
        "str | None",
        int,
    )

    class ModelObject(BaseModel):
        x: object = None

    field_info = ModelObject.model_fields["x"]
    field_type, *_ = builder._process_field_metadata("x", field_info)
    assert field_type is str


def test_command_wrapper_exec_failure_paths(monkeypatch) -> None:
    class DemoModel(BaseModel):
        name: str

    builder = m.Cli.ModelCommandBuilder(DemoModel, lambda _m: "ok", None)

    original_exec = builtins.exec

    def no_wrapper(_code, scope):
        scope["x"] = 1

    monkeypatch.setattr(builtins, "exec", no_wrapper)
    with pytest.raises(RuntimeError):
        builder._execute_command_wrapper("name: str", {"name": str})

    class NonFunctionWrapper:
        __annotations__: dict[str, object] = {}

    def non_function_wrapper(_code, scope):
        scope["command_wrapper"] = NonFunctionWrapper()

    monkeypatch.setattr(builtins, "exec", non_function_wrapper)
    with pytest.raises(TypeError):
        builder._execute_command_wrapper("name: str", {"name": str})

    monkeypatch.setattr(builtins, "exec", original_exec)


def test_model_converter_error_paths(monkeypatch) -> None:
    class NoValidate:
        __name__ = "NoValidate"

    assert m.Cli.CliModelConverter.cli_args_to_model(NoValidate, {}).is_failure

    class NoFields:
        pass

    assert m.Cli.CliModelConverter.model_to_cli_params(NoFields).is_failure

    class BadFields:
        model_fields = {"x": object()}

    monkeypatch.setattr(
        m.Cli.CliModelConverter,
        "python_type_to_click_type",
        staticmethod(
            lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("click type boom"))
        ),
    )
    assert m.Cli.CliModelConverter.model_to_cli_params(BadFields).is_failure

    class HasattrBoom:
        def __getattribute__(self, _name: str):
            raise RuntimeError("attr boom")

    assert m.Cli.CliModelConverter.model_to_cli_params(HasattrBoom()).is_failure

    monkeypatch.setattr(
        m.Cli.CliModelConverter,
        "model_to_cli_params",
        staticmethod(lambda *_a, **_k: FlextResult.fail("param fail")),
    )
    assert m.Cli.CliModelConverter.model_to_click_options(BaseModel).is_failure


def test_field_conversion_and_type_helpers_paths() -> None:
    class FieldLike:
        annotation = int | None
        default = 1
        description = "d"

    ok = m.Cli.CliModelConverter.field_to_cli_param("x", FieldLike())
    assert ok.is_success

    class BrokenField:
        def __getattr__(self, _name: str):
            raise RuntimeError("broken")

    broken = m.Cli.CliModelConverter.field_to_cli_param("x", BrokenField())
    assert broken.is_failure

    assert m.Cli.CliModelConverter.handle_union_type(int | None) is int
    assert m.Cli.CliModelConverter.handle_union_type((Literal["x"] | None)) is str
    assert m.Cli.CliModelConverter.handle_generic_type(tuple[Literal["x"], int]) is None
    assert m.Cli.CliModelConverter.handle_generic_type(tuple[int, str]) is int

    from types import SimpleNamespace

    assert (
        m.Cli.CliModelConverter.handle_generic_type(
            SimpleNamespace(__origin__=tuple, __args__=())
        )
        is None
    )

    monkeypatcher = pytest.MonkeyPatch()
    monkeypatcher.setattr(
        m.Cli.CliModelConverter,
        "is_simple_type",
        staticmethod(lambda _x: True),
    )
    assert m.Cli.CliModelConverter.pydantic_type_to_python_type(object()) is str
    monkeypatcher.undo()

    assert m.Cli.CliModelConverter.pydantic_type_to_python_type(object()) is str


def test_field_property_merge_and_metadata_error_paths() -> None:
    class DictLike(Mapping[str, object]):
        def __init__(self, data: dict[str, object]) -> None:
            self.data = data

        def __getitem__(self, key: str) -> object:
            return self.data[key]

        def __iter__(self):
            return iter(self.data)

        def __len__(self) -> int:
            return len(self.data)

    class FieldLikeA:
        json_schema_extra = {"x": 1}

    props = {"metadata": DictLike({"a": 1})}
    with pytest.raises(TypeError):
        m.Cli.CliModelConverter.merge_json_schema_extra(props, FieldLikeA())

    class FieldLikeB:
        json_schema_extra = DictLike({"x": 1})

    props2 = {"metadata": {}}
    with pytest.raises(TypeError):
        m.Cli.CliModelConverter.merge_json_schema_extra(props2, FieldLikeB())

    m.Cli.CliModelConverter.merge_json_schema_extra({}, object())

    class FieldLikeC:
        json_schema_extra = None

    m.Cli.CliModelConverter.merge_json_schema_extra({}, FieldLikeC())

    p = {}
    m.Cli.CliModelConverter.merge_field_info_dict(p, {"a": 1, "__dict__": 2})
    assert "a" in p

    class HasDict:
        def __init__(self) -> None:
            self.extra = 1

    m.Cli.CliModelConverter.merge_field_info_dict(p, HasDict())
    assert "extra" in p

    metadata = m.Cli.CliModelConverter.process_metadata_list([{"m": 1}])
    assert metadata["m"] == 1

    p_no_meta = {}
    m.Cli.CliModelConverter.merge_metadata_attr(p_no_meta, object())

    class MetaNone:
        metadata = None

    class MetaDict:
        metadata = {"x": 1}

    m.Cli.CliModelConverter.merge_metadata_attr(p_no_meta, MetaNone())
    m.Cli.CliModelConverter.merge_metadata_attr(p_no_meta, MetaDict())
    assert p_no_meta["metadata"]["x"] == 1

    class BadFieldInfo:
        def __getattr__(self, _name: str):
            raise RuntimeError("extract boom")

    extracted = m.Cli.CliModelConverter.extract_field_properties(
        "x", BadFieldInfo(), {"t": str}
    )
    assert extracted.is_failure


def test_validation_and_decorator_wrapper_paths() -> None:
    assert m.Cli.CliModelConverter.validate_field_schema({
        "python_type": "bad"
    }).is_failure
    assert m.Cli.CliModelConverter.validate_field_schema({
        "python_type": str
    }).is_success

    with pytest.raises(ValueError):
        m.Cli.CliModelConverter.convert_field_value(None)
    assert m.Cli.CliModelConverter.convert_field_value({"a": 1}).is_success
    assert m.Cli.CliModelConverter.convert_field_value(object()).is_success

    dict_value = m.Cli.CliModelConverter.validate_dict_field_data("x", {"x": 1})
    assert dict_value.is_success

    assert m.Cli.CliModelConverter._validate_field_data("x", {}, {"y": 1}).is_failure
    assert m.Cli.CliModelConverter._validate_field_data("x", {}, None).is_failure
    assert m.Cli.CliModelConverter._validate_field_data(
        "x", object(), {"y": 1}
    ).is_failure
    assert m.Cli.CliModelConverter._validate_field_data(
        "x", object(), {"x": 1}
    ).is_success

    class MappingBoom(Mapping[str, object]):
        def __getitem__(self, _key: str) -> object:
            raise RuntimeError("map boom")

        def __iter__(self):
            return iter([])

        def __len__(self) -> int:
            return 0

    assert m.Cli.CliModelConverter._validate_field_data(
        "x", MappingBoom(), None
    ).is_failure
    assert m.Cli.CliModelConverter._process_validators(1) == []

    class ModelA(BaseModel):
        a: int = Field(default=1)

    class ModelB(BaseModel):
        b: str = Field(default="x")

    dec = m.Cli.CliModelDecorators.cli_from_model(ModelA)

    @dec
    def handle_model_a(model: BaseModel):
        return m.Cli.CliCommand.validate_command_input({"name": str(model)})

    assert isinstance(handle_model_a(ModelA(a=1)), str)

    @dec
    def handle_result_success(_model: BaseModel):
        return FlextResult.ok(1)

    assert handle_result_success(ModelA(a=1)) == 1

    @dec
    def handle_result_failure(_model: BaseModel):
        return FlextResult.fail("boom")

    assert handle_result_failure(ModelA(a=1)) == "boom"

    @dec
    def handle_tuple(_model: BaseModel):
        return ("x",)

    assert handle_tuple(ModelA(a=1)) == ("x",)

    @dec
    def handle_object(_model: BaseModel):
        return object()

    assert isinstance(handle_object(ModelA(a=1)), str)

    multi = m.Cli.CliModelDecorators.cli_from_multiple_models(ModelA, ModelB)

    @multi
    def handle_multiple(model_a: ModelA, model_b: ModelB):
        return f"{model_a.a}:{model_b.b}"

    assert handle_multiple(ModelA(a=1), ModelB(b="ok")) == "1:x"


def test_models_remaining_branch_coverage(monkeypatch) -> None:
    # normalize_level non-str path
    built = m.Cli.DebugInfo(service="svc", level=123, message="m")
    assert built.level == "123"

    # dump_masked fallback branches for non-dict-like values
    info = m.Cli.DebugInfo.model_construct(
        service="svc",
        level="INFO",
        message="m",
        system_info=1,
        config_info=2,
    )
    dumped = info.dump_masked()
    assert dumped["system_info"] == {}
    assert dumped["config_info"] == {}

    builder = m.Cli.ModelCommandBuilder(BaseModel, lambda _m: "ok", None)

    # _extract_optional_inner_type branches
    result_type, _is_optional = builder._extract_optional_inner_type(Literal["x"] | int)
    assert result_type is str

    models_module = __import__("flext_cli.models", fromlist=["dummy"])

    # Force branch where non_none_types is empty
    original_get_args = models_module.get_args
    models_module.get_args = lambda _t: ()
    try:
        result_type_empty, _ = builder._extract_optional_inner_type(int | str)
    finally:
        models_module.get_args = original_get_args
    assert result_type_empty is str

    # handle_optional_type Literal branch via patched get_origin
    original_get_origin = models_module.get_origin
    models_module.get_origin = lambda _t: Literal
    try:
        opt_name, _opt_type = builder.handle_optional_type((str, type(None)), {"int"})
    finally:
        models_module.get_origin = original_get_origin
    assert opt_name == "str | None"

    # _get_type_name_for_signature union branch
    models_module.get_origin = lambda _t: models_module.Union
    models_module.get_args = lambda _t: (int, type(None))
    try:
        union_name, _union_type = builder._get_type_name_for_signature(
            int | None, {"int"}
        )
    finally:
        models_module.get_origin = original_get_origin
        models_module.get_args = original_get_args
    assert "None" in union_name

    # _process_field_metadata object annotation branch
    class FieldInfoLike:
        annotation = object
        default = 9
        default_factory = None

        def is_required(self) -> bool:
            return False

    field_type, *_rest = builder._process_field_metadata("x", FieldInfoLike())
    assert field_type is str

    # _create_real_annotations non-bool union branch
    anns = builder._create_real_annotations({"x": int | None})
    assert "x" in anns

    # handle_generic_type fallback branches
    assert m.Cli.CliModelConverter.handle_generic_type(tuple[int, str]) is int
    models_module.get_origin = lambda _t: models_module.Union
    models_module.get_args = lambda _t: (type(None),)
    try:
        assert m.Cli.CliModelConverter.handle_generic_type(object()) is None
    finally:
        models_module.get_origin = original_get_origin
        models_module.get_args = original_get_args

    # pydantic_type_to_python_type fallback branch 2305
    monkeypatch.setattr(
        m.Cli.CliModelConverter,
        "is_simple_type",
        staticmethod(lambda _t: True),
    )
    assert m.Cli.CliModelConverter.pydantic_type_to_python_type(object()) is str

    # merge_json_schema_extra early-return branches
    props = {"metadata": {}}
    m.Cli.CliModelConverter.merge_json_schema_extra(props, object())

    class FieldNone:
        json_schema_extra = None

    m.Cli.CliModelConverter.merge_json_schema_extra(props, FieldNone())

    # convert_field_value fallback branch
    converted = m.Cli.CliModelConverter.convert_field_value(object())
    assert converted.is_success
    assert isinstance(converted.value, str)

    # _validate_field_data branches
    missing = m.Cli.CliModelConverter._validate_field_data("k", object(), {"x": 1})
    assert missing.is_failure
    found = m.Cli.CliModelConverter._validate_field_data("k", object(), {"k": 1})
    assert found.is_success
    no_data = m.Cli.CliModelConverter._validate_field_data("k", object(), None)
    assert no_data.is_failure

    assert m.Cli.CliModelConverter._process_validators(1) == []

    # cli_from_model success r value branch
    class ModelX(BaseModel):
        a: int = 1

    dec = m.Cli.CliModelDecorators.cli_from_model(ModelX)

    @dec
    def handle_success_value(_model: BaseModel):
        return FlextResult.ok(1)

    assert handle_success_value(ModelX(a=1)) == 1
