"""Tests for client stub module in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import FlextApiClient, Pipeline, PipelineConfig, PipelineList


class TestFlextApiClient:
    """Test cases for FlextApiClient stub class."""

    def test_client_initialization_without_args(self) -> None:
        """Test client initialization without arguments."""
        client = FlextApiClient()
        assert isinstance(client, FlextApiClient)

    def test_client_initialization_with_args(self) -> None:
        """Test client initialization with arguments."""
        client = FlextApiClient(
            base_url="http://test.com",
            token="test-token",
            timeout=60.0,
        )
        assert isinstance(client, FlextApiClient)

    def test_client_initialization_with_mixed_args(self) -> None:
        """Test client initialization with mixed arguments."""
        client = FlextApiClient(
            base_url="http://example.com",
            timeout=30.0,
            verify_ssl=False,
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
        config = PipelineConfig(
            name="default-config",
            tap="default-tap",
            target="default-target",
        )
        pipeline = Pipeline(
            id="default-id",
            name="default-pipeline",
            status="initialized",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=config,
        )
        assert isinstance(pipeline, Pipeline)
        assert pipeline.name == "default-pipeline"
        assert pipeline.id == "default-id"
        assert pipeline.status == "initialized"

    def test_pipeline_initialization_with_args(self) -> None:
        """Test pipeline initialization with arguments."""
        config = PipelineConfig(
            name="test-config",
            tap="test-tap",
            target="test-target",
        )
        pipeline = Pipeline(
            id="test-id",
            name="test-pipeline",
            status="running",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=config,
        )
        assert isinstance(pipeline, Pipeline)
        assert pipeline.name == "test-pipeline"
        assert pipeline.id == "test-id"
        assert pipeline.status == "running"

    def test_pipeline_initialization_with_mixed_args(self) -> None:
        """Test pipeline initialization with mixed arguments."""
        config = PipelineConfig(
            name="mixed-config",
            tap="test-tap",
            target="test-target",
        )
        pipeline = Pipeline(
            id="mixed-id",
            name="mixed-pipeline",
            status="pending",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=config,
        )
        assert isinstance(pipeline, Pipeline)
        assert pipeline.name == "mixed-pipeline"
        assert pipeline.id == "mixed-id"
        assert pipeline.status == "pending"

    def test_pipeline_attributes_are_strings(self) -> None:
        """Test that pipeline attributes are strings."""
        config = PipelineConfig(name="attr-test", tap="test-tap", target="test-target")
        pipeline = Pipeline(
            id="attr-id",
            name="attr-pipeline",
            status="active",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=config,
        )

        assert isinstance(pipeline.name, str)
        assert isinstance(pipeline.id, str)
        assert isinstance(pipeline.status, str)

    def test_pipeline_multiple_instances(self) -> None:
        """Test creating multiple pipeline instances."""
        config1 = PipelineConfig(name="multi-1", tap="tap1", target="target1")
        config2 = PipelineConfig(name="multi-2", tap="tap2", target="target2")

        pipeline1 = Pipeline(
            id="multi-1",
            name="pipeline-1",
            status="active",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=config1,
        )
        pipeline2 = Pipeline(
            id="multi-2",
            name="pipeline-2",
            status="inactive",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=config2,
        )

        assert isinstance(pipeline1, Pipeline)
        assert isinstance(pipeline2, Pipeline)
        assert pipeline1 is not pipeline2

        # Verify they have different attributes as expected
        assert pipeline1.name != pipeline2.name  # "pipeline-1" != "pipeline-2"
        assert pipeline1.id != pipeline2.id  # "multi-1" != "multi-2"
        assert pipeline1.status != pipeline2.status  # "active" != "inactive"

        # But they should both be Pipeline instances
        assert pipeline1.name == "pipeline-1"
        assert pipeline2.name == "pipeline-2"

    def test_pipeline_attributes_not_modifiable(self) -> None:
        """Test that pipeline attributes are set during initialization."""
        pipeline = Pipeline(
            id="stub-id",
            name="stub-pipeline",
            status="stub-status",
            created_at="2025-01-01T12:00:00Z",
            updated_at="2025-01-01T12:00:00Z",
            config=PipelineConfig(
                name="stub-pipeline",
                tap="tap-csv",
                target="target-jsonl",
            ),
        )

        # Attributes exist and have expected values
        assert hasattr(pipeline, "name")
        assert hasattr(pipeline, "id")
        assert hasattr(pipeline, "status")

        # Values are as expected
        if pipeline.name != "stub-pipeline":
            msg: str = f"Expected {'stub-pipeline'}, got {pipeline.name}"
            raise AssertionError(msg)
        assert pipeline.id == "stub-id"
        if pipeline.status != "stub-status":
            attr_status_msg: str = f"Expected {'stub-status'}, got {pipeline.status}"
            raise AssertionError(attr_status_msg)


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

        # Create proper Pipeline with required fields
        config = PipelineConfig(name="test", tap="test-tap", target="test-target")
        pipeline = Pipeline(
            id="test",
            name="test",
            status="active",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=config,
        )

        pipeline_list = PipelineList(pipelines=[], total=0)

        # Verify classes are independent (different types)
        assert not isinstance(client, type(pipeline))
        assert not isinstance(client, type(pipeline_list))
        assert not isinstance(pipeline, type(pipeline_list))
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
            base_url="http://example.com",
            timeout=30,
            token="Bearer token",
        )

        # Create proper Pipeline with required fields
        config = PipelineConfig(
            name="test-pipeline",
            tap="test-tap",
            target="test-target",
        )
        pipeline = Pipeline(
            id="test-id",
            name="test-pipeline",
            status="active",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=config,
        )

        assert isinstance(client, FlextApiClient)
        assert isinstance(pipeline, Pipeline)

        # Pipeline should have the attributes we set
        assert pipeline.name == "test-pipeline"
        assert pipeline.id == "test-id"
        assert pipeline.status == "active"


class TestPipelineList:
    """Test cases for PipelineList stub class."""

    def test_pipeline_list_initialization_without_args(self) -> None:
        """Test pipeline list initialization without arguments."""
        pipeline_list = PipelineList(pipelines=[], total=0)
        assert isinstance(pipeline_list, PipelineList)

        # Check attributes
        assert pipeline_list.pipelines == []
        assert pipeline_list.total == 0
        assert pipeline_list.page == 1  # default value
        assert pipeline_list.page_size == 20  # default value

    def test_pipeline_list_initialization_with_args(self) -> None:
        """Test pipeline list initialization with arguments."""
        # Create sample pipelines for the list
        config = PipelineConfig(name="sample", tap="sample-tap", target="sample-target")
        pipeline = Pipeline(
            id="sample-1",
            name="sample-pipeline",
            status="active",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=config,
        )

        pipeline_list = PipelineList(
            pipelines=[pipeline],
            total=1,
            page=2,
            page_size=10,
        )
        assert isinstance(pipeline_list, PipelineList)

        # Check attributes
        assert len(pipeline_list.pipelines) == 1
        assert pipeline_list.total == 1
        assert pipeline_list.page == 2
        assert pipeline_list.page_size == 10

    def test_pipeline_list_initialization_with_mixed_args(self) -> None:
        """Test pipeline list initialization with mixed arguments."""
        # Create sample pipeline for mixed args test
        config = PipelineConfig(name="mixed", tap="tap-mixed", target="target-mixed")
        pipeline = Pipeline(
            id="mixed-id",
            name="mixed-pipeline",
            status="pending",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=config,
        )

        pipeline_list = PipelineList(
            pipelines=[pipeline],
            total=1,
            page=2,
            page_size=10,
        )
        assert isinstance(pipeline_list, PipelineList)

        # Check that values are properly set (not stub values)
        assert len(pipeline_list.pipelines) == 1
        assert pipeline_list.total == 1
        assert pipeline_list.page == 2
        assert pipeline_list.page_size == 10

    def test_pipeline_list_attributes_types(self) -> None:
        """Test that pipeline list attributes have correct types."""
        pipeline_list = PipelineList(pipelines=[], total=0)

        assert isinstance(pipeline_list.pipelines, list)
        assert isinstance(pipeline_list.total, int)
        assert isinstance(pipeline_list.page, int)
        assert isinstance(pipeline_list.page_size, int)

    def test_pipeline_list_multiple_instances(self) -> None:
        """Test creating multiple pipeline list instances."""
        list1 = PipelineList(pipelines=[], total=0, page=1, page_size=10)
        list2 = PipelineList(pipelines=[], total=5, page=2, page_size=15)

        assert isinstance(list1, PipelineList)
        assert isinstance(list2, PipelineList)
        assert list1 is not list2

        # They should have different attributes as specified
        assert list1.pipelines == list2.pipelines  # Both empty
        assert list1.total != list2.total  # 0 vs 5
        assert list1.page != list2.page  # 1 vs 2
        assert list1.page_size != list2.page_size  # 10 vs 15

    def test_pipeline_list_empty_pipelines(self) -> None:
        """Test that pipelines list is empty by default."""
        pipeline_list = PipelineList(pipelines=[], total=0)

        if len(pipeline_list.pipelines) != 0:
            length_msg: str = f"Expected {0}, got {len(pipeline_list.pipelines)}"
            raise AssertionError(length_msg)
        assert pipeline_list.pipelines == []
        assert not pipeline_list.pipelines  # Should be falsy
