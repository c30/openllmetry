#!/usr/bin/env python3
"""
Generate a module relationship diagram for the OpenLLMetry repository.
生成OpenLLMetry仓库的模块关系图。
"""

import os
import re
import sys
import json
from pathlib import Path
from collections import defaultdict
import toml

def parse_pyproject_toml(filepath):
    """Parse pyproject.toml file and extract dependencies"""
    try:
        with open(filepath, 'r') as f:
            data = toml.load(f)
        
        package_info = {
            'name': data.get('tool', {}).get('poetry', {}).get('name', 'unknown'),
            'description': data.get('tool', {}).get('poetry', {}).get('description', ''),
            'dependencies': {},
            'local_dependencies': []
        }
        
        # Extract dependencies
        deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
        for dep_name, dep_info in deps.items():
            if dep_name == 'python':
                continue
            
            if isinstance(dep_info, dict) and 'path' in dep_info:
                # Local dependency
                package_info['local_dependencies'].append(dep_name)
            else:
                # External dependency
                package_info['dependencies'][dep_name] = str(dep_info)
        
        return package_info
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def find_packages(root_dir):
    """Find all packages in the repository"""
    packages = []
    packages_dir = os.path.join(root_dir, 'packages')
    
    if not os.path.exists(packages_dir):
        return packages
    
    for item in os.listdir(packages_dir):
        item_path = os.path.join(packages_dir, item)
        if os.path.isdir(item_path) and item != '.gitkeep':
            pyproject_path = os.path.join(item_path, 'pyproject.toml')
            if os.path.exists(pyproject_path):
                pkg_info = parse_pyproject_toml(pyproject_path)
                if pkg_info:
                    pkg_info['directory'] = item
                    packages.append(pkg_info)
    
    return packages

def categorize_packages(packages):
    """Categorize packages by their type"""
    categories = {
        'core': [],  # Core SDK and semantic conventions
        'llm_providers': [],  # LLM provider instrumentations
        'vector_dbs': [],  # Vector database instrumentations
        'frameworks': [],  # Framework instrumentations
        'samples': [],  # Sample applications
        'others': []  # Other packages
    }
    
    for pkg in packages:
        name = pkg['name']
        
        if name in ['traceloop-sdk', 'opentelemetry-semantic-conventions-ai']:
            categories['core'].append(pkg)
        elif 'sample' in name.lower():
            categories['samples'].append(pkg)
        elif any(provider in name for provider in ['openai', 'anthropic', 'cohere', 'ollama', 'mistralai', 'bedrock', 'vertexai', 'google-generativeai', 'replicate', 'together', 'alephalpha', 'groq', 'watsonx', 'sagemaker']):
            categories['llm_providers'].append(pkg)
        elif any(db in name for db in ['pinecone', 'qdrant', 'weaviate', 'chromadb', 'milvus', 'lancedb', 'marqo']):
            categories['vector_dbs'].append(pkg)
        elif any(fw in name for fw in ['langchain', 'llamaindex', 'haystack', 'crewai', 'transformers', 'openai-agents']):
            categories['frameworks'].append(pkg)
        elif 'mcp' in name:
            categories['others'].append(pkg)
        else:
            categories['others'].append(pkg)
    
    return categories

