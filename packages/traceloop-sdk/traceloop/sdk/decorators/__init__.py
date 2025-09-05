from typing import Optional, TypeVar, Callable, Any, ParamSpec, Awaitable, Dict
import warnings

from opentelemetry.semconv_ai import TraceloopSpanKindValues

from traceloop.sdk.decorators.base import (
    entity_class,
    entity_method,
)

P = ParamSpec("P")
R = TypeVar("R")
F = TypeVar("F", bound=Callable[P, R | Awaitable[R]])


def task(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    tlp_span_kind: Optional[TraceloopSpanKindValues] = TraceloopSpanKindValues.TASK,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    if method_name is None:
        return entity_method(name=name, version=version, tlp_span_kind=tlp_span_kind, attributes=attributes)
    else:
        return entity_class(
            name=name,
            version=version,
            method_name=method_name,
            tlp_span_kind=tlp_span_kind,
            attributes=attributes,
        )


def workflow(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    tlp_span_kind: Optional[TraceloopSpanKindValues] = TraceloopSpanKindValues.WORKFLOW,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    if method_name is None:
        return entity_method(name=name, version=version, tlp_span_kind=tlp_span_kind, attributes=attributes)
    else:
        return entity_class(
            name=name,
            version=version,
            method_name=method_name,
            tlp_span_kind=tlp_span_kind,
            attributes=attributes,
        )


def agent(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    return workflow(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=TraceloopSpanKindValues.AGENT,
        attributes=attributes,
    )


def tool(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    return task(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=TraceloopSpanKindValues.TOOL,
        attributes=attributes,
    )


def llm(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    llm_span_kind = getattr(TraceloopSpanKindValues, 'LLM', TraceloopSpanKindValues.TASK)
    return task(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=llm_span_kind,
        attributes=attributes,
    )


def mcp(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    mcp_span_kind = getattr(TraceloopSpanKindValues, 'MCP', TraceloopSpanKindValues.TASK)
    return task(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=mcp_span_kind,
        attributes=attributes,
    )


# Async Decorators - Deprecated
def atask(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    tlp_span_kind: Optional[TraceloopSpanKindValues] = TraceloopSpanKindValues.TASK,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    warnings.warn(
        "DeprecationWarning: The @atask decorator will be removed in a future version. "
        "Please migrate to @task for both sync and async operations.",
        DeprecationWarning,
        stacklevel=2,
    )
    if method_name is None:
        return entity_method(name=name, version=version, tlp_span_kind=tlp_span_kind, attributes=attributes)
    else:
        return entity_class(
            name=name,
            version=version,
            method_name=method_name,
            tlp_span_kind=tlp_span_kind,
            attributes=attributes,
        )


def aworkflow(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    tlp_span_kind: Optional[TraceloopSpanKindValues] = TraceloopSpanKindValues.WORKFLOW,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    warnings.warn(
        "DeprecationWarning: The @aworkflow decorator will be removed in a future version. "
        "Please migrate to @workflow for both sync and async operations.",
        DeprecationWarning,
        stacklevel=2,
    )
    if method_name is None:
        return entity_method(name=name, version=version, tlp_span_kind=tlp_span_kind, attributes=attributes)
    else:
        return entity_class(
            name=name,
            version=version,
            method_name=method_name,
            tlp_span_kind=tlp_span_kind,
            attributes=attributes,
        )


def aagent(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    warnings.warn(
        "DeprecationWarning: The @aagent decorator will be removed in a future version. "
        "Please migrate to @agent for both sync and async operations.",
        DeprecationWarning,
        stacklevel=2,
    )
    return atask(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=TraceloopSpanKindValues.AGENT,
        attributes=attributes,
    )


def atool(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    warnings.warn(
        "DeprecationWarning: The @atool decorator will be removed in a future version. "
        "Please migrate to @tool for both sync and async operations.",
        DeprecationWarning,
        stacklevel=2,
    )
    return atask(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=TraceloopSpanKindValues.TOOL,
        attributes=attributes,
    )
