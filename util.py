"""Code from http://djangosnippets.org/snippets/942/

TODO: This won't work for IncludeNode.
"""

from django.template.loader_tags import BlockNode, ExtendsNode
from django.template import loader, Context


def _get_template(template):
    if isinstance(template, (tuple, list)):
        return loader.select_template(template)
    return loader.get_template(template)


class BlockNotFound(Exception):
    """The requested block did not exist."""
    pass


def render_template_block(template, block, context):
    """
    Renders a single block from a template.
    This template should have previously been rendered.
    """
    template._render(context)
    return _render_template_block_nodelist(template.nodelist, block, context)


def _render_template_block_nodelist(nodelist, block, context):
    for node in nodelist:
        if isinstance(node, BlockNode) and node.name == block:
            return node.render(context)
        for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
            if hasattr(node, key):
                try:
                    rendered = _render_template_block_nodelist(
                        getattr(node, key), block, context)
                except:
                    pass
                else:
                    return rendered
    for node in nodelist:
        if isinstance(node, ExtendsNode):
            try:
                rendered = render_template_block(
                    node.get_parent(context), block, context)
            except BlockNotFound:
                pass
            else:
                return rendered
    raise BlockNotFound


def render_block_to_string(template_name, block, dictionary=None, context_instance=None):
    dictionary = dictionary or {}
    t = _get_template(template_name)
    if context_instance:
        context_instance.update(dictionary)
    else:
        context_instance = Context(dictionary)
    return render_template_block(t, block, context_instance)