def generate_graphviz_diagram(packages, categories, output_path):
    """Generate Graphviz DOT format diagram"""
    
    # Create a mapping of package names for easier lookup
    pkg_map = {pkg['name']: pkg for pkg in packages}
    
    dot_content = '''digraph OpenLLMetry {
    rankdir=TB;
    node [fontname="Arial", fontsize=10];
    edge [fontname="Arial", fontsize=8];
    
    // Graph styling
    graph [fontname="Arial", fontsize=12, labelloc="t", label="OpenLLMetry模块关系图\\nModule Relationship Diagram"];
    
    // Define subgraphs for categories
    subgraph cluster_core {
        label="核心组件 Core Components";
        style=filled;
        fillcolor=lightblue;
        fontsize=11;
        fontname="Arial";
'''
    
    # Add core components
    for pkg in categories['core']:
        dot_content += f'        "{pkg["name"]}" [shape=box, style=filled, fillcolor=lightcyan];\n'
    
    dot_content += '''    }
    
    subgraph cluster_llm {
        label="LLM提供商 LLM Providers";
        style=filled;
        fillcolor=lightgreen;
        fontsize=11;
        fontname="Arial";
'''
    
    # Add LLM providers
    for pkg in categories['llm_providers']:
        dot_content += f'        "{pkg["name"]}" [shape=ellipse, style=filled, fillcolor=lightgoldenrodyellow];\n'
    
    dot_content += '''    }
    
    subgraph cluster_vectordb {
        label="向量数据库 Vector Databases";
        style=filled;
        fillcolor=lightpink;
        fontsize=11;
        fontname="Arial";
'''
    
    # Add vector databases
    for pkg in categories['vector_dbs']:
        dot_content += f'        "{pkg["name"]}" [shape=ellipse, style=filled, fillcolor=mistyrose];\n'
    
    dot_content += '''    }
    
    subgraph cluster_frameworks {
        label="框架 Frameworks";
        style=filled;
        fillcolor=lightyellow;
        fontsize=11;
        fontname="Arial";
'''
    
    # Add frameworks
    for pkg in categories['frameworks']:
        dot_content += f'        "{pkg["name"]}" [shape=ellipse, style=filled, fillcolor=lemonchiffon];\n'
    
    dot_content += '''    }
    
    subgraph cluster_samples {
        label="示例应用 Sample Applications";
        style=filled;
        fillcolor=lavender;
        fontsize=11;
        fontname="Arial";
'''
    
    # Add samples
    for pkg in categories['samples']:
        dot_content += f'        "{pkg["name"]}" [shape=diamond, style=filled, fillcolor=thistle];\n'
    
    dot_content += '''    }
    
    // Other packages
'''
    
    for pkg in categories['others']:
        dot_content += f'    "{pkg["name"]}" [shape=hexagon, style=filled, fillcolor=lightgray];\n'
    
    dot_content += '\n    // Dependencies\n'
    
    # Add dependencies
    for pkg in packages:
        for dep in pkg['local_dependencies']:
            if dep in pkg_map:
                dot_content += f'    "{pkg["name"]}" -> "{dep}" [color=blue, style=solid];\n'
    
    # Add special relationships
    # All instrumentation packages depend on semantic conventions
    semantic_conv_name = 'opentelemetry-semantic-conventions-ai'
    for pkg in packages:
        if 'opentelemetry-instrumentation' in pkg['name'] and pkg['name'] != semantic_conv_name:
            dot_content += f'    "{pkg["name"]}" -> "{semantic_conv_name}" [color=red, style=dashed, label="uses"];\n'
    
    dot_content += '''
    // Legend
    subgraph cluster_legend {
        label="图例 Legend";
        style=filled;
        fillcolor=white;
        fontsize=10;
        fontname="Arial";
        
        legend_core [label="核心组件\\nCore", shape=box, style=filled, fillcolor=lightcyan];
        legend_llm [label="LLM提供商\\nLLM Provider", shape=ellipse, style=filled, fillcolor=lightgoldenrodyellow];
        legend_vector [label="向量数据库\\nVector DB", shape=ellipse, style=filled, fillcolor=mistyrose];
        legend_framework [label="框架\\nFramework", shape=ellipse, style=filled, fillcolor=lemonchiffon];
        legend_sample [label="示例\\nSample", shape=diamond, style=filled, fillcolor=thistle];
        legend_other [label="其他\\nOther", shape=hexagon, style=filled, fillcolor=lightgray];
        
        legend_dep_line [label="本地依赖 Local Dependency", shape=none];
        legend_use_line [label="使用关系 Uses", shape=none];
        
        legend_core -> legend_llm [style=invis];
        legend_llm -> legend_vector [style=invis];
        legend_vector -> legend_framework [style=invis];
        legend_framework -> legend_sample [style=invis];
        legend_sample -> legend_other [style=invis];
        legend_other -> legend_dep_line [style=invis];
        legend_dep_line -> legend_use_line [style=invis];
    }
}
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(dot_content)
    
    return dot_content

def generate_mermaid_diagram(packages, categories, output_path):
    """Generate Mermaid format diagram"""
    
    # Create a mapping of package names for easier lookup
    pkg_map = {pkg['name']: pkg for pkg in packages}
    
    mermaid_content = '''graph TB
    %% OpenLLMetry模块关系图 Module Relationship Diagram
    
    %% 核心组件 Core Components
    subgraph Core["核心组件 Core Components"]
'''
    
    # Add core components
    for pkg in categories['core']:
        safe_name = pkg['name'].replace('-', '_')
        mermaid_content += f'        {safe_name}["{pkg["name"]}"]\n'
    
    mermaid_content += '''    end
    
    %% LLM提供商 LLM Providers
    subgraph LLM["LLM提供商 LLM Providers"]
'''
    
    # Add LLM providers (limit to avoid overcrowding)
    for i, pkg in enumerate(categories['llm_providers'][:8]):  # Limit to first 8
        safe_name = pkg['name'].replace('-', '_')
        mermaid_content += f'        {safe_name}["{pkg["name"]}"]\n'
    
    if len(categories['llm_providers']) > 8:
        mermaid_content += f'        more_llm["... and {len(categories["llm_providers"]) - 8} more LLM providers"]\n'
    
    mermaid_content += '''    end
    
    %% 向量数据库 Vector Databases
    subgraph VectorDB["向量数据库 Vector Databases"]
'''
    
    # Add vector databases
    for pkg in categories['vector_dbs']:
        safe_name = pkg['name'].replace('-', '_')
        mermaid_content += f'        {safe_name}["{pkg["name"]}"]\n'
    
    mermaid_content += '''    end
    
    %% 框架 Frameworks
    subgraph Frameworks["框架 Frameworks"]
'''
    
    # Add frameworks
    for pkg in categories['frameworks']:
        safe_name = pkg['name'].replace('-', '_')
        mermaid_content += f'        {safe_name}["{pkg["name"]}"]\n'
    
    mermaid_content += '''    end
    
    %% 示例应用 Sample Applications
    subgraph Samples["示例应用 Sample Applications"]
