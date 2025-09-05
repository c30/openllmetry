#!/usr/bin/env python3
"""
Integration test demonstrating custom attributes functionality.
Uses the test environment to verify spans with custom attributes.
"""

import pytest
from traceloop.sdk.decorators import task, workflow, agent, tool


def test_full_attributes_integration(exporter):
    """Integration test showing all decorators with custom attributes working together"""
    
    # Define a workflow that uses tasks, agents, and tools with custom attributes
    @tool(
        name="calculator_tool", 
        attributes={
            "tool.type": "calculator",
            "tool.precision": "high",
            "tool.validated": True,
        }
    )
    def add_numbers(a, b):
        return a + b

    @agent(
        name="math_agent",
        attributes={
            "agent.model": "gpt-4",
            "agent.capability": "mathematics",
            "agent.confidence": 0.95,
        }
    )
    def solve_math_problem(problem):
        # Simulate using the calculator tool
        result = add_numbers(10, 5)
        return f"Solution to '{problem}': {result}"

    @task(
        name="validation_task",
        attributes={
            "task.category": "validation",
            "task.importance": "critical",
            "task.retry_count": 3,
        }
    )
    def validate_solution(solution):
        return f"Validated: {solution}"

    @workflow(
        name="math_solving_workflow",
        attributes={
            "workflow.domain": "education",
            "workflow.user_type": "student",
            "workflow.complexity": "medium",
        }
    )
    def solve_and_validate(problem):
        # Use agent to solve
        solution = solve_math_problem(problem)
        
        # Use task to validate
        validated = validate_solution(solution)
        
        return validated

    # Execute the workflow
    result = solve_and_validate("What is 10 + 5?")
    
    # Verify the result
    assert "15" in result
    assert "Validated" in result
    
    # Get all spans and verify they have the custom attributes
    spans = exporter.get_finished_spans()
    
    # Should have spans for: tool, agent, validation task, and workflow
    assert len(spans) == 4
    
    # Find each span type and verify custom attributes
    tool_span = next(span for span in spans if "calculator_tool.tool" in span.name)
    agent_span = next(span for span in spans if "math_agent.agent" in span.name)
    task_span = next(span for span in spans if "validation_task.task" in span.name)
    workflow_span = next(span for span in spans if "math_solving_workflow.workflow" in span.name)
    
    # Verify tool attributes
    assert tool_span.attributes.get("tool.type") == "calculator"
    assert tool_span.attributes.get("tool.precision") == "high"
    assert tool_span.attributes.get("tool.validated") is True
    
    # Verify agent attributes
    assert agent_span.attributes.get("agent.model") == "gpt-4"
    assert agent_span.attributes.get("agent.capability") == "mathematics"
    assert agent_span.attributes.get("agent.confidence") == 0.95
    
    # Verify task attributes
    assert task_span.attributes.get("task.category") == "validation"
    assert task_span.attributes.get("task.importance") == "critical"
    assert task_span.attributes.get("task.retry_count") == 3
    
    # Verify workflow attributes
    assert workflow_span.attributes.get("workflow.domain") == "education"
    assert workflow_span.attributes.get("workflow.user_type") == "student"
    assert workflow_span.attributes.get("workflow.complexity") == "medium"
    
    # Verify standard attributes are still present
    assert tool_span.attributes.get("traceloop.span.kind") == "tool"
    assert agent_span.attributes.get("traceloop.span.kind") == "agent"
    assert task_span.attributes.get("traceloop.span.kind") == "task"
    assert workflow_span.attributes.get("traceloop.span.kind") == "workflow"
    
    print("✅ Integration test passed! All custom attributes are correctly set.")
    

if __name__ == "__main__":
    # This would normally be run by pytest, but we can run it standalone
    # for demonstration purposes by mocking the exporter
    print("This integration test demonstrates the custom attributes functionality.")
    print("Run with: poetry run pytest test_integration_attributes.py -v")
