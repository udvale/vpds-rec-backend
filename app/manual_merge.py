"""
Manual/regex-based component merging when AI is unavailable.
Creates a basic but functional combined component.
"""
import re
from typing import List, Set

def extract_imports(code_snippets: List[str]) -> Set[str]:
    """Extract and deduplicate all import statements."""
    imports = set()
    
    for snippet in code_snippets:
        # Find all import lines
        import_lines = re.findall(r'^import\s+.*?;?$', snippet, re.MULTILINE)
        for imp in import_lines:
            # Clean up the import
            clean_import = imp.strip().rstrip(';') + ';'
            imports.add(clean_import)
    
    return imports

def extract_component_logic(code: str) -> dict:
    """Extract key parts of a component for merging."""
    # Extract component name
    comp_match = re.search(r'export\s+const\s+(\w+)\s*=', code)
    comp_name = comp_match.group(1) if comp_match else "Component"
    
    # Extract JSX content (everything between return and the closing of return)
    jsx_match = re.search(r'return\s*\(?([^}]+)\)?;?\s*}', code, re.DOTALL)
    jsx_content = jsx_match.group(1).strip() if jsx_match else "<div>Error extracting JSX</div>"
    
    # Clean up JSX (remove outer parentheses if present)
    jsx_content = re.sub(r'^\s*\(\s*', '', jsx_content)
    jsx_content = re.sub(r'\s*\)\s*$', '', jsx_content)
    
    # Extract any variable declarations
    var_matches = re.findall(r'const\s+\w+\s*=\s*[^;]+;', code)
    
    return {
        "name": comp_name,
        "jsx": jsx_content,
        "variables": var_matches
    }

def create_form_layout(components: List[dict], export_name: str) -> str:
    """Create a form-like layout when appropriate."""
    jsx_parts = []
    
    for comp in components:
        jsx = comp["jsx"]
        # Wrap in form-friendly containers
        if "input" in jsx.lower() or "textfield" in jsx.lower():
            jsx_parts.append(f"      <div className=\"mb-4\">\n        {jsx}\n      </div>")
        elif "button" in jsx.lower():
            jsx_parts.append(f"      <div className=\"mt-6\">\n        {jsx}\n      </div>")
        else:
            jsx_parts.append(f"      <div className=\"mb-3\">\n        {jsx}\n      </div>")
    
    form_content = "\n".join(jsx_parts)
    
    return f"""    <div className=\"max-w-md mx-auto p-6 bg-white rounded-lg shadow-md\">
      <form className=\"space-y-4\">
{form_content}
      </form>
    </div>"""

def create_profile_layout(components: List[dict], export_name: str) -> str:
    """Create a profile-like layout."""
    jsx_parts = []
    
    for comp in components:
        jsx = comp["jsx"]
        if "avatar" in jsx.lower():
            jsx_parts.append(f"      <div className=\"flex justify-center mb-4\">\n        {jsx}\n      </div>")
        elif "badge" in jsx.lower():
            jsx_parts.append(f"      <div className=\"flex flex-wrap gap-2 mb-3\">\n        {jsx}\n      </div>")
        else:
            jsx_parts.append(f"      <div className=\"mb-3\">\n        {jsx}\n      </div>")
    
    profile_content = "\n".join(jsx_parts)
    
    return f"""    <div className=\"max-w-sm mx-auto p-6 bg-white rounded-lg shadow-lg text-center\">
{profile_content}
    </div>"""

def create_generic_layout(components: List[dict], export_name: str) -> str:
    """Create a generic vertical layout."""
    jsx_parts = []
    
    for comp in components:
        jsx = comp["jsx"]
        jsx_parts.append(f"      <div className=\"mb-4\">\n        {jsx}\n      </div>")
    
    generic_content = "\n".join(jsx_parts)
    
    return f"""    <div className=\"p-6 space-y-4\">
{generic_content}
    </div>"""

def merge_variants(code_snippets: List[str], export_name: str) -> str:
    """
    Merge multiple component code snippets using regex-based approach.
    """
    if not code_snippets:
        return f"export default function {export_name}() {{ return <div>No components provided</div>; }}"
    
    # Extract imports
    all_imports = extract_imports(code_snippets)
    imports_section = "\n".join(sorted(all_imports))
    
    # Extract component logic from each snippet
    components = []
    variables = []
    
    for snippet in code_snippets:
        comp_info = extract_component_logic(snippet)
        components.append(comp_info)
        variables.extend(comp_info["variables"])
    
    # Deduplicate variables
    unique_vars = list(set(variables))
    variables_section = "\n  ".join(unique_vars) if unique_vars else ""
    
    # Determine layout based on export name/content
    export_lower = export_name.lower()
    
    if any(word in export_lower for word in ['form', 'login', 'signup', 'register']):
        main_jsx = create_form_layout(components, export_name)
    elif any(word in export_lower for word in ['profile', 'user', 'account']):
        main_jsx = create_profile_layout(components, export_name)
    else:
        main_jsx = create_generic_layout(components, export_name)
    
    # Build the final component
    component_body = f"""export default function {export_name}() {{
  {variables_section}

  return (
{main_jsx}
  );
}}"""
    
    # Combine everything
    full_component = f"""{imports_section}

{component_body}"""
    
    print(f"🔧 Manual merge completed for {export_name}")
    return full_component