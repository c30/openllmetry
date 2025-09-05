import pytest
from traceloop.sdk.decorators import task, workflow, agent, tool


def test_task_with_custom_attributes(exporter):
    """Test that custom attributes are set on task spans"""
    custom_attributes = {
        "my.custom.attribute": "custom_value",
        "numeric.attribute": 42,
        "boolean.attribute": True,
    }

    @task(name="test_task", attributes=custom_attributes)
    def test_task():
        return "result"

    test_task()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    task_span = spans[0]
    assert task_span.name == "test_task.task"

    # Verify custom attributes are set
    assert task_span.attributes.get("my.custom.attribute") == "custom_value"
    assert task_span.attributes.get("numeric.attribute") == 42
    assert task_span.attributes.get("boolean.attribute") is True

    # Verify standard attributes are still set
    assert task_span.attributes.get("traceloop.span.kind") == "task"
    assert task_span.attributes.get("traceloop.entity.name") == "test_task"


def test_workflow_with_custom_attributes(exporter):
    """Test that custom attributes are set on workflow spans"""
    custom_attributes = {
        "workflow.type": "test",
        "workflow.priority": 1,
    }

    @workflow(name="test_workflow", attributes=custom_attributes)
    def test_workflow():
        return "workflow_result"

    test_workflow()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    workflow_span = spans[0]
    assert workflow_span.name == "test_workflow.workflow"

    # Verify custom attributes are set
    assert workflow_span.attributes.get("workflow.type") == "test"
    assert workflow_span.attributes.get("workflow.priority") == 1

    # Verify standard attributes are still set
    assert workflow_span.attributes.get("traceloop.span.kind") == "workflow"
    assert workflow_span.attributes.get("traceloop.entity.name") == "test_workflow"


def test_agent_with_custom_attributes(exporter):
    """Test that custom attributes are set on agent spans"""
    custom_attributes = {
        "agent.model": "gpt-4",
        "agent.temperature": 0.7,
    }

    @agent(name="test_agent", attributes=custom_attributes)
    def test_agent():
        return "agent_result"

    test_agent()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    agent_span = spans[0]
    assert agent_span.name == "test_agent.agent"

    # Verify custom attributes are set
    assert agent_span.attributes.get("agent.model") == "gpt-4"
    assert agent_span.attributes.get("agent.temperature") == 0.7

    # Verify standard attributes are still set
    assert agent_span.attributes.get("traceloop.span.kind") == "agent"
    assert agent_span.attributes.get("traceloop.entity.name") == "test_agent"


def test_tool_with_custom_attributes(exporter):
    """Test that custom attributes are set on tool spans"""
    custom_attributes = {
        "tool.name": "calculator",
        "tool.version": "1.2.3",
    }

    @tool(name="test_tool", attributes=custom_attributes)
    def test_tool():
        return "tool_result"

    test_tool()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    tool_span = spans[0]
    assert tool_span.name == "test_tool.tool"

    # Verify custom attributes are set
    assert tool_span.attributes.get("tool.name") == "calculator"
    assert tool_span.attributes.get("tool.version") == "1.2.3"

    # Verify standard attributes are still set
    assert tool_span.attributes.get("traceloop.span.kind") == "tool"
    assert tool_span.attributes.get("traceloop.entity.name") == "test_tool"


def test_attributes_with_none_values(exporter):
    """Test that None values in attributes are ignored"""
    custom_attributes = {
        "valid.attribute": "value",
        "none.attribute": None,
        "empty.string": "",
    }

    @task(name="test_task_none", attributes=custom_attributes)
    def test_task():
        return "result"

    test_task()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    task_span = spans[0]

    # Verify valid attribute is set
    assert task_span.attributes.get("valid.attribute") == "value"

    # Verify empty string is set (empty strings are valid)
    assert task_span.attributes.get("empty.string") == ""

    # Verify None attribute is not set
    assert "none.attribute" not in task_span.attributes


def test_no_attributes_parameter(exporter):
    """Test that decorators work normally without attributes parameter"""
    @task(name="test_task_no_attrs")
    def test_task():
        return "result"

    test_task()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    task_span = spans[0]
    assert task_span.name == "test_task_no_attrs.task"

    # Verify standard attributes are still set
    assert task_span.attributes.get("traceloop.span.kind") == "task"
    assert task_span.attributes.get("traceloop.entity.name") == "test_task_no_attrs"


def test_empty_attributes_dict(exporter):
    """Test that empty attributes dict doesn't cause issues"""
    @task(name="test_task_empty_attrs", attributes={})
    def test_task():
        return "result"

    test_task()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    task_span = spans[0]
    assert task_span.name == "test_task_empty_attrs.task"

    # Verify standard attributes are still set
    assert task_span.attributes.get("traceloop.span.kind") == "task"
    assert task_span.attributes.get("traceloop.entity.name") == "test_task_empty_attrs"


@pytest.mark.asyncio
async def test_async_task_with_custom_attributes(exporter):
    """Test that custom attributes work with async tasks"""
    custom_attributes = {
        "async.task": True,
        "execution.mode": "async",
    }

    @task(name="async_test_task", attributes=custom_attributes)
    async def async_test_task():
        return "async_result"

    await async_test_task()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    task_span = spans[0]
    assert task_span.name == "async_test_task.task"

    # Verify custom attributes are set
    assert task_span.attributes.get("async.task") is True
    assert task_span.attributes.get("execution.mode") == "async"

    # Verify standard attributes are still set
    assert task_span.attributes.get("traceloop.span.kind") == "task"
    assert task_span.attributes.get("traceloop.entity.name") == "async_test_task"


def test_class_decorator_with_attributes(exporter):
    """Test that custom attributes work with class decorators"""
    custom_attributes = {
        "class.type": "service",
        "class.module": "test",
    }

    @task(name="test_service", method_name="process", attributes=custom_attributes)
    class TestService:
        def process(self):
            return "processed"

    service = TestService()
    service.process()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    task_span = spans[0]
    assert task_span.name == "test_service.task"

    # Verify custom attributes are set
    assert task_span.attributes.get("class.type") == "service"
    assert task_span.attributes.get("class.module") == "test"

    # Verify standard attributes are still set
    assert task_span.attributes.get("traceloop.span.kind") == "task"
    assert task_span.attributes.get("traceloop.entity.name") == "test_service"