'''
    
    # Add samples
    for pkg in categories['samples']:
        safe_name = pkg['name'].replace('-', '_')
        mermaid_content += f'        {safe_name}["{pkg["name"]}"]\n'
    
    mermaid_content += '''    end
    
    %% Dependencies
'''
    
    # Add key dependencies (focus on main relationships to avoid clutter)
    traceloop_sdk = None
    semantic_conv = None
    
    for pkg in packages:
        if pkg['name'] == 'traceloop-sdk':
            traceloop_sdk = pkg
        elif pkg['name'] == 'opentelemetry-semantic-conventions-ai':
            semantic_conv = pkg
    
    # Show traceloop-sdk dependencies to main categories
    if traceloop_sdk:
        sdk_safe = traceloop_sdk['name'].replace('-', '_')
        if semantic_conv:
            conv_safe = semantic_conv['name'].replace('-', '_')
            mermaid_content += f'    {sdk_safe} --> {conv_safe}\n'
        
        # Show dependencies to some representative packages from each category
        for category_name, pkg_list in categories.items():
            if category_name in ['llm_providers', 'vector_dbs', 'frameworks'] and pkg_list:
                # Pick first package from each category as representative
                pkg = pkg_list[0]
                pkg_safe = pkg['name'].replace('-', '_')
                mermaid_content += f'    {sdk_safe} --> {pkg_safe}\n'
    
    # Show semantic conventions used by instrumentation packages
    if semantic_conv:
        conv_safe = semantic_conv['name'].replace('-', '_')
        for category_name in ['llm_providers', 'vector_dbs', 'frameworks']:
            if categories[category_name]:
                pkg = categories[category_name][0]  # Representative package
                pkg_safe = pkg['name'].replace('-', '_')
                mermaid_content += f'    {pkg_safe} -.-> {conv_safe}\n'
    
    # Sample apps use traceloop-sdk
    if traceloop_sdk and categories['samples']:
        sdk_safe = traceloop_sdk['name'].replace('-', '_')
        for pkg in categories['samples']:
            pkg_safe = pkg['name'].replace('-', '_')
            mermaid_content += f'    {pkg_safe} --> {sdk_safe}\n'
    
    # Add styling
    mermaid_content += '''
    %% Styling
    classDef coreStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef llmStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef vectorStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef frameworkStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef sampleStyle fill:#fff8e1,stroke:#f57c00,stroke-width:2px
'''
    
    # Apply styles
    for pkg in categories['core']:
        safe_name = pkg['name'].replace('-', '_')
        mermaid_content += f'    class {safe_name} coreStyle\n'
    
    for pkg in categories['llm_providers'][:8]:  # Match the limit above
        safe_name = pkg['name'].replace('-', '_')
        mermaid_content += f'    class {safe_name} llmStyle\n'
    
    for pkg in categories['vector_dbs']:
        safe_name = pkg['name'].replace('-', '_')
        mermaid_content += f'    class {safe_name} vectorStyle\n'
    
    for pkg in categories['frameworks']:
        safe_name = pkg['name'].replace('-', '_')
        mermaid_content += f'    class {safe_name} frameworkStyle\n'
    
    for pkg in categories['samples']:
        safe_name = pkg['name'].replace('-', '_')
        mermaid_content += f'    class {safe_name} sampleStyle\n'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(mermaid_content)
    
    return mermaid_content

def main():
    repo_root = '/home/runner/work/openllmetry/openllmetry'
    
    print("正在分析OpenLLMetry仓库结构...")
    print("Analyzing OpenLLMetry repository structure...")
    
    # Find all packages
    packages = find_packages(repo_root)
    print(f"发现 {len(packages)} 个包 Found {len(packages)} packages")
    
    # Categorize packages
    categories = categorize_packages(packages)
    
    print("\n包分类 Package Categories:")
    for category, pkg_list in categories.items():
        print(f"  {category}: {len(pkg_list)} packages")
        for pkg in pkg_list:
            print(f"    - {pkg['name']}")
    
    # Generate diagrams
    print("\n生成图表 Generating diagrams...")
    
    # Graphviz DOT format
    dot_path = '/tmp/openllmetry_modules.dot'
    generate_graphviz_diagram(packages, categories, dot_path)
    print(f"Graphviz DOT文件已生成: {dot_path}")
    
    # Mermaid format
    mermaid_path = '/tmp/openllmetry_modules.mmd'
    generate_mermaid_diagram(packages, categories, mermaid_path)
    print(f"Mermaid文件已生成: {mermaid_path}")
    
    # Generate summary JSON
    summary = {
        'total_packages': len(packages),
        'categories': {cat: len(pkgs) for cat, pkgs in categories.items()},
        'packages': [{'name': pkg['name'], 'description': pkg['description']} for pkg in packages]
    }
    
    with open('/tmp/openllmetry_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("分析完成！Analysis complete!")
    return packages, categories

if __name__ == '__main__':
    main()