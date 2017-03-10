import os
import sys

package_file = os.path.normpath(os.path.abspath(__file__))
package_path = os.path.dirname(package_file)
lib_path = os.path.join(package_path, "lib")

from premailer import Premailer
from docutils.core import publish_parts
from docutils.writers.html4css1 import Writer, HTMLTranslator

css_file = os.path.abspath(os.path.join(package_path, "../github.css"))
# print (css_file)

class GitHubHTMLTranslator(HTMLTranslator):

    # removes the <div class="document"> tag wrapped around docs
    # see also: http://bit.ly/1exfq2h (warning! sourceforge link.)
    def depart_document(self, node):
        HTMLTranslator.depart_document(self, node)
        self.html_body.pop(0)  # pop the starting <div> off
        self.html_body.pop()   # pop the ending </div> off

    def visit_literal_block(self, node):
        classes = node.attributes['classes']
        if len(classes) >= 2 and classes[0] == 'code':
            language = classes[1]
            del classes[:]
            self.body.append(self.starttag(node, 'pre', lang=language, CLASS='codehilite'))
        else:
            self.body.append(self.starttag(node, 'pre', CLASS='codehilite'))

    def visit_section(self, node):
        self.section_level += 1
        #self.body.append(
        #    self.starttag(node, 'div', CLASS='section'))

    def depart_section(self, node):
        self.section_level -= 1


def render(text, **kwargs):
    settings_overrides = {
        'cloak_email_addresses': True,
        'file_insertion_enabled': False,
        'raw_enabled': False,
        'strip_comments': True,
        'doctitle_xform': False,
        'report_level': 5,
        'syntax_highlight': 'short',
        'math_output': 'latex',
        'input_encoding': 'utf-8',
        'output_encoding': 'utf-8',
    }

    writer = Writer()
    writer.translator_class = GitHubHTMLTranslator
    output = publish_parts(
        text, writer=writer, settings_overrides=settings_overrides
    )

    if 'html_body' not in output:
        return ""

    out = '<div class="markdown-body">'
    out += output['html_body']
    out += '</div>'

    p = Premailer(out, remove_classes=True, external_styles=css_file,
                  disable_leftover_css=True, disable_basic_attributes=['bgcolor'])
    content = p.transform()
    return content.replace('html><body', 'div').replace('body></html', 'div')
