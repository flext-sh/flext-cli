"""Tests for client stub module in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.client import FlextApiClient, Pipeline, PipelineList


class TestFlextApiClient:
    """Test cases for FlextApiClient stub class."""

    def test_client_initialization_without_args(self) -> None:
        """Test client initialization without arguments."""
        client = FlextApiClient()
        assert isinstance(client, FlextApiClient)

    def test_client_initialization_with_args(self) -> None:
        """Test client initialization with arguments."""
        client = FlextApiClient("arg1", "arg2", key1="value1", key2="value2")
        assert isinstance(client, FlextApiClient)

    def test_client_initialization_with_mixed_args(self) -> None:
        """Test client initialization with mixed arguments."""
        client = FlextApiClient(
            "positional_arg",
            timeout=30,
            api_url="http://example.com",
            debug=True,
        )
        assert isinstance(client, FlextApiClient)

    def test_client_initialization_empty_kwargs(self) -> None:
        """Test client initialization with empty kwargs."""
        client = FlextApiClient()
        assert isinstance(client, FlextApiClient)

    def test_client_multiple_instances(self) -> None:
        """Test creating multiple client instances."""
        client1 = FlextApiClient("arg1")
        client2 = FlextApiClient("arg2")

        assert isinstance(client1, FlextApiClient)
        assert isinstance(client2, FlextApiClient)
        assert client1 is not client2


class TestPipeline:
    """Test cases for Pipeline stub class."""

    def test_pipeline_initialization_without_args(self) -> None:
        """Test pipeline initialization without arguments."""
        pipeline = Pipeline()
        assert isinstance(pipeline, Pipeline)

        # Check default stub attributes
        if pipeline.name != "stub-pipeline":
            msg = f"Expected {"stub-pipeline"}, got {pipeline.name}"
            raise AssertionError(msg)
        assert pipeline.id == "stub-id"
        if pipeline.status != "stub-status":
            msg = f"Expected {"stub-status"}, got {pipeline.status}"
            raise AssertionError(msg)

    def test_pipeline_initialization_with_args(self) -> None:
        """Test pipeline initialization with arguments."""
        pipeline = Pipeline("arg1", "arg2", key1="value1", key2="value2")
        assert isinstance(pipeline, Pipeline)

        # Stub attributes should still be defaults
        if pipeline.name != "stub-pipeline":
            msg = f"Expected {"stub-pipeline"}, got {pipeline.name}"
            raise AssertionError(msg)
        assert pipeline.id == "stub-id"
        if pipeline.status != "stub-status":
            msg = f"Expected {"stub-status"}, got {pipeline.status}"
            raise AssertionError(msg)

    def test_pipeline_initialization_with_mixed_args(self) -> None:
        """Test pipeline initialization with mixed arguments."""
        pipeline = Pipeline(
            "positional_arg",
            timeout=30,
            name="custom-pipeline",
            debug=True,
        )
        assert isinstance(pipeline, Pipeline)

        # Stub attributes should still be defaults regardless of kwargs
        if pipeline.name != "stub-pipeline":
            msg = f"Expected {"stub-pipeline"}, got {pipeline.name}"
            raise AssertionError(msg)
        assert pipeline.id == "stub-id"
        if pipeline.status != "stub-status":
            msg = f"Expected {"stub-status"}, got {pipeline.status}"
            raise AssertionError(msg)

    def test_pipeline_attributes_are_strings(self) -> None:
        """Test that pipeline attributes are strings."""
        pipeline = Pipeline()

        assert isinstance(pipeline.name, str)
        assert isinstance(pipeline.id, str)
        assert isinstance(pipeline.status, str)

    def test_pipeline_multiple_instances(self) -> None:
        """Test creating multiple pipeline instances."""
        pipeline1 = Pipeline("arg1")
        pipeline2 = Pipeline("arg2")

        assert isinstance(pipeline1, Pipeline)
        assert isinstance(pipeline2, Pipeline)
        assert pipeline1 is not pipeline2

        # Both should have same stub attributes
        if pipeline1.name != pipeline2.name:
            msg = f"Expected {pipeline2.name}, got {pipeline1.name}"
            raise AssertionError(msg)
        assert pipeline1.id == pipeline2.id
        if pipeline1.status != pipeline2.status:
            msg = f"Expected {pipeline2.status}, got {pipeline1.status}"
            raise AssertionError(msg)

    def test_pipeline_attributes_not_modifiable(self) -> None:
        """Test that pipeline attributes are set during initialization."""
        pipeline = Pipeline()

        # Attributes exist and have expected values
        assert hasattr(pipeline, "name")
        assert hasattr(pipeline, "id")
        assert hasattr(pipeline, "status")

        # Values are as expected
        if pipeline.name != "stub-pipeline":
            msg = f"Expected {"stub-pipeline"}, got {pipeline.name}"
            raise AssertionError(msg)
        assert pipeline.id == "stub-id"
        if pipeline.status != "stub-status":
            msg = f"Expected {"stub-status"}, got {pipeline.status}"
            raise AssertionError(msg)


class TestClientModule:
    """Test cases for client module functionality."""

    def test_module_imports(self) -> None:
        """Test that all expected classes can be imported."""
        assert FlextApiClient is not None
        assert Pipeline is not None
        assert PipelineList is not None
        assert callable(FlextApiClient)
        assert callable(Pipeline)
        assert callable(PipelineList)

    def test_classes_are_independent(self) -> None:
        """Test that the classes are independent."""
        client = FlextApiClient()
        pipeline = Pipeline()
        pipeline_list = PipelineList()

        assert type(client) is not type(pipeline)
        assert type(client) is not type(pipeline_list)
        assert type(pipeline) is not type(pipeline_list)
        assert isinstance(client, FlextApiClient)
        assert isinstance(pipeline, Pipeline)
        assert isinstance(pipeline_list, PipelineList)
        assert not isinstance(client, Pipeline)
        assert not isinstance(pipeline, FlextApiClient)
        assert not isinstance(client, PipelineList)
        assert not isinstance(pipeline_list, FlextApiClient)

    def test_backward_compatibility_interface(self) -> None:
        """Test that the stub maintains expected interface."""
        # Should be able to create instances without errors
        client = FlextApiClient(
            url="http://example.com",
            timeout=30,
            headers={"Authorization": "Bearer token"},
        )

        pipeline = Pipeline(
            name="test-pipeline",
            config={"key": "value"},
            steps=["step1", "step2"],
        )

        assert isinstance(client, FlextApiClient)
        assert isinstance(pipeline, Pipeline)

        # Pipeline should still have stub attributes
        if pipeline.name != "stub-pipeline":
            msg = f"Expected {"stub-pipeline"}, got {pipeline.name}"
            raise AssertionError(msg)
        assert pipeline.id == "stub-id"
        if pipeline.status != "stub-status":
            msg = f"Expected {"stub-status"}, got {pipeline.status}"
            raise AssertionError(msg)


class TestPipelineList:
    """Test cases for PipelineList stub class."""

    def test_pipeline_list_initialization_without_args(self) -> None:
        """Test pipeline list initialization without arguments."""
        pipeline_list = PipelineList()
        assert isinstance(pipeline_list, PipelineList)

        # Check default stub attributes
        if pipeline_list.pipelines != []:
            msg = f"Expected {[]}, got {pipeline_list.pipelines}"
            raise AssertionError(msg)
        assert pipeline_list.total == 0
        if pipeline_list.page != 1:
            msg = f"Expected {1}, got {pipeline_list.page}"
            raise AssertionError(msg)
        assert pipeline_list.page_size == 10

    def test_pipeline_list_initialization_with_args(self) -> None:
        """Test pipeline list initialization with arguments."""
        pipeline_list = PipelineList("arg1", "arg2", key1="value1", key2="value2")
        assert isinstance(pipeline_list, PipelineList)

        # Stub attributes should still be defaults
        if pipeline_list.pipelines != []:
            msg = f"Expected {[]}, got {pipeline_list.pipelines}"
            raise AssertionError(msg)
        assert pipeline_list.total == 0
        if pipeline_list.page != 1:
            msg = f"Expected {1}, got {pipeline_list.page}"
            raise AssertionError(msg)
        assert pipeline_list.page_size == 10

    def test_pipeline_list_initialization_with_mixed_args(self) -> None:
        """Test pipeline list initialization with mixed arguments."""
        pipeline_list = PipelineList(
            "positional_arg",
            timeout=30,
            pipelines=["custom"],
            debug=True,
        )
        assert isinstance(pipeline_list, PipelineList)

        # Stub attributes should still be defaults regardless of kwargs
        if pipeline_list.pipelines != []:
            msg = f"Expected {[]}, got {pipeline_list.pipelines}"
            raise AssertionError(msg)
        assert pipeline_list.total == 0
        if pipeline_list.page != 1:
            msg = f"Expected {1}, got {pipeline_list.page}"
            raise AssertionError(msg)
        assert pipeline_list.page_size == 10

    def test_pipeline_list_attributes_types(self) -> None:
        """Test that pipeline list attributes have correct types."""
        pipeline_list = PipelineList()

        assert isinstance(pipeline_list.pipelines, list)
        assert isinstance(pipeline_list.total, int)
        assert isinstance(pipeline_list.page, int)
        assert isinstance(pipeline_list.page_size, int)

    def test_pipeline_list_multiple_instances(self) -> None:
        """Test creating multiple pipeline list instances."""
        list1 = PipelineList("arg1")
        list2 = PipelineList("arg2")

        assert isinstance(list1, PipelineList)
        assert isinstance(list2, PipelineList)
        assert list1 is not list2

        # Both should have same stub attributes
        if list1.pipelines != list2.pipelines:
            msg = f"Expected {list2.pipelines}, got {list1.pipelines}"
            raise AssertionError(msg)
        assert list1.total == list2.total
        if list1.page != list2.page:
            msg = f"Expected {list2.page}, got {list1.page}"
            raise AssertionError(msg)
        assert list1.page_size == list2.page_size

    def test_pipeline_list_empty_pipelines(self) -> None:
        """Test that pipelines list is empty by default."""
        pipeline_list = PipelineList()

        if len(pipeline_list.pipelines) != 0:

            msg = f"Expected {0}, got {len(pipeline_list.pipelines)}"
            raise AssertionError(msg)
        assert pipeline_list.pipelines == []
        assert not pipeline_list.pipelines  # Should be falsy
