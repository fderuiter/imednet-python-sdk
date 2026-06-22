"""Sphinx extension for generating configuration documentation."""

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx.util.docutils import SphinxDirective

from imednet.config import Config


class ConfigSchemaDirective(SphinxDirective):
    """A custom Sphinx directive to document configuration variables."""
    has_content = False
    required_arguments = 0
    optional_arguments = 1
    option_spec = {
        'category': directives.unchanged
    }

    def run(self):
        """Generate the documentation nodes for the configuration schema."""
        filter_category = self.options.get('category', None)
        
        table = nodes.table(classes=["docutils", "align-default"])
        tgroup = nodes.tgroup(cols=4)
        table += tgroup
        
        # Columns: Variable, Category, Description, Default
        for w in (25, 15, 45, 15):
            tgroup += nodes.colspec(colwidth=w)
            
        thead = nodes.thead()
        tgroup += thead
        row = nodes.row()
        for text in ("Variable", "Category", "Description", "Default"):
            entry = nodes.entry()
            entry += nodes.paragraph(text=text)
            row += entry
        thead += row
        
        tbody = nodes.tbody()
        tgroup += tbody
        
        prefix = Config.model_config.get("env_prefix", "")
        
        count = 0
        for name, field in Config.model_fields.items():
            category = field.json_schema_extra.get("category", "General") if field.json_schema_extra else "General"
            
            if filter_category and category != filter_category:
                continue
                
            count += 1
            env_name = (prefix + name).upper()
            row = nodes.row()
            
            # Variable name
            entry = nodes.entry()
            entry += nodes.literal(text=env_name)
            row += entry
            
            # Category
            entry = nodes.entry()
            entry += nodes.paragraph(text=category)
            row += entry
            
            # Description
            desc = field.description or "No description provided."
            entry = nodes.entry()
            parsed_node = nodes.Element()
            self.state.nested_parse(StringList([desc]), 0, parsed_node)
            entry += parsed_node.children
            row += entry
            
            # Default
            if getattr(field, "is_required", lambda: False)():
                default_val = "Required"
            else:
                default_val = str(field.default) if field.default is not None else "None"
            entry = nodes.entry()
            entry += nodes.literal(text=default_val)
            row += entry
            
            tbody += row
            
        if count == 0:
            return []
            
        return [table]


def setup(app):
    """Register the extension with Sphinx."""
    app.add_directive('config-schema', ConfigSchemaDirective)
    return {'version': '1.0', 'parallel_read_safe': True}
