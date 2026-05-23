import html.parser
import sys

class HTMLTagChecker(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        
    def handle_starttag(self, tag, attrs):
        # void elements do not have closing tags
        if tag in ['img', 'br', 'hr', 'input', 'meta', 'link', 'source']:
            return
        self.stack.append((tag, self.getpos()))
        
    def handle_endtag(self, tag):
        if tag in ['img', 'br', 'hr', 'input', 'meta', 'link', 'source']:
            return
        if not self.stack:
            print(f"Extra closing tag </{tag}> at line {self.getpos()[0]}")
            return
        last_tag, pos = self.stack.pop()
        if last_tag != tag:
            print(f"Mismatch: open <{last_tag}> at line {pos[0]} closed by </{tag}> at line {self.getpos()[0]}")
            # Put back to keep tracking if needed, or exit
            
    def check(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            # remove django template syntax to avoid parsing confusion
            import re
            content = re.sub(r'{%.*?%}', '', content)
            content = re.sub(r'{{.*?}}', '', content)
            self.feed(content)
        if self.stack:
            print("Unclosed tags:")
            for tag, pos in reversed(self.stack):
                print(f"<{tag}> open at line {pos[0]}")
        else:
            print("All tags matched successfully!")

if __name__ == '__main__':
    checker = HTMLTagChecker()
    checker.check(sys.argv[1])
